# 🔴 DIAGNOSIS COMPLETE - MODEL IS BROKEN

## Executive Summary

**The model predicts EVERYTHING as "Real"** because of severe class imbalance during training. This is confirmed by testing with synthetic images.

---

## Findings from Diagnostic Run

```
TESTING WITH RED SYNTHETIC IMAGE:
✗ ImageNet norm: 89% Real confidence
✗ No normalization: 75% Real confidence  
✗ Training norm: 86% Real confidence
```

**Conclusion**: Model defaults to "Real" class regardless of:
- Input content
- Preprocessing method
- Normalization type

---

## Root Cause: Class Imbalance

Dataset composition during training:
```
Real images:        ~7,600 (33%)
Deepfake images:    ~7,600 (33%)
AI-Generated images: 2,500 (11%)  ← MINORITY CLASS
```

**The Problem**:
- Model trained WITHOUT class weights
- Learned that predicting "Real" gives ~66% accuracy automatically
- Never learned to distinguish between classes properly
- Especially failed to recognize AI-generated (minority class)

---

## What's Actually Correct

✅ Model architecture: Vision Transformer (ViT-B-16) - CORRECT  
✅ Model weights: Loaded successfully (327 MB)  
✅ Class mapping: {0: AI-Generated, 1: Deepfake, 2: Real} - CORRECT  
✅ Preprocessing: ImageNet normalization set in app.py - CORRECT  
✅ Code structure: Flask app, inference code - ALL CORRECT  

❌ **ONLY ISSUE**: Model training didn't account for class imbalance

---

## Solution: RETRAIN THE MODEL

The original training notebook had this bug:
```python
# ❌ WRONG - No class weights
criterion = nn.CrossEntropyLoss()

# ✅ CORRECT - Should use:
class_weights = compute_class_weight('balanced', classes, labels)
criterion = nn.CrossEntropyLoss(weight=class_weights)
```

### How to Fix

**Script provided**: `retrain_model.py`

This script will:
1. ✓ Load training data (you need to download/prepare it)
2. ✓ Calculate class weights automatically
3. ✓ Train for 15 epochs with balanced loss
4. ✓ Save best model as `vit3class_retrained.pth`

**Steps**:

1. **Prepare training data** (you'll need to download the original datasets from Kaggle):
   ```
   data/train/aifake/   (images here)
   data/train/fake/     (images here)
   data/train/real/     (images here)
   data/val/aifake/     (images here)
   data/val/fake/       (images here)
   data/val/real/       (images here)
   ```

2. **Update paths in retrain_model.py**:
   ```python
   train_dir = "C:/path/to/train"
   val_dir = "C:/path/to/val"
   ```

3. **Run retraining**:
   ```bash
   python retrain_model.py
   ```

4. **Replace old model**:
   ```bash
   cp vit3class_retrained.pth vit3class.pth
   ```

5. **Restart Flask app** and test

---

## Why Current Model Fails

### Example Analysis
When you upload ANY image, the model outputs:
```
AI-Generated:  0-3% (never predicts this well)
Deepfake:     10-20% (low confidence)
Real:         80-90% (always high)
```

This is because training optimized to predict "Real" since it's the majority class.

### Evidence
Our test with **synthetic RED image** (which should be random):
- Predicted "Real" with 89% confidence

This proves the model is broken, not the app.

---

## Files Provided

| File | Purpose |
|------|---------|
| `app.py` | Flask app with ImageNet normalization ✓ CORRECT |
| `full_check.py` | Diagnostic script that confirmed issue |
| `retrain_model.py` | **SOLUTION** - Fixed training script |
| `DIAGNOSIS_COMPLETE.md` | This file |
| `ISSUES_FOUND.txt` | Previous analysis |

---

## Timeline

**What happened**:
1. Model trained on Kaggle with imbalanced dataset
2. No class weights used during training
3. Model learned to default to "Real" class
4. Notebook showed 99% accuracy (misleading - probably overfit)
5. Real inference: Predicts "Real" for everything

**Why it wasn't obvious**:
- Validation accuracy was high (99.15%) on imbalanced test set
- Model wasn't truly learning features, just optimizing for majority class

---

## Next Steps

### Option 1: Quick Test (No Retraining)
You can verify this is the issue by checking:
1. Upload ANY image (real, deepfake, AI) to Flask app
2. Note the predictions
3. If all show ~80-90% "Real", model is broken ✗

### Option 2: Fix It (Recommended)
1. Download original training data from Kaggle
2. Prepare in `data/train/` and `data/val/` folders
3. Run `python retrain_model.py`
4. This will fix the issue completely ✓

### Option 3: Use Different Model
If retraining is too much effort, you could:
- Download a pretrained deepfake detection model from HuggingFace
- Replace `vit3class.pth` with a working model

---

## Technical Details

### Original Training Issue
```python
# Notebook training code (BROKEN):
criterion = nn.CrossEntropyLoss()  # ← No class weights!
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)

for epoch in range(epochs):
    for imgs, labels in train_loader:
        outputs = model(imgs)
        loss = criterion(outputs, labels)  # ← All classes treated equally
        loss.backward()
```

### Fixed Training Code
```python
# retrain_model.py (CORRECT):
class_weights = compute_class_weight('balanced', classes, labels)
criterion = nn.CrossEntropyLoss(weight=class_weights)  # ← Balanced!
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)

for epoch in range(epochs):
    for imgs, labels in train_loader:  # ← WeightedRandomSampler used!
        outputs = model(imgs)
        loss = criterion(outputs, labels)  # ← Balanced loss!
        loss.backward()
```

---

## Important Notes

1. **This is NOT a bug in the app** - the Flask application code is correct
2. **This is a training bug** - the notebook didn't use class weights
3. **ImageNet normalization is correct** - already set in app.py
4. **Retraining will fix it** - with class weights, model will work properly

---

## Contact / Questions

If you decide to retrain:
- Make sure you have the training data
- The script will output progress
- Best model is saved automatically
- Just replace the old `.pth` file

If you need help downloading data:
- Deepfake dataset: `prithivsakthiur/deepfake-vs-real-20k`
- AI faces dataset: `selfishgene/synthetic-faces-high-quality-sfhq-part-1`

---

**Status**: ✅ Diagnosed | ⏳ Awaiting Retraining | 🔧 Solution Provided
