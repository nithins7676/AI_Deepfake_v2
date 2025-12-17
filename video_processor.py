"""
Video Processing Module for Deepfake Detection

Extracts frames from video and analyzes them
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import os
from pathlib import Path

from gradcam_vit import generate_vit_gradcam_map, overlay_heatmap_on_image

class VideoProcessor:
    """Process video files for deepfake detection"""
    
    def __init__(self, model, device, class_names, transform):
        """
        Args:
            model: PyTorch model
            device: torch device (cuda/cpu)
            class_names: dict mapping class indices to names
            transform: preprocessing transform
        """
        self.model = model
        self.device = device
        self.class_names = class_names
        self.transform = transform
    
    def extract_frames(self, video_path, sample_rate=1, max_frames=30):
        """Smart frame extraction from video.

        Instead of reading and using all frames, this method:
        - Reads total frame count from metadata
        - Uniformly samples up to ``max_frames`` frames across the whole video
        - Falls back gracefully if metadata is missing

        Args:
            video_path: path to video file
            sample_rate: kept for backward-compatibility but largely ignored;
                         sampling is primarily controlled by ``max_frames``.
            max_frames: maximum frames to extract

        Returns:
            list of numpy arrays (BGR format)
        """
        cap = cv2.VideoCapture(video_path)
        frames = []

        # Try to get total frame count from metadata
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # If metadata is available and valid, use uniform sampling across the video
        if total_frames > 0:
            # Limit how many frames we will ever process
            max_frames = max(1, max_frames)
            num_samples = min(max_frames, total_frames)

            # Indices we want to grab (uniformly spaced)
            sample_indices = np.linspace(0, total_frames - 1, num=num_samples, dtype=int)
            sample_index_set = set(sample_indices.tolist())

            current_index = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if current_index in sample_index_set:
                    frames.append(frame)

                current_index += 1
        else:
            # Fallback: metadata not available; use old-style every-Nth-frame sampling
            frame_count = 0
            extracted_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % max(1, sample_rate) == 0 and extracted_count < max_frames:
                    frames.append(frame)
                    extracted_count += 1

                frame_count += 1

        cap.release()
        return frames
    
    def get_video_info(self, video_path):
        """Get video metadata"""
        cap = cv2.VideoCapture(video_path)
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }
        cap.release()
        return info
    
    def process_frame(self, frame, save_heatmap: bool = False, heatmap_path: str | None = None):
        """
        Process single frame and get predictions.

        Optionally computes and saves a Grad-CAM heatmap overlay.
        
        Args:
            frame: numpy array (BGR)
            save_heatmap: whether to generate and save Grad-CAM overlay
            heatmap_path: full file path where the overlay will be saved
        
        Returns:
            dict with predictions, probabilities, and optional heatmap path
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        from PIL import Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Apply transform
        tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1)[0]
        
        probs_np = probs.cpu().numpy()
        pred_idx = probs.argmax().item()
        confidence = probs_np[pred_idx] * 100

        # Optional Grad-CAM heatmap
        heatmap_file = None
        if save_heatmap and heatmap_path is not None:
            try:
                heatmap = generate_vit_gradcam_map(
                    model=self.model,
                    device=self.device,
                    pil_image=pil_image,
                    transform=self.transform,
                    target_index=pred_idx,
                )
                overlay = overlay_heatmap_on_image(pil_image, heatmap, alpha=0.5)
                os.makedirs(os.path.dirname(heatmap_path), exist_ok=True)
                overlay.save(heatmap_path)
                heatmap_file = heatmap_path
            except Exception:
                heatmap_file = None
        
        return {
            'predicted_class': self.class_names[pred_idx],
            'confidence': confidence,
            'probabilities': {
                self.class_names[i]: probs_np[i] * 100
                for i in range(len(self.class_names))
            },
            'class_index': pred_idx,
            'heatmap_path': heatmap_file,
        }
    
    def process_video(self, video_path, sample_rate=2, max_frames=30, callback=None):
        """Process entire video and get detection results.

        Uses *smart* frame selection under the hood:
        - Uniformly samples up to ``max_frames`` frames across the video
        - Ensures coverage from start to end without using every frame

        Args:
            video_path: path to video file
            sample_rate: kept for compatibility; not the primary control
            max_frames: max frames to analyze
            callback: function called with progress info

        Returns:
            dict with analysis results
        """
        print(f"[VIDEO] Processing: {video_path}")
        
        # Get video info
        info = self.get_video_info(video_path)
        print(f"[VIDEO] Info: {info['frame_count']} frames @ {info['fps']} fps")
        
        # Extract frames using smart uniform sampling
        frames = self.extract_frames(video_path, sample_rate, max_frames)
        print(f"[VIDEO] Extracted {len(frames)} frames for analysis")
        
        if not frames:
            raise ValueError("No frames extracted from video")
        
        # Directory for frame heatmaps for this video
        video_stem = Path(video_path).stem
        heatmap_root = os.path.join('uploads', 'video_heatmaps', video_stem)
        os.makedirs(heatmap_root, exist_ok=True)
        
        # Process each frame
        results = []
        frame_predictions = []
        
        for i, frame in enumerate(frames):
            heatmap_path = os.path.join(heatmap_root, f"frame_{i+1}.png")
            result = self.process_frame(frame, save_heatmap=True, heatmap_path=heatmap_path)
            results.append(result)
            frame_predictions.append(result['class_index'])
            
            # Callback for progress
            if callback:
                callback(i + 1, len(frames))
            
            print(f"[VIDEO] Frame {i+1}/{len(frames)}: {result['predicted_class']} ({result['confidence']:.1f}%)")
        
        # Aggregate results
        aggregated = self._aggregate_results(results, frame_predictions)
        
        return {
            'video_info': info,
            'frames_analyzed': len(frames),
            'frame_results': results,
            'aggregated': aggregated
        }
    
    def _aggregate_results(self, results, predictions):
        """Aggregate frame-level predictions"""
        
        # Count predictions
        from collections import Counter
        pred_counts = Counter(predictions)
        
        # Calculate average confidence for each class
        class_confidences = {}
        for class_idx in range(len(self.class_names)):
            class_name = self.class_names[class_idx]
            confidences = [r['probabilities'][class_name] for r in results]
            class_confidences[class_name] = {
                'mean': np.mean(confidences),
                'std': np.std(confidences),
                'min': np.min(confidences),
                'max': np.max(confidences),
            }
        
        # Final prediction (most common class, or highest average confidence)
        avg_probs = {}
        for class_idx in range(len(self.class_names)):
            class_name = self.class_names[class_idx]
            avg_probs[class_idx] = np.mean([r['probabilities'][class_name] for r in results])
        
        final_pred_idx = max(avg_probs, key=avg_probs.get)
        final_pred_name = self.class_names[final_pred_idx]
        final_confidence = avg_probs[final_pred_idx]
        
        return {
            'final_prediction': final_pred_name,
            'final_confidence': final_confidence,
            'class_confidences': class_confidences,
            'prediction_counts': dict(pred_counts),
            'average_probabilities': {
                self.class_names[i]: avg_probs[i]
                for i in range(len(self.class_names))
            }
        }
    
    def save_frame_samples(self, frames, output_dir, num_samples=3):
        """Save sample frames from video for visualization"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Sample evenly across video
        indices = np.linspace(0, len(frames) - 1, num_samples, dtype=int)
        sample_paths = []
        
        for i, idx in enumerate(indices):
            frame = frames[idx]
            filename = f"frame_{i+1}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            sample_paths.append(filepath)
        
        return sample_paths
