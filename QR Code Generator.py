#!/usr/bin/env python3
import argparse
import qrcode

def generate_qr(data, output_file):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QR Code Generator")
    parser.add_argument("data", help="Text/URL to encode")
    parser.add_argument("-o", "--output", default="qrcode.png", help="Output filename")
    args = parser.parse_args()
    generate_qr(args.data, args.output)
