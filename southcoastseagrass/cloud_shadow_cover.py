import numpy as np # maths 
import matplotlib.pyplot as plt # plots
import cv2 # image processing
import rasterio # file loading

class ImageMasker():

    '''
    Loads and masks a satellite image. 
    Arguments:
    path_to_image: the path to the image, .tif format
    path_to_land_mask: path to the land mask, .npy format 
    '''
    
    def __init__(self, path_to_image, path_to_land_mask):
        # Assign paths
        self.path_to_image = path_to_image
        self.path_to_land_mask = path_to_land_mask
        
        # Set Landsat / Sentinel 2 scaling
        if 'LS' in self.path_to_image:
            self.scale = 66000
        else:
            self.scale = 10000
        
        # Load data
        self.load_data()
        
        # Get cloud and shadow masks
        self.cloud_mask = self.get_cloud_mask()
        self.shadow_mask = self.get_shadow_mask()
        
        # Add cloud and shadow masks
        self.full_mask = np.logical_or(self.cloud_mask, self.shadow_mask)
        
        # Apply masks to images
        self.cloud_masked_image = self.apply_mask(self.image, self.cloud_mask)
        self.shadow_masked_image = self.apply_mask(self.image, self.shadow_mask)
        self.full_masked_image = self.apply_mask(self.image, self.full_mask)
        self.land_full_masked_image = self.apply_mask(self.full_masked_image, self.land_mask)

        # Calculate cover percentages
        self.ocean_cloud_cover_percent = self.ocean_cover_percent(self.cloud_mask)
        self.ocean_shadow_cover_percent = self.ocean_cover_percent(self.shadow_mask)
        self.ocean_full_cover_percent = self.ocean_cover_percent(self.full_mask)
        
    def load_data(self):
        '''
        Loads image, cloud bits and land mask
        '''
        # Load image
        image = rasterio.open(self.path_to_image).read()
        # Scale image
        self.image = np.dstack([image[2]/self.scale, image[1]/self.scale, image[0]/self.scale])*3
        # Load cloud bits
        self.cloud_data = rasterio.open(self.path_to_image.replace('rgb', 'extra')).read(4)
        # Load land mask
        mask = np.load(self.path_to_land_mask)
        mask = mask.astype(np.uint8)
        # Resize land mask
        self.land_mask = cv2.resize(mask, self.image.shape[:2][::-1]) != 1
      
    def get_cloud_mask(self):
        '''
        Gets a cloud mask from the cloud data
        '''
        # Convert cloud data from int to binary
        cloud_bits = self.vec_bin_array(self.cloud_data, 16)
        # Create logical array as a mask. 
        # Here, the 12th index corresponds to the 3rd QA (cloud) bit
        cloud_mask = cloud_bits[:, :, 12] == 1
        return cloud_mask

    def get_shadow_mask(self):
        '''
        Gets a shadow mask from the cloud data
        '''
        # Convert shadow data from int to binary
        shadow_bits = self.vec_bin_array(self.cloud_data, 16)
        # Create a logical array as a mask
        # Here, the 11th index corresponds to the 4th QA (shadow) bit
        shadow_mask = shadow_bits[:, :, 11] == 1
        return shadow_mask

    def ocean_cover_percent(self, mask):
        ''' 
        Returns the total ocean coverage percent of a given mask 
        '''
        return 100*(np.sum(mask[self.land_mask]) / np.sum(self.land_mask) )
    
    @staticmethod
    def apply_mask(image, mask, fill_value = 0.0):
        '''
        Applies a mask to an image, filling with a given value 
        '''
        im = image.copy()
        im[mask] = fill_value
        return im

    @staticmethod
    def vec_bin_array(arr, m):
      """
      Returns a copy of arr with every element replaced with a bit vector.
      Bits encoded as int8's.

      Thanks to https://stackoverflow.com/questions/22227595/convert-integer-to-binary-array-with-suitable-padding

      Arguments: 
      arr: Numpy array of positive integers
      m: Number of bits of each integer to retain

     
      """
      to_str_func = np.vectorize(lambda x: np.binary_repr(x).zfill(m))
      strs = to_str_func(arr)
      ret = np.zeros(list(arr.shape) + [m], dtype=np.int8)
      for bit_ix in range(0, m):
          fetch_bit_func = np.vectorize(lambda x: x[bit_ix] == '1')
          ret[...,bit_ix] = fetch_bit_func(strs).astype("int8")

      return ret
    
