from enum import Enum
import struct

class TextureFormat():
    """
    Base class of the supported texture formats
    """
    def __init__(self, img: int, alpha: int):
        self.img = img
        self.alpha = alpha

class BlockTextureFormat(TextureFormat):
    """
    Base class of the supported block based texture formats
    """
    def __init__(self, img: int, alpha: int, width: int, height: int, size: int):
        TextureFormat.__init__(self, img, alpha)
        self.width = width # Block width
        self.height = height # Block height
        self.size = size # Block size

    def get_size(self, width: int, height: int):
        """
        Return the size of the texture with the specified width and height values
        """
        return max(1, (width + self.width - 1) // self.width) * max(1, (height + self.height - 1) // self.height) * self.size

    def get_size_mipmap(self, width: int, height: int, mipmap: int):
        """
        Return the size of the texture with specifed width, height and mipmap count
        """
        size = 0
        w = width
        h = height

        for _ in range(mipmap):
            size += self.get_size(w, h)
            w //= 2
            h //= 2

        return size

class PVRFormat(TextureFormat, Enum):
    """
    Enum of the supported iOS texture formats
    """
    PVRTC1_4 = (0x00_00_00_00, 0x00_00)

    def __init__(self, img: int, alpha: int):
        TextureFormat.__init__(self, img, alpha)

    @staticmethod
    def get_sizes_from_header(header: bytes):
        """
        Return the width and height values from the PVR header of a texture
        """
        return int.from_bytes(header[28:32], byteorder='little'), int.from_bytes(header[24:28], byteorder='little')

class DDSFormat(BlockTextureFormat, Enum):
    """
    Enum of the supported DDS texture formats
    """
    BC1 = (0x00_00_00_05, 0x00_00, bytes([0x44, 0x58, 0x54, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 8, True) # DXT1
    BC2 = (0x00_00_00_07, 0x00_01, bytes([0x44, 0x58, 0x54, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 16, True) # DXT3
    BC3 = (0x00_00_00_09, 0x00_FF, bytes([0x44, 0x58, 0x54, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 16, True) # DXT5
    R8G8B8A8 = (0x00_00_00_03, 0x00_00, bytes([0x44, 0x58, 0x31, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1C, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 32, False)

    def __init__(self, img: int, alpha: int, dxt: bytes, size: int, compressed: bool):
        BlockTextureFormat.__init__(self, img, alpha, 4, 4, size)
        self.dxt = dxt
        self.compressed = compressed

    def get_pitch(self, width: int):
        """
        Return the pitch of the DDS texture with the specified width
        """
        return (width * self.size + 7) // 8

    def get_flags(self, mipmap: int):
        """
        Return the flags of the DDS header with the specified mipmap count
        """
        flags = 0b00000111_00010000_00000000_00000000
        flags |= 0b00001000_00000000 if self.compressed else 0b0001000_00000000_00000000_00000000
        if mipmap > 1:
            flags |= 0b00000010_00000000
        return flags

    def get_header(self, width: int, height: int, mipmap: int):
        """
        Return a DDS header with the specified width, height and mipmap count values
        """
        header = bytearray([0x44, 0x44, 0x53, 0x20, 0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00])

        header[8:12] = self.get_flags(mipmap).to_bytes(4, byteorder='big')
        header[12:16] = height.to_bytes(4, byteorder='little')
        header[16:20] = width.to_bytes(4, byteorder='little')
        header[20:24] = self.get_size_mipmap(width, height, mipmap).to_bytes(4, byteorder='little') if self.compressed else self.get_pitch(width).to_bytes(4, byteorder='little')
        header[28:32] = mipmap.to_bytes(4, byteorder='little')
        header += self.dxt

        # Change flags for mipmapped texture in DXT header
        if mipmap > 1:
            header[108:112] = bytes([0x08, 0x10, 0x40, 0x00])

        return header

    def get_header_size(self):
        """
        Return the size of the DDS header of this format
        """
        return 84 + len(self.dxt)

    @staticmethod
    def get_sizes_from_header(header: bytes):
        """
        Return the width and height values from the DDS header of a texture
        """
        return int.from_bytes(header[16:20], byteorder='little'), int.from_bytes(header[12:16], byteorder='little')

    @staticmethod
    def from_string(value: str):
        """
        Return the DDS format associated with its name as defined in the command line options
        """
        for dds in DDSFormat:
            if value == dds.name:
                return dds
        raise ValueError('Unknown format')

class TEX0Format(BlockTextureFormat, Enum):
    """
    Enum of the supported TEX0 texture formats
    """
    CMPR = (0x00_00_00_05, 0x00_00, bytes([0x00, 0x00, 0x00, 0x0E]), 8, 8, 32)
    RGB5A3 = (0x00_00_00_02, 0x00_00, bytes([0x00, 0x00, 0x00, 0x05]), 4, 4, 32)
    IA4 = (0x00_00_00_01, 0x00_00, bytes([0x00, 0x00, 0x00, 0x02]), 8, 4, 32)

    def __init__(self, img: int, alpha: int, tex0: bytes, width: int, height: int, size: int):
        BlockTextureFormat.__init__(self, img, alpha, width, height, size)
        self.tex0 = tex0

    def get_header(self, width: int, height: int, mipmap: int):
        """
        Return a TEX0 header with the specified width, height and mipmap count values
        """
        size = self.get_size_mipmap(width, height, mipmap)

        header = bytes([0x54, 0x45, 0x58, 0x30])
        header += (size + 64).to_bytes(4, byteorder='big')
        header += (3).to_bytes(4, byteorder='big')
        header += bytes([0x00, 0x00, 0x00, 0x00])
        header += (64).to_bytes(4, byteorder='big')
        header += (size + 64).to_bytes(4, byteorder='big')
        header += bytes([0x00, 0x00, 0x00, 0x00])
        header += width.to_bytes(2, byteorder='big')
        header += height.to_bytes(2, byteorder='big')
        header += self.tex0
        header += mipmap.to_bytes(4, byteorder='big')
        header += bytes([0x00, 0x00, 0x00, 0x00])
        header += struct.pack(">f", mipmap - 1.0)
        header += bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        return header

    @staticmethod
    def get_sizes_from_header(header: bytes):
        """
        Return the width and height values from the TEX0 header of a texture
        """
        return int.from_bytes(header[28:30], byteorder='big'), int.from_bytes(header[30:32], byteorder='big')

    @staticmethod
    def from_string(value: str):
        """
        Return the TEX0 format associated with its name as defined in the command line options
        """
        for tex0 in TEX0Format:
            if value == tex0.name:
                return tex0
        raise ValueError('Unknown format')