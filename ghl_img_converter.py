import configparser
import os
import subprocess

from imgformat import IMGFormat, Platform, Game
from textureformat import DDSFormat, PVRFormat, TEX0Format
from typing import Optional

config = configparser.ConfigParser()
config.read('config.ini')

def __read(filename: str):
    """
    Read the specified file.
    Return a byte array of the file.
    """
    file = open(filename, 'rb')
    blob = bytearray(file.read())
    file.close()
    return blob

def __read_header(filename: str):
    """
    Read the specified file.
    Return a byte array of the IMG header.
    """
    file = open(filename, 'rb')
    header = file.read(20)
    file.close()
    return header

def __write(dest: str, blob: bytes):
    """
    Write binary to the destination file.
    """
    file = open(dest, 'wb')
    file.write(blob)
    file.close()

def __create__pvrtextoolcli(source: str, dest: str, ext: str, width: int, height: int, texture: str, mipmap: int, flip: bool):
    """
    Convert the source image using PVRTexToolCLI
    """
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '" -o "' + dest + ext + '"' + ('' if width == None or height == None else (' -r ' + str(width) + ',' + str(height))) + ' -f ' +texture + ' -m ' + str(mipmap) + (' -flip y' if flip else ''))

def __create_dds_img(img: IMGFormat, source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, mipmap=1, flip=False):
    """
    Convert the source image file to an IMG file with the specified size, format, game and mipmap count.
    """
    __create__pvrtextoolcli(source, dest, '.dds', width, height, dds.name, mipmap, flip)

    blob = __read(dest + '.dds')

    if width == None or height == None:
        width, height = dds.get_sizes_from_header(blob)

    os.remove(dest + '.dds')

    if not dds.compressed:
        # Swap bytes to ABGR
        for i in range(dds.get_header_size(), len(blob), 4):
            blob[i], blob[i + 1], blob[i + 2], blob[i + 3] = blob[i + 3], blob[i + 2], blob[i + 1], blob[i]

    # Replace DDS header with IMG 20 bytes header
    blob[0:dds.get_header_size()] = img.get_header(width, height, dds, mipmap)

    __write(dest, blob)

def create_ps3_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, game=Game.GHL, mipmap=1, flip=False):
    """
    Convert the source image file to a PlayStation 3 IMG file with the specified size, format, game and mipmap count.
    """
    __create_dds_img(IMGFormat.from_enums(Platform.PS3, game), source, dest, width, height, dds, mipmap, flip)

def create_pc_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, mipmap=1, flip=False):
    """
    Convert the source image file to a PC IMG file with the specified size, format and mipmap count.
    """
    __create_dds_img(IMGFormat.GHLPC, source, dest, width, height, dds, mipmap, flip)
    
def create_x1_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, mipmap=1, flip=False):
    """
    Convert the source image file to a Xbox One IMG file with the specified size, format and mipmap count.
    """
    __create_dds_img(IMGFormat.GHLX1, source, dest, width, height, dds, mipmap, flip)

def create_ios_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, pvr=PVRFormat.PVRTC1_4, mipmap=1, flip=False):
    """
    Convert the source image file to a GHL iOS IMG file with the specified size and mipmap count.
    """
    __create__pvrtextoolcli(source, dest, '.pvr', width, height, pvr.name, mipmap, flip)

    blob = __read(dest + '.pvr')

    if width == None or height == None:
        width, height = PVRFormat.get_sizes_from_header(blob)

    os.remove(dest + '.pvr')

    # Truncate metadata block and adjust metadata size in the PVR header
    del blob[67:91]
    blob[48:52] = (15).to_bytes(4, byteorder='little')
    
    # Prepend GHL iOS IMG 20 bytes header
    blob = IMGFormat.GHLIOS.get_header(width, height, pvr, mipmap) + blob

    __write(dest, blob)

def create_x360_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, game=Game.GHL, mipmap=1, flip=False):
    """
    Convert the source image file to a Xbox 360 IMG file with the specified size, format, game and mipmap count.
    """
    __create__pvrtextoolcli(source, dest, '.dds', width, height, dds.name, mipmap, flip)

    blob = __read(dest + '.dds')

    if width == None or height == None:
        width, height = dds.get_sizes_from_header(blob)

    os.remove(dest + '.dds')

    # Swap bytes
    for i in range(dds.get_header_size(), len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    if not dds.compressed:
        # Swap bytes to ABGR
        for i in range(dds.get_header_size(), len(blob), 4):
            blob[i], blob[i + 1], blob[i + 2], blob[i + 3] = blob[i + 3], blob[i + 2], blob[i + 1], blob[i]

    # Replace DDS header with X360 IMG 20 bytes header from the specified game
    blob[0:dds.get_header_size()] = IMGFormat.from_enums(Platform.X360, game).get_header(width, height, dds, mipmap)

    __write(dest, blob)

def create_wiiu_img(source: str, dest: str, width: Optional[int]=None, height: Optional[int]=None, dds=DDSFormat.BC1, mipmap=1, flip=False):
    """
    Convert the source image file to a GHL Wii U IMG file with the specified size and mipmap count.
    """
    __create__pvrtextoolcli(source, dest, '.temp.dds', width, height, dds.name, mipmap, flip)

    # Convert the temporary file to a GTX texture
    subprocess.call('python3 ' + config['path']['gtx_extract'] + ' -o "' + dest + '.gtx" "' + dest + '.temp.dds"', shell=True)

    blob = __read(dest + '.temp.dds')

    if width == None or height == None:
        width, height = DDSFormat.get_sizes_from_header(blob)

    os.remove(dest + '.temp.dds')

    blob = __read(dest + '.gtx')
    os.remove(dest + '.gtx')

    # Replace GX2 Surface block and padding block by GX2 Surface data
    blob[32:4096] = blob[64:220]

    # Remove 32 bytes end of file block header
    blob = blob[:-32]

    # Replace GTX 32 bytes header with GHL Wii U IMG 20 bytes header
    blob[0:32] = IMGFormat.GHLWIIU.get_header(width, height, dds, mipmap)

    __write(dest, blob)

def create_wii_img(source: str, dest: str, tex0=TEX0Format.RGB5A3, game=Game.DJH2, mipmap=1):
    """
    Convert the source image file to a Wii IMG file with the specified format, game and mipmap count.
    """
    # Convert the source file to a TEX0 texture
    subprocess.call(config['path']['wimgt'] + ' encode "' + source + '" -d "' + dest + '.tex" -x ' + tex0.name + ' --n-mm ' + str(mipmap - 1))

    blob = __read(dest + '.tex')

    width, height = TEX0Format.get_sizes_from_header(blob)

    os.remove(dest + '.tex')

    # Replace TEX0 header with Wii IMG 20 bytes header from the specified game
    blob[0:64] = IMGFormat.from_enums(Platform.WII, game).get_header(width, height, tex0, mipmap)
    
    # Remove name metadata
    blob = blob[:tex0.get_size_mipmap(width, height, mipmap) + 20]

    __write(dest, blob)

def __extract_dds_img(source: str, dest: str, width: int, height: int, dds: DDSFormat, mipmap: int):
    """
    Extract the source DDS IMG file with the specified width, height, format and mipmap count to a decompressed format
    """
    blob = __read(source)

    # Replace IMG 20 bytes header with DDS header
    blob[0:20] = dds.get_header(width, height, mipmap)

    if not dds.compressed:
        # Swap bytes to RGBA
        for i in range(dds.get_header_size(), len(blob), 4):
            blob[i], blob[i + 1], blob[i + 2], blob[i + 3] = blob[i + 3], blob[i + 2], blob[i + 1], blob[i]

    # Create temporary DDS file
    __write(source + '.dds', blob)

    # Convert DDS to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.dds" -o "' + source + '.dds" -d "' + dest + '" -f ' + dds.name)
    os.remove(source + '.dds')

def __extract_ios_img(source: str, dest: str):
    """
    Extract the source iOS IMG file to a decompressed format
    """
    blob = __read(source)

    # Remove iOS IMG 20 bytes header
    del blob[0:20]

    # Create temporary PVR file
    __write(source + '.pvr', blob)

    # Convert PVR to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.pvr" -o "' + source + '.pvr" -d "' + dest + '" -f PVRTC1_4_RGB')
    os.remove(source + '.pvr')

def __extract_x360_img(source: str, dest: str, width: int, height: int, dds: DDSFormat, mipmap: int):
    """
    Extract the source Xbox 360 IMG file with the specified width, height, format and mipmap count to a decompressed format
    """
    blob = __read(source)

    # Replace X360 IMG 20 bytes header with DDS header
    blob[0:20] = dds.get_header(width, height, mipmap)

    if not dds.compressed:
        # Swap bytes to RGBA
        for i in range(dds.get_header_size(), len(blob), 4):
            blob[i], blob[i + 1], blob[i + 2], blob[i + 3] = blob[i + 3], blob[i + 2], blob[i + 1], blob[i]

    # Swap bytes
    for i in range(dds.get_header_size(), len(blob), 2):
        blob[i], blob[i + 1] = blob[i + 1], blob[i]

    # Create temporary DDS file
    __write(source + '.dds', blob)

    # Convert DDS to decompressed format
    subprocess.call(config['path']['PVRTexToolCLI'] + ' -i "' + source + '.dds" -o "' + source + '.dds" -d "' + dest + '" -f ' + dds.name)
    os.remove(source + '.dds')

def __extract_wiiu_img(source: str, dest: str):
    """
    Extract the source Wii U IMG file to a decompressed format
    """
    blob = __read(source)

    # Replace Wii U IMG 20 bytes header with GTX header and GX2 Surface block header
    blob[0:20] = bytes.fromhex('47 66 78 32 00 00 00 20 00 00 00 07 00 00 00 01 00 00 00 02 00 00 00 01 00 00 00 00 00 00 00 00 42 4C 4B 7B 00 00 00 20 00 00 00 01 00 00 00 00 00 00 00 0B 00 00 00 9C 00 00 00 00 00 00 00 00')

    # Add swizzled image data block header and adjust data length
    blob[220:220] = bytes.fromhex('42 4C 4B 7B 00 00 00 20 00 00 00 01 00 00 00 00 00 00 00 0C 00 00 00 00 00 00 00 00 00 00 00 00')
    blob[240:244] = blob[96:100]

    # Create temporary GTX file
    __write(source + '.gtx', blob)

    # Convert GTX to decompressed format
    subprocess.call('python3 ' + config['path']['gtx_extract'] + ' -o "' + dest + '" "' + source + '.gtx"', shell=True)
    os.remove(source + '.gtx')

def __extract_wii_img(source: str, dest: str, width: int, height: int, tex0: TEX0Format, mipmap: int):
    """
    Extract the source Wii IMG file with the specified width, height, format and mipmap count to a decompressed format
    """
    blob = __read(source)

    # Replace Wii IMG 20 bytes header with TEX0 header
    blob[0:20] = tex0.get_header(width, height, mipmap)

    # Create temporary TEX0 file
    __write(source + '.tex', blob)
    
    # Convert TEX0 to decompressed format
    subprocess.call(config['path']['wimgt'] + ' decode "' + source + '.tex" -d "' + dest + '" --no-mm')
    os.remove(source + '.tex')

def extract_img(source: str, dest: str, platform: Optional[Platform]=None):
    """
    Extract the source IMG file to a decompressed format
    """
    header = __read_header(source)

    # Identify the platform of the IMG
    if platform == None:
        platform = IMGFormat.from_img(header).platform

    if platform == Platform.X360:
        __extract_x360_img(source, dest, platform.get_width_from_img(header), platform.get_height_from_img(header), platform.get_dds_from_img(header), platform.get_mipmap_from_img(header))
    elif platform == Platform.PS3 or platform == Platform.PC or platform == Platform.X1:
        __extract_dds_img(source, dest, platform.get_width_from_img(header), platform.get_height_from_img(header), platform.get_dds_from_img(header), platform.get_mipmap_from_img(header))
    elif platform == Platform.WII:
        __extract_wii_img(source, dest, platform.get_width_from_img(header), platform.get_height_from_img(header), platform.get_tex0_from_img(header), platform.get_mipmap_from_img(header))
    elif platform == Platform.WIIU:
        __extract_wiiu_img(source, dest)
    elif platform == Platform.IOS:
        __extract_ios_img(source, dest)
    else:
        raise ValueError('Platform not supported')

def __format_list(elements: list, separator = ', ', last_separator = ', ', empty = 'Empty', selector = lambda x : str(x)):
    """
    Return a formatted string from a list of elements
    """
    count = len(elements)

    if count > 0:
        result = ''

        for i in range(count):
            result += selector(elements[i])

            if i <  count - 1:
                if i < count - 2:
                    result += separator
                else:
                    result += last_separator
        
        return result
    else:
        return empty

def get_texture_formats(img: IMGFormat, header: bytes):
    """
    Return the texture formats associated with the specified IMG header value
    """
    textures = []
    
    try:
        textures.append(img.platform.get_dds_from_img(header))
    except ValueError:
        pass
        
    if not img.game == Game.GHL:
        try:
            textures.append(img.platform.get_tex0_from_img(header))
        except ValueError:
            pass
    
    return textures

def __get_texture_format_info(img: IMGFormat, header: bytes):
    """
    Return a formatted string of the texture format information from an IMG format and its IMG header value
    """
    if img.platform == Platform.IOS:
        return PVRFormat.PVRTC1_4.name
    else:
        textures = get_texture_formats(img, header)
        return __format_list(textures, ', ', ' or ', 'Unknown format', lambda x : x.name)

def print_info(path: str):
    """
    Prints information about the IMG file
    """
    header = __read_header(path)
    img = IMGFormat.from_img(header)

    print('Width          = ' + str(img.platform.get_width_from_img(header)))
    print('Height         = ' + str(img.platform.get_height_from_img(header)))
    print('Texture format = ' + __get_texture_format_info(img, header))
    print('Mipmap count   = ' + str(img.platform.get_mipmap_from_img(header)))
    print('Platform       = ' + (img.platform.fullname if img.game == Game.GHL else (Platform.X360.fullname + ', ' + Platform.PS3.fullname + ' or ' + Platform.WII.fullname)))
    print('Game           = ' + (img.game.value if img.game == Game.GHL else (Game.DJH.value + ' or ' + Game.DJH2.value)))

def __extract_args(args):
    """
    Extract using command line arguments
    """
    # Batch extract
    if os.path.isdir(args.input):
        for subdir, _, files in os.walk(args.input):
            out_folder = os.path.join(args.output if args.output != None else args.input, os.path.relpath(subdir, args.input))
            if not os.path.exists(out_folder):
                os.mkdir(out_folder)

            for f in files:
                if f.lower().endswith('.img'):
                    try:
                        __extract_args_single(args, os.path.join(subdir, f), os.path.join(out_folder, os.path.splitext(f)[0] + '.png'))
                    except ValueError:
                        print('Error with file : ' + os.path.join(subdir, f))
    # Single extract
    else:
        __extract_args_single(args, args.input, args.output if args.output != None else os.path.splitext(args.input)[0] + '.png')

def __extract_args_single(args, source: str, dest: str):
    """
    Extract a single file using the command line arguments and the specified input and output
    """
    extract_img(source, dest, None if args.platform == None else Platform.from_string(args.platform))

def __convert_args(args):
    """
    Convert using the commannd line arguments
    """
    # Batch convert
    if os.path.isdir(args.input):
        for subdir, _, files in os.walk(args.input):
            out_folder = os.path.join(args.output if args.output != None else args.input, os.path.relpath(subdir, args.input))
            if not os.path.exists(out_folder):
                os.mkdir(out_folder)

            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    try:
                        __convert_args_single(args, os.path.join(subdir, f), os.path.join(out_folder, os.path.splitext(f)[0] + '.img'))
                    except ValueError:
                        print('Error with file : ' + os.path.join(subdir, f))
    # Single convert
    else:
        __convert_args_single(args, args.input, args.output if args.output != None else os.path.splitext(args.input)[0] + '.img')

def __convert_args_single(args, source: str, dest: str):
    """
    Convert a single file using the command line arguments and the specified input and output
    """
    if args.platform == 'ps3':
        create_ps3_img(source, dest, args.width, args.height, DDSFormat.from_string(args.format), Game.from_string(args.game), args.mipmap, args.flip)
    elif args.platform == 'pc':
        create_pc_img(source, dest, args.width, args.height, DDSFormat.from_string(args.format), args.mipmap, args.flip)
    elif args.platform == 'x1':
        create_x1_img(source, dest, args.width, args.height, DDSFormat.from_string(args.format), args.mipmap, args.flip)
    elif args.platform == 'ios':
        create_ios_img(source, dest, args.width, args.height, PVRFormat.PVRTC1_4, args.mipmap, args.flip)
    elif args.platform == 'x360':
        create_x360_img(source, dest, args.width, args.height, DDSFormat.from_string(args.format), Game.from_string(args.game), args.mipmap, args.flip)
    elif args.platform == 'wiiu':
        create_wiiu_img(source, dest, args.width, args.height, DDSFormat.from_string(args.format), args.mipmap, args.flip)
    elif args.platform == 'wii':
        create_wii_img(source, dest, TEX0Format.from_string(args.tex0), Game.from_string(args.game), args.mipmap)

def __info_args(args):
    """
    Prints the informations using the command line arguments
    """
    print_info(args.input)

if __name__ == "__main__":
    import sys

    # Drag and drop extraction
    if len(sys.argv) == 2 and sys.argv[1].lower().endswith('.img'):
        extract_img(sys.argv[1], os.path.splitext(sys.argv[1])[0] + '.png')
    # Command line usage
    else:
        import argparse

        parser = argparse.ArgumentParser(description='A python script to extract and convert to IMG files used in some FSG games like Guitar Hero Live, DJ Hero and DJ Hero 2.')
        sp = parser.add_subparsers(help='You must choose one of the following commands')
        
        sp_extract = sp.add_parser('extract', help='Extract a IMG file to a decompressed format')
        sp_extract.set_defaults(func=__extract_args)
        sp_extract.add_argument('input', help='Path of the input IMG file or root folder to extract')
        sp_extract.add_argument('--output', help='Path to the output decompressed format or output folder')
        sp_extract.add_argument('--platform', choices=['ps3', 'pc', 'x1', 'ios', 'x360', 'wiiu', 'wii'], help='Force extraction from the specified platform')

        sp_convert = sp.add_parser('convert', help='Convert an image to a IMG file')
        sp_convert.set_defaults(func=__convert_args)
        sp_convert.add_argument('input', help='Path of the input image or root folder to convert')
        sp_convert.add_argument('--output', help='Path to the output IMG or folder')
        sp_convert.add_argument('--platform', choices=['ps3', 'pc', 'x1', 'ios', 'x360', 'wiiu', 'wii'], required=True, help='Platform to convert the IMG to')
        sp_convert.add_argument('--game', choices=['ghl', 'djh', 'djh2'], default='ghl', help='Game to convert the IMG to, used in PS3 and X360 textures. Default option is ghl')
        sp_convert.add_argument('--width', type=int, help='Width of the output IMG. Not supported on Wii textures')
        sp_convert.add_argument('--height', type=int, help='Height of the output IMG. Not supported on Wii textures')
        sp_convert.add_argument('--format', choices=['BC1', 'BC2', 'BC3', 'R8G8B8A8'], default='BC1', help='DDS format of the output IMG, used in PS3, PC, X1, X360 and Wii U textures. Default option is BC1')
        sp_convert.add_argument('--tex0', choices=['CMPR', 'RGB5A3', 'IA4'], default='RGB5A3', help='TEX0 format of the output IMG, used in Wii textures. Default option is RGB5A3')
        sp_convert.add_argument('--mipmap', type=int, default=1, help='Mipmap count of the output IMG')
        sp_convert.add_argument('--flip', action="store_true", default=False, help='Vertically flip the output IMG. Not supported on Wii textures')

        sp_info = sp.add_parser('info', help='Prints information about the IMG file')
        sp_info.set_defaults(func=__info_args)
        sp_info.add_argument('input', help='Path of the input IMG file')

        args = parser.parse_args()
        args.func(args)
