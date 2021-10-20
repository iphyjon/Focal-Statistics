import matplotlib.pyplot  as plt
import argparse
import os
import focal_stats

parser = argparse.ArgumentParser(description = 'Focal statistics')
parser.add_argument('--filepath', default = os.getcwd(), type = str, help ='Path to dataset')
parser.add_argument('--name', default = "data/image.jpg", type = str, help ='name of the image file to be filtered')
parser.add_argument('--mask', default = "rectangular", type = str, help ='Type of mask to implement (square, rectangular, circular and elliptical)')
parser.add_argument('--size', default = (3,3), type = tuple, help ='Size of the mask to use. Must be a tuple.')
parser.add_argument('--statsmod', default = "mean", type = str, help ='Statistical method to use (mean, max, min etc..)')


args = parser.parse_args()
image_path = os.path.join(args.filepath, args.name)


f = focal_stats.FocalStats(image_path, func = args.statsmod, size = args.size)
# Apply the function mask
if args.mask in ["square", "rectangular"]:
    filtered = f.Rec()
elif args.mask in ["circular", "elliptical"]:
    filtered = f.Circ()
# And show the results
plt.imshow(filtered)
plt.axis('off')
plt.show()



