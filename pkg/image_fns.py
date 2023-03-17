import numpy as np
import rasterio

def LS7_band_mask(rgb_raster):
    '''
    Returns a mask for the bands of empty pixels in the Landsat 7 images.

    The function looks for pixels that have a zero value for all red, green, and blue
    bands.

    Args:
        rgb_raster (rasterio.io.DatasetReader): ``rasterio.io.DatasetReader`` object with red, green, and blue bands.

    Returns:
        Mask for zero value bands. 
    '''

    mask = np.where(
        np.logical_and(
            rgb_raster.read(1) == 0,
            np.logical_and(
                rgb_raster.read(2) == 0,
                rgb_raster.read(3) == 0
            )
        ),
        1,
        0
    )

    return mask

def QA_cloud_perc(file_list, QA_band):
    '''
    With a given list of ``.tif`` files that contain ``QA_PIXEL`` find the number of water pixels
    according to the bitmask

    Args:
        file_list (list): List of file names.
        QA_band (int): The band id for the ``QA_PIXEL`` bitmask.
    Returns:
        water_count (array): Nummber of water pixels in each file, will have same length as ``file_list``.
    '''

    # Define some empty arrays for the counts.
    cloud_count = np.zero((len(file_list, )))
    water_count = np.zeros((len(file_list, )))

    # Loop over all files.
    for i, fi in enumerate(file_list):

        # Load bitmask
        QA = rasterio.open(fi).read(QA_band)

        # Find the boolean mask from the bit mask.
        water_i = water_from_bitmask(QA)

        # Simply sum the boolean masks to find the total counts
        water_count[i] = np.sum(water_i)

    return water_count

def water_from_bitmask(bitmask):
    '''
    Converts a earth engine QA bitmask to a boolean array of water pixels.
    Bitmask array conversion from https://stackoverflow.com/questions/22227595/convert-integer-to-binary-array-with-suitable-padding
    Arguments:
    bitmask:np.ndarray, shape(pix_x, pix_y)

    returns:
    water_bitmask : np.ndarray, shape(pix_x, pix_y). Boolean array of pixels where water is present 
    '''

    # number of bits to convert bitmask to 
    m = 16 
    # Function to convert an integer to a string binary representation
    to_str_func = np.vectorize(lambda x: np.binary_repr(x).zfill(m))
    # Calculte binary representations
    strs = to_str_func(bitmask)
    # Create empty array for the bitmask
    bitmask_bits = np.zeros(list(bitmask.shape) + [m], dtype=np.int8)
    # Iterate over all m  bits
    for bit_ix in range(0, m):
        # Get the bits
        fetch_bit_func = np.vectorize(lambda x: x[bit_ix] == '1')
        # Store the bits
        bitmask_bits[:, :, bit_ix] = fetch_bit_func(strs).astype("int8")

    # The water bitmask is stored in bit 7 (index 15-7=8).
    water_bitmask = bitmask_bits[:, :, 8] == 0

    return water_bitmask

def calculate_cloud_percentage(water_counts):
    '''
    Calculates the percentage of water covered by clouds for a given array
    of sums of water pixels. Assumes the maximum water count corresponds to the 
    clearest, least cloudy day and calculates the percentages from there. 

    Arguments:
    water_counts : np.ndarray, shape (n_files,), counts of all water pixels for a given image

    Returns:
    cover_percents : np.ndarray, shape (n_files), percentage of cloud cover for a given image

    '''
    cover_percents = 100*(water_counts / water_counts.max())

    return cover_percents
