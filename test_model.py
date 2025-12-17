import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import os

print("=" * 60)
print("DEEPFAKE DETECTION MODEL TEST")
print("=" * 60)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n✓ Device: {device}")

# Load model
print("\nLoading model...")
try:
    model = models.vit_b_16(weights="IMAGENET1K_V1")
    model.heads.head = torch.nn.Linear(768, 3)
    
    state = torch.load("vit3class.pth", map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    exit(1)

# Check class mapping
class_names = {0: "AI-Generated Face", 1: "Deepfake", 2: "Real"}
print(f"✓ Classes: {class_names}")

# Try different transforms
print("\n" + "=" * 60)
print("TESTING PREPROCESSING TRANSFORMS")
print("=" * 60)

transforms_list = {
    "ImageNet normalization (RECOMMENDED)": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    "No normalization": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ]),
    "Training normalization [0.5,0.5,0.5]": transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
}

# Find a test image
test_dir = "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\aifake"
real_dir = "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\real"
fake_dir = "C:\\Users\\NITHIN S\\Desktop\\Deepfake\\New folder\\data\\val\\fake"

test_images = {}

if os.path.exists(test_dir):
    files = os.listdir(test_dir)
    if files:
        test_images["AI-Generated"] = os.path.join(test_dir, files[0])
        
if os.path.exists(real_dir):
    files = os.listdir(real_dir)
    if files:
        test_images["Real"] = os.path.join(real_dir, files[0])

if os.path.exists(fake_dir):
    files = os.listdir(fake_dir)
    if files:
        test_images["Deepfake"] = os.path.join(fake_dir, files[0])

if not test_images:
    print("⚠ No test images found in validation folders!")
    print(f"  Checked: {test_dir}")
    print(f"  Checked: {real_dir}")
    print(f"  Checked: {fake_dir}")
else:
    print(f"\nFound {len(test_images)} test images")

# Test with each image and transform
for img_type, img_path in test_images.items():
    print(f"\n{'='*60}")
    print(f"IMAGE TYPE: {img_type}")
    print(f"PATH: {img_path}")
    print("=" * 60)
    
    try:
        img = Image.open(img_path).convert('RGB')
        print(f"✓ Image size: {img.size}")
        
        for transform_name, transform in transforms_list.items():
            img_tensor = transform(img).unsqueeze(0).to(device)
            
            with torch.no_grad():
                logits = model(img_tensor)
                probs = F.softmax(logits, dim=1)
            
            probs_np = probs.cpu().numpy()[0]
            pred_idx = probs.argmax(dim=1).item()
            confidence = probs_np[pred_idx] * 100
            
            print(f"\n  Transform: {transform_name}")
            print(f"  Prediction: {class_names[pred_idx]} ({confidence:.2f}%)")
            print(f"  All scores:")
            for i, (class_name, score) in enumerate(class_names.items()):
                print(f"    {class_name}: {probs_np[i]*100:.2f}%")
            
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
