import cv2
import numpy as np
import object_hglee
#import carla
import time

import asyncio;
import websockets;
import json
import base64

model_location = cv2.dnn.readNet("/opencv/opencv-4.2.0/build/yolov3.weights", "/opencv/opencv-4.2.0/build/yolov3.cfg")
num_label = []
with open("/opencv/opencv-4.2.0/build/hglee_nene.names", "r") as f:
    num_label = [line.strip() for line in f.readlines()]
model_layer, model_out, rainbow = object_hglee.model_setting(model_location, num_label)


class_num = []
num_2 = []
box = []

async def accept(websocket, path):
    while True:
        data = await websocket.recv()
        #await websocket.send("echo")
      #print(json.dumps(data,indent=4))
      #print("receive : " + data)
        #print(sj)
      #print("type : ",type(data))
        #hg_b =list()
        #r =list()
        #hg_b = str(data)
        if len(data) != 0:
            r= base64.b64decode(data) # byte 248832
            #print('s',data)
            hg_qi = np.frombuffer(r, dtype=np.uint8)
            hg_q = hg_qi.reshape((288,512,3))
            hg_r=hg_q[:, :, :3]

            photo_location = hg_r
            photo, height, width, channels, nothing, outs = object_hglee.photo_setting(photo_location, model_location, model_out)


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

                        box.append([x, y, w, h])
                        num_2.append(float(confidence))
                        class_num.append(class_id)
            indexes = cv2.dnn.NMSBoxes(box, num_2, 0.5, 0.4)
            indexes_str = str(indexes.T)
            await websocket.send(indexes_str) #--------------------------------------------------------------------------
            #print(indexes)
            '''
            font = cv2.FONT_HERSHEY_PLAIN
            for i in range(len(box)):
                if i in indexes:
                    x, y, w, h = box[i]
                    label = str(num_label[class_num[i]])
                    color = rainbow[class_num[i]]
                    cv2.rectangle(photo, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(photo, label, (x, y + 30), font, 3, color, 3)
            '''
            #await websocket.send("ok")

            #cv2.imshow("Image", photo)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
        else :
            print("no")
            await websocket.send("no")

        #await websocket.send("end bye")

start_server = websockets.serve(accept, "0.0.0.0", 5700)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

'''
model_location = cv2.dnn.readNet("/home/hglee/Downloads/python_dev_carla/bomin/kang/Kang_JJang_version1.weights",
                                 "/home/hglee/Downloads/python_dev_carla/bomin/kang/1k.cfg")
num_label = []
with open("/home/hglee/Downloads/python_dev_carla/bomin/kang/hglee_nene.names", "r") as f:
    num_label = [line.strip() for line in f.readlines()]
model_layer, model_out, rainbow = object_hglee.model_setting(
    model_location, num_label)

# photo_location = cv2.imread("/home/kangjjang/photo/4.jpg")
im_width = 1280
im_heigt = 720


def process_img(image):

    image.convert(carla.ColorConverter.Raw)
    i = np.array(image.raw_data)
    i2 = i.reshape((720, 1280, 4))
    i3 = i2[:, :, :3]
    photo_location = i3
    photo, height, width, channels, nothing, outs = object_hglee.photo_setting(
        photo_location, model_location, model_out)
    class_num = []
    num_2 = []
    box = []
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

                box.append([x, y, w, h])
                num_2.append(float(confidence))
                class_num.append(class_id)

    indexes = cv2.dnn.NMSBoxes(box, num_2, 0.5, 0.4)
    print(indexes)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(box)):
        if i in indexes:
            x, y, w, h = box[i]
            label = str(num_label[class_num[i]])
            color = rainbow[class_num[i]]
            cv2.rectangle(photo, (x, y), (x + w, y + h), color, 2)
            cv2.putText(photo, label, (x, y + 30), font, 3, color, 3)

    cv2.imshow("Image", photo)
    print(photo.shape)
    cv2.waitKey(0)
    print("tlqkfanjfqhsi")
    cv2.destroyAllWindows()
    return i3


actor_list = []

while True:
    vehicle_num = 259

    client = carla.Client("localhost", 2000)
    #world = client.load_world('Town04')
    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    vehicle = world.get_actors().find(vehicle_num)
    print('1')
    cam_bp = blueprint_library.find('sensor.camera.rgb')
    cam_bp.set_attribute('image_size_x', '1280')
    cam_bp.set_attribute('image_size_y', '720')
    cam_bp.set_attribute('fov', '90')
    cam_bp.set_attribute('sensor_tick', '0.0')
    cam_bp.set_attribute('shutter_speed', '10.0')
    camera_sp = carla.Transform(carla.Location(x=2, z=2))
    camera = world.spawn_actor(cam_bp, camera_sp, attach_to=vehicle)
    actor_list.append(camera)
    camera.listen(lambda data: process_img(data))
    print('2')
    #camera.listen(lambda data: data.save_to_disk('/home/hglee/cam_hg/%.6d.jpg' % data.frame))
'''
