def FISH_finder(img,thresh,exclude_border):
    from skimage.feature import peak_local_max
    from scipy import ndimage as ndi
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
    coordinates = peak_local_max(img, min_distance=20, threshold_rel=thresh,exclude_border=exclude_border)
    return coordinates
    

def im_prj(img,z_ind,method='max-prj'):
    # img should be hyperstack image in numpy format.
    # You can findout which axis is z by the following coomand: img.shape
    # You can tell which axis is Z if you know number of Z stacks.
    import numpy as np
    #Project image along Z axis
    if method=="max":
        return(np.amax(img,axis=z_ind))
    if method=="sum":
        return(np.sum(img,axis=z_ind))

def plotter(prj,coord1,coord2,file_name):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharex=True, sharey=True)
    ax = axes.ravel()
    
    ax[0].imshow(prj[:,:,1], cmap=plt.cm.gray)
    ax[0].set_title('Cyan-A488')
    
    ax[1].imshow(prj[:,:,1], cmap=plt.cm.gray)
    ax[1].plot(coord1[:, 1], coord1[:, 0], 'c.')
    ax[1].plot(coord2[:, 1], coord2[:, 0], 'm.')
    ax[1].set_title('Local_Peaks')
    
    ax[2].imshow(prj[:,:,2], cmap=plt.cm.gray)
    ax[2].set_title('Magenta-A594')
    plt.savefig(file_name+".png",dpi=150,bbox_inches='tight')

def PRJtoRGB(crop):
    import numpy as np
    from skimage.exposure import rescale_intensity
    crop_rgb=np.zeros_like(crop)
    crop_rgb[:,:,0]=rescale_intensity(crop[:,:,2],out_range=(0, 255))
    crop_rgb[:,:,1]=rescale_intensity(crop[:,:,1],out_range=(0, 255))
    crop_rgb[:,:,2]=np.zeros_like(crop[:,:,1])
    return crop_rgb



def cmass_3D(img,max_feature=False):
    ### Gets a 3D image as numpy 3D-array and return center of mass of the biggest blob as 3D coordinates.
    from scipy import ndimage as ndi
    import skimage.io as io
    from skimage import filters
    import matplotlib.pyplot as plt

    gaus= ndi.filters.gaussian_filter(img,1)
    thresh = filters.threshold_otsu(gaus)
    binary = gaus > thresh
    
    # Find the biggest feature in the binary image.
    # s = ndi.generate_binary_structure(2,2,2) # iterate structure
    if max_feature==True:
        lbl, num_feat=ndi.label(binary)
        sizes = ndi.sum(binary,lbl,range(1,num_feat+1))
        map = np.where(sizes==sizes.max())[0] + 1 
        max_index = np.zeros(num_feat + 1, np.uint8)
        max_index[map] = 1
        max_feature = max_index[lbl]
        return ndi.center_of_mass(input=img, labels=max_feature, index=1)
    elif max_feature==False:
        return ndi.center_of_mass(input=img, labels=binary)

def cmass(img,max_feature=True, in_2D=True):
    ### Gets a 2D image as numpy 3D-array and return center of mass of the biggest blob as 3D coordinates.
#     cmass does not work in 3d yet. :()
    from scipy import ndimage as ndi
    import skimage.io as io
    from skimage import filters
    import matplotlib.pyplot as plt
    from oligo_lib_functions import im_prj
    import numpy as np
    
    if in_2D:
        img=im_prj(img,z_ind=0)
    gaus= ndi.filters.gaussian_filter(img,1)
    thresh = filters.threshold_otsu(gaus)
    binary = gaus > thresh
    
    # Find the biggest feature in the binary image.
    # s = ndi.generate_binary_structure(2,2,2) # iterate structure
    if max_feature==True:
        lbl, num_feat=ndi.label(binary)
        sizes = ndi.sum(binary,lbl,range(1,num_feat+1))
        map = np.where(sizes==sizes.max())[0] + 1 
        max_index = np.zeros(num_feat + 1, np.uint8)
        max_index[map] = 1
        max_feature = max_index[lbl]
        return ndi.center_of_mass(input=img, labels=max_feature, index=1)
    elif max_feature==False:
        return ndi.center_of_mass(input=img, labels=binary)


def max_diff_old(img,ch1,ch2,file_name,cropNo,voxel_size=[0.2,0.08,0.08],max_feature=False):
    import numpy as np
    ch1=img[:,:,:,ch1]
    ch2=img[:,:,:,ch2]
    max_ch1=np.asarray( np.unravel_index(np.argmax(ch1, axis=None), ch1.shape))*voxel_size
    max_ch2=np.asarray(np.unravel_index(np.argmax(ch2, axis=None), ch2.shape))*voxel_size
    # Cartesian distance in 2d and 3d
    diff=max_ch1-max_ch2
    max_dist_2d=round(np.sqrt(np.sum(diff[1:]**2)),2)
    max_dist_3d=round(np.sqrt(np.sum(diff**2)),2)

    cmass_ch1=np.asarray(cmass_3D(ch1,max_feature=max_feature))*voxel_size
    cmass_ch2=np.asarray(cmass_3D(ch2,max_feature=max_feature))*voxel_size
    diff_cmass=cmass_ch1-cmass_ch2
    cmass_dist_2d=round(np.sqrt(np.sum(diff_cmass[1:]**2)),2)
    cmass_dist_3d=round(np.sqrt(np.sum(diff_cmass**2)),2)
    
    return{'file_name':file_name,'crop#':cropNo
           ,'max_signal_dist_2d':max_dist_2d,'max_signal_dist_3d':max_dist_3d
           ,'cmass_dist_2d':cmass_dist_2d,'cmass_dist_3d':cmass_dist_3d
           #,'diff':diff,'max_A488':max_ch1,'max-A594':max_ch2
    }

def max_diff(img,ch1,ch2,file_name,cropNo,voxel_size=[0.2,0.08,0.08],max_feature=False):
    import numpy as np
    ch1=img[:,:,:,ch1]
    ch2=img[:,:,:,ch2]
    max_ch1_pixel=np.asarray( np.unravel_index(np.argmax(ch1, axis=None), ch1.shape))
    max_ch1=max_ch1_pixel*voxel_size
    max_ch2_pixel=np.asarray(np.unravel_index(np.argmax(ch2, axis=None), ch2.shape))
    max_ch2=max_ch2_pixel*voxel_size
    # Cartesian distance in 2d and 3d
    diff=max_ch1-max_ch2
    max_dist_2d=round(np.sqrt(np.sum(diff[1:]**2)),2)
    max_dist_3d=round(np.sqrt(np.sum(diff**2)),2)
    
#     cmass only works in 2D that's why voxel doesn't have good dimensions.
    cmass_ch1_pixel=np.asarray(cmass(ch1,max_feature=max_feature,in_2D=True))
    cmass_ch1=cmass_ch1_pixel*voxel_size[1:]
    cmass_ch2_pixel=np.asarray(cmass(ch2,max_feature=max_feature,in_2D=True))
    cmass_ch2=cmass_ch2_pixel*voxel_size[1:]
    diff_cmass=cmass_ch1-cmass_ch2
    cmass_dist_2d=round(np.sqrt(np.sum(diff_cmass**2)),2)
    
    return{'file_name':file_name,'crop#':cropNo
           ,'max_signal_dist_2d':max_dist_2d,'max_signal_dist_3d':max_dist_3d
           ,'cmass_dist_2d':cmass_dist_2d#,'cmass_dist_3d':cmass_dist_3d
#            ,'diff':diff
           ,'max_signal-coord-A488':max_ch1_pixel,'max_signal-coord-A594':max_ch2_pixel
           ,'cmass-2d-coord-ch1':cmass_ch1_pixel,'cmass-2d-coord-ch2':cmass_ch2_pixel
    }

