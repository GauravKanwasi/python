#!/usr/bin/env python3
# Requires qrcode and pyzbar libraries. Install with:
# pip install qrcode[pil] pyzbar pillow
import argparse
import sys
import os
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFilter
from pyzbar.pyzbar import decode

ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

def validate_color(color):
    """Validate color input (name or hex code)."""
    try:
        Image.new('RGB', (1, 1), color)
        return True
    except ValueError:
        return False

def generate_qr(data, output_file, error_correction, box_size, border, fg_color, bg_color, logo_file=None, rounded=False):
    """Generate a QR code with the given data and settings."""
    if not data or len(data) > 2953:
        raise ValueError("Data must be non-empty and not exceed 2953 characters")
    
    # Validate colors before QR generation
    if not validate_color(fg_color):
        raise ValueError(f"Invalid foreground color: {fg_color}")
    if not validate_color(bg_color):
        raise ValueError(f"Invalid background color: {bg_color}")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECTION[error_correction],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')
    
    # Add rounded corners if requested
    if rounded:
        img = add_rounded_corners(img, radius=20)
    
    # Embed logo in center
    if logo_file:
        if not os.path.exists(logo_file):
            raise FileNotFoundError(f"Logo file not found: {logo_file}")
        try:
            logo = Image.open(logo_file).convert('RGBA')
            qr_width = img.size[0]
            logo_max_size = int(qr_width * 0.2)
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
            
            # Create white background for logo
            logo_bg = Image.new('RGB', (logo_max_size + 10, logo_max_size + 10), bg_color)
            pos = ((logo_bg.size[0] - logo.size[0]) // 2, (logo_bg.size[1] - logo.size[1]) // 2)
            logo_bg.paste(logo, pos, logo)
            
            center_x = (qr_width - logo_bg.size[0]) // 2
            center_y = (qr_width - logo_bg.size[1]) // 2
            img.paste(logo_bg, (center_x, center_y))
        except Exception as e:
            raise RuntimeError(f"Failed to embed logo: {e}")
    
    img.save(output_file)
    print(f"QR code generated: {output_file}")

def add_rounded_corners(img, radius=20):
    """Add rounded corners to the image."""
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    img.putalpha(mask)
    return img

def decode_qr(input_file):
    """Decode QR code from image file."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    try:
        decoded_objects = decode(Image.open(input_file))
        
        if not decoded_objects:
            raise ValueError("No QR code detected in image")
        if len(decoded_objects) > 1:
            print(f"Warning: Found {len(decoded_objects)} QR codes. Using the first one.")
        
        qr_data = decoded_objects[0]
        if qr_data.type != 'QRCODE':
            raise ValueError(f"Invalid QR code type: {qr_data.type}")
        
        return qr_data.data.decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"Failed to decode QR code: {e}")

def add_common_args(parser):
    """Add shared arguments for both generate and enhance commands."""
    parser.add_argument("-o", "--output", default="qrcode.png", help="Output filename")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="M", 
                        help="Error correction level (L=7%%, M=15%%, Q=25%%, H=30%% redundancy)")
    parser.add_argument("--box-size", type=int, default=10, help="Size of each QR code module in pixels")
    parser.add_argument("--border", type=int, default=4, help="Border size in modules")
    parser.add_argument("--fg-color", default="black", help="Foreground color (e.g., 'black' or '#000000')")
    parser.add_argument("--bg-color", default="white", help="Background color (e.g., 'white' or '#FFFFFF')")
    parser.add_argument("--logo", help="Path to logo image file to embed in the QR code")
    parser.add_argument("--rounded", action="store_true", help="Add rounded corners to the QR code")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="QR Code Generator and Enhancer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a QR code from data")
    generate_parser.add_argument("data", help="Text/URL to encode")
    add_common_args(generate_parser)
    
    # Enhance command (re-encode existing QR codes with new styling)
    enhance_parser = subparsers.add_parser("enhance", help="Enhance an existing QR code with new styling")
    enhance_parser.add_argument("input", help="Input QR code image file")
    add_common_args(enhance_parser)
    
    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Decode a QR code from image")
    decode_parser.add_argument("input", help="Input QR code image file")
    
    args = parser.parse_args()
    
    try:
        if args.command == "generate":
            generate_qr(
                args.data, args.output, args.error_correction,
                args.box_size, args.border, args.fg_color, args.bg_color,
                args.logo, args.rounded
            )
        
        elif args.command == "enhance":
            data = decode_qr(args.input)
            generate_qr(
                data, args.output, args.error_correction,
                args.box_size, args.border, args.fg_color, args.bg_color,
                args.logo, args.rounded
            )
        
        elif args.command == "decode":
            data = decode_qr(args.input)
            print(f"Decoded QR code: {data}")
    
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
