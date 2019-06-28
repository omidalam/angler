import numpy as np
import matplotlib.pyplot as plt
from skimage import io
import imagej
import angler

import os
import javabridge
import bioformats
import sys
from bioformats import *
import warnings

def start_bioformats():
    """Start a JVM containing Bioformat. Packed by Cell-Profiler"""
    javabridge.start_vm(class_path=bioformats.JARS,run_headless=True)
    print("Bioformats JVM started!")

def stop_bioformats():
    """Stop the JVM created by start_bioformats"""
    javabridge.kill_vm()
    print("Bioformats JVM ended!")

class MicMetadata:
    """A class for processing and storing OME-XML microscopic images meta data."""
    def __init__(self,image_path):
        xml=omexml.OMEXML(get_omexml_metadata(path=image_path))
        self.name=xml.image().Name
        self.file_path=image_path
        self.size_x=xml.image().Pixels.SizeX
        self.size_y=xml.image().Pixels.SizeY
        self.size_z=xml.image().Pixels.SizeZ
        self.size_c=xml.image().Pixels.SizeC
        self.x_resolution=xml.image().Pixels.PhysicalSizeX
        self.y_resolution=xml.image().Pixels.PhysicalSizeY
        if xml.image().Pixels.PhysicalSizeX!= xml.image().Pixels.PhysicalSizeY:
            warnings.warn("X and Y resolutions are not the same", UserWarning)
            self.pixel_size= None
        else:
            self.pixel_size=xml.image().Pixels.PhysicalSizeX
        self.z_resolution=xml.image().Pixels.PhysicalSizeZ
        self.pixel_type=xml.image().Pixels.PixelType

class MicImage(MicMetadata):
    """A class for storing Microscopic images as numpy ndarray with their metadata."""
    
    def __init__(self,image_path):
        super().__init__(image_path)
        self.pixels=np.zeros((self.size_z,self.size_y,self.size_x,self.size_c))
        for channel in range(self.size_c):
            for z_index in range(self.size_z):
                self.pixels[z_index,:,:,channel]= load_image(image_path,c=channel,z=z_index,rescale=False)
        bioformats.clear_image_reader_cache()


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
