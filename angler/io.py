def tiff_imp(file_path,zxy_ch):
    '''
    Import a ome.tif file and returns it as an numpy ndarray.
    
    It move the first axis to the end to match skimage dimension recommendations.
    
    Prameters:
    file_path: Location of the ome.tif file.
    zxy_ch: NEED explanation

    Returns:
    ndarray: Pixel values of ome.tif file.

    '''

    from skimage import io
    import numpy as np
    img = io.imread(file_path)
    #In my images the channel is the first dimension
    #skikit recommends to have the following order for fast computation (Z,X,Y,ch)
    return np.moveaxis(img,zxy_ch,[0,1,2,3])