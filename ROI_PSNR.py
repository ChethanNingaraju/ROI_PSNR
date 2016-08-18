#!/usr/bin/python

import sys
import docopt
import numpy as np
import array
import os
import math

def psnr(mse):
    log10 = math.log10
    if mse == 0:
        return 100;##the best possible PSNR assumption
    return 10.0 * log10(float(255 * 255) / float(mse))
'''
LumaMSEBlock: block wise MSE in raster scan order
'''
def createPSNRMap(LumaMSEBlock, MIN_PSNR, MAX_PSNR,file_name):
    if file_name == "":
        PSNR_map_file = open("./PSNR_map_file.bin","wb");
    else:
        PSNR_map_file = open(file_name, "wb");

    psnr_map_bytearray = bytearray(len(LumaMSEBlock));

    ##Find the typical range of PSNR values, considering 90th percentile as max and 10th percentile as min
    ##This is make the PSNR representation immune to outliers
    LumaPSNRBlock = []
    for i in range(0,len(LumaMSEBlock)):
        LumaPSNRBlock.append(psnr(LumaMSEBlock[i] / (16 * 16)));
    #Min and Max PSNR thresholds can be user configurable
    if MAX_PSNR == -1:
        MAX_PSNR = np.percentile(LumaPSNRBlock,90);
    if MIN_PSNR == -1:
        MIN_PSNR = np.percentile(LumaPSNRBlock, 10);
    print("Min PSNR chosen = ", MIN_PSNR,"Max PSNR chosen = ",MAX_PSNR);
    for i in range(0,len(LumaMSEBlock)):
        cur_psnr = psnr(LumaMSEBlock[i]/(16*16))
        ##cllip the PSNR value to min and max values
        if cur_psnr > MAX_PSNR:
            cur_psnr = MAX_PSNR;
        if cur_psnr < MIN_PSNR:
            cur_psnr = MIN_PSNR;
        rel_psnr_val = int((cur_psnr - MIN_PSNR)/(MAX_PSNR-MIN_PSNR) * 255);
        psnr_map_bytearray[i] = rel_psnr_val;
    ##write then entire byte to binary file in one shot
    PSNR_map_file.write(psnr_map_bytearray);
    PSNR_map_file.close();

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
     -f, --psnrFile=STRING         Binary file with the PSNR map to be generated (optional, default file will be created in current folder)
     -x, --minPSNR=NUMBER              Minimum PSNR for generating the relative PSNR map (Optioanl, default: calculated based on 10th percentile of PSNR)
     -y, --maxPSNR=NUMEBR              Maximum PSNR for generating the relative PSNR map (Optioanl, default: calculated based on 90th percentile of PSNR)

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
##Values either user defined or calculated internally
MAX_PSNR = -1;
MIN_PSNR = -1;
if(cmdargs['--minPSNR'] != None):
    MIN_PSNR = float(cmdargs['--minPSNR']);
if(cmdargs['--maxPSNR'] != None):
    MIN_PSNR = float(cmdargs['--maxPSNR']);
##Binary file to be created for PSNR map file generation
PSNR_map_file = "";
if(cmdargs['--psnrFile'] != None):
    PSNR_map_file = cmdargs['--psnrFile'];
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
seq_mse = [0] * 3;
seq_mse_ROI = [0] * 3;
seq_psnr = [0] * 3;
seq_psnr_ROI = [0] * 3;
seq_avg_psnr = 0;
seq_avg_psnr_ROI = 0;
##create a PSNR MAP over the frame
luma_mse_block = [];##Fill in the data in raster-scan order
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

            full_block_mse = 0;
            ##loop for LUMA MSE
            for i in range(0,16):
                stride = curStartByte + i * frameWidth;
                endStride = curStartByte + i * frameWidth + 16;
                cur_row_mse = sum((a - b) * (a - b) for a, b in zip(refData[stride:endStride], decData[stride:endStride]));
                mse += cur_row_mse;
                full_block_mse += cur_row_mse;
                if(mapfile != None and is_ROI_block != 0):
                    mse_roi += cur_row_mse;
                #print(refData[stride:endStride]);
                #print(decData[stride:endStride]);
            luma_mse_block.append(full_block_mse);
            #loop for chroma PSNR
            curStartByte_u = (frameWidth * frameHeight) + (yBlock * 16/2 * frameWidth/2) + (xBlock * 16/2);
            for i in range(0,int(16/2)):
                stride_u = int(curStartByte_u + i * frameWidth/2);
                endStride_u = int(curStartByte_u + i * frameWidth/2 + 8);
                stride_v = int(stride_u + (frameWidth/2 * frameHeight/2));
                endStride_v = int(endStride_u + (frameWidth/2 * frameHeight/2));
                cur_row_mse_u = sum((a - b) * (a - b) for a, b in zip(refData[stride_u:endStride_u], decData[stride_u:endStride_u]));
                cur_row_mse_v = sum((a - b) * (a - b) for a, b in zip(refData[stride_v:endStride_v], decData[stride_v:endStride_v]));
                mse_u += cur_row_mse_u;
                mse_v += cur_row_mse_v;
                ##Accumulate ROI croma PSNR
                #print(ROI_map_data[yBlock * numBlockWidth  + xBlock]);
                if(mapfile != None and is_ROI_block != 0):
                    mse_u_roi += cur_row_mse_u;
                    mse_v_roi += cur_row_mse_v;

    ##Full frame calculation
    total_mse = (mse + mse_u + mse_v)/(frameSize);
    seq_avg_psnr += psnr(total_mse);
    mse = mse / (frameWidth * frameHeight);
    mse_u = mse_u / (frameWidth * frameHeight / 4);
    mse_v = mse_v / (frameWidth * frameHeight / 4);
    seq_psnr[0] += psnr(mse);
    seq_psnr[1] += psnr(mse_u);
    seq_psnr[2] += psnr(mse_v);
    seq_mse[0] += mse;
    seq_mse[1] += mse_u;
    seq_mse[2] += mse_v;

    ##Region of interest based calculation
    seq_avg_psnr_ROI += psnr((mse_roi + mse_u_roi + mse_v_roi)/ (num_ROI_blocks * 16 * 16 * 3 / 2));
    mse_roi_luma = mse_roi/(num_ROI_blocks * 16 * 16);
    mse_roi_u = mse_u_roi/(num_ROI_blocks * 8 * 8);
    mse_roi_v = mse_v_roi / (num_ROI_blocks * 8 * 8);
    seq_psnr_ROI[0] += psnr(mse_roi_luma);
    seq_psnr_ROI[1] += psnr(mse_roi_u);
    seq_psnr_ROI[2] += psnr(mse_roi_v);

    '''
    print("n = ", numFrame ,"Luma PSNR = ", "%.2f" % psnr(mse), "%.2f" % mse ,
          "U_psnr = ", "%.2f" % psnr(mse_u), "%.2f" % (mse_u),"Vpsnr = ",
          "%.2f" % psnr(mse_v) ,"%.2f" % (mse_v) ,"Wt PSNR = " ,
          "%.2f" % ((6 * psnr(mse) + psnr(mse_u) + psnr(mse_v))/8) , "total PSNR = ", "%.2f" % psnr(total_mse),total_mse,
          "Luma ROI PSNR = ", "%.2f" % psnr(mse_roi_luma));'''
    ##Accumulate states to b printed in the end.
    seq_mse_ROI[0] += mse_roi_luma;
    seq_mse_ROI[1] += mse_roi_u;
    seq_mse_ROI[2] += mse_roi_v;


print("##############################################################");
print("---------MSE PSNR---------------");
print("MSE based Seq PSNR = ", "%.2f" %  psnr((seq_mse[0] * 4 + seq_mse[1] + seq_mse[2])/(6* totalFrames)), "ROI PSNR = ", "%.2f" %  psnr((seq_mse_ROI[0] * 4 + seq_mse_ROI[1] + seq_mse_ROI[2])/(6* totalFrames)))
print("Luma PSNR =  ", "%.2f" % psnr(seq_mse[0]/totalFrames), "Luma PSNR ROI = ", "%.2f" % psnr(seq_mse_ROI[0]/totalFrames));
print("---------AVG PSNR---------------");
print("Avg PSNR = ","%.2f" % (seq_avg_psnr/totalFrames), "ROI Avg PSNR = ","%.2f" % (seq_avg_psnr_ROI/totalFrames));
print("Avg Luma PSNR =  ", "%.2f" % (seq_psnr[0]/totalFrames), "Avg Luma PSNR ROI = ", "%.2f" % (seq_psnr_ROI[0]/totalFrames));
print("---------WT AVG PSNR------------");
print("Wt Avg PSNR = ", "%.2f" %  (( 6 * seq_psnr[0] + seq_psnr[1] + seq_psnr[2])/(8 * totalFrames)), "Wt Avg PSNR ROI = ", "%.2f" %  (( 6 * seq_psnr_ROI[0] + seq_psnr_ROI[1] + seq_psnr_ROI[2])/(8 * totalFrames)));

##Code to generate PSNR Map
createPSNRMap(luma_mse_block, MIN_PSNR, MAX_PSNR, PSNR_map_file);
print("Exiting!!!!!");
decFile.close();
refFile.close();





