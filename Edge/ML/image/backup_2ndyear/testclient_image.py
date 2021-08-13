import asyncio
import websockets
import base64
import pandas as pd
import json
import csv
import requests
from datetime import datetime
import time
import os

server = 'http://xxx.xxx.xxx.xxx:xxxxx/app-service'

WS = "ws://localhost:"

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value",
"Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand",
"Torque_converter_speed","Class"]

classes= ['A','B','C','D','E','F','G','H','I','J']

'''
parsed data index is i(0~39).
And load a csv file and only 15 columns and 400 sample using
json type is 'column : value'
this json is list of 400 dict.
'''

def request_to_edge(ml_type, client_id):
    try:
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" :tm}
        print("Send data : {}".format(str(para_dict)))
        resp = requests.get(server, params=para_dict)
    except Exception as e:
        print(e)
    return resp;

async def scalar_connect(port):
    async with websockets.connect((WS+port)) as websocket:
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
            while True:
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
                sp_time = time.time() -st
                print("RECEVIE : {}, End-to-End time : {}".format(result, sp_time))
                skiprow = skiprow + 40

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

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(image_connect('5700'));

