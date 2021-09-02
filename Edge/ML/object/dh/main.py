import cv2
import numpy as np
<<<<<<< HEAD
import websockets
import json
import time
import asyncio

async def running_ml(websocket, path):
    # 0. Preset part for Learning model 40 data is received
    # Load Yolo
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # 1. inf loop working
    while True:
        try:
            # 2. image data is received from CARLA
            rcv_data = await websocket.recv()
            temp = json.loads(rcv_data)
            client_timestmap = temp['timestamp']
            del temp['timestamp']
            json_list.append(temp)
            del json_list[0]

            np_df = pd.DataFrame(json_list)
            df = np_df[columns]
            test_data = np.expand_dims(df, axis=0)
            ascii_string, endtime, confidence = Testing_model(test_data, Trained_model)
            Results = "[ Output result : {}, Execution_Time : {}, confidence : {} ]".format(ascii_string, endtime, confidence)
            await websocket.send(Results)

        except Exception as e:
            print(e)
            asyncio.get_event_loop().stop();
            break;



=======

# Load Yolo
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))
>>>>>>> dbf1df94c22ed3c1e824e8a39265ba2bd7b060a1

# Loading image
img = cv2.imread("2.jpg")
img = cv2.resize(img, None, fx=1, fy=1)
height, width, channels = img.shape

# Detecting objects
blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

net.setInput(blob)
outs = net.forward(output_layers)

# Showing informations on the screen
class_ids = []
confidences = []
boxes = []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            # Object detected
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)

            # Rectangle coordinates
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)

            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
print(indexes)
font = cv2.FONT_HERSHEY_PLAIN
for i in range(len(boxes)):
    if i in indexes:
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        color = colors[class_ids[i]]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, label, (x, y + 30), font, 3, color, 3)


cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
<<<<<<< HEAD


# Main started here
start_server = websockets.serve(running_ml, '0.0.0.0', 5700);
print('object_server_running')
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever()
=======
>>>>>>> dbf1df94c22ed3c1e824e8a39265ba2bd7b060a1
