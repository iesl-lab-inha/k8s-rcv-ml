import websockets
import requests
import time
import threading
import asyncio
import websockets
import pandas as pd
import json
import os
import csv
from datetime import datetime

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value", "Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand", "Torque_converter_speed","Class"]

classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

async def scalar_connect(WS, port):
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
                    sp_time = time.time() -st
                    #dict_result = json.loads(result)
                    print("skiprow: {},  RECEVIE : {}, End-to-End time : {}".format(skiprow, result, sp_time))
                except Exception as e:
                    print(e)
                skiprow = skiprow + 40
                #loop infi
                if skiprow >= 18650:
                    skiprow = 41

def center_api_call(center):
    print('call the Center API')
    response = requests.post(center)
    print(response.status_code)
    print(response.json())

if __name__ == '__main__':
    URL = "http://ec2-3-23-18-37.us-east-2.compute.amazonaws.com/driver-class-predict/80"
    WS = "ws://ec2-3-23-18-37.us-east-2.compute.amazonaws.com:"
    
    thread_api = threading.Thread(target = center_api_call, args=(URL,))
    thread_api.start()
    time.sleep(6)

    asyncio.get_event_loop().run_until_complete(scalar_connect(WS, '31101'))
