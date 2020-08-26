import configparser
import os
import subprocess

config = configparser.ConfigParser()
config.read('config.ini')

# Byte value associated with each platform
# It is the last byte of the IMG header
platform = {
    '360': 0,
    'ps3': 1,
    'wiiu': 4,
    'ios': 6
}

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
    Return the IMG header with the specified width and height values.
    Values are in big endian order for PS3, 360 and Wii U.
    Values are in little endian order for iOS.
    """
    header[0:2] = header[6:8] = width.to_bytes(2, byteorder='little' if header[19] == platform['ios'] else 'big')
    header[2:4] = height.to_bytes(2, byteorder='little' if header[19] == platform['ios'] else 'big')
    return header

def create_ps3_img(source, dest, width, height):
    """
    Convert the source image file to a PlayStation 3 IMG file for GHL with the specified size.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    blob = __read(dest, '.dds')

    # Replace default 128 bytes header with PS3 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 01'), width, height)

    __write(dest, blob)

def create_ios_img(source, dest, width, height):
    """
    Convert the source image file to an iOS IMG file for GHL with the specified size.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.pvr" -r ' + str(width) + ',' + str(height) + ' -f PVRTC1_4')

    blob = __read(dest, '.pvr')

    # Truncate metadata block and adjust metadata size in the PVR header
    del blob[67:91]
    blob[48:52] = (15).to_bytes(4, byteorder='little')
    
    # Add iOS GHL 20 bytes header
    blob = __img_header(bytearray.fromhex('00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 01 00 00 06'), width, height) + blob

    __write(dest, blob)

def create_360_img(source, dest, width, height):
    """
    Convert the source image file to a Xbox 360 IMG file for GHL with the specified size.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    blob = __read(dest, '.dds')

    # Swap bytes
    for i in range(128, len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Replace default 128 bytes header with 360 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 00'), width, height)

    __write(dest, blob)

def create_wiiu_img(source, dest, width, height):
    """
    Convert the source image file to a Wii U IMG file for GHL with the specified size.
    """
    # Resize and convert the original image to a temporary DDS texture
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.temp.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    # Convert the temporary file to a GTX texture
    subprocess.call('python ' + config['path']['gtx_extract'] + ' -o ' + dest + '.gtx ' + dest + '.temp.dds', shell=True)
    os.remove(dest + '.temp.dds')

    blob = __read(dest, '.gtx')

    # Replace GX2 Surface block and padding block by GX2 Surface data
    blob[32:4096] = blob[64:220]

    # Remove 32 bytes end of file block header
    blob = blob[:-32]

    # Replace default 32 bytes header with Wii U GHL 20 bytes header
    blob[0:32] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 04'), width, height)

    __write(dest, blob)

# Command line usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='A python script to convert popular image file formats to IMG files for Guitar Hero Live.')
    parser.add_argument('--platform', choices=['ps3', 'ios', '360', 'wiiu'], required=True, help='Platform of the output IMG')
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
    elif args.platform == 'wiiu':
        create_wiiu_img(args.input, args.output, args.width, args.height)