# GHL IMG Converter
A python script and module to extract and convert to IMG files used in some FSG games like Guitar Hero Live, DJ Hero and DJ Hero 2

## Usage
### Extraction
**Extract** a IMG file to a decompressed format

```
ghl_img_converter.py extract input [--output OUTPUT] [--platform {ps3,ios,x360,wiiu}]
```

#### Arguments
`input` Path of the input IMG file or root folder to extract

`--output OUTPUT` Path to the output decompressed format or output folder

`--platform {ps3,ios,x360,wiiu}` Force extraction from the specified platform

### Conversion
**Convert** an image to a IMG file

```
ghl_img_converter.py convert input [--output OUTPUT] --platform {ps3,ios,x360,wiiu} [--game {ghl,djh,djh2}] [--width WIDTH] [--height HEIGHT] [--format {BC1,BC3,R8G8B8A8}] [--mipmap MIPMAP]
```

#### Arguments
`input` Path of the input image to convert

`--output OUTPUT` Path to the output IMG

`--platform {ps3,ios,x360,wiiu}` Platform to convert the IMG to

`--game {ghl,djh,djh2}` Game to convert the IMG to, used in PS3 and X360 textures. Default option is `ghl`

`--width WIDTH` Width of the output IMG

`--height HEIGHT` Height of the output IMG

`--format {BC1,BC3,R8G8B8A8}` DDS format of the output IMG, used in PS3 and X360 textures. Default option is `BC1`

`--mipmap MIPMAP` Mipmap count of the output IMG. Default option is `1`

## Requirements
This program currently requires [PVRTexToolCLI.exe](https://www.imgtec.com/developers/powervr-sdk-tools/pvrtextool/) installed and added to your `config.ini` file

Wii U conversion also requires [gtx_extractor.py](https://github.com/aboood40091/GTX-Extractor) installed and added to your `config.ini` file

## Contributing
Feel free to contribute for more formats and platforms support

## Thanks
A special thanks to everyone in the [GHLRE organization](https://github.com/ghlre) and Discord who helped figure out the image formats before me!