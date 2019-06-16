def FISH_finder(img,thresh,exclude_border):
    '''
    This function finds the coordinates of local maxima in max-projected FISH
    data.

    It uses peak_local_max from skimage.feature module.  If two local maxima
    happen to be on proximity of 20 pixel,only the brighter one will be kept.

    Parameters:
    img: 2-D ndarray (i.e,single channel) 

    min_distance= minimum distance of two FISH spot
    
    thresh: flaot 0.0-1.0 relative threshold of the peaks value, compared to maximum value of the image.
    
    exclude_border: int excludes local peaks that are in the border of an
    image.


    Returns:
    ndarray: (row, column, …) coordinates of peaks.

    '''
    from skimage.feature import peak_local_max
    from scipy import ndimage as ndi
    
    coordinates = peak_local_max(img, min_distance=20, threshold_rel=thresh,exclude_border=exclude_border)
    return coordinates

    

def im_prj(img,z_ind,method='max'):
    # img should be hyperstack image in numpy format.
    # You can findout which axis is z by the following coomand: img.shape
    # You can tell which axis is Z if you know number of Z stacks.
    import numpy as np
    #Project image along Z axis
    if method=="max":
        return(np.amax(img,axis=z_ind))
    if method=="sum":
        return(np.sum(img,axis=z_ind))
