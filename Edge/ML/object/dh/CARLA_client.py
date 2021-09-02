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
#---------------------------------------------------

#import main
#import object_hglee


#---------------------------------------------------
#---------------------------------------------------
'''
EDGE = 'http://165.246.41.45:5666/app-service'
EDGE_WS = "ws://165.246.41.45"

tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
para_dict={"type" : 'object', "clientID" : 1, "clienttime" :tm}
resp = requests.get(EDGE, params=para_dict)
print(resp)
num_port = resp.json()['service_port']
print(num_port)
'''

async def image_connect(ws,port,hg_data):
#    async with websockets.connect(ws + ":" + "5700") as websocket:
    async with websockets.connect(ws + ":" + port) as websocket:
        await websocket.send(hg_data)
        print("data sent")
        data = await websocket.recv()
        print("data recieve")
        print(type(data))

#---------------------------------------------------
#---------------------------------------------------

im_width = 1280
im_heigt = 720
i3data = ""
rsw_data = ""
#"ws://localhost:3001"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:3004"
#"ws://165.246.41.45:5705"
async def connect(wdata):
    async with websockets.connect("ws://localhost:9998") as websocket:
        #wdata=Cam_kh.GetCamdata()
        await websocket.send(wdata)
        rsw_data = await websocket.recv()
        print(rsw_data)


def process_img(image):
    global i3data
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
    i4 = np.ravel(i4,order='C')
    #print ("4",i4.shape)#995328
    #t= np.arange(3686400, dtype=np.uint8)
    #t =i4
    i3data = base64.b64encode(i4) # i3data => bytes 
 

    #r= base64.decodestring(i3data)
    #hg_qi = np.frombuffer(r, dtype=np.uint8)
    #hg_q = hg_qi.reshape((720,1280,3))
    #hg_r=hg_q[:, :, :3]
    #asyncio.get_event_loop().run_until_complete(connect(i3data))
    #cv2.imshow("3",i3)
    
    #cv2.waitKey(1)
    # --------------------------------------------
    #asyncio.get_event_loop().run_until_complete(connect(self.hg_b))s
    #self.i3data = hg_i
    


actor_list = []
def cam():
    client = carla.Client("localhost", 2000)
    client.set_timeout(2.0)
    #world = client.load_world('Town04')
    world = client.get_world()
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
    '''
    blueprint_library = world.get_blueprint_library()
    cam_bp = blueprint_library.find('sensor.camera.rgb')
    cam_bp.set_attribute('image_size_x','1280')
    cam_bp.set_attribute('image_size_y','720')
    cam_bp.set_attribute('fov','90')
    cam_bp.set_attribute('sensor_tick','0.0')
    cam_bp.set_attribute('shutter_speed','10.0')
    camera_sp = carla.Transform(carla.Location(x=2, z=2))
    camera = world.spawn_actor(cam_bp, camera_sp, attach_to = vehicle)
    '''

    #actor_list.append(actor_list)
    #actor_list.append(camera)

def main():
    global i3data
    #client = carla.Client("localhost", 2000)
    #client.set_timeout(2.0)
    #world = client.load_world('Town04')
    #world = client.get_world()
    #vehicle = world.get_actors().filter('vehicle.toyota.prius')
    #vehicle_num = vehicle[0].id
    #vehicle = world.get_actors().find(vehicle_num)

    #camera  = world.get_actors().find(260)
    camera = cam()

    #camera = world.spawn_actor(cam_bp, camera_sp, attach_to = vehicle)
    camera.listen(lambda data: process_img(data))
    time.sleep(0.05)
    #asyncio.get_event_loop().run_until_complete(connect())
    
    #camera.listen(lambda data: data.save_to_disk('/home/hglee/cam_hg/%.6d.png' % data.frame))
    dddd = i3data
    asyncio.get_event_loop().run_until_complete(connect(dddd))
    #asyncio.get_event_loop().run_until_complete(image_connect(EDGE_WS, num_port ,dddd))
    #print('1')
    

if __name__ == "__main__":
    try:
        while True:
            main()
    finally:
        for actor in actor_list:
            actor.destroy()
        
        print ('all actor cleaned up')