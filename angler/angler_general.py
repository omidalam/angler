def FISH_finder_dry(folder_path,file_ext,FISH_ch,FISH_ch_names,thresh=0.5,exclude_border=40):
    '''
    This function performs a dry run to detect FISH spots.
    The sole purpose of this function to emprically find best threshold for a ceratin FISH experiment.

    Input Parameters:
    folder_path: str, A folder containing FISH mciroscopy data
    files_ext: str, file extension to search in the folder (e.g. "D3D.dv", ".dv",".flex")
    FISH_ch: tuple of ints containing channel numbers containing FISH signals (index is zero based)
    FISH_ch_names: tuple of strs containing channel names for FISH signals (e.g. "RP11-33o9", "lib11",etc)
    thresh: float 0.0-1.0 relative threshold of the peaks value, compared to maximum value of the image.
    exclude_border: int excludes local peaks that are in the border of an image.
    min_dist: int excludes local peaks that are closer than this value to each other. 
    '''
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    


def FISH_finder(img,thresh,crop_size=40):
    '''
    This function finds the coordinates of local maxima in max-projected FISH
    data.

    It uses peak_local_max from skimage.feature module.  If two local maxima
    happen to be on proximity of 20 pixel,only the brighter one will be kept.

    Parameters:
    img: 2-D ndarray (i.e,single channel) 

    min_distance= minimum distance of two FISH spot
    
    thresh: flaot 0.0-1.0 relative threshold of the peaks value, compared to maximum value of the image.
    
    exclude_border: int excludes local peaks that are in the border of an image.


    Returns:
    ndarray: (row, column, …) coordinates of peaks.

    '''
    from skimage.feature import peak_local_max
    from scipy import ndimage as ndi
    from math import sqrt
    min_dist=sqrt(2*(crop_size/2^2))
    coordinates = peak_local_max(img, min_distance=sqrt(2*crop_size)20,
     threshold_rel=thresh,exclude_border=crop_size/2)
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
