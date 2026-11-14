#the place for our image algorthim
import cv2 as cv
import numpy
import pandas

def ImportImage (path:str):
    cv.imread(path,cv.IMREAD_GREYSCALE)
