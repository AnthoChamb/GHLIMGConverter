# GHL IMG Converter
A python script and module to extract and convert to IMG files used in some FSG games like Guitar Hero Live, DJ Hero and DJ Hero 2

## Arguments
`--extract` to extract a IMG file to a decompressed format

`--platform` to specify the platform of the IMG

`--input` to specify the path of the input
- original image when converting,
- IMG file or root folder to extract

`--output` to specify the path of the output
- IMG file when converting,
- decompressed format or output folder to extract to

`--width` to specify the width of the output IMG

`--height` to specify the height of the output IMG

`--format` to specify the DDS format of the output IMG, used in some PS3 and 360 textures

## Requirements
This program currently requires [PVRTexToolCLI.exe](https://www.imgtec.com/developers/powervr-sdk-tools/pvrtextool/) installed and added to your `config.ini` file

Wii U conversion also requires [gtx_extractor.py](https://github.com/aboood40091/GTX-Extractor) installed and added to your `config.ini` file

## Contributing
Feel free to contribute for more formats and platforms support

## Thanks
A special thanks to everyone in the [GHLRE organization](https://github.com/ghlre) and Discord who helped figure out the image formats before me!