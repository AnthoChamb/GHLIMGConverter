from enum import Enum

class TextureFormat():
    """
    Base class of the supported texture formats
    """
    def __init__(self, img):
        self.img = img

class WiiUFormat(TextureFormat, Enum):
    """
    Enum of the supported Wii U texture formats
    """
    GTX = (bytes([0x00, 0x05, 0x00, 0x00]))

    def __init__(self, img):
        TextureFormat.__init__(self, img)

class IOSFormat(TextureFormat, Enum):
    """
    Enum of the supported iOS texture formats
    """
    PVR = (bytes([0x00, 0x00, 0x00, 0x00]))

    def __init__(self, img):
        TextureFormat.__init__(self, img)

class DDSFormat(TextureFormat, Enum):
    """
    Enum of the supported DDS texture formats
    """
    BC1 = (bytes([0x00, 0x05, 0x00, 0x00]), bytes([0x44, 0x58, 0x54, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 8, True) # DXT1
    BC3 = (bytes([0x00, 0x09, 0x00, 0xFF]),bytes([0x44, 0x58, 0x54, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 16, True) # DXT5
    R8G8B8A8 = (bytes([0x00, 0x03, 0x00, 0x00]), bytes([0x44, 0x58, 0x31, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1C, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), 32, False)

    def __init__(self, img, dxt, size, compressed):
        TextureFormat.__init__(self, img)
        self.dxt = dxt
        self.size = size # Bytes to store a block of 4x4 pixels
        self.compressed = compressed

    def get_size(self, width, height):
        """
        Return the size of the DDS texture with the specified width and height values
        """
        return max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * self.size

    def get_size_mipmap(self, width, height, mipmap):
        """
        Return the size of the DDS texture with specifed width, height and mipmap count
        """
        size = 0
        w = width
        h = height

        for _ in range(mipmap):
            size += self.get_size(w, h)
            w //= 2
            h //= 2

        return size

    def get_pitch(self, width):
        """
        Return the pitch of the DDS texture with the specified width
        """
        return (width * self.size + 7) // 8

    def get_flags(self, mipmap):
        """
        Return the flags of the DDS header with the specified mipmap count
        """
        flags = 0b00000111_00010000_00000000_00000000
        flags |= 0b00001000_00000000 if self.compressed else 0b0001000_00000000_00000000_00000000
        if mipmap > 1:
            flags |= 0b00000010_00000000
        return flags

    def get_header(self, width, height, mipmap):
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
    def from_string(value):
        """
        Return the DDS format associated with its name as defined in the command line options
        """
        for dds in DDSFormat:
            if value == dds.name:
                return dds
        raise ValueError('Unknown format')

    @staticmethod
    def from_img(value):
        """
        Return the DDS format associated with its IMG header value
        """
        for dds in DDSFormat:
            if value[10:12] == dds.img[0:2]:
                return dds
        raise ValueError('Unknown format')