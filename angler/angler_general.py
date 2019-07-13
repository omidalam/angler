from skimage.feature import peak_local_max
from math import *
import numpy as np
import matplotlib.pyplot as plt
from skimage import io as skio
from skimage.draw import ellipse
from skimage.measure import label, regionprops
from skimage.transform import rotate
from skimage.morphology import convex_hull_image
from skimage.exposure import rescale_intensity
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
import ntpath
import tempfile
import time
import sys
from PyPDF2 import PdfFileMerger, PdfFileReader
from angler import *
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm,inch

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from io import BytesIO

import angler
import bioformats
from angler import *

from PyPDF2 import PdfFileMerger, PdfFileReader
import glob
import os
import time, sys
import tempfile
import gc
import pickle

import logging
import numpy as np
import pandas as pd

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

    min_loci_dist=int(sqrt(2*((crop_size/2)**2)))
    coordinates = peak_local_max(img, min_distance=min_loci_dist,threshold_rel=thresh,exclude_border=int(crop_size/2))
    return coordinates
    

def im_prj(img,z_ind,method='max'):
    # img should be hyperstack image in numpy format.
    # You can findout which axis is z by the following coomand: img.shape
    # You can tell which axis is Z if you know number of Z stacks.
    
    #Project image along Z axis
    if method=="max":
        return(np.amax(img,axis=z_ind))
    if method=="sum":
        return(np.sum(img,axis=z_ind))

def rep_first_page(pars):


    sample_style_sheet = getSampleStyleSheet()
    flowables = []
    paragraph_1 = Paragraph("ANGLER dryrun for FISH_finder", sample_style_sheet['Heading1'])
    flowables.append(paragraph_1)

    para = Paragraph("This run was generated on %s" % time.strftime("%a, %d %b %Y %H:%M:%S"),
                     sample_style_sheet['BodyText'])
    flowables.append(para)

    paragraph_2 = Paragraph(
        """This report has been generated by ANGLER package to determine the perfect threshold value 
        for finding FISH signal""",
        sample_style_sheet['BodyText'])
    flowables.append(paragraph_2)

    para = Paragraph("Parameteres used:", sample_style_sheet['Heading2'])
    flowables.append(para)

    para = Paragraph("Microscopy file folder: %s" % pars["folder_path"], sample_style_sheet['BodyText'])
    flowables.append(para)

    para = Paragraph("Number of file in filer: %s" % pars["file_no"], sample_style_sheet['BodyText'])
    flowables.append(para)

    para = Paragraph("Report name: %s" % pars["pdf_report_path"], sample_style_sheet['BodyText'])
    flowables.append(para)

    for ch,threshold in zip(pars["FISH_ch"],pars["threshold"]):
        para = Paragraph("Threshold for channel {0}: {1}".format(ch,threshold), sample_style_sheet['BodyText'])
        flowables.append(para)

    para = Paragraph("Exclude border: %i" % pars["exclude_border"], sample_style_sheet['BodyText'])
    flowables.append(para)

    flowables.append(PageBreak())

    return flowables


def path_leaf(path):

    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def update_progress(job_title, index, total):
    progress = index / total
    length = 20  # modify this to change the length
    block = int(round(length * progress))
    msg = "\r{0}: [{1}] {2}% : {3} out of {4}".format(job_title, "#" * block + "-" * (length - block),
                                                      round(progress * 100, 2), index, total)
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


def PDF_gen(flowables, path, counter):

    pdf_path = path + "/" + str(counter) + ".pdf"
    pdf_report = SimpleDocTemplate(pdf_path)
    sample_style_sheet = getSampleStyleSheet()
    pdf_report.build(flowables)
    counter += 1
    return counter


def pdf_merger(output_path, input_paths):
    merged = PdfFileMerger()

    for path in input_paths:
        merged.append(path)

    with open(output_path, 'wb') as fileobj:
        merged.write(fileobj)

def subtract_bkg(MicImage_cls):
    """
    Subtract background as measured by pixels mode from the image.
    Returns a new MicImage with previous meta data but new pixels.
    """
    from statistics import mode as dmode
    def modes_max(a):
        vals, cnts = np.unique(a, return_counts=True)
        max_cnts=cnts[cnts.argmax()]
        mode_ind=np.equal(cnts,np.full_like(cnts,max_cnts))
        modes=vals[mode_ind]
        return np.amax(modes)
    # img_mod=np.full_like(MicImage_cls.pixels, dmode(MicImage_cls.pixels.flatten()))
    img_mod=np.full_like(MicImage_cls.pixels, modes_max(MicImage_cls.pixels))
    image_de_noise=MicImage()
    image_de_noise._metaData={**MicImage_cls._metaData}
    image_de_noise.pixels=np.subtract(MicImage_cls.pixels,img_mod)
    return image_de_noise 

def feret(prj,pixel_size,threshold=0.5):
    def measure_feret(regions):
        max_feret=0
        for props in regions:
            y0, x0 = props.centroid
            orientation = props.orientation
            x1 = x0 + cos(orientation) * 0.5 * props.major_axis_length
            y1 = y0 - sin(orientation) * 0.5 * props.major_axis_length
            x2 = x0 - cos(orientation) * 0.5 * props.major_axis_length
            y2 = y0 + sin(orientation) * 0.5 * props.major_axis_length

            feret_region=(sqrt((x1-x2)**2+(y1-y2)**2) * float(pixel_size["pixel_size"]))
            if feret_region>max_feret:
                max_feret=feret_region
        return {"feret":max_feret,"feret_xy1":[x1,y1],"feret_xy2":[x2,y2]}
    feret={}
    feret.update({"threshold":threshold})
    feret.update(pixel_size)
    T=np.amax(prj)*threshold
    binary_prj=np.zeros_like(prj)
    binary_prj[prj>T]=1
    label_img, tot_objects = label(binary_prj,return_num=True)
    if tot_objects==1:
        regions = regionprops(label_img, coordinates='xy') #Only workds with skimage=0.14.*. Starting 0.16 they are changing coordinate system.
        feret=measure_feret(regions)
        feret.update({"convex_hull":False})
        
    elif tot_objects>1:
        chull=convex_hull_image(binary_prj)
        binary_prj[chull]=1
        convex_hull=True
        regions = regionprops(label_img, coordinates='xy') #Only workds with skimage=0.14.*. Starting 0.16 they are changing coordinate system.
        feret=measure_feret(regions)
        feret.update({"convex_hull":True})
    if regions[0].area<4:
        feret.update({"noise?":True})
    else:
        feret.update({"noise?":False})
    return feret

def pixel_size(img):
    pixel={}
    if img.meta("pixel_size") is None:
        if img.meta("x_resolution") is None:
            pixel.update({"pixel_size":1,"pixel_type":"default=1px"})
        else:
            pixel.update({"pixel_size":img.meta("x_resolution"),"pixel_type":"x_resolution"})
    else:
        pixel.update({"pixel_size":img.meta("pixel_size"),"pixel_type":"xy_resolution"})
    return pixel

def FISH_finder_plotter(img,FISH_crds,crds_box_color):
    """
    annotates FISH image with coordinates found by FISH_finder.
    Parameters:
    img: MicImage 4D(3D +channels) instant
    FISH_crds: list of coordinates of FISH signal found by FISH_finder
    
    Returns: Marked figure.
    """

    rectangle_crds=crds-pars['crop_size']/2
    text_crds=[(x,y) for y,x in crds]

    # Make the graph
    fig, ax = plt.subplots(figsize=(7, 5),dpi=300, sharex=True, sharey=True)
    #             ax = axes.ravel()
    rgb=np.zeros((img.meta("size_y"),img.meta("size_x"),3),dtype=int)
    rgb[:,:,0]=rescale_intensity(img.maxprj[..., ch],out_range=(0, 255))
    rgb[:,:,1]=np.zeros((img.meta("size_y"),img.meta("size_x")),dtype=int)
    rgb[:,:,2]=rescale_intensity(img.maxprj[..., pars['DAPI_ch']],out_range=(0, 150))

    ax.imshow(rgb)
    loci_rectangles=[Rectangle((crd_x, crd_y),pars['crop_size'],pars['crop_size'],
        linewidth=0.5,edgecolor=crds_box_color[j],facecolor='none') for j,(crd_y, crd_x) in enumerate(rectangle_crds)]

    for j,rectangle in enumerate(loci_rectangles):
        ax.add_patch(rectangle)
        ax.annotate(str(j), c=crds_box_color[j],fontsize=7, xy=text_crds[j],
                xycoords='data', xytext=(10,10),
                textcoords='offset pixels')

    title = "Channel #:" + pars['ch_names'][ch]
    fig.suptitle(title, fontsize=10)
    return fig

def compaction_plotter(img,ch,ch_pandas,pars):
    """
    annotates FISH image with coordinates found by FISH_finder.
    Parameters:
    img: MicImage 4D(3D +channels) instant
    FISH_crds: list of coordinates of FISH signal found by FISH_finder
    
    Returns: Marked figure.
    """
    crds=ch_pandas["crop_coordinates"]
    rectangle_crds=crds-pars['crop_size']/2
    text_crds=[(x,y) for y,x in crds]

    fig, ax = plt.subplots(figsize=(7, 5),dpi=300, sharex=True, sharey=True)
    rgb=np.zeros((img.meta("size_y"),img.meta("size_x"),3),dtype=int)
    rgb[:,:,0]=rescale_intensity(img.maxprj[..., ch],out_range=(0, 255))
    rgb[:,:,1]=np.zeros((img.meta("size_y"),img.meta("size_x")),dtype=int)
#     rgb[:,:,2]=np.zeros((img.meta("size_y"),img.meta("size_x")),dtype=int)
    rgb[:,:,2]=rescale_intensity(img.maxprj[..., pars['DAPI_ch']],out_range=(0, 200))

    ax.imshow(rgb)
    for index,loci in ch_pandas.iterrows():
        crd_y,crd_x=[i-10 for i in loci['crop_coordinates']]
        
        loci_rectangle=Rectangle((crd_x,crd_y),pars['crop_size'],pars['crop_size'],
                                linewidth=.4,edgecolor=loci["box_color"],facecolor='none')
        ax.add_patch(loci_rectangle)
        
        x1,y1=loci['feret_xy1']
        x2,y2=loci['feret_xy2']
        x1+=crd_x
        x2+=crd_x
        y1+=crd_y
        y2+=crd_y
        plt.plot((x2, x1), (y2, y1), 'g', linewidth=.2)
        
        ax.annotate(str(index), c=loci["box_color"],fontsize=6, xy=(crd_x,crd_y),
                    xycoords='data', xytext=(10,10),textcoords='offset pixels')
        

    title = "Channel #:" + pars['ch_names'][ch]
    fig.suptitle(title, fontsize=10)
    return fig
                             
                             
    