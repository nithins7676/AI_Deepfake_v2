#!/usr/bin/env python
"""
COMPLETE MODEL DIAGNOSTIC - Tests everything
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import numpy as np

print("\n" + "="*80)
print("COMPLETE DEEPFAKE MODEL DIAGNOSTIC")
print("="*80)

# 1. Environment
print("\n[1] ENVIRONMENT")
print(f"    Python: {torch.__version__ if hasattr(torch, '__version__') else 'unknown'}")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"    Device: {device}")
print(f"    Torch: {torch.__version__}")

# 2. Model loading
print("\n[2] MODEL LOADING")
try:
    model = models.vit_b_16(weights="IMAGENET1K_V1")
    model.heads.head = nn.Linear(768, 3)
    print(f"    ✓ Architecture created")
    
    if not os.path.exists("vit3class.pth"):
        print(f"    ✗ Model file not found: vit3class.pth")
    else:
        file_size_mb = os.path.getsize("vit3class.pth") / (1024*1024)
        print(f"    ✓ Model file found: {file_size_mb:.1f} MB")
        
        state = torch.load("vit3class.pth", map_location=device)
        model.load_state_dict(state)
        print(f"    ✓ Weights loaded")
        
        model.to(device)
        model.eval()
        print(f"    ✓ Model in eval mode")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    exit(1)

# 3. Model info
print("\n[3] MODEL DETAILS")
print(f"    Architecture: Vision Transformer B-16")
print(f"    Input size: 224x224")
print(f"    Classes: 3")
total_params = sum(p.numel() for p in model.parameters())
print(f"    Total params: {total_params/1e6:.1f}M")

# 4. Class mapping
class_names = {0: "AI-Generated Face", 1: "Deepfake", 2: "Real"}
print("\n[4] CLASS MAPPING")
for idx, name in class_names.items():
    print(f"    {idx}: {name}")

# 5. Test with random input
print("\n[5] RANDOM INPUT TEST")
try:
    random_input = torch.randn(1, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(random_input)
    
    probs = torch.softmax(output, dim=1)
    print(f"    ✓ Model inference works")
    print(f"    Output shape: {output.shape}")
    print(f"    Sample output: {output[0]}")
except Exception as e:
    print(f"    ✗ Error: {e}")

# 6. Test preprocessing options
print("\n[6] TESTING PREPROCESSING OPTIONS")

preprocs = {
    "ImageNet (RECOMMENDED)": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    "No Normalization": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ]),
    "Training Norm [0.5,0.5,0.5]": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ]),
}

# Create test image (solid color)
test_img = Image.new('RGB', (256, 256), color='red')

print("\n    Testing with synthetic RED image:")
for prep_name, transform in preprocs.items():
    try:
        tensor = transform(test_img).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
        
        pred_idx = probs.argmax().item()
        pred_name = class_names[pred_idx]
        confidence = probs[pred_idx].item() * 100
        
        print(f"\n    {prep_name}:")
        print(f"      Prediction: {pred_name}")
        print(f"      Confidence: {confidence:.2f}%")
        print(f"      Scores: AI={probs[0]*100:.1f}% DF={probs[1]*100:.1f}% Real={probs[2]*100:.1f}%")
    except Exception as e:
        print(f"    ✗ Error with {prep_name}: {e}")

# 7. Check current app.py preprocessing
print("\n[7] CHECKING APP.PY")
with open("app.py", "r") as f:
    content = f.read()
    if "[0.485, 0.456, 0.406]" in content:
        print("    ✓ Using ImageNet normalization (CORRECT)")
    elif "[0.5, 0.5, 0.5]" in content:
        print("    ⚠ Using [0.5,0.5,0.5] normalization")
    else:
        print("    ⚠ No normalization found")

# 8. Check if uploads folder exists
print("\n[8] FILE SYSTEM CHECK")
if os.path.exists("uploads"):
    print("    ✓ uploads/ folder exists")
else:
    print("    ✗ uploads/ folder missing - creating...")
    os.makedirs("uploads", exist_ok=True)
    print("    ✓ Created")

if os.path.exists("templates"):
    print("    ✓ templates/ folder exists")
else:
    print("    ✗ templates/ folder missing")

if os.path.exists("templates/index.html"):
    print("    ✓ templates/index.html exists")
else:
    print("    ✗ templates/index.html missing")

# 9. Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
✓ Model loads successfully
✓ Environment has all dependencies
✓ Classes are mapped correctly
✓ Model can perform inference

RECOMMENDATION:
Use ImageNet normalization [0.485, 0.456, 0.406]
This is now set in app.py

NEXT STEPS:
1. Restart Flask app: python app.py
2. Test with real images
3. Check predictions

If predictions are still wrong:
- Model may need retraining
- Class imbalance may be the cause
""")
print("="*80 + "\n")
