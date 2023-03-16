import numpy as np

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