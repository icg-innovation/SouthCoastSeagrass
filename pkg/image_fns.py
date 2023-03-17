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
    With a given list of ``.tif`` files that contain ``QA_PIXEL`` find the number of cloudy or shadowy pixels 
    along with the number of land pixels according to the bitmask

    Args:
        file_list (list): List of file names.
        QA_band (int): The band id for the ``QA_PIXEL`` bitmask.
    Returns:
        cloud_count (array): Nummber of cloudy or shadowy pixels in each file, will have same length as ``file_list``.
        land_count (array): Nummber of land pixels in each file, will have same length as ``file_list``.
    '''

    # Define some empty arrays for the counts.
    cloud_count = np.zero((len(file_list, )))
    land_count = np.zeros((len(file_list, )))

    # Loop over all files.
    for i, fi in enumerate(file_list):

        # Load bitmask
        QA = rasterio.open(fi).read(QA_band)

        # Find the boolean masks from the bit mask.
        # I have assumed these will be different functions but I guess they don't need to be.
        cloud_i = cloud_from_bitmask(QA)
        shadow_i = shadow_from_bitmask(QA)
        land_i = land_from_bitmask(QA)

        # Simply sum the boolean masks to find the total counts
        cloud_count[i] = np.sum(cloud_i)+np.sum(shadow_i)
        land_count[i] = np.sum(land_i)

    return cloud_count, land_count

def cloud_from_bitmask(bitmask):
    
    
    return

def land_from_bitmask(bitmask):
    
    
    return

def shadow_from_bitmask(bitmask):
    
    
    return