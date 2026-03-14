#!/usr/bin/env python3
"""Generate one image with Tongyi-MAI/Z-Image-Turbo via Hugging Face Inference Providers."""

from __future__ import annotations

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a single image with Tongyi-MAI/Z-Image-Turbo via Hugging Face."
    )
    parser.add_argument("--prompt", required=True, help="Main text prompt.")
    parser.add_argument(
        "--output",
        required=True,
        help="Output image path, for example /tmp/zimage.png",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Optional Hugging Face token. Defaults to HF_TOKEN or HUGGINGFACEHUB_API_TOKEN.",
    )
    parser.add_argument(
        "--model",
        default="Tongyi-MAI/Z-Image-Turbo",
        help="Model id. Defaults to Tongyi-MAI/Z-Image-Turbo.",
    )
    parser.add_argument(
        "--provider",
        default="wavespeed",
        help="Inference provider name. Defaults to wavespeed.",
    )
    parser.add_argument(
        "--negative-prompt",
        default=None,
        help="Optional negative prompt.",
    )
    parser.add_argument("--width", type=int, default=1024, help="Output width in pixels.")
    parser.add_argument("--height", type=int, default=1024, help="Output height in pixels.")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed.",
    )
    parser.add_argument(
        "--num-inference-steps",
        type=int,
        default=9,
        help="Number of inference steps. Defaults to 9.",
    )
    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=0.0,
        help="Guidance scale. Defaults to 0.0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate arguments without making a network call.",
    )
    return parser.parse_args()


def resolve_token(explicit_token: Optional[str]) -> str:
    token = explicit_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing Hugging Face token. Provide --token or set HF_TOKEN / HUGGINGFACEHUB_API_TOKEN."
        )
    return token


def validate_dimensions(width: int, height: int) -> None:
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers.")
    if width > 4096 or height > 4096:
        raise ValueError("Width and height must be 4096 or smaller.")


def save_result(image_obj, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # huggingface_hub typically returns a PIL.Image.Image, but keep a bytes fallback.
    if hasattr(image_obj, "save"):
        image_obj.save(output_path)
        return

    from PIL import Image

    if isinstance(image_obj, (bytes, bytearray)):
        image = Image.open(BytesIO(image_obj))
        image.save(output_path)
        return

    raise TypeError(f"Unsupported image result type: {type(image_obj).__name__}")


def main() -> int:
    args = parse_args()
    validate_dimensions(args.width, args.height)
    token = resolve_token(args.token)

    if args.dry_run:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        print("dry-run ok")
        print(f"model={args.model}")
        print(f"provider={args.provider}")
        print(f"token_prefix={token[:4]}***")
        print(f"size={args.width}x{args.height}")
        return 0

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency huggingface_hub. Install with: pip install -r scripts/requirements.txt"
        ) from exc

    client = InferenceClient(provider=args.provider, api_key=token)

    request_kwargs = {
        "model": args.model,
        "negative_prompt": args.negative_prompt,
        "width": args.width,
        "height": args.height,
        "num_inference_steps": args.num_inference_steps,
        "guidance_scale": args.guidance_scale,
    }
    if args.seed is not None:
        request_kwargs["seed"] = args.seed

    image = client.text_to_image(args.prompt, **request_kwargs)
    save_result(image, Path(args.output))
    print(str(Path(args.output).resolve()))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
