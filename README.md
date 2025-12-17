# 🔍 Deepfake Detection Web Interface

A simple Flask web application to test your trained Vision Transformer model for detecting deepfakes, real faces, and AI-generated images.

## 📋 Prerequisites

- Python 3.8+
- CUDA-capable GPU (optional, but recommended)
- Python 3.8+
- CUDA-capable GPU (optional, but recommended)
- **Important**: You must download the trained model `vit3class.pth` manually (it is too large for Git) and place it in the root directory.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install flask torch torchvision pillow werkzeug
```

### 2. Run the Application

```bash
python app.py
```

You should see:
```
Using device: cuda
Model loaded successfully!
Starting Flask app...
Open http://localhost:5000 in your browser
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## 📸 How to Use

1. **Upload an Image**
   - Click on the upload box or drag & drop an image
   - Supported formats: PNG, JPG, JPEG, GIF, BMP, AVIF, WebP
   - Maximum file size: 50MB

2. **Analyze**
   - Click "Analyze Image" button
   - The model will process the image and display results

3. **View Results**
   - **Prediction**: The classification result
   - **Confidence**: How confident the model is in its prediction
   - **Detailed Scores**: Probability scores for all three classes

## 🏷️ Classification Classes

- **Real**: Authentic human face
- **Deepfake**: Face generated using deepfake techniques
- **AI-Generated Face**: Face created by generative AI models

## 🛠️ Model Information

- **Architecture**: Vision Transformer (ViT-B-16)
- **Pre-trained**: ImageNet1K
- **Fine-tuned Classes**: 3 (Real, Deepfake, AI-Generated)
- **Input Size**: 224×224 pixels
- **Accuracy**: ~99.15% on validation set

## 🐛 Troubleshooting

### Model loading fails
- Ensure `vit3class.pth` is in the same directory as `app.py`
- Check that PyTorch and torchvision versions match the requirements

### Out of memory (CUDA)
- The app will automatically fall back to CPU
- Processing will be slower on CPU

### Port 5000 already in use
- Edit `app.py` line 106: change `port=5000` to `port=5001` (or any free port)
- Then access: `http://localhost:5001`

## 📁 File Structure

```
.
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── vit3class.pth         # Trained model weights
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface
└── uploads/              # Temporary image storage (auto-created)
```

## ⚙️ Performance Notes

- **First run**: Model loading may take 10-30 seconds
- **Inference time**: 1-3 seconds per image (GPU), 5-10 seconds (CPU)
- **Batch processing**: Currently processes one image at a time

## 🔒 Security

- Uploaded images are stored temporarily and deleted after processing
- No images are saved to disk
- File size is limited to 50MB
- File type validation is enforced

## 📝 Notes

- The model is optimized for face images (224×224)
- Performance may vary with image quality and resolution
- Best results with clear, front-facing face images

Enjoy testing! 🚀
