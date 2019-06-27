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

def dv_import(file_path,ij):
    '''
    Imports a DeltaVision file using FIJI. This requires an imagej Java VM to be open.

    Prameters:
    file_path: location of .dv file
    ij: imageJ instance

    Returns:
    Image as an numpy array. The axes order is z,x,y,ch.
    '''

    import numpy as np

    img=ij.io().open(file_path)
    as_np=ij.py.from_java(img)
    np_reorder=np.moveaxis(as_np,0,-1)

    return np_reorder

def zstack_import(file_path,ij,file_type):
    '''
    Imports a DeltaVision file using FIJI. This requires an imagej Java VM to be open.

    Prameters:
    file_path: location of .dv file
    ij: imageJ instance

    Returns:
    Image as an numpy array. The axes order is z,x,y,ch.
    '''

    import numpy as np

    img=ij.io().open(file_path)
    # img=ij.openImage(str(file_path))
    as_np=ij.py.from_java(img)
    if file_type=="dv":
        np_reorder=np.moveaxis(as_np,0,-1)
    elif file_type=="flex":
        np_reorder=np.moveaxis(as_np,1,-1)
    # img.close()
    return np_reorder
