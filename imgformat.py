from enum import Enum
from textureformat import TextureFormat
from typing import Literal

class Platform(Enum):
    """
    Enum of the supported platforms
    """
    X360 = ('Xbox 360', 'big', 1)
    PS3 = ('PlayStation 3', 'big', 1)
    WII = ('Wii', 'big', 1)
    WIIU = ('Wii U', 'big', 1)
    IOS = ('iOS', 'little', 0)

    def __init__(self, fullname: str, byteorder: Literal['little', 'big'], mipmap: int):
        self.fullname = fullname
        self.byteorder = byteorder
        self.mipmap = mipmap # Default mipmap count

    def get_mipmap_from_img(self, header: bytes):
        """
        Return the mipmap count from the specified IMG header and platform
        """
        return int.from_bytes(header[16:18], byteorder=self.byteorder) + self.mipmap

    @staticmethod
    def from_string(value: str):
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
    def from_string(value: str):
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
    DJHWII = (Platform.WII, Game.DJH, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJH2X360 = (Platform.X360, Game.DJH2, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJH2PS3 = (Platform.PS3, Game.DJH2, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
    DJH2WII = (Platform.WII, Game.DJH2, bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))

    def __init__(self, platform: Platform, game: Game, img: bytes):
        self.platform = platform
        self.game = game
        self.img = img

    def get_header(self, width: int, height: int, texture: TextureFormat, mipmap=1):
        """
        Return a IMG header with specified width, height, mipmap count and texture format values
        """
        header = bytearray(width.to_bytes(2, byteorder=self.platform.byteorder))
        header += height.to_bytes(2, byteorder=self.platform.byteorder)
        header += (1).to_bytes(2, byteorder=self.platform.byteorder)
        header += width.to_bytes(2, byteorder=self.platform.byteorder)
        header += bytes([0x00, 0x00])
        header += texture.img
        header += self.img
        header[16:18] = (mipmap - self.platform.mipmap).to_bytes(2, byteorder=self.platform.byteorder)

        return header

    @staticmethod
    def from_enums(platform: Platform, game: Game):
        """
        Return the IMGFormat associated with its platform and game combination
        """
        for img in IMGFormat:
            if platform == img.platform and game == img.game:
                return img
        raise ValueError('Unknown IMG format. This platform and/or game may not be supported')

    @staticmethod
    def from_img(value: bytes):
        """
        Return the IMGFormat associated with its IMG header values
        """
        for img in IMGFormat:
            if value[18:20] == img.img[-2:]:
                return img
        raise ValueError('Unknown IMG format. This platform and/or game may not be supported')