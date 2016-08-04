#!/usr/bin/python

import sys
import docopt
import numpy as np
import array
import os
import math

def psnr(mse):
    log10 = math.log10
    return 10.0 * log10(float(256 * 256) / float(mse))
###
# Docopt
###
DOC = """
usage:
   ROI_PSNR [options]

options:
     -w, --width=NUMBER            Width of yuv files
     -h, --height=NUMBER           height of yuv files
     -r, --reffile=STRING          path of reference file for PSNR calculation, yuv420p format
     -i, --infile=STRING           path of path file for PSNR calculation, yuv420p format
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
#Calculate width and height in number of blocks
if frameWidth / 16 != int(frameWidth/16):
    print("ERROR: Frame width not multiple of block size, ignoring incomplete blocks");
    exit(0);
if frameHeight / 16 != int(frameHeight / 16):
    print("WARNING: Frame height not multiple of block size, ignoring incomplete blocks");
    exit(0);
numBlockWidth = int(frameWidth / 16); #This shall ignore the incomplete blocks if width and height are not multiple of block size
numBlockHeight = int(frameHeight / 16);

for numFrame in range(0,totalFrames):
    decData = array.array('B');
    refData = array.array('B');
    #Read one from worth of data
    decFile.seek(frameSize * numFrame);
    refFile.seek(frameSize * numFrame);
    decData.fromfile(decFile,frameSize);
    refData.fromfile(refFile,frameSize);


    #iterate through 16x16 blocks
    mse = 0;
    mse_u = 0;
    mse_v = 0;
    for yBlock in range(0, numBlockHeight):
        for xBlock in range(0,numBlockWidth):
            startx = xBlock * 16;
            starty = yBlock * 16;
            curStartByte = starty * frameWidth + startx;
            ##loop for LUMA MSE
            for i in range(0,16):
                stride = curStartByte + i * frameWidth;
                endStride = curStartByte + i * frameWidth + 16;
                mse += sum( (a - b)* (a - b) for a,b in zip(refData[stride:endStride],decData[stride:endStride]));
                #print(refData[stride:endStride]);
                #print(decData[stride:endStride]);
            #loop for chroma PSNR
            curStartByte_u = (frameWidth * frameHeight) + (yBlock * 16/2 * frameWidth/2) + (xBlock * 16/2);
            for i in range(0,int(16/2)):
                stride_u = int(curStartByte_u + i * frameWidth/2);
                endStride_u = int(curStartByte_u + i * frameWidth/2 + 8);
                stride_v = int(stride_u + (frameWidth/2 * frameHeight/2));
                endStride_v = int(endStride_u + (frameWidth/2 * frameHeight/2));
                mse_u += sum((a - b) * (a - b) for a, b in zip(refData[stride_u:endStride_u], decData[stride_u:endStride_u]));
                mse_v += sum((a - b) * (a - b) for a, b in zip(refData[stride_v:endStride_v], decData[stride_v:endStride_v]));



    total_mse = (mse + mse_u + mse_v)/(frameSize);
    mse = mse / (frameWidth * frameHeight);

    #print(mse);
    print("Luma PSNR = ",psnr(mse) ,"total PSNR = ", psnr(total_mse));

print("Exiting!!!!!");
decFile.close();
refFile.close();





