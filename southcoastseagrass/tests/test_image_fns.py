import pytest
import numpy as np
import rasterio

# Import module we want to test functions from.
from southcoastseagrass import image_fns

def test_LS7_SLE_mask():

    # Create some dummy data.
    # Start with a 3X3 array tha is all ones.
    dummy_raster = np.ones(
        (3, 3),
        dtype=np.uint8 # Make sure we have ints, as this is what will be in the image file.
    )

    # Make the upper triangle zero to simulate SLE
    dummy_raster = np.tril(dummy_raster)

    # Stack the above array so that we have 3 bands with shape (3,3).
    # The resulting array will have shape (3, 3, 3)
    dummy_raster = np.stack(
        3*[dummy_raster]
    )

    with rasterio.open(
        'dummy.tif',
        'w', # We want to write the file
        driver='GTiff', # Our files will be TIFs so we want tp test this type.
        height=3,
        width=3,
        count=3, # The number of bands in the dummy image. We have three; r, g, b.
        dtype=np.uint8 # Make sure we have ints.
    ) as dst:
        
        dst.write(
            dummy_raster,
            indexes=[1, 2, 3] # Tell rasterio we want to write to the first three bands.
        )

    # Read the dummy file and call the masking function.
    with rasterio.open('dummy.tif', 'r') as src:
        mask = image_fns.LS7_band_mask(src)

    # Check that the upper triangle is masked.
    expected_mask = np.zeros((3,3), dtype=np.uint8)
    expected_mask[np.triu_indices(3,k=1)] = 1
    assert np.array_equal(mask, expected_mask)