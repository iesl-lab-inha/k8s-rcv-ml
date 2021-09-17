import cv2
#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt
import time
start_all = time.time()
classLabels = [] ## empty list of python
file_name = 'Labels.txt'
with open(file_name,'rt') as fpt:
    classLabels = fpt.read().rstrip('\n').split('\n')
    #classLables.append(fpt.read())

config_file = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
frozen_model = 'frozen_inference_graph.pb'

model = cv2.dnn_DetectionModel(frozen_model,config_file)
model.setInputSize(320,320)
model.setInputScale(1.0/127.5) ## 255/2 = 127.5
model.setInputMean((127.5,127.5,127.5)) ## 
model.setInputSwapRB(True)

img = cv2.imread('4.jpg')

#plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
start = time.time()
ClassIndex, confidece, bbox = model.detect(img,confThreshold=0.5)
end = time.time()
print("[INFO] SSD_mobileNetv3 took {:.6f} seconds".format(end - start))
font_scale = 3
font = cv2.FONT_HERSHEY_PLAIN
for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
    #cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    #cv2.putText(img, text, (text_offset_x, text_offset_y), font, fontScale=font_scale, color=(0, 0, 0), thickness=1)
    cv2.rectangle(img,boxes,(255, 0, 0), 2 )
    cv2.putText(img,classLabels[ClassInd-1],(boxes[0]+10,boxes[1]+40), font, fontScale=font_scale,color=(0, 255, 0), thickness=3 )
    print(classLabels[ClassInd-1] + "     " + str(boxes[0]) + " " +str(boxes[1])+" " +str(boxes[2]) +" " +str(boxes[3]) )

End_all = time.time()
print("[INFO] Total Time took {:.6f} seconds".format(End_all - start_all))

cv2.imwrite("4_result.jpg", img)

#import matplotlib.pyplot as plt
#plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#plt.show()
