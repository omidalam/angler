import numpy as np
import javabridge
import bioformats
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
    def _meta_init(self):
        key_values=["name","file_path","size_x","size_y","size_z","size_c","x_resolution",
        "y_resolution","pixel_size","z_resolution","pixel_type"]
        return dict.fromkeys(key_values)
    def __init__(self,image_path=None):
        self._metaData=self._meta_init()
        if image_path is not None:
            self.importMeta(image_path)



        # self.name=xml.image().Name
        # self.file_path=image_path
        # self.size_x=xml.image().Pixels.SizeX
        # self.size_y=xml.image().Pixels.SizeY
        # self.size_z=xml.image().Pixels.SizeZ
        # self.size_c=xml.image().Pixels.SizeC
        # self.x_resolution=xml.image().Pixels.PhysicalSizeX
        # self.y_resolution=xml.image().Pixels.PhysicalSizeY
        # if xml.image().Pixels.PhysicalSizeX!= xml.image().Pixels.PhysicalSizeY:
        #     warnings.warn("X and Y resolutions are not the same", UserWarning)
        #     self.pixel_size= None
        # else:
        #     self.pixel_size=xml.image().Pixels.PhysicalSizeX
        # self.z_resolution=xml.image().Pixels.PhysicalSizeZ
        # self.pixel_type=xml.image().Pixels.PixelType
        bioformats.clear_image_reader_cache()
        javabridge._javabridge.reap()
    def importMeta(self, image_path):
        if javabridge.get_env() is None:
            start_bioformats()
        xml=omexml.OMEXML(get_omexml_metadata(path=image_path))
        self._metaData.update({"name":xml.image().Name})
        self._metaData.update({"file_path":image_path})
        self._metaData.update({"size_x":xml.image().Pixels.SizeX})
        self._metaData.update({"size_y":xml.image().Pixels.SizeY})
        self._metaData.update({"size_z":xml.image().Pixels.SizeZ})
        self._metaData.update({"size_c":xml.image().Pixels.SizeC})
        self._metaData.update({"x_resolution":xml.image().Pixels.PhysicalSizeX})
        self._metaData.update({"y_resolution":xml.image().Pixels.PhysicalSizeY})
        self._metaData.update({"z_resolution":xml.image().Pixels.PhysicalSizeZ})
        if xml.image().Pixels.PhysicalSizeX!= xml.image().Pixels.PhysicalSizeY:
            warnings.warn("X and Y resolutions are not the same", UserWarning)
        else:
            self._metaData.update({"pixel_size":xml.image().Pixels.PhysicalSizeX})
        self._metaData.update({"pixel_type":xml.image().Pixels.PixelType})
        # print (self._metaData)
    def meta(self,key=None):
        if self._metaData is None:
            print("Use importMeta method to import metadata first")
        elif key is None:
            return (self._metaData)
        elif key not in self._metaData:
            print("provided key not available. Available keys are:")
            print(self._metaData.keys())
        else:
            return(self._metaData[key])



class MicImage(MicMetadata):
    """A class for storing Microscopic images as numpy ndarray with their metadata."""
    
    def __init__(self,image_path=None):
        super().__init__(image_path)
        if image_path is not None:
            self.pixels=np.zeros((self._metaData["size_z"],self._metaData["size_y"],self._metaData["size_x"],self._metaData["size_c"]))
            with ImageReader(image_path) as rdr:
                for channel in range(self._metaData["size_c"]):
                    for z_index in range(self._metaData["size_z"]):
                        # self.pixels[z_index,:,:,channel]= load_image(image_path,c=channel,z=z_index,rescale=False)
                        self.pixels[z_index,:,:,channel]= rdr.read(c=channel,z=z_index,rescale=False)
                rdr.close()
            bioformats.clear_image_reader_cache()
            javabridge._javabridge.reap()
            self.sumprj=(np.sum(self.pixels,axis=0))
            self.maxprj=(np.amax(self.pixels,axis=0))

    def prj(self,method):
        valid_methods={"max","sum"}
        if method not in valid_methods:
            warnings.warn("Projection method is not valid, pick from following valid methods: {valid_methods}", UserWarning)
        elif method=="max":
            self.maxprj=(np.amax(self.pixels,axis=0))
            # print("3D-image max projected along z axis. You can access it through image.maxprj")
            # return self.maxprj
        elif method=="sum":
            self.sumprj=(np.sum(self.pixels,axis=0))
            # print("3D-image max projected along z axis. You can access it through image.sumprj")
            # return self.sumprj
    def crop(self,channel,center_coord,crop_size):
        x1=center_coord[0]-int(crop_size/2)
        x2=x1+crop_size
        y1=center_coord[1]-int(crop_size/2)
        y2=y1+crop_size
        img_crop=MicImage()
        img_crop._metaData={**self._metaData}
        img_crop.pixels= self.pixels[:,x1:x2,y1:y2,channel]
        img_crop.prj("max")
        img_crop.prj("sum")

        return img_crop
    #     import copycrp= self



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
