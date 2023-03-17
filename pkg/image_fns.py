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
    
    
    return
