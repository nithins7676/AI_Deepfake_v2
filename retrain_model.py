"""
RETRAINING SCRIPT - Fixes class imbalance issue

The original model predicts everything as "Real" because:
- Dataset was imbalanced: 3x more real/deepfake than AI-generated
- No class weights were used during training
- Model learned to output high "Real" probability regardless

This script retrains with:
✓ Class-weighted loss function
✓ Proper preprocessing (no normalization)
✓ More epochs
✓ Better validation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import transforms, datasets, models
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import os

print("\n" + "="*80)
print("DEEPFAKE MODEL RETRAINING WITH CLASS BALANCING")
print("="*80)

# Setup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\nDevice: {device}")

# Directories - CHANGE THESE TO YOUR DATA PATHS
train_dir = "C:/path/to/train/data"  # Format: train/aifake/, train/fake/, train/real/
val_dir = "C:/path/to/val/data"      # Format: val/aifake/, val/fake/, val/real/

# Verify directories exist
print(f"\nTrain directory: {train_dir}")
print(f"Val directory: {val_dir}")

if not os.path.exists(train_dir):
    print(f"\n✗ ERROR: Train directory not found: {train_dir}")
    print("  Please update train_dir and val_dir in this script")
    print("  Directories should contain subfolders: aifake/, fake/, real/")
    exit(1)

# Data transforms - CONSISTENT between train and test
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    # NO NORMALIZATION - Use raw pixel values
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

print("\n[1] LOADING DATA")

# Load datasets
try:
    train_dataset = datasets.ImageFolder(train_dir, transform=transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=transform_val)
    print(f"✓ Train samples: {len(train_dataset)}")
    print(f"✓ Val samples: {len(val_dataset)}")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit(1)

# Check class distribution
print(f"\n[2] CLASS DISTRIBUTION")
class_to_idx = train_dataset.class_to_idx
print(f"Class mapping: {class_to_idx}")

targets = np.array(train_dataset.targets)
for class_name, class_idx in sorted(class_to_idx.items()):
    count = np.sum(targets == class_idx)
    print(f"  {class_name}: {count} samples")

# Calculate class weights
print(f"\n[3] CALCULATING CLASS WEIGHTS")
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(targets),
    y=targets
)
print(f"Class weights: {class_weights}")
class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

# Create weighted sampler for balanced batches
weights = class_weights[targets]
sampler = WeightedRandomSampler(
    weights=weights,
    num_samples=len(targets),
    replacement=True
)

# Data loaders
batch_size = 32
train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    sampler=sampler,
    num_workers=0
)
val_loader = DataLoader(
    val_dataset,
    batch_size=batch_size,
    shuffle=False,
    num_workers=0
)

# Model
print(f"\n[4] LOADING MODEL")
model = models.vit_b_16(weights="IMAGENET1K_V1")
model.heads.head = nn.Linear(768, 3)
model = model.to(device)
print(f"✓ Model loaded with ImageNet weights")

# Loss with class weights (CRITICAL FIX)
criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', factor=0.5, patience=2, verbose=True
)

print(f"\n[5] TRAINING SETUP")
print(f"Loss: CrossEntropyLoss (with class weights)")
print(f"Optimizer: AdamW (lr=3e-5)")
print(f"Batch size: {batch_size}")
print(f"Scheduler: ReduceLROnPlateau")

# Training
print(f"\n[6] STARTING TRAINING")
print(f"Training for 15 epochs with class-weighted loss\n")

best_acc = 0
best_epoch = 0

epochs = 15
for epoch in range(epochs):
    # Train
    model.train()
    train_loss = 0
    
    for batch_idx, (images, labels) in enumerate(train_loader):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        
        if batch_idx % 10 == 0:
            print(f"  Epoch {epoch+1}/{epochs} [{batch_idx}/{len(train_loader)}] Loss: {loss.item():.4f}")
    
    avg_loss = train_loss / len(train_loader)
    
    # Validate
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} | Val Acc: {accuracy:.2f}%")
    
    # Save best model
    if accuracy > best_acc:
        best_acc = accuracy
        best_epoch = epoch + 1
        torch.save(model.state_dict(), "vit3class_retrained.pth")
        print(f"  ✓ New best model saved (Acc: {accuracy:.2f}%)")
    
    scheduler.step(accuracy)

print(f"\n{'='*80}")
print(f"TRAINING COMPLETE")
print(f"Best accuracy: {best_acc:.2f}% at epoch {best_epoch}")
print(f"Best model saved as: vit3class_retrained.pth")
print(f"{'='*80}\n")

print("NEXT STEPS:")
print("1. Replace vit3class.pth with vit3class_retrained.pth")
print("   cp vit3class_retrained.pth vit3class.pth")
print("2. Restart Flask app")
print("3. Test with real images\n")
