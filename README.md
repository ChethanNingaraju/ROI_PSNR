# ROI_PSNR Version - v1_1
Calculates PSNR in a frame based on region of interest based on binary map file marking ROI given as input

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

Version Log v1_1
[x] Added fomratted printing.
[x] Adding prints based on MSE PSNR, Avg PSNR and weighted average PSNR.
[x] Added manual and auto calculation of min and max PSNR threshold to create PSNR map.
[x] Added configurable file name for creation of PSNR map


