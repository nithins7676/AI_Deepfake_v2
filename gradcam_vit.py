"""Grad-CAM utilities for Vision Transformer (ViT-B-16).

This module provides functions to generate attention heatmaps using
Grad-CAM-like gradients on the last encoder block, and to overlay
those heatmaps on top of input images.

Designed to work with torchvision.models.vit_b_16.
"""

from __future__ import annotations

import cv2
import numpy as np
import torch
from typing import Tuple


def _get_last_encoder_norm(model: torch.nn.Module) -> torch.nn.Module:
    """Return the layer to hook for ViT Grad-CAM.

    Assumes a torchvision ViT with ``model.encoder.layers`` attribute,
    but does *not* depend on its exact container type (ModuleList, Sequential, etc.).
    """

    encoder = getattr(model, "encoder", None)
    if encoder is None or not hasattr(encoder, "layers"):
        raise RuntimeError("Model does not have encoder.layers; unsupported architecture for Grad-CAM")

    layers_container = encoder.layers

    # Convert to a simple list of blocks regardless of container type
    if isinstance(layers_container, torch.nn.ModuleList) or isinstance(layers_container, torch.nn.Sequential):
        blocks = list(layers_container)
    else:
        # Generic iterable of modules
        try:
            blocks = list(layers_container)
        except TypeError:
            blocks = []

    if not blocks:
        raise RuntimeError("encoder.layers is empty; unsupported architecture for Grad-CAM")

    last_block = blocks[-1]
    # torchvision's EncoderBlock exposes ln_1 / ln_2
    hook_attr = None
    for candidate in ("ln_1", "ln_2"):
        if hasattr(last_block, candidate):
            hook_attr = candidate
            break

    if hook_attr is None:
        raise RuntimeError("Last encoder block has no ln_1/ln_2; unsupported architecture for Grad-CAM")

    return getattr(last_block, hook_attr)


def generate_vit_gradcam_map(
    model: torch.nn.Module,
    device: torch.device | str,
    pil_image,
    transform,
    target_index: int,
    resize: Tuple[int, int] = (224, 224),
) -> np.ndarray:
    """Generate a Grad-CAM style heatmap for a ViT model.

    This implementation hooks the last encoder norm, which is stable across
    torchvision ViT versions and produces a reliable token-importance map.
    """

    model.eval()

    activations = {}
    gradients = {}

    target_layer = _get_last_encoder_norm(model)

    def forward_hook(module, input, output):  # pylint: disable=unused-argument
        activations["value"] = output

    def backward_hook(module, grad_input, grad_output):  # pylint: disable=unused-argument
        gradients["value"] = grad_output[0]

    handle_fwd = target_layer.register_forward_hook(forward_hook)
    handle_bwd = target_layer.register_full_backward_hook(backward_hook)

    try:
        # Prepare input tensor with gradients enabled
        input_tensor = transform(pil_image).unsqueeze(0).to(device)
        input_tensor.requires_grad_(True)

        # Forward pass
        logits = model(input_tensor)
        if logits.ndim != 2 or logits.size(0) != 1:
            raise RuntimeError("Unexpected logits shape for Grad-CAM: %r" % (tuple(logits.shape),))

        # Select logit for target class
        target_logit = logits[0, target_index]

        # Backward to get gradients at target layer
        model.zero_grad()
        if input_tensor.grad is not None:
            input_tensor.grad.zero_()
        target_logit.backward()

        if "value" not in gradients or "value" not in activations:
            raise RuntimeError("Failed to capture gradients/activations for Grad-CAM")

        # activations and gradients: (B, tokens, dim)
        grads = gradients["value"][0]  # (tokens, dim)

        # Drop class token (token 0), keep patch tokens only
        grads_patches = grads[1:]  # (N_patches, dim)

        # Aggregate across embedding dimension (mean)
        cam = grads_patches.mean(dim=-1)  # (N_patches,)

        cam = cam.detach().cpu().numpy().astype(np.float32)

        # Normalize to [0, 1]
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()

        # Reshape tokens to a square grid (14x14 for ViT-B/16 at 224x224)
        tokens = cam.shape[0]
        grid_size = int(np.sqrt(tokens))
        if grid_size * grid_size != tokens:
            grid_size = int(np.floor(np.sqrt(tokens)))
            cam = cam[: grid_size * grid_size]
        cam = cam.reshape(grid_size, grid_size)

        # Resize to match image / model input resolution
        cam_resized = cv2.resize(cam, resize, interpolation=cv2.INTER_CUBIC)

        # Ensure values in [0, 1] after interpolation
        cam_resized = cam_resized - cam_resized.min()
        if cam_resized.max() > 0:
            cam_resized = cam_resized / cam_resized.max()

        return cam_resized
    finally:
        handle_fwd.remove()
        handle_bwd.remove()


def overlay_heatmap_on_image(
    pil_image,
    heatmap: np.ndarray,
    alpha: float = 0.5,
    colormap: int = cv2.COLORMAP_JET,
):
    """Overlay a heatmap on top of a PIL RGB image.

    Args:
        pil_image: PIL.Image RGB
        heatmap: 2D numpy array in [0, 1]
        alpha: blending factor between heatmap and original image
        colormap: OpenCV colormap id (default: JET)

    Returns:
        PIL.Image RGB with heatmap overlay.
    """

    from PIL import Image  # imported here to avoid circular dependencies

    # Ensure heatmap is float32 in [0, 1]
    heatmap = np.asarray(heatmap, dtype=np.float32)
    heatmap = np.clip(heatmap, 0.0, 1.0)

    # Resize original image to match heatmap spatial size
    h, w = heatmap.shape
    image_resized = pil_image.resize((w, h))
    image_np = np.array(image_resized, dtype=np.float32)

    # Convert heatmap to color
    heatmap_uint8 = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, colormap)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB).astype(np.float32)

    # Blend
    overlay = alpha * heatmap_color + (1.0 - alpha) * image_np
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    return Image.fromarray(overlay)