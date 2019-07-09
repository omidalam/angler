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
    min_loci_dist=int(sqrt(2*((crop_size/2)**2)))
    coordinates = peak_local_max(img, min_distance=min_loci_dist,threshold_rel=thresh,exclude_border=int(crop_size/2))
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

def rep_first_page(pars):
    import time
    from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm, inch

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
    import ntpath
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
    import tempfile
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

