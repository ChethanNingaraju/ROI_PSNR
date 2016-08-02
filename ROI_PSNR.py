#!/usr/bin/python

import sys
import docopt
import numpy as np
import array
import os
###
# Docopt
###
DOC = """
usage:
   ROI_PSNR [options]

options:
     -w, --width=NUMBER            Width of yuv files
     -h, --height=NUMBER           height of yuv files
     -r, --reffile=STRING          path of reference file for PSNR calculation
     -i, --infile=STRING           path of path file for PSNR calculation
     -m, --mapfile=STRING          Binary file to specify region of interest
"""

###
# Script
###

"""
****************** Startup *****************
"""

# get cmd line arguments
cmdargs = docopt.docopt(DOC, version='bernstein2005 0.1')
if (cmdargs['--width'] == None) or \
        (cmdargs['--height'] == None) or \
        (cmdargs['--reffile'] == None) or \
        (cmdargs['--infile'] == None) or \
        (cmdargs['--mapfile'] == None):
    print(DOC)
    sys.exit()
frameWidth = int(cmdargs['--width']);
frameHeight = int(cmdargs['--height']);
frameSize = int(frameWidth * frameHeight * 3 / 2);

#Open decoded and reference file
decFile = open(cmdargs['--infile'], "rb");
refFile = open(cmdargs['--reffile'], "rb");

#Get minimum of both size until which PSNR computation is possible
file1_size = os.path.getsize(cmdargs['--infile']);
file2_size = os.path.getsize(cmdargs['--reffile']);
minsize = min(file1_size, file2_size);

print(minsize);
if minsize/frameSize != int(minsize/frameSize):
    print('WARNING: File size not multiple of frame size');
#Total number of frames for which PSNR is evaluated
totalFrames = int(minsize/frameSize);

###
# Calculate YUV PSNR of entire frame considering 16x16 blocks
###
decData = array.array('B');
refData = array.array('B');

for numFrame in range(0,totalFrames):
    #Read one from worth of data
    decData.fromfile(decFile,frameSize);
    refData.fromfile(refFile,frameSize);

    #iterate through 16x16 blocks

print("Exiting!!!!!");
decFile.close();
refFile.close();



