[![Build Status](https://travis-ci.org/amiaopensource/DVD2LS.svg?branch=master)](https://travis-ci.org/amiaopensource/DVD2LS)
# DVD2LS
Python based app for ripping DVD to ISO, and converting extracted ISO .vob files to an access video file.

## Install

To install, open a terminal and run the following command from the DVD2LS 
directory 

`python setup.py install`

## Usage

### Ripping a DVD to ISO

`dvdrip -o [PATH_TO_OUTPUT_DIRECTORY]`

### Transcoding ISO to Access File

`dvdtranscode -i [PATH_TO_ISO] -f [OUTPUT_FORMAT]`

### Available Output Formats

```
H.264
v210
ProRes
FFv1
```

## Documentation

To build HTML documentation, open a terminal and run the following command from the DVD2LS 
directory  

`python setup.py build_sphinx`

**NOTE:** This requires the 
[Sphinx Python package](https://pypi.org/project/Sphinx/) to be installed.

## Development

if you have pipenv installed you can create a development environment with 
the following command run inside the DVD2LS source directory.

`pipenv install --dev`

## Credits

The scripting and documentation was created by author = ['Henry Borchers', 'Michael Campos-Quinn', 'Claire Fox', 'Morgan Oscar Morel']