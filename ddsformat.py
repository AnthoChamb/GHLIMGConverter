from enum import Enum

class TextureFormat(Enum):
    """
    Enum of the supported texture formats
    """
    GTX = (bytes([0x00, 0x05]))
    PVR = (bytes([0x00, 0x00]))

    def __init__(self, img):
        self.img = img

class DDSFormat(TextureFormat, Enum):
    """
    Enum of the supported DDS texture formats
    """
    BC1 = (bytes([0x00, 0x05]), bytes([0x44, 0x58, 0x54, 0x31]), 8) # DXT1
    BC3 = (bytes([0x00, 0x09]), bytes([0x44, 0x58, 0x54, 0x35]), 16) # DXT5

    def __init__(self, img, magic, size):
        TextureFormat.__init__(self, img)
        self.magic = magic
        self.size = size # Bytes to store a block of 4x4 pixels

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

        for i in range(mipmap):
            size += self.get_size(w, h)
            w //= 2
            h //= 2

        return size

    def get_header(self, width, height, mipmap=1):
        """
        Return a DDS header with the specified width, height and mipmap count values
        """
        header = bytearray([0x44, 0x44, 0x53, 0x20, 0x7C, 0x00, 0x00, 0x00, 0x07, 0x10, 0x08, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        header[12:16] = height.to_bytes(4, byteorder='little')
        header[16:20] = width.to_bytes(4, byteorder='little')
        header[20:24] = self.get_size_mipmap(width, height, mipmap).to_bytes(4, byteorder='little')
        header[28:32] = mipmap.to_bytes(4, byteorder='little')
        header[84:88] = self.magic

        # Change flags for mipmapped texture
        if mipmap > 1:
            header[8:12] = bytes([0x07, 0x10, 0x0A, 0x00])
            header[108:112] = bytes([0x08, 0x10, 0x40, 0x00])

        return header

    @staticmethod
    def from_string(value):
        """
        Return the DDS format associated with its name as defined in the command line options
        """
        for format in DDSFormat:
            if value == format.name:
                return format
        raise ValueError('Unknown format')

    @staticmethod
    def from_img(value):
        """
        Return the DDS format associated with its IMG header value
        """
        for format in DDSFormat:
            if value[10:12] == format.img:
                return format
        raise ValueError('Unknown format')