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
CLOUD_WS = "ws://13.125.216.68"
CLOUD_port = "5710"
dest = ""
web_queue = Queue()
sensor_queue = Queue()
tx_path = "/sys/class/net/enp4s0/statistics/tx_bytes" #for bw measurement, enp4s0=lan
rx_path = "/sys/class/net/enp4s0/statistics/rx_bytes"

tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
para_dict={"type" : 'object', "clientID" : 1, "clienttime" :tm}
resp = requests.get(EDGE, params=para_dict)
print(resp) ##
if resp.json()['offloading'] == 0:
    dest = EDGE_WS
    num_port = resp.json()['service_port']
elif resp.json()['offloading'] == 1:
    dest = CLOUD_WS
    num_port = CLOUD_port
print(num_port) ##should add offloading flag

def timer(start, end):
    seconds = end - start;
    return str("{:08.5f}".format(seconds))

#---------------------------------------------------
im_width = 1280
im_heigt = 720
i3data = "1"
rsw_data ={}
count = 0
time_total = 0
res_all = 0
cnt = 0
bnw = 0
#"ws://localhost:3001"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:5705"

async def connect(dest, num_port, s_frame, start_time):
    async with websockets.connect(dest + ":" + num_port) as websocket:
    #async with websockets.connect("ws://3.135.218.53:9998") as websocket: #jh
        #global rsw_data
        #global count #jh
        #global time_total, i3data #jh
        global tx_path, rx_path, res_all, cnt, bnw

        #Data set for measurement of bandwidth
        rx_f = open(rx_path, "r");
        tx_f = open(tx_path, "r");
        rx_bytes_before = int(rx_f.read());
        tx_bytes_before = int(tx_f.read());
        rx_f.close()
        tx_f.close()
        #Time set
        #time_st = time.time() #check total time - jh
        res_start = time.time()

        s_frame = sensor_queue.get(True, 1.0)
        await websocket.send((s_frame[1]))
        #await websocket.send(i3data)
        data=''
        data = await websocket.recv()

        # Timer calculate
        #time_total = time_total + time_end
        res_end = time.time()
        inter_res = res_end - res_start
        res_all = res_all + inter_res
        #count = count + 1 #jh
        cnt = cnt + 1
        elapsed_time = time.time()
        #Data calculate
        rx_f = open(rx_path,"r");
        tx_f = open(tx_path,"r");
        rx_bytes_after = int(rx_f.read())
        tx_bytes_after = int(tx_f.read())
        all_byte = rx_bytes_after - rx_bytes_before + tx_bytes_after - tx_bytes_before
        bnw = bnw + all_byte
        rx_f.close()
        tx_f.close()

        print("count : {}\t End-to-End time : {}\t proceed time : {}".format(cnt, timer(res_start,res_end), timer(start_time, elapsed_time)))
        print("Receive bytes : {}".format(all_byte));
        print(">>>> (AVR)End-to-End time : {}, Bandwidth : {}, all request : {}\n".format(res_all/cnt, bnw/cnt, cnt));

        jh_show_result(data) ##check order

        '''
        time_avr = time_total / count
        print("------------- count & total end-to-end time average -------------")
        print(count)
        print(str(time_avr))
        print("-----------------------------------------------------------------")
        '''
        #if (int(elapsed_time - start_time) >= 30):
            #print(">>>> (AVR)End-to-End time : {}, Bandwidth : {}, all request : {}".format(res_all/cnt, bnw/cnt, cnt));

def jh_show_result(sensor_queue):
    hg_qii= base64.b64decode(sensor_queue)
    hg_qi = np.frombuffer(hg_qii, dtype=np.uint8)
    hg_q = hg_qi.reshape((416,416,3))
    hg_r=hg_q[:, :, :3]
    #print("enf : ")
    #time.sleep(0.5) #test for queue delay
    cv2.imshow("3",hg_r)
    cv2.waitKey(1)

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
    sensor_queue.put((i4,i3data))

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

def main():
    global i3data ,dest, num_port, res_all, cnt, bnw
    client = carla.Client("localhost", 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    world = client.get_world()
    camera = cam(client,world)
    
    camera.listen(lambda data: sensor_callback(data, sensor_queue))

    start_time = time.time()

    while True:
        try:
            s_frame = sensor_queue.get(True, 1.0)
            asyncio.get_event_loop().run_until_complete(connect(dest, num_port, s_frame, start_time))
        except Empty:
            print("    Some of the sensor information is missed")


if __name__ == "__main__":
    try:
        main()
    finally:
        for actor in actor_list:
            actor.destroy()
        print ('all actor cleaned up')

