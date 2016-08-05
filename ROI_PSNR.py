#!/usr/bin/python

import sys
import docopt
import numpy as np
import array
import os
import math

def psnr(mse):
    log10 = math.log10
    return 10.0 * log10(float(255 * 255) / float(mse))
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
     -m, --mapfile=STRING          Binary file to specify region of interest(optional)
     -n, --maxFrames=NUMBER        Number of frames to be considered (optional, default: min of total number of frames)
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
        (cmdargs['--infile'] == None):
    print(DOC)
    sys.exit()
frameWidth = int(cmdargs['--width']);
frameHeight = int(cmdargs['--height']);
frameSize = int(frameWidth * frameHeight * 3 / 2);

#Open decoded and reference file
decFile = open(cmdargs['--infile'], "rb");
refFile = open(cmdargs['--reffile'], "rb");
if (cmdargs['--mapfile'] != None):
    mapfile = open(cmdargs['--mapfile'], "rb");

#Get minimum of both size until which PSNR computation is possible
file1_size = os.path.getsize(cmdargs['--infile']);
file2_size = os.path.getsize(cmdargs['--reffile']);

minsize = min(file1_size, file2_size);

if minsize/frameSize != int(minsize/frameSize):
    print('WARNING: File size not multiple of frame size');
#Total number of frames for which PSNR is evaluated
totalFrames = int(minsize/frameSize);
if(cmdargs['--maxFrames'] != None):
    totalFrames = min(totalFrames,int(cmdargs['--maxFrames']));
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
seq_mse_luma_ROI = 0;
seq_mse_luma = 0;
for numFrame in range(0,totalFrames):
    decData = array.array('B');
    refData = array.array('B');
    ROI_map_data = array.array('B');
    #Place the file pointers to start of frame
    decFile.seek(frameSize * numFrame);
    refFile.seek(frameSize * numFrame);
    if mapfile != None:
        mapfile.seek(int(frameSize/(16*16)) * numFrame);#since map file has one byte of data for every macro-block

    decData.fromfile(decFile,frameSize);
    refData.fromfile(refFile,frameSize);

    if mapfile != None:
        ROI_map_data.fromfile(mapfile,int((frameSize/(16*16))));

    #iterate through 16x16 blocks
    #MSE OF entire frame
    mse = 0;
    mse_u = 0;
    mse_v = 0;
    #MSE OF ROI
    mse_roi = 0;
    mse_u_roi = 0;
    mse_v_roi = 0;
    num_ROI_blocks = 0;
    for yBlock in range(0, numBlockHeight):
        for xBlock in range(0,numBlockWidth):
            startx = xBlock * 16;
            starty = yBlock * 16;
            curStartByte = starty * frameWidth + startx;
            is_ROI_block = ROI_map_data[yBlock * numBlockWidth  + xBlock]
            if is_ROI_block != 0:
                num_ROI_blocks += 1;
            ##loop for LUMA MSE
            for i in range(0,16):
                stride = curStartByte + i * frameWidth;
                endStride = curStartByte + i * frameWidth + 16;
                cur_block_mse = sum((a - b) * (a - b) for a, b in zip(refData[stride:endStride], decData[stride:endStride]));
                mse += cur_block_mse;
                if(mapfile != None and is_ROI_block != 0):
                    mse_roi += cur_block_mse;
                #print(refData[stride:endStride]);
                #print(decData[stride:endStride]);
            #loop for chroma PSNR
            curStartByte_u = (frameWidth * frameHeight) + (yBlock * 16/2 * frameWidth/2) + (xBlock * 16/2);
            for i in range(0,int(16/2)):
                stride_u = int(curStartByte_u + i * frameWidth/2);
                endStride_u = int(curStartByte_u + i * frameWidth/2 + 8);
                stride_v = int(stride_u + (frameWidth/2 * frameHeight/2));
                endStride_v = int(endStride_u + (frameWidth/2 * frameHeight/2));
                cur_block_mse_u = sum((a - b) * (a - b) for a, b in zip(refData[stride_u:endStride_u], decData[stride_u:endStride_u]));
                cur_block_mse_v = sum((a - b) * (a - b) for a, b in zip(refData[stride_v:endStride_v], decData[stride_v:endStride_v]));
                mse_u += cur_block_mse_u;
                mse_v += cur_block_mse_v;
                ##Accumulate ROI croma PSNR
                #print(ROI_map_data[yBlock * numBlockWidth  + xBlock]);
                if(mapfile != None and is_ROI_block != 0):
                    mse_u_roi += cur_block_mse_u;
                    mse_v_roi += cur_block_mse_v;


    total_mse = (mse + mse_u + mse_v)/(frameSize);
    mse = mse / (frameWidth * frameHeight);

    ##ROI based PSNR
    mse_roi_luma = mse_roi/(num_ROI_blocks * 16 * 16);
    #print(mse);
    #print("n = ", numFrame ,"Luma PSNR = ", psnr(mse), mse , "total PSNR = ", psnr(total_mse),total_mse, "Luma ROI PSNR = ", psnr(mse_roi_luma));
    ##Accumulate states to b printed in the end.
    seq_mse_luma += mse;
    seq_mse_luma_ROI += mse_roi_luma;
print("##############################################################");
print("Luma PSNR =  ", psnr(seq_mse_luma/totalFrames), "Luma PSNR ROI = ", psnr(seq_mse_luma_ROI/totalFrames));
print("Exiting!!!!!");
decFile.close();
refFile.close();





