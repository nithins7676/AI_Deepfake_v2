from flask import Flask, render_template, request, jsonify, send_from_directory
import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import os
from werkzeug.utils import secure_filename
import requests
import numpy as np
from flask_cors import CORS
import time
import glob
from functools import wraps

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[ENV] Loaded .env file")
except ImportError:
    print("[ENV] python-dotenv not installed, using system environment variables only")

from video_processor import VideoProcessor
from gradcam_vit import generate_vit_gradcam_map, overlay_heatmap_on_image

# Sightengine API credentials (support multiple accounts via environment variables)
# Primary (backward compatible):
SIGHTENGINE_API_USER = os.getenv('SIGHTENGINE_API_USER', 'YOUR_API_USER')
SIGHTENGINE_API_SECRET = os.getenv('SIGHTENGINE_API_SECRET', 'YOUR_API_SECRET')

# Optional secondary accounts (e.g. multiple free-tier accounts)
SIGHTENGINE_ACCOUNTS = []

# SerpAPI reverse image search (primary - more reliable)
SERPAPI_KEY = os.getenv('SERPAPI_API_KEY') or os.getenv('SERPAPI_KEY')

# RapidAPI reverse image search (fallback)
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'reverse-image-search1.p.rapidapi.com')

# Supabase authentication
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://klhdatzliltkqvrpbnry.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsaGRhdHpsaWx0a3F2cnBibnJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUwOTYwNjgsImV4cCI6MjA4MDY3MjA2OH0.Duh3NyHGVO2wvl2klEJo8rXEp8HxV2F9FL0VB3jCyDU')

# Collect up to two extra accounts: SIGHTENGINE_API_USER_1/2, SIGHTENGINE_API_SECRET_1/2
for idx in (1, 2):
    user = os.getenv(f'SIGHTENGINE_API_USER_{idx}')
    secret = os.getenv(f'SIGHTENGINE_API_SECRET_{idx}')
    if user and secret and user != 'YOUR_API_USER' and secret != 'YOUR_API_SECRET':
        SIGHTENGINE_ACCOUNTS.append((user, secret))

# Always include the primary account last if it is configured
if SIGHTENGINE_API_USER != 'YOUR_API_USER' and SIGHTENGINE_API_SECRET != 'YOUR_API_SECRET':
    SIGHTENGINE_ACCOUNTS.append((SIGHTENGINE_API_USER, SIGHTENGINE_API_SECRET))

app = Flask(__name__)
# Allow CORS so the Next.js frontend (localhost:3000) can call this API
CORS(app, resources={r"/*": {"origins": "*"}})

# Authentication decorator
def verify_token(f):
    """Verify Supabase JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth for root endpoint
        if request.path == '/':
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        try:
            token = auth_header.replace('Bearer ', '')
            # Verify token with Supabase
            verify_url = f"{SUPABASE_URL}/auth/v1/user"
            headers = {
                'Authorization': f'Bearer {token}',
                'apikey': SUPABASE_ANON_KEY,
            }
            resp = requests.get(verify_url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                user_data = resp.json()
                # Token is valid, add user info to request context
                request.user = user_data
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Invalid or expired token'}), 401
        except requests.exceptions.RequestException as e:
            print(f"[AUTH] Token verification error: {e}")
            return jsonify({'error': 'Token verification failed'}), 401
        except Exception as e:
            print(f"[AUTH] Unexpected error: {e}")
            return jsonify({'error': 'Authentication error'}), 401
    
    return decorated_function

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Cleanup function for old heatmap files (older than 1 hour)
def cleanup_old_heatmaps(max_age_hours=1):
    """Delete heatmap files older than max_age_hours"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Clean up image heatmaps
        image_heatmap_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'image_heatmaps')
        if os.path.exists(image_heatmap_dir):
            for filepath in glob.glob(os.path.join(image_heatmap_dir, '*_heatmap.png')):
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        print(f"[CLEANUP] Deleted old heatmap: {os.path.basename(filepath)}")
                except Exception as e:
                    print(f"[CLEANUP] Error deleting {filepath}: {e}")
        
        # Clean up video heatmaps
        video_heatmap_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'video_heatmaps')
        if os.path.exists(video_heatmap_dir):
            for root, dirs, files in os.walk(video_heatmap_dir):
                for file in files:
                    if file.endswith('.png'):
                        filepath = os.path.join(root, file)
                        try:
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > max_age_seconds:
                                os.remove(filepath)
                                print(f"[CLEANUP] Deleted old video heatmap: {filepath}")
                        except Exception as e:
                            print(f"[CLEANUP] Error deleting {filepath}: {e}")
    except Exception as e:
        print(f"[CLEANUP] Error during cleanup: {e}")

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load model
def load_model():
    model = models.vit_b_16(weights="IMAGENET1K_V1")
    model.heads.head = torch.nn.Linear(768, 3)
    
    # Load weights
    model_path = "vit3class.pth"
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    
    return model

model = load_model()
print("Model loaded successfully!")

# Class names
class_names = {0: "AI-Generated Face", 1: "Deepfake", 2: "Real"}

# Image / frame transform
# MUST match training preprocessing exactly!
# Training used [0.5, 0.5, 0.5] normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

# Video processor (reuses same model, device and transform)
video_processor = VideoProcessor(model=model, device=device, class_names=class_names, transform=transform)


# Run cleanup on startup
cleanup_old_heatmaps(max_age_hours=1)
print("[CLEANUP] Initial cleanup completed")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded/generated files (e.g. Grad-CAM heatmaps)."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/cleanup', methods=['POST'])
def cleanup_endpoint():
    """Manual cleanup endpoint to delete old heatmap files"""
    try:
        cleanup_old_heatmaps(max_age_hours=1)
        return jsonify({'message': 'Cleanup completed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
@verify_token
def predict():
    """Image prediction endpoint (local ViT model + optional Sightengine ensemble)."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Allowed extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'avif', 'webp'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, AVIF, WebP'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # ------------------------------
        # 1) Local model inference
        # ------------------------------
        img = Image.open(filepath).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            logits = model(img_tensor)
            probs_local = F.softmax(logits, dim=1)[0]
        
        probs_local_np = probs_local.cpu().numpy()
        pred_idx_local = probs_local.argmax().item()
        conf_local = probs_local_np[pred_idx_local] * 100.0
        
        # Grad-CAM heatmap overlay for the local prediction
        heatmap_url = None
        try:
            heatmap = generate_vit_gradcam_map(
                model=model,
                device=device,
                pil_image=img,
                transform=transform,
                target_index=pred_idx_local,
            )
            overlay = overlay_heatmap_on_image(img, heatmap, alpha=0.5)

            # Save under uploads/image_heatmaps/
            heatmap_rel_dir = os.path.join('image_heatmaps')
            heatmap_dir = os.path.join(app.config['UPLOAD_FOLDER'], heatmap_rel_dir)
            os.makedirs(heatmap_dir, exist_ok=True)
            heatmap_filename = f"{os.path.splitext(filename)[0]}_heatmap.png"
            heatmap_rel_path = os.path.join(heatmap_rel_dir, heatmap_filename)
            heatmap_fs_path = os.path.join(app.config['UPLOAD_FOLDER'], heatmap_rel_path)
            overlay.save(heatmap_fs_path)

            # Public URL for browser
            heatmap_url = '/uploads/' + heatmap_rel_path.replace('\\', '/')
            
            # Clean up old heatmaps after generating new one
            cleanup_old_heatmaps(max_age_hours=1)
        except Exception:
            heatmap_url = None

        # ------------------------------
        # 2) Optional Sightengine ensemble (kept in main /predict for speed)
        # ------------------------------
        se_probs = None
        se_raw = None

        if SIGHTENGINE_ACCOUNTS:
            last_error = None

            for idx, (api_user, api_secret) in enumerate(SIGHTENGINE_ACCOUNTS, start=1):
                try:
                    print(f"[SIGHTENGINE][image] Using account #{idx} for analysis: {filepath}")
                    with open(filepath, 'rb') as img_file:
                        resp = requests.post(
                            'https://api.sightengine.com/1.0/check.json',
                            files={'media': img_file},
                            data={
                                'models': 'genai',
                                'api_user': api_user,
                                'api_secret': api_secret,
                            },
                            timeout=60,
                        )

                    if resp.status_code != 200:
                        last_error = f"Sightengine image API error (account #{idx}): {resp.status_code} - {resp.text}"
                        print(f"[SIGHTENGINE][image] {last_error}")
                        continue

                    se_raw = resp.json()
                    print(f"[SIGHTENGINE][image] API response from account #{idx}: {se_raw}")

                    # Parse AI / deepfake scores from response (similar logic to video)
                    ai_score = 0.0
                    deepfake_score = 0.0

                    if 'type' in se_raw:
                        t = se_raw['type']
                        ai_score = float(t.get('ai_generated', 0.0))
                        deepfake_score = float(t.get('deepfake', 0.0)) if 'deepfake' in t else 0.0
                    elif 'genai' in se_raw:
                        g = se_raw['genai']
                        ai_score = float(g.get('ai_generated', 0.0))
                        deepfake_score = float(g.get('deepfake', 0.0))

                    real_score = 1.0 - max(ai_score, deepfake_score)
                    real_score = max(0.0, min(1.0, real_score))

                    se_probs = [ai_score, deepfake_score, real_score]
                    break
                except requests.exceptions.RequestException as e:
                    last_error = f"Sightengine image request failed for account #{idx}: {e}"
                    print(f"[SIGHTENGINE][image] {last_error}")
                    continue

        # ------------------------------
        # 3) Combine local + Sightengine (confidence-aware ensemble)
        # ------------------------------
        combined_probs = probs_local_np.copy()
        ensemble_source = 'local_model_only'

        if se_probs is not None:
            se_probs_np = np.array(se_probs, dtype=float)
            if se_probs_np.shape == combined_probs.shape:
                ai_se, df_se, real_se = se_probs_np.tolist()

                # If Sightengine is very confident it's AI-generated or deepfake,
                # trust Sightengine and override the prediction for that class.
                if ai_se >= 0.80:
                    combined_probs = se_probs_np
                    ensemble_source = 'sightengine_strong_ai_generated'
                elif df_se >= 0.80:
                    combined_probs = se_probs_np
                    ensemble_source = 'sightengine_strong_deepfake'
                else:
                    # Otherwise, average local + Sightengine (simple ensemble)
                    combined_probs = 0.5 * combined_probs + 0.5 * se_probs_np
                    ensemble_source = 'local_model + sightengine (avg)'

        final_idx = int(combined_probs.argmax())
        final_conf = combined_probs[final_idx] * 100.0

        # Clean up original upload
        os.remove(filepath)
        
        # Return results (keeping backward-compatible fields)
        result = {
            'prediction': class_names[final_idx],
            'confidence': f"{final_conf:.2f}%",
            'all_scores': {
                class_names[i]: f"{combined_probs[i]*100:.2f}%" 
                for i in range(3)
            },
'heatmap_url': heatmap_url,
            'sources': {
                'ensemble': ensemble_source,
                'local_model': {
                    'prediction': class_names[pred_idx_local],
                    'confidence': f"{conf_local:.2f}%",
                    'scores': {
                        class_names[i]: f"{probs_local_np[i]*100:.2f}%" for i in range(3)
                    },
                },
                'sightengine': se_raw,
            },
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reverse_search', methods=['POST'])
@verify_token
def reverse_search():
    """Separate endpoint: reverse image search with multiple providers.

    This keeps /predict fast (model + Sightengine), while this endpoint can be slower
    without blocking primary deepfake detection.
    
    Priority order:
    1. SerpAPI (Google reverse image search) - primary, most reliable
    2. RapidAPI (reverse-image-search1) - fallback
    3. Google direct link - final fallback
    """
    # This endpoint should NEVER break the app; on any error, just return reverse_search: null
    if 'file' not in request.files:
        return jsonify({'reverse_search': None, 'error': 'No file provided'}), 200

    file = request.files['file']
    if file.filename == '':
        return jsonify({'reverse_search': None, 'error': 'No file selected'}), 200

    # Check if at least one API is configured
    if not SERPAPI_KEY and not RAPIDAPI_KEY:
        return jsonify({'reverse_search': None, 'error': 'No API keys configured (SERPAPI_API_KEY or RAPIDAPI_KEY)'}), 200

    # Save file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    reverse_search_info = None
    image_public_url = None
    
    try:
        # Upload to tmpfiles.org to get public URL (needed for both SerpAPI and RapidAPI)
        with open(filepath, 'rb') as f_img:
            tmp_resp = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files={'file': (filename, f_img)},
                timeout=10,
            )
        if tmp_resp.status_code == 200:
            tmp_data = tmp_resp.json()
            if isinstance(tmp_data, dict):
                data_block = tmp_data.get('data') or tmp_data
                image_public_url = data_block.get('url') or data_block.get('link')

        if image_public_url:
            # ============================================
            # 1. Try SerpAPI first (most reliable)
            # ============================================
            if SERPAPI_KEY and not reverse_search_info:
                try:
                    # Convert tmpfiles.org URL to direct download URL if needed
                    # tmpfiles.org returns URLs like: http://tmpfiles.org/14357200/682810.jpg
                    # Need to convert to: https://tmpfiles.org/dl/14357200/682810.jpg
                    direct_url = image_public_url
                    if 'tmpfiles.org' in image_public_url and '/dl/' not in image_public_url:
                        # Replace the path to use /dl/ for direct download
                        parts = image_public_url.replace('http://', 'https://').split('/')
                        if len(parts) >= 4:
                            direct_url = f"https://tmpfiles.org/dl/{'/'.join(parts[3:])}"
                    
                    print(f"[REVERSE_SEARCH] Trying SerpAPI...")
                    
                    serpapi_url = 'https://serpapi.com/search'
                    serpapi_resp = None
                    
                    # Method 1: Try base64 encoding (most reliable)
                    try:
                        import base64
                        with open(filepath, 'rb') as img_file:
                            image_data = img_file.read()
                            # Limit image size to avoid API limits (max ~2MB for base64)
                            if len(image_data) > 1500000:  # ~1.5MB
                                # Resize image if too large
                                from PIL import Image
                                img = Image.open(filepath)
                                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                                import io
                                buffer = io.BytesIO()
                                img.save(buffer, format='JPEG', quality=85)
                                image_data = buffer.getvalue()
                            
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                        
                        serpapi_params = {
                            'engine': 'google_reverse_image',
                            'image': image_base64,
                            'api_key': SERPAPI_KEY,
                            'num': 10,
                        }
                        
                        print(f"[REVERSE_SEARCH] SerpAPI: Trying base64 method (size: {len(image_base64)} chars)")
                        serpapi_resp = requests.get(serpapi_url, params=serpapi_params, timeout=45)
                        
                        if serpapi_resp.status_code != 200:
                            raise Exception(f"Base64 method returned {serpapi_resp.status_code}")
                            
                    except Exception as base64_error:
                        print(f"[REVERSE_SEARCH] Base64 method failed: {base64_error}, trying URL method...")
                        
                        # Method 2: Fallback to URL method
                        # Convert tmpfiles.org URL to direct download URL
                        direct_url = image_public_url
                        if 'tmpfiles.org' in image_public_url:
                            # tmpfiles.org format: http://tmpfiles.org/14357200/682810.jpg
                            # Direct format: https://tmpfiles.org/dl/14357200/682810.jpg
                            if '/dl/' not in image_public_url:
                                url_parts = image_public_url.replace('http://', '').replace('https://', '').split('/')
                                if len(url_parts) >= 3:
                                    direct_url = f"https://tmpfiles.org/dl/{'/'.join(url_parts[1:])}"
                        
                        serpapi_params = {
                            'engine': 'google_reverse_image',
                            'image_url': direct_url,
                            'api_key': SERPAPI_KEY,
                            'num': 10,
                        }
                        
                        print(f"[REVERSE_SEARCH] SerpAPI: Trying URL method: {direct_url[:60]}...")
                        serpapi_resp = requests.get(serpapi_url, params=serpapi_params, timeout=45)
                    
                    if serpapi_resp.status_code == 200:
                        serpapi_data = serpapi_resp.json()
                        print(f"[REVERSE_SEARCH] SerpAPI response keys: {list(serpapi_data.keys())[:10]}")
                        
                        links = []
                        
                        # Parse SerpAPI response - check multiple possible result locations
                        # SerpAPI reverse image search returns results in various formats
                        result_sections = [
                            serpapi_data.get('inline_images', []),
                            serpapi_data.get('related_images', []),
                            serpapi_data.get('image_results', []),
                            serpapi_data.get('visual_matches', []),
                            serpapi_data.get('images_results', []),
                        ]
                        
                        for section in result_sections:
                            if isinstance(section, list):
                                for item in section[:10]:
                                    if isinstance(item, dict):
                                        title = (
                                            item.get('title')
                                            or item.get('name')
                                            or item.get('source')
                                            or item.get('thumbnail_title')
                                            or ''
                                        )
                                        link = (
                                            item.get('link')
                                            or item.get('url')
                                            or item.get('source_url')
                                            or item.get('original')
                                            or item.get('source_page_link')
                                            or ''
                                        )
                                        if link and link not in [l['link'] for l in links]:
                                            links.append({'title': title or link, 'link': link})
                        
                        # Also check for regular search results (pages where image appears)
                        if 'organic_results' in serpapi_data:
                            for result in serpapi_data['organic_results'][:10]:
                                if isinstance(result, dict):
                                    title = result.get('title', '')
                                    link = result.get('link', '')
                                    if link and link not in [l['link'] for l in links]:
                                        links.append({'title': title or link, 'link': link})
                        
                        # Check for visual matches (most relevant for reverse image search)
                        if 'visual_matches' in serpapi_data:
                            for match in serpapi_data['visual_matches'][:10]:
                                if isinstance(match, dict):
                                    title = match.get('title', match.get('source', ''))
                                    link = match.get('link', match.get('source_url', ''))
                                    if link and link not in [l['link'] for l in links]:
                                        links.append({'title': title or link, 'link': link})
                        
                        if links:
                            reverse_search_info = {
                                'engine': 'serpapi_google_reverse_image',
                                'image_url': image_public_url,
                                'results': links[:10],  # Limit to 10 results
                            }
                            print(f"[REVERSE_SEARCH] ✅ SerpAPI successfully found {len(links)} results")
                        else:
                            print(f"[REVERSE_SEARCH] ⚠️ SerpAPI returned no results (response: {str(serpapi_data)[:200]})")
                    elif serpapi_resp.status_code == 401:
                        print(f"[REVERSE_SEARCH] ❌ SerpAPI: Invalid API key (401)")
                    elif serpapi_resp.status_code == 429:
                        print(f"[REVERSE_SEARCH] ⚠️ SerpAPI: Rate limit exceeded (429)")
                    else:
                        print(f"[REVERSE_SEARCH] ❌ SerpAPI returned status code: {serpapi_resp.status_code}")
                        print(f"[REVERSE_SEARCH] Response: {serpapi_resp.text[:200]}")
                except requests.exceptions.Timeout:
                    print(f"[REVERSE_SEARCH] ⏱️ SerpAPI request timed out after 45 seconds - trying fallback")
                except Exception as serpapi_error:
                    print(f"[REVERSE_SEARCH] ❌ SerpAPI error: {serpapi_error}")
                    import traceback
                    print(f"[REVERSE_SEARCH] Traceback: {traceback.format_exc()}")

            # ============================================
            # 2. Fallback to RapidAPI if SerpAPI failed
            # ============================================
            if not reverse_search_info and RAPIDAPI_KEY:
                # Call RapidAPI reverse-image-search with that URL
                url = 'https://reverse-image-search1.p.rapidapi.com/reverse-image-search'
                headers = {
                    'x-rapidapi-key': RAPIDAPI_KEY,
                    'x-rapidapi-host': RAPIDAPI_HOST,
                }
                params = {
                    'url': image_public_url,
                    'limit': '10',
                    'safe_search': 'off',
                }
                # Increased timeout to 30 seconds for better reliability
                try:
                    rapid_resp = requests.get(url, headers=headers, params=params, timeout=30)
                except requests.exceptions.Timeout:
                    print(f"[REVERSE_SEARCH] RapidAPI request timed out after 30 seconds")
                    rapid_resp = None
                except requests.exceptions.RequestException as e:
                    print(f"[REVERSE_SEARCH] RapidAPI request failed: {e}")
                    rapid_resp = None
                
                if rapid_resp and rapid_resp.status_code == 200:
                    try:
                        data = rapid_resp.json()
                        # According to sample, data is a list under top-level "data"
                        raw_list = []
                        if isinstance(data, dict) and isinstance(data.get('data'), list):
                            raw_list = data['data']
                        elif isinstance(data, list):
                            raw_list = data

                        links = []
                        for item in raw_list[:5]:
                            if not isinstance(item, dict):
                                continue
                            title = (
                                item.get('title')
                                or item.get('name')
                                or item.get('page_title')
                                or item.get('text')
                                or ''
                            )
                            link = (
                                item.get('url')
                                or item.get('link')
                                or item.get('page_url')
                                or item.get('href')
                                or ''
                            )
                            if link:
                                links.append({'title': title or link, 'link': link})

                        if links:
                            reverse_search_info = {
                                'engine': 'rapidapi_reverse_image_search1',
                                'image_url': image_public_url,
                                'results': links,
                            }
                            print(f"[REVERSE_SEARCH] Successfully found {len(links)} results")
                        else:
                            print(f"[REVERSE_SEARCH] No links found in API response")
                    except Exception as parse_error:
                        print(f"[REVERSE_SEARCH] Error parsing API response: {parse_error}")
                elif rapid_resp:
                    print(f"[REVERSE_SEARCH] RapidAPI returned status code: {rapid_resp.status_code}")
                    if rapid_resp.status_code == 429:
                        print(f"[REVERSE_SEARCH] Rate limit exceeded - consider upgrading API plan")
                    elif rapid_resp.status_code == 401:
                        print(f"[REVERSE_SEARCH] Invalid API key")
                else:
                    print(f"[REVERSE_SEARCH] No response from RapidAPI (timeout or connection error)")

            # ============================================
            # 3. Final fallback: Google direct link
            # ============================================
            if not reverse_search_info and image_public_url:
                reverse_search_info = {
                    'engine': 'google_fallback',
                    'image_url': image_public_url,
                    'results': [{
                        'title': 'Search this image on Google',
                        'link': f'https://www.google.com/searchbyimage?image_url={image_public_url}'
                    }],
                    'note': 'All APIs failed. Using Google reverse image search as fallback.'
                }
                print(f"[REVERSE_SEARCH] Using Google fallback link")
    except Exception as e:
        # Log server-side, but do not surface as 500
        print(f"[REVERSE_SEARCH] Error: {e}")
        import traceback
        print(f"[REVERSE_SEARCH] Traceback: {traceback.format_exc()}")
        # If we have an image URL but all APIs failed, provide Google fallback
        if 'image_public_url' in locals() and image_public_url and not reverse_search_info:
            reverse_search_info = {
                'engine': 'google_fallback',
                'image_url': image_public_url,
                'results': [{
                    'title': 'Search this image on Google',
                    'link': f'https://www.google.com/searchbyimage?image_url={image_public_url}'
                }],
                'note': 'All APIs failed. Using Google reverse image search as fallback.'
            }
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify({'reverse_search': reverse_search_info}), 200


@app.route('/predict_video', methods=['POST'])
@verify_token
def predict_video():
    """Video prediction endpoint using Sightengine API for deepfake detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Allowed video extensions
        ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({'error': 'Invalid video type. Allowed: MP4, AVI, MOV, MKV, WebM'}), 400

        # Check if at least one API account is configured
        if not SIGHTENGINE_ACCOUNTS:
            return jsonify({
                'error': 'Sightengine API credentials not configured. Please set at least one of:\n'
                         'SIGHTENGINE_API_USER / SIGHTENGINE_API_SECRET or '
                         'SIGHTENGINE_API_USER_1 / SIGHTENGINE_API_SECRET_1.'
            }), 500

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Try each configured Sightengine account until one succeeds
            last_error = None
            api_result = None

            for idx, (api_user, api_secret) in enumerate(SIGHTENGINE_ACCOUNTS, start=1):
                try:
                    print(f"[SIGHTENGINE] Using account #{idx} to analyze video: {filepath}")
                    with open(filepath, 'rb') as video_file:
                        response_api = requests.post(
                            'https://api.sightengine.com/1.0/video/check-sync.json',
                            files={'media': video_file},
                            data={
                                'models': 'genai',  # Sightengine's deepfake/AI-generated detection model
                                'api_user': api_user,
                                'api_secret': api_secret,
                            },
                            timeout=120  # 2 minutes timeout for video processing
                        )

                    if response_api.status_code != 200:
                        last_error = f"Sightengine API error (account #{idx}): {response_api.status_code} - {response_api.text}"
                        print(f"[SIGHTENGINE] {last_error}")
                        continue

                    api_result = response_api.json()
                    print(f"[SIGHTENGINE] API response from account #{idx}: {api_result}")
                    break
                except requests.exceptions.RequestException as e:
                    last_error = f"Sightengine request failed for account #{idx}: {e}"
                    print(f"[SIGHTENGINE] {last_error}")
                    continue

            if api_result is None:
                raise Exception(last_error or 'All Sightengine accounts failed')
            
            # Parse Sightengine response
            # In your current response, each frame looks like:
            #   {'info': {...}, 'type': {'ai_generated': 0.99}}
            # Some plans may return 'genai': {'ai_generated': ..., 'deepfake': ...}
            
            if 'data' in api_result and 'frames' in api_result['data']:
                frames_data = api_result['data']['frames']
                
                # Aggregate frame-level results
                ai_scores = []
                deepfake_scores = []
                
                for frame in frames_data:
                    # Newer API: 'type' field with ai_generated
                    if 'type' in frame:
                        t = frame['type']
                        ai_scores.append(float(t.get('ai_generated', 0.0)))
                        # Some responses might also include 'deepfake' here
                        if 'deepfake' in t:
                            deepfake_scores.append(float(t.get('deepfake', 0.0)))
                    # Older/genai field (kept for compatibility)
                    elif 'genai' in frame:
                        genai = frame['genai']
                        ai_scores.append(float(genai.get('ai_generated', 0.0)))
                        deepfake_scores.append(float(genai.get('deepfake', 0.0)))
                
                # If no deepfake scores are present, treat deepfake as 0
                if not deepfake_scores and ai_scores:
                    deepfake_scores = [0.0] * len(ai_scores)
                
                # Calculate per-class stats
                def stats(values, transform=lambda x: x):
                    if not values:
                        return 0.0, 0.0, 0.0
                    vals = [transform(v) for v in values]
                    return sum(vals) / len(vals), min(vals), max(vals)
                
                # AI-generated scores are given directly by the API
                avg_ai, min_ai, max_ai = stats(ai_scores)
                # Deepfake scores may be absent (all zeros)
                avg_deepfake, min_deepfake, max_deepfake = stats(deepfake_scores)
                # Real is complementary to the max of (ai, deepfake)
                real_scores = [1.0 - max(a, d) for a, d in zip(ai_scores or [0.0], deepfake_scores or [0.0])]
                avg_real, min_real, max_real = stats(real_scores)
                
                # Determine final prediction by highest average probability
                best_class = max(
                    [
                        ('AI-Generated Face', avg_ai),
                        ('Deepfake', avg_deepfake),
                        ('Real', avg_real),
                    ],
                    key=lambda x: x[1],
                )
                final_prediction = best_class[0]
                final_confidence = best_class[1] * 100.0
                
                response = {
                    'final_prediction': final_prediction,
                    'final_confidence': f"{final_confidence:.2f}%",
                    'frames_analyzed': len(frames_data),
                    'video_info': {
                        'status': api_result.get('status'),
                        'frames_processed': len(frames_data),
                    },
                    'class_scores': {
                        'AI-Generated Face': {
                            'mean': f"{avg_ai * 100:.2f}%",
                            'min': f"{min_ai * 100:.2f}%",
                            'max': f"{max_ai * 100:.2f}%",
                        },
                        'Deepfake': {
                            'mean': f"{avg_deepfake * 100:.2f}%",
                            'min': f"{min_deepfake * 100:.2f}%",
                            'max': f"{max_deepfake * 100:.2f}%",
                        },
                        'Real': {
                            'mean': f"{avg_real * 100:.2f}%",
                            'min': f"{min_real * 100:.2f}%",
                            'max': f"{max_real * 100:.2f}%",
                        },
                    },
                    'api_provider': 'Sightengine',
                    'detection_method': 'Cloud-based deepfake detection',
                }
            else:
                # Fallback if response format is different
                response = {
                    'final_prediction': 'Unknown',
                    'final_confidence': '0.00%',
                    'frames_analyzed': 0,
                    'video_info': api_result,
                    'class_scores': {},
                    'api_provider': 'Sightengine',
                    'error': 'Unexpected API response format',
                }
            
            return jsonify(response)
            
        finally:
            # Clean up uploaded video file
            if os.path.exists(filepath):
                os.remove(filepath)

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Video analysis timeout. Please try with a shorter video.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask app...")
    print(f"Open http://localhost:5000 in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)
