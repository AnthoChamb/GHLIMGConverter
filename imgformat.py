from enum import Enum
from ddsformat import TextureFormat

class Platform(Enum):
    """
    Enum of the supported platforms
    """
    X360 = ('Xbox 360', 'big', None)
    PS3 = ('PlayStation 3', 'big', None)
    WIIU = ('Wii U', 'big', TextureFormat.GTX)
    IOS = ('iOS', 'little', TextureFormat.PVR)

    def __init__(self, fullname, byteorder, format):
        self.fullname =fullname
        self.byteorder = byteorder
        self.format = format # Default format

    @staticmethod
    def from_string(value):
        """
        Return the platform associated with its name as defined in the command line options
        """
        for platform in Platform:
            if value == platform.name.lower():
                return platform
        raise ValueError('Unknown platform')

class Game(Enum):
    """
    Enum of the supported games
    """
    GHL = 'Guitar Hero Live'
    DJH = 'DJ Hero'
    DJH2 = 'DJ Hero 2'

    @staticmethod
    def from_string(value):
        """
        Return the game associated with its name as defined in the command line options
        """
        for game in Game:
            if value == game.name.lower():
                return game
        raise ValueError('Unknown game')

class IMGFormat(Enum):
    """
    Enum of the supported combinations of platforms and games
    """
    GHLX360 = (Platform.X360, Game.GHL, bytes([0x01, 0x00, 0x00 ,0x00, 0x03, 0x00]))
    GHLPS3 = (Platform.PS3, Game.GHL, bytes([0x01, 0x00, 0x00, 0x00, 0x03, 0x01]))
    GHLWIIU = (Platform.WIIU, Game.GHL, bytes([0x01, 0x00, 0x00, 0x00, 0x03, 0x04]))
    GHLIOS = (Platform.IOS, Game.GHL, bytes([0x00, 0x00, 0x01 ,0x00, 0x00, 0x06]))
    DJHX360 = (Platform.X360, Game.DJH, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJHPS3 = (Platform.PS3, Game.DJH, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJH2X360 = (Platform.X360, Game.DJH2, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJH2PS3 = (Platform.PS3, Game.DJH2, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))

    def __init__(self, platform, game, img):
        self.platform = platform
        self.game = game
        self.img = img

    def get_header(self, width, height, format, mipmap=1):
        """
        Return a IMG header with specified width, height, mipmap count and texture format values
        """
        header = bytearray(width.to_bytes(2, byteorder=self.platform.byteorder))
        header += height.to_bytes(2, byteorder=self.platform.byteorder)
        header += (1).to_bytes(2, byteorder=self.platform.byteorder)
        header += width.to_bytes(2, byteorder=self.platform.byteorder)
        header += bytes([0x00, 0x00])
        header += format.img
        header += bytes([0x00, 0x00])
        header += self.img

        if mipmap > 1:
            header[16:18] = (mipmap - 0 if self.platform == Platform.IOS else 1).to_bytes(2, byteorder=self.platform.byteorder)

        return header

    @staticmethod
    def from_enums(platform, game):
        """
        Return the IMGFormat associated with its platform and game combination
        """
        for format in IMGFormat:
            if platform == format.platform and game == format.game:
                return format
        raise ValueError('Unknown IMG format. This platform and/or game may not be supported')

    @staticmethod
    def from_img(value):
        """
        Return the IMGFormat associated with its IMG header values
        """
        for format in IMGFormat:
            if value[18:20] == format.img[-2:]:
                return format
        raise ValueError('Unknown IMG format. This platform and/or game may not be supported')