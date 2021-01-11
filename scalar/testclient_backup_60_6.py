import asyncio
import websockets
import base64
import pandas as pd
import json
import csv
import requests
from datetime import datetime
import time


server = 'http://165.246.41.45:5600/app-service'

WS = "ws://localhost:"

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value",
"Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand",
"Torque_converter_speed","Time(s)","Class"]

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
#test data(json) <- csv convert dataframe and json
      #this test only 40 rows
#[
#       'time': ...
#        'data': ['asd':'123','abc':'234',...]
#]


#csv_f = open('full_data_test.csv')
#datax = 8000 #sample data window
#df = pd.read_csv(csv_f, nrows = datax, usecols=columns2)

#result = df.to_json(orient='records')
#parsed = json.loads(result)
#temp = { 'timestamp' : datetime.utcnow().isoformat(sep=' ', timespec='milliseconds') }
#parsed[1].update(temp)
#print(parsed[1])


async def scalar_connect(port):
    async with websockets.connect((WS+port)) as websocket:
        #1. first 60 data is sent(preset)
        skiprow = 0
        df = pd.read_csv('full_data_test.csv',nrows=60,usecols=columns)
        result = df.to_json(orient='records')
        parsed = json.loads(result)
        for skiprow in range(0,60):
            temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
            parsed[skiprow].update(temp)
            stdata1 = json.dumps(parsed[skiprow])
            await websocket.send(stdata1)
        data = await websocket.recv()
        if data == 'Model ready':
            #2. Each 1 line data is sent
            skiprow = 61
            while True:
                # start time 
                st = time.time()
                for i in range(0,6):
                    #make new data lows
                    df = pd.read_csv('full_data_test.csv',skiprows=range(1,skiprow+i), usecols=columns, nrows=1);
                    df_json = df.to_json(orient='records')
                    parsed = json.loads(df_json)[0]
                    temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
                    parsed.update(temp)
                    stdata = json.dumps(parsed)
                    await websocket.send(stdata)
                result = await websocket.recv()
                sp_time = time.time() -st
                print("RECEVIE : {}, End-to-End time : {}".format(result, sp_time))
                skiprow = skiprow + 6

'''
        for df in pd.read_csv('full_data_test.csv',iterator=True, chunksize=40, usecols=columns):
            result = df.to_json(orient='records')
            parsed = json.loads(result)
            for i in range(0, 40):
                temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
                parsed[i].update(temp)
                stdata1 = json.dumps(parsed[i])
                await websocket.send(stdata1)
            #bidirection connection
            data = await websocket.recv()
            print('Sending json : {}'.format(stdata1))
            print('Receive : {}'.format(data))
'''

async def image_connect(port):
    async with open("Test.png","rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        image_json = dict()
        image_json = {'type':'image', 'data':encoded_string}
        print(json.dumps(image_json));
        imgdata = json.dumps(image_json,indent=4);
#bidirection connection
    async with websockets.connect(WS_I) as websocket:
        await websocket.send(imgdata);
        data = await websocket.recv();
        print(data);

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(scalar_connect('5700'));
