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

def __img_header(header, width, height):
    """
    Return the IMG header with the specified width and height values in big endian order.
    """
    header[0:2] = header[6:8] = width.to_bytes(2, byteorder='big')
    header[2:4] = height.to_bytes(2, byteorder='big')
    return header

def create_ps3_img(source, dest, width, height):
    """
    Convert the source image file to a PlayStation 3 IMG file for GHL with the specified size.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    blob = __read(dest, '.dds')

    # Replace default 128 bytes header with PS3 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 01'), width, height)

    __write(dest, blob)

def create_ios_img(source, dest, width, height):
    """
    Convert the source image file to an iOS IMG file for GHL with the specified size.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.pvr" -r ' + str(width) + ',' + str(height) + ' -f PVRTC1_4_RGB')

    blob = __read(dest, '.pvr')

    # Write width and height values into the IMG and PVR header
    header = bytearray.fromhex('00 00 00 00 01 00 00 02 00 00 00 00 00 00 00 00 01 00 00 06 50 56 52 03 00 00 00 00 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 0F 00 00 00 50 56 52 03 03 00 00 00 03 00 00 00 00 00 00')
    header[0:2] = header[6:8] = header[48:50] = width.to_bytes(2, byteorder='little')
    header[2:4] = header[44:46] = height.to_bytes(2, byteorder='little')

    # Replace default 91 bytes header with iOS GHL 87 bytes header
    blob[0:91] = header

    __write(dest, blob)

def create_360_img(source, dest, width, height):
    """
    Convert the source image file to a Xbox 360 IMG file for GHL with the specified size.
    This function requires PVRTexToolCLI installed and added to your path environment variable.
    """
    # Resize and convert the original image
    subprocess.call('PVRTexToolCLI -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    blob = __read(dest, '.dds')

    # Swap bytes
    for i in range(128, len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Replace default 128 bytes header with 360 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 00'), width, height)

    __write(dest, blob)

# Command line usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='A python script to convert popular image file formats to IMG files for Guitar Hero Live.')
    parser.add_argument('--platform', choices=['ps3', 'ios', '360'], required=True, help='Platform of the output IMG')
    parser.add_argument('--input', required=True, help='Path of the input image')
    parser.add_argument('--output', default='output.img', help='Path to the output IMG. Default value is output.img')
    parser.add_argument('--width', required=True, type=int, help='Width of the output IMG')
    parser.add_argument('--height', required=True, type=int, help='Height of the output IMG')

    args = parser.parse_args()

    if args.platform == 'ps3':
        create_ps3_img(args.input, args.output, args.width, args.height)
    elif args.platform == 'ios':
        create_ios_img(args.input, args.output, args.width, args.height)
    elif args.platform == '360':
        create_360_img(args.input, args.output, args.width, args.height)