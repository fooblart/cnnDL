# cnnDL
## simple cli application to download videos from cnn articles

Setup: `python3 main.py addalias --alias && chmod +x main.py && exec bash`

Usage: `cnnDL https://cnn.com/fakenewsbshere`

### Flags: 
[-o, --output] Directory to place downloaded files, one will be created if it does not exist already.

E.g: `cnnDL https://cnn.com/blahblahblah --output output`

[--file] Uses the input argument as the name of a file which contains multiple links to download.

E.g: `cnnDL input --file`

