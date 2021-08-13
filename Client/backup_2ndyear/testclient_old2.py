import asyncio
import websockets
import base64
import pandas as pd
import json
import csv
import requests
import threading
from datetime import datetime
import time
import os
import sys

server = 'http://xxx.xxx.xxx.xxx:xxxxxx/app-service'
center = 'http://ec2-3-23-18-37.us-east-2.compute.amazonaws.com/'
WS = "ws://xxx.xxx:"

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value", "Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand", "Torque_converter_speed","Class"]

classes= ['A','B','C','D','E','F','G','H','I','J']

def request_to_edge(ml_type, client_id):
    try:
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" :tm}
        print("Send data : {}".format(str(para_dict)))
        resp = requests.get(server, params=para_dict)
        return resp;
    except Exception as e:
        print(e)

def request_to_center(ml_type, client_id):
    print('Call the Center API')    
    if ml_type == 'scalar':
        resp = requests.post((center+'driver-class-predict/'+client_id))
    elif ml_type == 'image':
        resp = requests.post((center+'driver-image-recognition/'+client_id))
    return resp;
    print(response.json())

async def scalar_connect(port):
    async with websockets.connect(WS+port) as websocket:
        #1. first 40 data is sent(preset)
        skiprow = 0
        df = pd.read_csv('full_data_test.csv',nrows=40,usecols=columns)
        result = df.to_json(orient='records')
        parsed = json.loads(result)
        for skiprow in range(0,40):
            temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
            parsed[skiprow].update(temp)
            stdata1 = json.dumps(parsed[skiprow])
            await websocket.send(stdata1)
        data = await websocket.recv()
        if data == 'Model ready':
            #2. Each 1 line data is sent
            skiprow = 41
            over_all = 0
            cnt = 0;
            start_time = time.time()
            while True:
                try:
                    # start time
                    st = time.time()
                    #make new data lows
                    df = pd.read_csv('full_data_test.csv',skiprows=range(1,skiprow), usecols=columns, nrows=40);
                    df_json = df.to_json(orient='records')
                    parsed = json.loads(df_json)
                    for i in range(0,40):
                        temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
                        parsed[i].update(temp)
                        stdata = json.dumps(parsed[i])
                        await websocket.send(stdata)
                    result = await websocket.recv()
                    sp_time = time.time() - st
                    over_all = over_all + sp_time
                    cnt = cnt + 1
                    print("RECEVIE : {}, End-to-End time : {}".format(result, sp_time))
                    if ((start_time - time.time()) >= 300):
                        print("Result time : {}".format(over_all/cnt));
                        break;
                except Exception as e:
                    print(e)
                
                # Before loop process
                skiprow = skiprow + 40
                if skiprow >= 18670:
                    skiprow = 41;


async def image_connect(port):
    async with websockets.connect((WS+port)) as websocket:
        #set path for transmit
        folder_path  = './ep0';
        if os.path.exists('./ep0') is True:
            datalist = os.listdir('./ep0')
            for item in datalist:
                st = time.time()
                item_path = os.path.join('./ep0',item)
                with open(item_path, 'rb') as f:
                    encoded_string = base64.b64encode(f.read()).decode('utf-8')
                    image_json =dict()
                    image_json = { 'data':encoded_string, 'timestamp': str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))}
                    imgdata = json.dumps(image_json,indent=4);
                    await websocket.send(imgdata)
                result = await websocket.recv()
                endtime = time.time() - st
                print(result)
                print("End to End time : {}".format(endtime))

##argv[1] : neural network type
##argv[2] : ID
'''
Main Client code process
1. request to edge server(rcv server)
2-1. 
(1) if offloading off, start websocket to edge
2-2.
(1) if offloading on, request to center server
(2) start websocket to center
'''

if __name__ == "__main__":
    try:
        resp = request_to_edge(sys.argv[1], sys.argv[2])
        if resp.json()['offloading'] is not 1:
            num_port = resp.json()['service_port']
            print("service port : {}".format(num_port))
            if sys.argv[1] == 'scalar':
                asyncio.get_event_loop().run_until_complete(scalar_connect(num_port))
            elif sys.argv[2] == 'image':
                asyncio.get_event_loop().run_until_complete(image_connect(num_port))
        elif resp.json()['offloading'] is 1:
            print('Offloading, Request to Datacenter')
            thread_api = threading.Thread(target = center_api_call, args=(sys.argv[1],sys.argv[2]))
            thread_api.start()
            if sys.argv[1] == 'scalar':
                time.sleep(6)
                asyncio.get_event_loop().run_until_complete(scalar_connect(WS, '31101'))
            elif sys.argv[1] == 'image':
                time.sleep(16)
                asyncio.get_event_loop().run_until_complete(image_connect(WS, '31102'))
            thread_api.join()
    except Exception as e:
        print(e)
