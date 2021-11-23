#!usr/lib/env/python
from re import S
import re
from typing import get_origin
import carla
import time
import random
import numpy as np
import cv2
import base64
import websockets
import asyncio
#import cwebsocket

#---------------------------------------------------
import json
import requests
from datetime import datetime
import object_hglee
from queue import Queue
from queue import Empty
#---------------------------------------------------

#import main
#import object_hglee

model_location = cv2.dnn.readNet("/home/hglee/Downloads/python_dev_carla/bomin/kang/Kang_JJang_version1.weights", "/home/hglee/Downloads/python_dev_carla/bomin/kang/yolov3.cfg")
num_label = []
with open("/home/hglee/Downloads/python_dev_carla/bomin/kang/hglee_nene.names", "r") as f:
    num_label = [line.strip() for line in f.readlines()]
model_layer, model_out, rainbow = object_hglee.model_setting(model_location, num_label)


#---------------------------------------------------
#---------------------------------------------------


EDGE = 'http://165.246.41.45:5666/app-service'
EDGE_WS = "ws://165.246.41.45"
num_port = "5705"
'''
tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
para_dict={"type" : 'object', "clientID" : 1, "clienttime" :tm}
resp = requests.get(EDGE, params=para_dict)
print(resp)
num_port = resp.json()['service_port']
#num_port = "5705"
print(num_port)
'''
CLOUD_WS = "ws://3.144.86.61"
CLOUD_port = "5705"

web_queue = Queue()
sensor_queue = Queue()



async def image_connect(ws,port,s_frame):
#    async with websockets.connect(ws + ":" + "5700") as websocket:
    async with websockets.connect(ws + ":" + port) as websocket:
        global rsw_data
        s_frame = sensor_queue.get(True, 1.0)
        #s_frame = sensor_queue.get(True, 1.0)
        await websocket.send((s_frame[1])) #image send
        data=''
        data = await websocket.recv()

        #print('tlqkf' )
        print(data)
        rsw_data = eval(data)
        show_result(s_frame,rsw_data)

#---------------------------------------------------
#---------------------------------------------------

im_width = 1280
im_heigt = 720
i3data = "1"
rsw_data ={}
count = 0
time_total = 0
#"ws://localhost:3001"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:5705"

async def connect(s_frame):
    #async with websockets.connect("ws://localhost:9998") as websocket:
    #async with websockets.connect(CLOUD_WS + ":" + CLOUD_port) as websocket:
    async with websockets.connect(EDGE_WS + ":" + num_port) as websocket: #jh
    #async with websockets.connect("ws://3.135.218.53:9998") as websocket: #jh
        #wdata=Cam_kh.GetCamdata()
        global rsw_data
        global count #jh
        global time_total #jh
        s_frame = sensor_queue.get(True, 1.0)
        #s_frame = sensor_queue.get(True, 1.0)
        time_st = time.time() #check total time - jh
        await websocket.send((s_frame[1]))
        data=''
        data = await websocket.recv()
        time_end = time.time() - time_st #check total time - jh
        time_total = time_total + time_end
        count = count + 1 #jh
        time_avr = time_total / count
        print("------------- count & total end-to-end time average -------------")
        print(count)
        print(str(time_avr))
        print("-----------------------------------------------------------------")
        #print('tlqkf' )
        #rsw_data = eval(data)
        #show_result(s_frame,rsw_data)
        #print(rsw_data)
        #print(type(rsw_data))
        jh_show_result(data)

#async def hg_mani():\

def jh_show_result(sensor_queue):
    hg_qii= base64.b64decode(sensor_queue)
    hg_qi = np.frombuffer(hg_qii, dtype=np.uint8)
    hg_q = hg_qi.reshape((416,416,3))
    hg_r=hg_q[:, :, :3]
    print("enf : ")
    cv2.imshow("3",hg_r)
    cv2.waitKey(1)



def show_result(sensor_queue,rsw_data):
    class_num= list(rsw_data['class_num'])
    indexes= list(rsw_data['indexes'])
    indexes = np.transpose(indexes)
    box= list(rsw_data['box'])
    
    font = cv2.FONT_HERSHEY_PLAIN
    #print('rsw_data',rsw_data)
    for i in range(len(box)):
        if i in indexes:
            x, y, w, h = box[i]
            label = str(num_label[class_num[i]])
            color = rainbow[class_num[i]]
            cv2.rectangle(sensor_queue[0], (x, y), (x + w, y + h), color, 2)
            cv2.putText(sensor_queue[0], label, (x, y + 30), font, 3, color, 3)
    cv2.imshow("s_frame",sensor_queue[0])
    cv2.waitKey(1)


def web_callback(web_queue):
    web_queue.put((web_queue))


blue = (255, 0, 0)
green= (0, 255, 0)
red= (0, 0, 255)
white= (255, 255, 255)
font =  cv2.FONT_HERSHEY_PLAIN

def sensor_callback(sensor_data, sensor_queue):
    # Do stuff with the sensor_data data like save it to disk
    # Then you just need to add to the queue
    sensor_data.convert(carla.ColorConverter.Raw)
    i = np.array(sensor_data.raw_data)
    i2 = i.reshape((720,1280,4))
    #print ("2", i2.shape)
    #print ("")
    i3 = i2[:, :, :3]
    i4 = cv2.resize(i3, None, fx=0.4, fy=0.4)
    i3data = base64.b64encode(i4)
    img = cv2.putText(i4, "It's Winter", (30, 40), font, 2, blue, 1, cv2.LINE_AA)
    sensor_queue.put((i4,i3data))
    cv2.imshow('test' , img)
    cv2.waitKey(1) 


def process_img(image):
    global i3data ,rsw_data
    image.convert(carla.ColorConverter.Raw)

    #print ("hg_1", i.shape)
    #hg_i = image
    i = np.array(image.raw_data)
    hg_a =i
    #hg_b= base64.b64encode(hg_a)
    #i3data =hg_b
    #asyncio.get_event_loop().run_until_complete(connect(self.hg_b))
    #hg_c = base64.decodebytes(hg_b)
    #self.hg_q = np.frombuffer(hg_c, dtype=np.uint8)
    
    #print(self.hg_q)
    #hg_i = np.array(image.raw_data)
    #print ("1", i.shape)
    #print ("")


    i2 = i.reshape((720,1280,4))
    #print ("2", i2.shape)
    #print ("")

    i3 = i2[:, :, :3]
    #print ("3",i3.shape)
    #print ("")
    hg_i =i3
    hg_a=i3
    i4 =i3

    i4 = cv2.resize(i3, None, fx=0.4, fy=0.4)
    i41 = cv2.resize(i3, None, fx=0.4, fy=0.4)
    i4 = np.ravel(i4,order='C')
    #print ("4",i4.shape)#995328
    #t= np.arange(3686400, dtype=np.uint8)
    #t =i4
    i3data = base64.b64encode(i4) # i3data => bytes 

    
    class_num= list(rsw_data['class_num'])
    indexes= list(rsw_data['indexes'])
    indexes = np.transpose(indexes)
    box= list(rsw_data['box'])
    
    font = cv2.FONT_HERSHEY_PLAIN
    #print('rsw_data',rsw_data)
    #print('dfdsf',len(box))
    for i in range(len(box)):
        if i in indexes:
            x, y, w, h = box[i]
            label = str(num_label[class_num[i]])
            color = rainbow[class_num[i]]
            cv2.rectangle(i41, (x, y), (x + w, y + h), color, 2)
            cv2.putText(i41, label, (x, y + 30), font, 3, color, 3)
    
 

    #r= base64.decodestring(i3data)
    #hg_qi = np.frombuffer(r, dtype=np.uint8)
    #hg_q = hg_qi.reshape((720,1280,3))
    #hg_r=hg_q[:, :, :3]
    #asyncio.get_event_loop().run_until_complete(connect(i3data))
    #cv2.imshow("3",i41)
    
    #cv2.waitKey(1)
    # --------------------------------------------
    #asyncio.get_event_loop().run_until_complete(connect(self.hg_b))s
    #self.i3data = hg_i
    


actor_list = []

def cam(client,world):

    spawn_points = world.get_map().get_spawn_points()
    vehicle = world.get_actors().filter('vehicle.toyota.prius')
    vehicle_num = vehicle[0].id
    vehicle = world.get_actors().find(vehicle_num)

    camera = world.get_actors().filter('sensor.camera.rgb')
    #cam_bp = blueprint_library.find('sensor.camera.rgb')
    camera_num = camera[0].id
    camera = world.get_actors().find(camera_num)
    '''
    camera = world.get_actors().find(camera_num)
    camera.set_attribute('image_size_x','1280')
    camera.set_attribute('image_size_y','720')
    camera.set_attribute('fov','90')
    camera.set_attribute('sensor_tick','0.0')
    camera.set_attribute('shutter_speed','1.0')
    '''

    return camera


    #actor_list.append(actor_list)
    #actor_list.append(camera)

def main():
    global i3data ,EDGE_WS, num_port
    client = carla.Client("localhost", 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    #client = carla.Client("localhost", 2000)
    #client.set_timeout(2.0)
    #world = client.load_world('Town04')
    #world = client.get_world()
    #vehicle = world.get_actors().filter('vehicle.toyota.prius')
    #vehicle_num = vehicle[0].id
    #vehicle = world.get_actors().find(vehicle_num)
    world = client.get_world()
    #camera  = world.get_actors().find(260)
    camera = cam(client,world)
    
   
    #camera = world.spawn_actor(cam_bp, camera_sp, attach_to = vehicle)
    camera.listen(lambda data: sensor_callback(data, sensor_queue))
    #time.sleep(0.5)
    #asyncio.get_event_loop().run_until_complete(connect())
    
    #camera.listen(lambda data: data.save_to_disk('/home/hglee/cam_hg/%.6d.png' % data.frame))
    #dddd = i3data
    #asyncio.get_event_loop().run_until_complete(connect(dddd))
    #asyncio.get_event_loop().run_until_complete(image_connect(EDGE_WS, num_port ,dddd))
    #print('1')
    while True:
        #world.tick()
        #w_frame = world.get_snapshot().frame
        #print("\nWorld's frame: %d" % w_frame)
        try:
            s_frame = sensor_queue.get(True, 1.0)
            #print("Frame")
            #print(type(s_frame))
            
            #show_result(s_frame,rsw_data)
            #await asyncio.gather(connect())
            #cv2.imshow("s_frame",s_frame[0])
            #cv2.waitKey(1)
            #asyncio.get_event_loop().run_until_complete(image_connect(CLOUD_WS, CLOUD_port, s_frame)) #for cloud -jh
            #asyncio.get_event_loop().run_until_complete(image_connect(EDGE_WS, num_port,s_frame))
            #asyncio.get_event_loop().run_until_complete(connect(s_frame))
        except Empty:
            print("    Some of the sensor information is missed")

#asyncio.get_event_loop().run_until_complete(connect(sensor_queue))    
    

if __name__ == "__main__":
    try:
        main()
        #asyncio.get_event_loop().run_until_complete(main())

    finally:
        for actor in actor_list:
            actor.destroy()
        
        print ('all actor cleaned up')
