import numpy as np
import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

frameSize = (640,480)
thresh = 0.1 # %10 threshold (10 bölüm)

def getAverage(num1,num2):
    return (num1+num2)/2

def getSolution(x0,x1):
    xAvg = getAverage(x0,x1)
    SizeX = frameSize[0]
    _thresh = SizeX*thresh

    # 2 şer katogarilerde hız kontrolü yapılabilr
    if (xAvg < 2*_thresh):
        return "<--- Sol" # 2. kademe Hız
    elif (xAvg >= 2*thresh and xAvg < 4*_thresh):
        return "<- Sol" # 1. kademe Hız
    elif (xAvg >= 4*thresh and xAvg < 6*_thresh):
        return "<- Ileri ->"
    elif (xAvg >= 6*thresh and xAvg < 8*_thresh):
        return "Sag ->" # 1. kademe Hız
    elif (xAvg >= 8*thresh and xAvg <= SizeX):
        return "Sag --->" # 2. kademe Hız

camera = PiCamera()
camera.resolution = frameSize
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=frameSize)
time.sleep(0.1)

# Frame'ler sonsuza dek teker teker alınıyor.
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    # Image de bulunan raw NumPy array değerlerini alıyoruz
    img = frame.array
    
    # Resmi gri tonlara dönüştür
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    # Resme blur (bulanıklaştırma) ekle (kener bulma kolaylaştırır)
    blur = cv.GaussianBlur(gray,(5,5),0)
    edges = cv.Canny(blur,180,280)
    contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    points = cv.findNonZero(edges)
    
    if points is None:
        raw_capture.truncate(0)
        # Yörüngeye Devam Et
        continue
    
    # Waste Detected ! (Send to STM)

    rect = cv.minAreaRect(points)
    box = cv.boxPoints(rect)
    box = np.int0(box)
    cv.drawContours(img,[box],0,(0,255,0),2)

    x0 = box[0][0]
    x1 = box[2][0]
    Sonuc = getSolution(x0,x1)

    cv.putText(img, Sonuc, (250, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    cv.imshow("Frame", img)
    cv.imshow("Edge", edges)
    raw_capture.truncate(0)
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break

camera.close()