
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,1000) 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

aweight = 0.5
num_frames = 0
bg = None


def run_avg(img,aweight):
    global bg
    if bg is None:
        bg = img.copy().astype('float')
        return
    cv2.accumulateWeighted(img,bg,aweight)
def segment(img,thres=25):
    global bg
    diff = cv2.absdiff(bg.astype('uint8'),img)
    _, thresholded = cv2.threshold(diff,thres,255,cv2.THRESH_BINARY)
    contours,_ = cv2.findContours(thresholded.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return
    else:
        segmented = max(contours,key = cv2.contourArea)
    return (thresholded,segmented)

flag = 0
i = 0
N1 = 0
while(cap.isOpened()):
    ret, frame = cap.read()

    if ret ==True:
        frame = cv2.flip(frame, 1)
        clone = frame.copy()
        (height, width) = frame.shape[:2]
        roi = frame[100:300, 300:500]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if num_frames < 30:
            run_avg(gray, aweight)
        else:
            hand = segment(gray)

            if hand is not None:
                (thresholded, segmented) = hand
                cv2.drawContours(clone, [segmented + (300, 100)], -1, (0, 0, 255))
                cv2.imshow("Thesholded", thresholded)
                contours, _= cv2.findContours(thresholded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                #cv2.drawContours(clone,contours,-1,(0,255,0),4)

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    #print(area)
                    if area >5000:
                        x,y,w,h = cv2.boundingRect(cnt)
                        #cv2.rectangle(clone,(x,y),(x+w,y+h),(0,255,0),4)
                        print("Hand is detected")
                        to_save = cv2.resize(thresholded,(64,64))
                        cv2.imwrite('./explo_prediction/img'+str(i)+'.jpg',to_save)
                        i = i + 1
        cv2.rectangle(frame, (300, 100), (500, 300), (0, 255, 0), 2)
        cv2.rectangle(clone, (300, 100), (500, 300), (0, 255, 0), 2)
        cv2.putText(clone, "Gesture Controlled Calculator", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)

        num_frames += 1

        cv2.imshow('frame', clone)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()