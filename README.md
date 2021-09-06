# GHL IMG Converter
A python script and module to extract and convert to IMG files used in some FSG games like Guitar Hero Live, DJ Hero and DJ Hero 2

## Usage
### Extraction
**Extract** a IMG file to a decompressed format

```
ghl_img_converter.py extract input [--output OUTPUT] [--platform {ps3,ios,x360,wiiu,wii}]
```

#### Arguments
`input` Path of the input IMG file or root folder to extract

`--output OUTPUT` Path to the output decompressed format or output folder

`--platform {ps3,ios,x360,wiiu,wii}` Force extraction from the specified platform

### Conversion
**Convert** an image to a IMG file

```
ghl_img_converter.py convert input [--output OUTPUT] --platform {ps3,ios,x360,wiiu,wii} [--game {ghl,djh,djh2}] [--width WIDTH] [--height HEIGHT] [--format {BC1,BC2,BC3,R8G8B8A8}] [--tex0 {CMPR,RGB5A3,IA4}] [--mipmap MIPMAP] [--flip]
```

#### Arguments
`input` Path of the input image or root folder to convert

`--output OUTPUT` Path to the output IMG or folder

`--platform {ps3,ios,x360,wiiu,wii}` Platform to convert the IMG to

`--game {ghl,djh,djh2}` Game to convert the IMG to, used in PS3 and X360 textures. Default option is `ghl`

`--width WIDTH` Width of the output IMG.  Not supported on Wii textures

`--height HEIGHT` Height of the output IMG.  Not supported on Wii textures

`--format {BC1,BC2,BC3,R8G8B8A8}` DDS format of the output IMG, used in PS3 and X360 textures. Default option is `BC1`

`--tex0 {CMPR,RGB5A3,IA4}` TEX0 format of the output IMG, used in Wii textures. Default option is `RGB5A3`

`--mipmap MIPMAP` Mipmap count of the output IMG

`--flip` Vertically flip the output IMG. Not supported on Wii textures

### Information
Prints **information** about the IMG file

```
ghl_img_converter.py info input
```

#### Arguments
`input` Path of the input IMG file

## Requirements
This program currently requires [PVRTexToolCLI.exe](https://www.imgtec.com/developers/powervr-sdk-tools/legacy-downloads/) version 4.23 or earlier installed and added to your `config.ini` file. Downloading PowerVRSDK-4.0 is recommended.

Wii U conversion also requires [gtx_extractor.py](https://github.com/aboood40091/GTX-Extractor) installed and added to your `config.ini` file.

Wii conversion only requires [wimgt.exe](https://szs.wiimm.de/wimgt/) installed and added to your `config.ini` file.

## Contributing
Feel free to contribute for more formats and platforms support

## Thanks
A special thanks to everyone in the [GHLRE organization](https://github.com/ghlre) and Discord who helped figure out the image formats before me!