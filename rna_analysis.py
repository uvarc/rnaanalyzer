# @ File (label="Input directory", style="directory") inputdir
# @ File (label="Output directory", style="directory") outputdir
# @ Integer (label="RNA Channel No (0-6)", min=0, max=6, value=1) ch_no
# @ Integer (label="Threshold Radius", min=0, max=100, value=10) radius 

from ij import IJ,Prefs
import os
from os import path
from ij.plugin import ChannelSplitter
from loci.plugins import BF
from loci.plugins.in import ImporterOptions


def open_image(f):
    options = ImporterOptions()
    options.setId(f)
    options.setAutoscale(True)
    options.setColorMode(ImporterOptions.COLOR_MODE_COMPOSITE)
    options.setSplitChannels(True)
    imps = BF.openImagePlus(options)
    return imps

def process_file(f):
    print "Processing", f
    imps = open_image(f)
    # ch_no is zero-indexed
    imp = imps[ch_no].duplicate()
    imps[ch_no].show()
    mask_title = os.path.splitext(imps[ch_no].getTitle())[0] + "-mask.tif"
    #IJ.run(imp, "Unsharp Mask...", "radius=1 mask=0.60")
    IJ.run(imp, "Median...", "radius=2")
    IJ.run(imp, "Morphological Filters", "operation=[White Top Hat] element=Disk radius=2")
    mask = IJ.getImage()
    mask.setTitle(mask_title)
    IJ.run(mask, "8-bit", "")
    IJ.run(mask, "Auto Local Threshold", "method=Bernsen radius="+str(radius)+" parameter_1=0 parameter_2=0 white")
    #IJ.setAutoThreshold(mask, "Moments dark")
    Prefs.blackBackground = True
    IJ.run(mask, "Convert to Mask", "")
    IJ.run(mask, "Set Measurements...", "area mean min centroid integrated display redirect='"+imps[ch_no].getTitle()+"' decimal=3")
    IJ.run(mask, "Analyze Particles...", "size=0-Infinity display exclude summarize add")
    return imps[1],mask

def save_as_tif(directory, image):
    title = image.getTitle()
    outputfile = path.join(outputdir, title)
    IJ.saveAs(image, "TIFF", outputfile)
    print "Saved", outputfile

# Main code
inputdir = str(inputdir)
outputdir = str(outputdir)
if not path.isdir(inputdir):
    print inputdir, " is does not exist or is not a directory."
else:
    if not path.isdir(outputdir):
        os.makedirs(outputdir)
    filenames = os.listdir(inputdir)
    imgfiles = [f for f in filenames if f.split(".")[-1] == "czi"]
    for ifile in imgfiles:
        fullpath = path.join(inputdir, ifile)
        imp,mask = process_file(fullpath)
        save_as_tif(outputdir, mask)
        imps.close()
        mask.close()

        #break
    print "Done.\n"