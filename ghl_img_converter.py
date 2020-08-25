import argparse
import os
import subprocess

def __read(filename, ext):
    """
    Read and delete the specified file.
    Return a byte array of the file.
    """
    file = open(filename + ext, 'rb')
    blob = bytearray(file.read())
    file.close()
    os.remove(filename + ext)
    return blob

def __write(dest, blob):
    """
    Write binary to the destination file.
    """
    file = open(dest, 'wb')
    file.write(blob)
    file.close()

def create_ps3_cover(source, dest):
    """
    Convert the source image file to a PlayStation 3 album cover IMG file for GHL.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.dds" -r 300,300 -f BC1')

    blob = __read(dest, '.dds')

    # Replace default 128 bytes header with PS3 GHL 20 bytes header
    blob[0:128] = bytearray.fromhex('01 2C 01 2C 00 01 01 2C 00 00 00 05 00 00 01 00 00 00 03 01')

    __write(dest, blob)

def create_ios_cover(source, dest):
    """
    Convert the source image file to an iOS album cover IMG file for GHL.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.pvr" -r 512,512 -f PVRTC1_4_RGB')

    blob = __read(dest, '.pvr')

    # Replace default 91 bytes header with iOS GHL 87 bytes header
    blob[0:91] = bytearray.fromhex('00 02 00 02 01 00 00 02 00 00 00 00 00 00 00 00 01 00 00 06 50 56 52 03 00 00 00 00 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 02 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 0F 00 00 00 50 56 52 03 03 00 00 00 03 00 00 00 00 00 00')

    __write(dest, blob)

def create_360_cover(source, dest):
    """
    Convert the source image file to a Xbox 360 album cover IMG file for GHL.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.dds" -r 300,300 -f BC1')

    blob = __read(dest, '.dds')

    # Swap bytes
    for i in range(128, len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Replace default 128 bytes header with 360 GHL 20 bytes header
    blob[0:128] = bytearray.fromhex('01 2C 01 2C 00 01 01 2C 00 00 00 05 00 00 01 00 00 00 03 00')

    __write(dest, blob)

# Command line usage
parser = argparse.ArgumentParser(description='A python script to convert popular image file formats to IMG files for Guitar Hero Live.')
parser.add_argument('-p', '--platform', choices=['ps3', 'ios', '360'], required=True, help='Platform of the output IMG')
parser.add_argument('-t', '--type', choices=['cover'], default='cover', help='Type of the output IMG')
parser.add_argument('-i', '--input', required=True, help='Path of the input image')
parser.add_argument('-o', '--output', default='output.img', help='Path to the output IMG. Default value is output.img')

args = parser.parse_args()

if args.platform == 'ps3':
    if args.type == 'cover':
        create_ps3_cover(args.input, args.output)
elif args.platform == 'ios':
    if args.type == 'cover':
        create_ios_cover(args.input, args.output)
elif args.platform == '360':
    if args.type == 'cover':
        create_360_cover(args.input, args.output)