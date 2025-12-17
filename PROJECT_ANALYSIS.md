# 🔍 UNMASK - Deepfake Detection Project - Complete Analysis

## 📋 Project Overview

**UNMASK** is a full-stack deepfake detection application that uses Vision Transformer (ViT) models to classify images and videos into three categories:
- **Real**: Authentic human faces
- **Deepfake**: Faces generated using deepfake techniques
- **AI-Generated Face**: Faces created by generative AI models

---

## 🏗️ Architecture

### Backend (Flask - Python)
- **Framework**: Flask 3.0.0
- **ML Framework**: PyTorch 2.0.1 with torchvision 0.15.2
- **Model**: Vision Transformer (ViT-B-16) fine-tuned for 3-class classification
- **Model File**: `vit3class.pth` (343MB)
- **Port**: 5000 (default)

### Frontend (Next.js - TypeScript/React)
- **Framework**: Next.js 16.0.3
- **Language**: TypeScript
- **UI Library**: Radix UI components
- **Styling**: Tailwind CSS 4.1.9
- **Port**: 3000 (default)

---

## 📁 Project Structure

```
.
├── app.py                      # Flask backend server
├── video_processor.py          # Video frame extraction & processing
├── gradcam_vit.py              # Grad-CAM heatmap generation
├── requirements.txt            # Python dependencies
├── vit3class.pth               # Trained model weights (343MB)
├── uploads/                    # Temporary file storage
│   ├── image_heatmaps/         # Generated heatmaps for images
│   └── video_heatmaps/         # Generated heatmaps for videos
│
├── FRONTEND/                   # Next.js frontend application
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx            # Landing page
│   │   ├── login/
│   │   │   └── page.tsx         # Login/authentication page
│   │   └── detect/
│   │       ├── page.tsx         # Detection mode selection
│   │       ├── image/
│   │       │   └── page.tsx     # Image detection page
│   │       └── video/
│   │           └── page.tsx    # Video detection page
│   │
│   ├── components/             # React components
│   │   ├── upload-zone.tsx      # File upload component
│   │   ├── result-panel.tsx    # Results display component
│   │   ├── forensic-loader.tsx # Loading animation
│   │   ├── disclaimer-box.tsx  # Legal disclaimer
│   │   └── ui/                 # UI primitives
│   │       ├── glass-card.tsx  # Glassmorphism card
│   │       └── glow-button.tsx # Animated button
│   │
│   ├── public/                 # Static assets
│   │   └── images/             # Background images
│   │
│   └── package.json            # Node.js dependencies
│
└── templates/                  # Legacy HTML templates (if any)
```

---

## 🔧 Backend API Endpoints

### 1. `POST /predict` - Image Detection
**Purpose**: Analyze uploaded images for deepfake/AI-generated content

**Features**:
- Local ViT model inference
- Optional Sightengine API ensemble (multi-account support)
- Grad-CAM heatmap generation
- Confidence-aware ensemble voting

**Request**:
- `file`: Image file (PNG, JPG, JPEG, GIF, BMP, AVIF, WebP)
- Max size: 50MB

**Response**:
```json
{
  "prediction": "Real" | "Deepfake" | "AI-Generated Face",
  "confidence": "88.50%",
  "all_scores": {
    "Real": "88.50%",
    "Deepfake": "5.20%",
    "AI-Generated Face": "6.30%"
  },
  "heatmap_url": "/uploads/image_heatmaps/filename_heatmap.png",
  "sources": {
    "ensemble": "local_model + sightengine (avg)",
    "local_model": { ... },
    "sightengine": { ... }
  }
}
```

### 2. `POST /predict_video` - Video Detection
**Purpose**: Analyze video files frame-by-frame

**Features**:
- Uses Sightengine API for video analysis
- Frame-by-frame analysis
- Aggregated statistics (mean, min, max per class)
- Supports multiple API accounts (fallback)

**Request**:
- `file`: Video file (MP4, AVI, MOV, MKV, WebM)
- Max size: 50MB

**Response**:
```json
{
  "final_prediction": "Real" | "Deepfake" | "AI-Generated Face",
  "final_confidence": "85.30%",
  "frames_analyzed": 30,
  "class_scores": {
    "AI-Generated Face": {
      "mean": "5.20%",
      "min": "2.10%",
      "max": "8.50%"
    },
    "Deepfake": { ... },
    "Real": { ... }
  },
  "api_provider": "Sightengine"
}
```

### 3. `POST /reverse_search` - Reverse Image Search
**Purpose**: Find similar images online (optional feature)

**Features**:
- Uploads image to tmpfiles.org
- Uses RapidAPI reverse-image-search1
- Returns top 5 matching URLs
- Non-blocking (runs in background)

**Request**:
- `file`: Image file

**Response**:
```json
{
  "reverse_search": {
    "engine": "rapidapi_reverse_image_search1",
    "image_url": "https://...",
    "results": [
      { "title": "...", "link": "https://..." },
      ...
    ]
  }
}
```

### 4. `GET /uploads/<filename>` - File Serving
**Purpose**: Serve uploaded files and generated heatmaps

---

## 🎨 Frontend Features

### Pages

1. **Landing Page** (`/`)
   - Hero section with animated background
   - Feature cards (Protect Truth, Verify Identity, AI Analysis, Forensic Precision)
   - Disclaimer box
   - Call-to-action to login

2. **Login Page** (`/login`)
   - Simple authentication form (currently frontend-only, no backend auth)
   - Terms acceptance checkbox
   - Forgot password modal (UI only)
   - Redirects to `/detect` on submit

3. **Detection Selection** (`/detect`)
   - Two options: Image Detection or Video Detection
   - Glassmorphism cards with hover effects
   - Feature badges for each mode

4. **Image Detection** (`/detect/image`)
   - Drag-and-drop file upload
   - Image preview
   - Analysis button
   - Results panel with:
     - Verdict (Likely Authentic/Fake/AI Generated)
     - Probability bars for each class
     - Grad-CAM heatmap visualization
     - Reverse image search results (if available)

5. **Video Detection** (`/detect/video`)
   - Video file upload
   - Video preview with controls
   - Analysis button
   - Results panel with aggregated statistics

### UI Components

- **GlassCard**: Glassmorphism effect with customizable glow
- **GlowButton**: Animated button with glow effects
- **UploadZone**: Drag-and-drop file upload with preview
- **ResultPanel**: Displays detection results with charts
- **ForensicLoader**: Loading animation during analysis
- **DisclaimerBox**: Legal disclaimer about experimental nature

### Styling

- **Theme**: Dark mode with neon blue/purple accents
- **Fonts**: 
  - Orbitron (headings)
  - Rajdhani (body text)
- **Effects**: 
  - Glassmorphism
  - Animated gradients
  - Neural network background
  - Floating particles
  - Scan lines

---

## 🤖 Machine Learning Model

### Architecture
- **Base Model**: Vision Transformer (ViT-B-16)
- **Pre-trained**: ImageNet1K
- **Fine-tuned Head**: Linear(768 → 3)
- **Input Size**: 224×224 pixels
- **Classes**: 3 (AI-Generated=0, Deepfake=1, Real=2)

### Preprocessing
```python
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # Custom normalization
])
```

### Model Performance
- **Training Accuracy**: ~99.15% on validation set
- **Note**: Model may have issues with real-world images due to:
  - Training/inference preprocessing mismatch
  - Class imbalance (AI-Generated class had fewer samples)
  - Possible overfitting to training data

### Grad-CAM Visualization
- Generates attention heatmaps showing which image regions influenced the prediction
- Uses gradients from the last encoder block
- Overlays heatmap on original image with configurable alpha

---

## 🔌 External APIs Integration

### Sightengine API
**Purpose**: Cloud-based deepfake detection (ensemble with local model)

**Configuration**:
- Primary account: `SIGHTENGINE_API_USER` / `SIGHTENGINE_API_SECRET`
- Secondary accounts: `SIGHTENGINE_API_USER_1/2` / `SIGHTENGINE_API_SECRET_1/2`
- Supports multiple accounts for rate limiting

**Usage**:
- Image detection: `/1.0/check.json` with `models=genai`
- Video detection: `/1.0/video/check-sync.json` with `models=genai`
- Automatic fallback if one account fails

### RapidAPI (Reverse Image Search)
**Purpose**: Find similar images online

**Configuration**:
- `RAPIDAPI_KEY`: API key for reverse-image-search1
- `RAPIDAPI_HOST`: reverse-image-search1.p.rapidapi.com

**Usage**:
- Uploads image to tmpfiles.org first
- Then queries RapidAPI with public URL
- Returns top 5 matching results

---

## 📦 Dependencies

### Backend (Python)
```
flask==3.0.0
torch==2.0.1
torchvision==0.15.2
pillow==10.0.0
werkzeug==3.0.1
numpy
opencv-python
requests
flask-cors  # (used but not in requirements.txt - needs to be added)
```

### Frontend (Node.js)
**Key Dependencies**:
- `next`: 16.0.3
- `react`: 19.2.0
- `react-dom`: 19.2.0
- `@radix-ui/*`: UI component library
- `tailwindcss`: 4.1.9
- `lucide-react`: Icons
- `recharts`: Charts for results visualization

---

## 🚀 Running the Application

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install flask-cors  # Missing from requirements.txt

# Set environment variables (optional)
export SIGHTENGINE_API_USER="your_user"
export SIGHTENGINE_API_SECRET="your_secret"
export RAPIDAPI_KEY="your_key"

# Run Flask server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup
```bash
cd FRONTEND

# Install dependencies
npm install
# or
pnpm install

# Run development server
npm run dev
# Server runs on http://localhost:3000

# Build for production
npm run build
npm start
```

### Environment Variables
**Backend** (optional):
- `SIGHTENGINE_API_USER`: Primary Sightengine API user
- `SIGHTENGINE_API_SECRET`: Primary Sightengine API secret
- `SIGHTENGINE_API_USER_1/2`: Secondary accounts
- `SIGHTENGINE_API_SECRET_1/2`: Secondary account secrets
- `RAPIDAPI_KEY`: RapidAPI key for reverse search
- `RAPIDAPI_HOST`: RapidAPI host (default: reverse-image-search1.p.rapidapi.com)

**Frontend**:
- `NEXT_PUBLIC_BACKEND_URL`: Backend API URL (default: http://localhost:5000)

---

## ⚠️ Known Issues & Limitations

### Model Issues
1. **Preprocessing Mismatch**: Training used normalization, but inference may work better without it
2. **Class Imbalance**: AI-Generated class had fewer training samples (~2,500 vs ~7,600)
3. **Overfitting**: Model may not generalize well to real-world images
4. **Bias**: Model tends to predict "Real" too often

**See**: `ANALYSIS_REPORT.md` and `ISSUES_FOUND.txt` for detailed analysis

### Missing Features
1. **Authentication**: Login page is UI-only, no backend authentication
2. **User Management**: No user accounts or session management
3. **Database**: No persistent storage for results or user data
4. **Error Handling**: Limited error handling in some edge cases

### Technical Debt
1. **flask-cors**: Used but not in `requirements.txt`
2. **Legacy Templates**: `templates/index.html` exists but may not be used
3. **File Cleanup**: Uploaded files are deleted after processing, but heatmaps may accumulate

---

## 🔒 Security Considerations

1. **File Upload**: Validates file types and size (50MB max)
2. **CORS**: Enabled for all origins (may need restriction in production)
3. **API Keys**: Stored in environment variables (good practice)
4. **No Authentication**: Currently no user authentication system
5. **Temporary Files**: Uploaded files are deleted after processing

---

## 📊 Data Flow

### Image Detection Flow
1. User uploads image → Frontend (`/detect/image`)
2. Frontend sends POST to `/predict` → Backend
3. Backend:
   - Saves file temporarily
   - Preprocesses image (resize, normalize)
   - Runs ViT model inference
   - Generates Grad-CAM heatmap
   - Optionally calls Sightengine API
   - Combines results (ensemble)
   - Deletes original file
   - Returns JSON response
4. Frontend displays results with heatmap and reverse search

### Video Detection Flow
1. User uploads video → Frontend (`/detect/video`)
2. Frontend sends POST to `/predict_video` → Backend
3. Backend:
   - Saves video temporarily
   - Calls Sightengine API (video endpoint)
   - Parses frame-by-frame results
   - Aggregates statistics
   - Deletes video file
   - Returns JSON response
4. Frontend displays aggregated results

---

## 🎯 Use Cases

1. **Content Verification**: Verify authenticity of images/videos
2. **Misinformation Detection**: Identify AI-generated or manipulated content
3. **Forensic Analysis**: Detailed analysis with heatmaps and probability scores
4. **Research**: Experimental deepfake detection prototype

---

## 📝 Notes

- **Experimental**: This is a prototype, not production-ready
- **Disclaimer**: Model accuracy is not guaranteed
- **Training Data**: Model was trained on Kaggle, dataset not available locally
- **Model File**: `vit3class.pth` is 343MB, ensure sufficient disk space
- **GPU Recommended**: CUDA support for faster inference

---

## 🔄 Future Improvements

1. **Model Retraining**: Fix preprocessing mismatch and class imbalance
2. **Authentication**: Implement proper user authentication
3. **Database**: Store results and user history
4. **Batch Processing**: Support multiple file uploads
5. **API Rate Limiting**: Implement rate limiting for API endpoints
6. **Error Handling**: Improve error messages and handling
7. **Testing**: Add unit tests and integration tests
8. **Documentation**: API documentation (Swagger/OpenAPI)
9. **Deployment**: Docker containerization
10. **Monitoring**: Add logging and monitoring

---

## 📚 Related Files

- `ANALYSIS_REPORT.md`: Detailed model analysis
- `ISSUES_FOUND.txt`: Known issues summary
- `README.md`: Quick start guide
- `deep_diagnostic.py`: Model diagnostic script
- `test_model.py`: Model testing script
- `retrain_model.py`: Model retraining script (if exists)

---

## 🌐 Repositories & Deployment

### Frontend Repository
- **Built with**: [v0.app](https://v0.app) (AI-powered UI generation)
- **Deployment**: [Vercel](https://vercel.com/sharletalex-gmailcoms-projects/v0-unmask-frontend-build)
- **Sync**: Automatically synced with v0.app deployments
- **v0 Chat**: [https://v0.app/chat/gyfk2aT7gUW](https://v0.app/chat/gyfk2aT7gUW)

### Backend Repository
- **Status**: Local development (no remote repository detected)
- **Deployment**: Not deployed (runs locally on port 5000)

### External Services/APIs

1. **Sightengine API**
   - **Purpose**: Cloud-based deepfake detection
   - **Endpoints Used**:
     - `/1.0/check.json` (image detection)
     - `/1.0/video/check-sync.json` (video detection)
   - **Model**: `genai` (AI-generated and deepfake detection)
   - **Multi-Account Support**: Yes (up to 3 accounts for rate limiting)

2. **RapidAPI - Reverse Image Search**
   - **Service**: reverse-image-search1
   - **Purpose**: Find similar images online
   - **Endpoint**: `https://reverse-image-search1.p.rapidapi.com/reverse-image-search`

3. **tmpfiles.org**
   - **Purpose**: Temporary file hosting for reverse image search
   - **Usage**: Upload images to get public URL for RapidAPI

4. **Vercel**
   - **Purpose**: Frontend hosting and deployment
   - **Analytics**: `@vercel/analytics` integrated

---

## 🔗 External Dependencies

### NPM Packages (Frontend)
- **UI Framework**: Radix UI components
- **Styling**: Tailwind CSS with custom animations
- **Icons**: Lucide React
- **Charts**: Recharts
- **Forms**: React Hook Form with Zod validation
- **Analytics**: Vercel Analytics

### Python Packages (Backend)
- **Web Framework**: Flask
- **ML Framework**: PyTorch + torchvision
- **Image Processing**: PIL/Pillow, OpenCV
- **HTTP Requests**: requests
- **CORS**: flask-cors (missing from requirements.txt)

---

*Last Updated: 2025-01-27*
*Project Status: Experimental Prototype*

