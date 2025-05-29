#!/usr/bin/env python3
# Requires qrcode and pyzbar libraries. Install with:
# pip install qrcode[pil] pyzbar

import argparse
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

def generate_qr(data, output_file, error_correction, box_size, border, fg_color, bg_color, logo_file=None):
    """Generate a QR code with the given data and settings."""
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION[error_correction],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    if logo_file:
        logo = Image.open(logo_file)
        qr_size = img.size[0]
        logo_size = int(qr_size * 0.2)
        logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)
        position = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
        img.paste(logo, position, logo if logo.mode == 'RGBA' else None)
    img.save(output_file)

def add_common_args(parser):
    """Add shared arguments for both generate and enhance commands."""
    parser.add_argument("-o", "--output", default="qrcode.png", help="Output filename")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="M", 
                        help="Error correction level (L=7%, M=15%, Q=25%, H=30% redundancy)")
    parser.add_argument("--box-size", type=int, default=10, help="Size of each QR code module in pixels")
    parser.add_argument("--border", type=int, default=4, help="Border size in modules")
    parser.add_argument("--fg-color", default="black", help="Foreground color (e.g., 'black' or '#000000')")
    parser.add_argument("--bg-color", default="white", help="Background color (e.g., 'white' or '#FFFFFF')")
    parser.add_argument("--logo", help="Path to logo image file to embed in the QR code")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QR Code Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a QR code from data")
    generate_parser.add_argument("data", help="Text/URL to encode")
    add_common_args(generate_parser)

    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance an existing QR code")
    enhance_parser.add_argument("input", help="Input QR code image file")
    add_common_args(enhance_parser)

    args = parser.parse_args()

    if args.command == "generate":
        data = args.data
    elif args.command == "enhance":
        try:
            decoded_objects = decode(Image.open(args.input))
            if len(decoded_objects) != 1:
                print("Error: Input image must contain exactly one QR code.")
                exit(1)
            if decoded_objects[0].type != 'QRCODE':
                print("Error: Input image is not a QR code.")
                exit(1)
            data = decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            print(f"Error decoding input image: {e}")
            exit(1)

    generate_qr(data, args.output, args.error_correction, args.box_size, args.border, 
                args.fg_color, args.bg_color, args.logo)
