# from ultralytics import YOLO

# # Load a pretrained model (or your custom trained model)
# model = YOLO("yolov8n.pt")  # can be yolov8s.pt, yolov8m.pt, or your own .pt

# # Export to ONNX
# model.export(format="onnx")

import argparse
import torch
import os
import sys
import torchvision.models as models


def get_model_by_name(name: str):
    """Return a torchvision model by name (extendable)."""
    if not hasattr(models, name):
        raise ValueError(
            f"Model type '{name}' not found in torchvision.models. "
            f"Available models: {list(models.__dict__.keys())}"
        )
    return getattr(models, name)()


def main():
    parser = argparse.ArgumentParser(description="Convert PyTorch .pt model to ONNX")
    parser.add_argument("model_path", type=str, help="Path to the PyTorch .pt file")
    parser.add_argument(
        "--model-type",
        type=str,
        default=None,
        help="Model architecture name (e.g., resnet18, resnet50) if loading state_dict",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: output ONNX file name (default: same as input .pt)",
    )
    parser.add_argument(
        "--input-size",
        type=int,
        nargs="+",
        default=[1, 3, 224, 224],
        help="Input tensor size as N C H W (default: 1 3 224 224)",
    )
    parser.add_argument(
        "--dynamic",
        action="store_true",
        help="Enable dynamic batch size in ONNX export",
    )
    args = parser.parse_args()

    print(f" Loading model from {args.model_path}")
    model_obj = torch.load(args.model_path, map_location="cpu")

    # Case 1: state_dict only
    if isinstance(model_obj, dict):
        if not args.model_type:
            print(" This .pt file contains a state_dict. You must provide --model-type.")
            sys.exit(1)

        print(f"Detected state_dict. Building model: {args.model_type}")
        model = get_model_by_name(args.model_type)
        model.load_state_dict(model_obj)

    # Case 2: full model
    else:
        print("🔹 Detected full model object.")
        model = model_obj

    model.eval()

    # Prepare dummy input
    dummy_input = torch.randn(*args.input_size)

    # Output file name
    output_file = args.output or os.path.splitext(args.model_path)[0] + ".onnx"

    # Export to ONNX
    print(f"🔹 Exporting to {output_file} ...")
    torch.onnx.export(
        model,
        dummy_input,
        output_file,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        if args.dynamic
        else None,
    )

    print(f"✅ Successfully exported to {output_file}")


if __name__ == "__main__":
    main()
