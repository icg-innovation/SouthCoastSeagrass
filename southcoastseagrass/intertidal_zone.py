import numpy as np
import rasterio

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

def get_intertidal_zone_mask(paths_to_files, filter_cloudy=True,
                             tol=0.1):
    '''
    Takes in list of paths to .tif files of earth engine binary masks, returns intertidal zone mask.
    Iterates through the images and adds all water pixels to an empty array. Mean of this
    array is taken and filtered between std < x < 2*std (which works well for LandSat but needs tuning
    for Sentinel). 
    --------------------------------------------------------------------------------------------------
    ARGUMENTS:
    paths_to_files (list): list of files pointing to extra data (LS7/extra/*/LS/*)
    filter_cloudy (bool): If ``True`` will filter images with cloud cover greater than ``tol``.
    tol (float): Tolerance for what defines a cloudy image. Default is ``0.1``. Will only be used if
    ``filter_cloudy=True``.

    RETURNS:
    intertidal_zone_mask (np.ndarray), shape (pix_x, pix_y): Boolean array of intertidal zone
    --------------------------------------------------------------------------------------------------
    '''

    # If specified filter out cloudy images.
    if filter_cloudy:
        good_files = filter_cloudy_files(paths_to_files, tol)
    else:
        good_files = paths_to_files

    # Empty array for storing water pixel counts
    water_sum = np.zeros_like(rasterio.open(good_files[0]).read(4))

    # Iterate through cloudless images 
    for file in good_files:
        # Get data
        extra = rasterio.open(file).read(4)
        # Convert to binary mask
        extra_mask = vec_bin_array(extra, 16)
        # Get water mask (15-8=7th bit)
        water = extra_mask[:, :, 8]
        # Add water pixels to water sum
        water_sum += water
    # Calculate mean
    water_mean = water_sum / len(good_files)
    # Create boolean mask
    intertidal_zone_mask = np.logical_and(water_mean > np.std(water_mean), water_mean < 2*np.std(water_mean))
    return intertidal_zone_mask

def filter_cloudy_files(paths_to_files, tol=0.1):
    '''
    Finds all the images with (tol*100)% or lower cloud coverage over entire image.

    Args:
        paths_to_files (list): list of files pointing to extra data (LS7/extra/*/LS/*)
        tol (float): Tolerance for what defines a cloudy image.

    Returns:
        A list of images with cloud levels lower than ``tol``.
    '''

    # Turn list of paths to np array for boolean indexing
    path_array = np.array(paths_to_files)
    # Array to store counts of cloud pixels
    cloud_counts = np.empty(path_array.shape[0])

    # Iterate through files
    for i, file in enumerate(path_array):
        # Open data
        extra = rasterio.open(file).read(4)
        # Create binary mask
        extra_mask = vec_bin_array(extra, 16)
        # Add sum of cloud pixels (15-12=3rd bit) to each entry in cloud_counts 
        cloud_counts[i] = (extra_mask[:, :, 12] == 1).sum()
    
    # Normalise cloud counts
    normalised_cloud_counts = cloud_counts / cloud_counts.max()

    # Find all files with less cloud 
    cloud_tol = normalised_cloud_counts < tol 
    good_files = path_array[cloud_tol]

    return good_files
