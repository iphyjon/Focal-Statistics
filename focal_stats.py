import os
import numpy as np
# for the statistical functions of the focus, the following functions are 
# imported from the numpy package
# the -nan- means, that the function is going to ignore nans in the array
from numpy import nanmean as mean, nanmax as max, nanmin as min
from numpy import nanmedian as median, nanstd as std, nanvar as var
# the ellipse function from skimage.draw will be utilized
# for the elliptical shaped mask 
from skimage.draw import ellipse
from imageio import imread

#____________________________________________________________________________
# Map the statistical methods with the user input
stat_mod = {"mean": mean, "max": max, "min": min, "median": median, "std": std, "var": var}


#____________________________________________________________________________


class FocalStats:

    def __init__(self, filepath, **kwargs):
        
        # assigning the filepath by given directory link
        self.filepath = filepath
        # assigning the statistical function of choice (mean,max,min,...)
        # from the keyword argument 'func'
        self.func =  stat_mod[kwargs['func']]
        # assigning the size of the mask from the keyword argument 'size'
        # the input must be a tuple or list with two values:
        # ->first value: number of rows of the mask
        # ->second value: number of columns of the mask
        self.size = kwargs['size']
        
        # loads datafile with imread 
        self.file = np.array(imread(self.filepath),dtype=int)
        
        # retrieve the number of rows and columns from the loaded file
        self.rows = self.file.shape[0]
        self.cols = self.file.shape[1]
        
        # at this point, the code defines a vertical and horizontal spacing
        # from the central point of the mask towards the edges of the mask
        # (no matter if it is angular or rounded...)
        # for this purpose, the amount of rows and columns of the mask is
        # subtracted by 1 (due to the central pixel) and devided by two.
        # Because there are no partital cells allowed, the values are going to 
        # be rounded up and converted to an integer
        self.vert_space = int(np.ceil((self.size[0]-1)/2))
        self.horz_space = int(np.ceil((self.size[1]-1)/2))
        
        # for the purpose, that the mask may handle the edges of the
        # input data, a frame of nans is attached to the boundaries
        # of the raster. The size depends of the amount of rows and columns
        # of the image as well as the length of the horizontal and vertical 
        # spacing of the mask (see lines above).
        # Initially, an array with zeros is build.        
        
        if self.file.ndim == 2:            
            
            # if the file is a single channel data set        
            self.horz_fill = np.zeros((self.horz_space, self.cols))            
            self.vert_fill = np.zeros((self.rows+2 * self.horz_space, self.vert_space))
         
        else:
            
            # if the file is a multichannel image, the number of channels is assigned 
            self.chans = self.file.shape[2]     
            self.horz_fill = np.zeros((self.horz_space,
                                       self.cols,
                                       self.chans))            
            self.vert_fill = np.zeros((self.rows+2*self.horz_space,
                                       self.vert_space,
                                       self.chans))
        
        # now fill the zero arrays from above with nans
        self.horz_fill.fill(np.nan) 
        self.vert_fill.fill(np.nan)
        
        # and stack them to the right, left, top and bottom boundaries of the original file
        self.file = np.vstack((self.file, self.horz_fill))
        self.file = np.vstack((self.horz_fill, self.file))                
        self.file = np.hstack((self.vert_fill, self.file))
        self.file = np.hstack((self.file, self.vert_fill))
    
    # For angular mask
    def Rec(self):  
        """
        This function first checks if the columns and rows of the mask are even or odd. 
        Then adds extra cells in the case of an even mask. This mask is used to filter the data with the
        statistical method provided by the user.

        Returns:
        returns an numpy array of the filtered data

        """

        if self.size[0] % 2 == 0 and self.size[1] % 2 == 0:   # rows and cols both even
            n = (self.size[0] + 1) * (self.size[1] + 1)       # add two extra cells
        elif self.size[0] % 2 == 0 and self.size[1] % 2 != 0: # rows even but cols odd
            n = (self.size[0] + 1) * self.size[1]             # add one extra cell to rows
        elif self.size[0] % 2 != 0 and self.size[1] % 2 == 0: # row odd but cols even
            n = self.size[0] * (self.size[1]+1)               # add one extra cell to cols
        elif self.size[0] % 2 != 0 and self.size[1] % 2 != 0: # rows and cols both odd
            n = self.size[0] * self.size[1]                   # no extra cells
        
        # the initially empty masks are integer zero-arrays with n-dimensions from above
        masks = np.zeros((self.rows,self.cols,n),dtype = np.uint8)            
        
        if self.file.ndim == 2:    

            
            # for single channel data
            count = 0 
            """
            Subsequently, the algorithm retrieves the cell values within the mask by two nested for-loops, which are indexing 
            the respective i-th row and respective j-th column in the mask array.
            For every i and j, the code also retrieves all neightboured cells in x and y direction for the
            whole width and length of the original (!) image by slicing the indeces i and j range from
            0 up to two times the size of the vertical or horizontal spacing.
            The parts are then inserted into the n-th slice of the 'masks' array.
            The number of n is indicated by 'count', which increased with every interation step by 1.
            """           

            for i in range(2*self.horz_space + 1):
                for j in range(2 * self.vert_space + 1):
                    part = self.file[i:(self.rows + i),
                                   j:(self.cols + j)]
                    masks[:,:,count] = part
                    count += 1                    
            
            # Finally, the statistical function of interest (max,min,mean,...)
            # for each cell of the original image are taken along the z-axis (n slices), 
            # which is indicated by 'axis = 2')
            filtered = self.func(masks, axis = 2)            
            
        else:            
               
            # for multi channel data
            
            #Prepare an empty array with the number of assigned channels for the finally filtered image
            filtered = np.zeros((self.rows, self.cols, self.chans), dtype = np.uint8)            

            for k in range(self.chans):
                count = 0
                for i in range(2*self.horz_space + 1):
                    for j in range(2*self.vert_space + 1):
                        part = self.file[i:(self.rows + i),
                                       j:(self.cols + j),
                                       k]
                        masks[:, :, count] = part
                        count += 1
                 
                filtered[:, :, k]=self.func(masks, axis = 2)

        #return the filtered image after finishing the stacking

        return filtered
    
    # for a round-ish mask
    def Circ(self):
        """
        This function uses ellipse function the from the skimage library to forms an elliptic shape
        with individual radii in x- and y-direction. The output will be the interfacing rows and columns
        of the circle. This mask is used to filter the data with the statistical method provided by the user.

        Returns:
        returns an numpy array of the filtered data
        """

        rr, cc = ellipse(self.horz_space, self.vert_space, 
                         self.horz_space + 1, self.vert_space + 1)
        # The len() of the rr or cc vector is corresponding to the total number of cells n within the mask
        n = len(rr)
        masks = np.zeros((self.rows, self.cols,n), dtype = np.uint8)
        
        if self.file.ndim == 2:        

            # for single channel data          
            # The count of the n slices in the 'masks'-array is set to zero
            count = 0
            for i in range(n):
                part = self.file[rr[i]:(self.rows + rr[i]),
                               cc[i]:(self.cols + cc[i])]
                masks[:, :, count] = part
                count += 1

            filtered = self.func(masks, axis = 2)           
            
        else:

            # for multi channel data  
          
            filtered = np.zeros((self.rows, self.cols, self.chans), dtype = np.uint8)

            for k in range(self.chans):
                count = 0
                for i in range(n):
                    part = self.file[rr[i]:(self.rows + rr[i]),
                                   cc[i]:(self.cols + cc[i]),
                                   k]
                    masks[:, :, count] = part
                    count += 1
                 
                filtered[:, :, k] = self.func(masks, axis = 2)
        
        # return the filtered image        
        return filtered        

#____________________________________________________________________________

