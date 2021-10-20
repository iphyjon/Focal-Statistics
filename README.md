# Focal-Statistics
The Focal statistics tool in many GIS applications like ArcGIS, QGIS and GRASS GIS is a standard method to gain a local overview of raster data behavior. Additionally, it might be also used to filter the zonal information by functions of interest.

The aim of this repo is to create a similar tool in python with varying filter window types with shapes of squares, rectangles, circles and ellipses. The size in x- and y-directions shall be individually adjustable. Furthermore, the user shall have the option to simply switch between a few common statistical functions like mean, max, min, median, std and var. Another advantage is the automatic differentiation between single-channel raster data (like DEMs) or multi-channel data (like RGBs), because the filter needs to be individually applied for each channel for the latter type, before each bands is stacked together again.

The algorithm is relatively fast for smaller images but tends to be slow for larger images (e.g satellite images).

# Running the code
code was tested on python 3.6 

Clone the repo 
`git clone https://github.com/iphyjon/Focal-Statistics.git`


User defined arguments: 

  -  --filepath - path to data
  -  --name - the name of the image file
  -  --mask - user choice of mask to be used (square, rectangular, circular and elliptical)
  -  --size - user choice of the size of the mask e.g (3,3), (5,5), (10,10), (6,3)
  -  --statsmod - statistical method to be applied to the image (mean, max, min, median, var, std)

run on command line 

example - `python run.py --filepath <path/to/datafile> --name image.jpg --mask rectangular --size (4,4) --statsmod var `
