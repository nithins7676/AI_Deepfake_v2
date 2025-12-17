"""
COMPREHENSIVE MODEL DIAGNOSTIC

This script thoroughly checks:
1. Model architecture
2. Model weights 
3. Class mapping
4. Preprocessing
5. Test predictions on real images
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import sys

print("\n" + "="*80)
print("DEEPFAKE DETECTION MODEL - COMPREHENSIVE DIAGNOSTIC")
print("="*80)

# 1. Check PyTorch and device
print("\n[1] CHECKING ENVIRONMENT")
print(f"    PyTorch version: {torch.__version__}")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"    Device: {device}")

# 2. Load model
print("\n[2] LOADING MODEL")
try:
    model = models.vit_b_16(weights="IMAGENET1K_V1")
    model.heads.head = nn.Linear(768, 3)
    print(f"    ✓ Model architecture created")
    
    if not os.path.exists("vit3class.pth"):
        print("    ✗ ERROR: vit3class.pth not found!")
        sys.exit(1)
    
    state = torch.load("vit3class.pth", map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    print(f"    ✓ Model weights loaded")
    print(f"    ✓ Model in eval mode")
    
except Exception as e:
    print(f"    ✗ Error loading model: {e}")
    sys.exit(1)

# 3. Check model parameters
print("\n[3] MODEL PARAMETERS")
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"    Total parameters: {total_params:,}")
print(f"    Trainable parameters: {trainable_params:,}")

# 4. Check model head specifically
print("\n[4] MODEL HEAD (Classification Layer)")
print(f"    Head layer: {model.heads.head}")
head_weight_shape = model.heads.head.weight.shape
head_bias_shape = model.heads.head.bias.shape
print(f"    Weight shape: {head_weight_shape}")
print(f"    Bias shape: {head_bias_shape}")
print(f"    ✓ Head configured for 3 classes")

# 5. Class mapping
class_names = {0: "AI-Generated Face", 1: "Deepfake", 2: "Real"}
print("\n[5] CLASS MAPPING")
for idx, name in class_names.items():
    print(f"    Class {idx}: {name}")

# 6. Test with synthetic input
print("\n[6] TEST WITH RANDOM INPUT")
try:
    random_input = torch.randn(1, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(random_input)
    print(f"    Input shape: {random_input.shape}")
    print(f"    Output shape: {output.shape}")
    print(f"    Output values: {output}")
    
    probs = torch.softmax(output, dim=1)
    print(f"    Probabilities: {probs}")
    print(f"    ✓ Model inference working")
except Exception as e:
    print(f"    ✗ Error: {e}")

# 7. Find and test with real images
print("\n[7] TESTING WITH REAL VALIDATION IMAGES")

test_dirs = {
    "AI-Generated": "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\aifake",
    "Deepfake": "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\fake",
    "Real": "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\real"
}

test_images = {}
for label, path in test_dirs.items():
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))]
        if files:
            test_images[label] = os.path.join(path, files[0])

if not test_images:
    print("    ⚠ No test images found in validation folders")
    print(f"    Checked paths:")
    for label, path in test_dirs.items():
        print(f"      - {path}: {os.path.exists(path)}")
else:
    print(f"    Found {len(test_images)} test images\n")
    
    # Test with different preprocessing approaches
    preprocessing_options = {
        "NO normalization (like notebook test)": transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]),
        "WITH normalization [0.5,0.5,0.5]": transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ]),
        "WITH ImageNet normalization": transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    
    for prep_name, transform in preprocessing_options.items():
        print(f"    {'─'*75}")
        print(f"    PREPROCESSING: {prep_name}")
        print(f"    {'─'*75}")
        
        for true_label, img_path in test_images.items():
            try:
                img = Image.open(img_path).convert('RGB')
                img_tensor = transform(img).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    logits = model(img_tensor)
                    probs = torch.softmax(logits, dim=1)
                
                probs_np = probs.cpu().numpy()[0]
                pred_idx = probs.argmax(dim=1).item()
                pred_label = class_names[pred_idx]
                confidence = probs_np[pred_idx] * 100
                
                match = "✓" if pred_label == true_label else "✗"
                print(f"\n    Image type: {true_label}")
                print(f"    Prediction: {pred_label} {match}")
                print(f"    Confidence: {confidence:.2f}%")
                print(f"    All scores:")
                for i in range(3):
                    print(f"      {class_names[i]}: {probs_np[i]*100:6.2f}%")
                    
            except Exception as e:
                print(f"    ✗ Error processing {true_label}: {e}")

# 8. Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)
print("""
WHAT TO CHECK:
1. Are predictions correct for all three classes?
2. Which preprocessing works best? (should be without normalization)
3. Are confidence scores reasonable (>90%)?

EXPECTED RESULTS:
✓ AI-Generated images → "AI-Generated Face"
✓ Deepfake images → "Deepfake"  
✓ Real images → "Real"

If results don't match:
- The model may need retraining
- Class indices might be swapped
- Preprocessing might be wrong
""")
print("="*80 + "\n")
