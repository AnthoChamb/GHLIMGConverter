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

# DDS formats, their associated bytes from the IMG header and their magic number
# This is used in some PS3 and 360 textures
dds = {
    'BC1': (bytes.fromhex('00 05 00 00'), bytes.fromhex('44 58 54 31')), # DXT1
    'BC3': (bytes.fromhex('00 09 00 FF'), bytes.fromhex('44 58 54 35'))  # DXT5
}

def __read(filename):
    """
    Read the specified file.
    Return a byte array of the file.
    """
    file = open(filename, 'rb')
    blob = bytearray(file.read())
    file.close()
    return blob

def __write(dest, blob):
    """
    Write binary to the destination file.
    """
    file = open(dest, 'wb')
    file.write(blob)
    file.close()

def __img_header(header, width, height, format=None):
    """
    Return the IMG header with the specified width, height and optional format values.
    Values are in big endian order for PS3, 360 and Wii U.
    Values are in little endian order for iOS.
    """
    header[0:2] = header[6:8] = width.to_bytes(2, byteorder='little' if header[19] == platform['ios'] else 'big')
    header[2:4] = height.to_bytes(2, byteorder='little' if header[19] == platform['ios'] else 'big')

    if format != None:
        header[10:14] = dds[format][0]

    return header

def __dds_header(width, height, format):
    """
    Return a DDS header with the specified width, height and format values.
    """
    header = bytearray.fromhex('44 44 53 20 7C 00 00 00 07 10 08 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    header[12:16] = height.to_bytes(4, byteorder='little')
    header[16:20] = width.to_bytes(4, byteorder='little')
    header[20:24] = (height * width // (2 if format == 'BC1' else 1)).to_bytes(4, byteorder='little')
    header[84:88] = dds[format][1]
    return header

def create_ps3_img(source, dest, width, height, format='BC1'):
    """
    Convert the source image file to a PlayStation 3 IMG file for GHL with the specified size and optional format.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f ' + format)

    blob = __read(dest + '.dds')
    os.remove(dest + '.dds')

    # Replace default 128 bytes header with PS3 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 01'), width, height, format)

    __write(dest, blob)

def create_ios_img(source, dest, width, height):
    """
    Convert the source image file to an iOS IMG file for GHL with the specified size.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.pvr" -r ' + str(width) + ',' + str(height) + ' -f PVRTC1_4')

    blob = __read(dest + '.pvr')
    os.remove(dest + '.pvr')

    # Truncate metadata block and adjust metadata size in the PVR header
    del blob[67:91]
    blob[48:52] = (15).to_bytes(4, byteorder='little')
    
    # Add iOS GHL 20 bytes header
    blob = __img_header(bytearray.fromhex('00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 01 00 00 06'), width, height) + blob

    __write(dest, blob)

def create_360_img(source, dest, width, height, format='BC1'):
    """
    Convert the source image file to a Xbox 360 IMG file for GHL with the specified size.
    """
    # Resize and convert the original image
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.dds" -r ' + str(width) + ',' + str(height) + ' -f ' + format)

    blob = __read(dest + '.dds')
    os.remove(dest + '.dds')

    # Swap bytes
    for i in range(128, len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Replace default 128 bytes header with 360 GHL 20 bytes header
    blob[0:128] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 00'), width, height, format)

    __write(dest, blob)

def create_wiiu_img(source, dest, width, height):
    """
    Convert the source image file to a Wii U IMG file for GHL with the specified size.
    """
    # Resize and convert the original image to a temporary DDS texture
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + '.temp.dds" -r ' + str(width) + ',' + str(height) + ' -f BC1')

    # Convert the temporary file to a GTX texture
    subprocess.call('python ' + config['path']['gtx_extract'] + ' -o "' + dest + '.gtx" "' + dest + '.temp.dds"', shell=True)
    os.remove(dest + '.temp.dds')

    blob = __read(dest + '.gtx')
    os.remove(dest + '.gtx')

    # Replace GX2 Surface block and padding block by GX2 Surface data
    blob[32:4096] = blob[64:220]

    # Remove 32 bytes end of file block header
    blob = blob[:-32]

    # Replace default 32 bytes header with Wii U GHL 20 bytes header
    blob[0:32] = __img_header(bytearray.fromhex('00 00 00 00 00 01 00 00 00 00 00 05 00 00 01 00 00 00 03 04'), width, height)

    __write(dest, blob)

def __extract_ps3_img(source, dest, width, height, format):
    """
    Extract the source PS3 IMG file with the specified width, height and format to a decompressed format
    """
    blob = __read(source)

    # Replace PS3 GHL 20 bytes header with DDS header
    blob[0:20] = __dds_header(width, height, format)

    # Create temporary DDS file
    __write(source + '.dds', blob)

    # Convert DDS to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.dds" -o "' + source + '.dds" -d "' + dest + '" -f ' + format)
    os.remove(source + '.dds')

def __extract_ios_img(source, dest):
    """
    Extract the source iOS IMG file to a decompressed format
    """
    blob = __read(source)

    # Remove iOS GHL 20 bytes header
    del blob[0:20]

    # Create temporary PVR file
    __write(source + '.pvr', blob)

    # Convert PVR to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.pvr" -o "' + source + '.pvr" -d "' + dest + '" -f PVRTC1_4_RGB')
    os.remove(source + '.pvr')

def __extract_360_img(source, dest, width, height, format):
    """
    Extract the source Xbox 360 IMG file with the specified width, height and format to a decompressed format
    """
    blob = __read(source)

    # Replace 360 GHL 20 bytes header with DDS header
    blob[0:20] = __dds_header(width, height, format)

    # Swap bytes
    for i in range(128, len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Create temporary DDS file
    __write(source + '.dds', blob)

    # Convert DDS to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.dds" -o "' + source + '.dds" -d "' + dest + '" -f ' + format)
    os.remove(source + '.dds')

def __extract_wiiu_img(source, dest):
    """
    Extract the source Wii U IMG file to a decompressed format
    """
    blob = __read(source)

    # Replace Wii U GHL 10 bytes header with GTX header and GX2 Surface block header
    blob[0:20] = bytes.fromhex('47 66 78 32 00 00 00 20 00 00 00 07 00 00 00 01 00 00 00 02 00 00 00 01 00 00 00 00 00 00 00 00 42 4C 4B 7B 00 00 00 20 00 00 00 01 00 00 00 00 00 00 00 0B 00 00 00 9C 00 00 00 00 00 00 00 00')

    # Add swizzled image data block header and adjust data length
    blob[220:220] = bytes.fromhex('42 4C 4B 7B 00 00 00 20 00 00 00 01 00 00 00 00 00 00 00 0C 00 00 00 00 00 00 00 00 00 00 00 00')
    blob[240:244] = blob[96:100]

    # Create temporary GTX file
    __write(source + '.gtx', blob)

    # Convert GTX to decompressed format
    subprocess.call(config['path']['gtx_extract'] + ' -o "' + dest + '" "' + source + '.gtx"', shell=True)
    os.remove(source + '.gtx')

def extract_img(source, dest):
    """
    Extract the source IMG file to a decompressed format
    """
    img = open(source, 'rb')
    header = img.read(20)
    img.close()

    # Identify the platform of the IMG
    if header[19] == platform['360']:
        __extract_360_img(source, dest, int.from_bytes(header[0:2], byteorder='big'), int.from_bytes(header[2:4], byteorder='big'), 'BC1' if header[10:14] == dds['BC1'][0] else 'BC3')
    elif header[19] == platform['ps3']:
        __extract_ps3_img(source, dest, int.from_bytes(header[0:2], byteorder='big'), int.from_bytes(header[2:4], byteorder='big'), 'BC1' if header[10:14] == dds['BC1'][0] else 'BC3')
    elif header[19] == platform['wiiu']:
        __extract_wiiu_img(source, dest)
    elif header[19] == platform['ios']:
        __extract_ios_img(source, dest)
    else:
        raise ValueError('Platform not supported')

# Command line usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='A python script to extract and convert to IMG files used in Guitar Hero Live.')
    parser.add_argument('--extract', action='store_true', default=False, help='Extract a IMG file to a decompressed format')
    parser.add_argument('--platform', choices=['ps3', 'ios', '360', 'wiiu'], help='Platform of the output IMG')
    parser.add_argument('--input', required=True, help='Path of the input image or a IMG when extracting')
    parser.add_argument('--output', required=True, help='Path to the output IMG or a decompressed format when extracting')
    parser.add_argument('--width', type=int, help='Width of the output IMG')
    parser.add_argument('--height', type=int, help='Height of the output IMG')
    parser.add_argument('--format', choices=['BC1', 'BC3'], default='BC1', help='DDS format of the output IMG, used in some PS3 and 360 textures. BC1 (DXT1) is the default option')

    args = parser.parse_args()

    if (args.extract):
        extract_img(args.input, args.output)
    elif args.platform != None and args.width != None and args.height != None:
        if args.platform == 'ps3':
            create_ps3_img(args.input, args.output, args.width, args.height, args.format)
        elif args.platform == 'ios':
            create_ios_img(args.input, args.output, args.width, args.height)
        elif args.platform == '360':
            create_360_img(args.input, args.output, args.width, args.height, args.format)
        elif args.platform == 'wiiu':
            create_wiiu_img(args.input, args.output, args.width, args.height)
    else:
        parser.print_help()
        print('You must specify a platform, a width and a height for the output IMG')