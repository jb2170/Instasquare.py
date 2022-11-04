#!/usr/bin/env python3

from typing import List
import argparse
import pathlib
import math
import subprocess

DEFAULT_BLUR_VALUE = 9

def square_image(filepath: pathlib.Path, blur: int):
    dimensions_buffer = bytearray()

    print(f"Identifying {filepath}")
    proc_identify = subprocess.Popen([
        "identify", "-format", "%wx%h", f"{filepath}"
    ], stdout = subprocess.PIPE)

    while proc_identify_stdout_read := proc_identify.stdout.read():
        dimensions_buffer += proc_identify_stdout_read

    if proc_identify.wait():
        return

    dimensions = dimensions_buffer.decode()

    width, height = dimensions.split("x")
    width = int(width)
    height = int(height)

    max_dimension = max(width, height)

    if width > height:
        height_new = width
        width_new = math.ceil(width * width / height)
    else:
        width_new = height
        height_new = math.ceil(height * height / width)

    filepath_new = filepath.with_suffix(f".insta{filepath.suffix}")

    print(f"Squaring from {filepath}")
    if subprocess.call([
        "convert", f"{filepath}",
        "(", "-clone", "0", "-blur", f"0x{blur}", "-resize", f"{width_new}x{height_new}!", ")",
        "(", "-clone", "0", ")",
        "-delete", "0",
        "-gravity", "center",
        "-compose", "over",
        "-composite",
        f"{filepath_new}"
    ]):
        return

    if subprocess.call([
        "convert", f"{filepath_new}",
        "-gravity", "center",
        "-crop", f"{max_dimension}x{max_dimension}+0+0",
        "+repage",
        f"{filepath_new}"
    ]):
        return

def main():
    parser = argparse.ArgumentParser(description = "instasquare: square pics for Instagram using ImageMagick")

    parser.add_argument("filepaths", metavar = "FILENAME", help = "filenames to process", nargs = "+", type = pathlib.Path)

    parser.add_argument("--blur",
        help = f"Blur value to pass to ImageMagick. Defaults to {DEFAULT_BLUR_VALUE}",
        type = int,
        default = DEFAULT_BLUR_VALUE
    )

    args = parser.parse_args()

    filepaths: List[pathlib.Path] = args.filepaths
    blur: int = args.blur

    for filepath in filepaths:
        square_image(filepath, blur)

if __name__ == "__main__":
    main()
