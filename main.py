import cv2 as cv
import pytesseract
import numpy as np
import os
from pdf2jpg import pdf2jpg






pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # path to tesseract executable (open source text recognition)

imgName = ''
while os.path.exists(imgName+'.png') == False:
    imgName = input('Enter name of image file to snip and sketch: ')

if os.path.exists(imgName+' questions') == False:
    os.mkdir(imgName+' questions')
img = cv.imread(imgName+'.png')
imageHeight= img.shape[0]
imageWidth = img.shape[1]



def cropImage(questionNum, y1, y2):
    croppedImage = img[y1-30:y2, 0:imageWidth]
    cv.imwrite(imgName + ' questions/Question{}.png'.format(str(questionNum)), croppedImage)
    # cv.imshow(str(questionNum), croppedImage)
    # cv.waitKey(100)
    # cv.destroyAllWindows()


def main():
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    threshold, threshImage = cv.threshold(gray, 200, 255, cv.THRESH_BINARY_INV) # looks at each pixel in the image and if it is above the value of 200 in intensity it is set to 255 so the image is binarized (i.e. high intensity colours set to white and low intensity colours set to black)
    # threshold is the threshold value (200) and thresh is the new binarized immage
    rectKernel = cv.getStructuringElement(cv.MORPH_RECT, (10, 10)) # detect groups of text
    # Applying dilation on the threshold image to detect groups of text more easily (as area around groups of text detected using 'getStructuringElement' is dilated)
    dilatedText = cv.dilate(threshImage, rectKernel, iterations = 1)
    # Finding contours
    contours, hierarchy = cv.findContours(dilatedText, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) # contours stores the (x,y) coordinates of the boundaries between the dilated rectangles of text stored by 'dilated' and the black background (operation perfomed accuratley and easily as image is binarized earlier using thresholding)
    firstIter = True
    numCoord_x = 0
    startNum = int(input("Enter the question number of the last question: "))
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if abs(w) <=50:
            mask = np.zeros_like(img)
            mask = cv.rectangle(mask, (x-10, y), (x+w+10, y+h), (255, 255, 255), -1)
            masked = cv.bitwise_and(img, mask)
            options = "-c tessedit_char_whitelist=0123456789 --psm 10" # limits text detection to numbers and allows single characters to be detected
            if (firstIter == False and numCoord_x-20<x<numCoord_x+20) or firstIter == True: # this x coord filter reduce run time of algorithm significantly as does not need to perform text recognition on text which is not aligned with the question numbers
                cv.imshow('masked', masked)
                cv.waitKey(1)
                try:
                    text = int(pytesseract.image_to_string(masked, config=options))
                    if (str(text).find(str(startNum)) == True or text == startNum) and firstIter == True and x <= 0.2*imageWidth: # question number must be in the leftmost fifth of the image
                        firstIter = False
                        numCoord_x = x
                        currentNum = startNum
                        print(currentNum)
                        cropImage(currentNum, y, imageHeight)
                        y2 = y-15
                    elif firstIter == False and (str(text).find(str(currentNum -1)) == True or text == currentNum-1):
                        currentNum = currentNum -1
                        print(currentNum)
                        cropImage(currentNum, y, y2)
                        y2 = y-15
                        if currentNum == 1:
                            break
                except:
                    pass

main()

