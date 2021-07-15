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

EDGE = 'http://192.168.1.11:5611/app-service'
EDGE1 = 'http://192.168.1.20:5601/app-service'

CENTER = 'http://ec2-3-23-18-37.us-east-2.compute.amazonaws.com'

EDGE_WS = "ws://165.246.41.45"

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value", "Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand", "Torque_converter_speed","Class"]

classes= ['A','B','C','D','E','F','G','H','I','J']
tx_path = "/sys/class/net/wlan0/statistics/tx_bytes"
rx_path = "/sys/class/net/wlan0/statistics/rx_bytes"

def timer(start, end):
    #print("a1");
    seconds = end - start;
    # print("a2");
    return str("{:08.5f}".format(seconds))

def request_to_edge(ml_type, client_id):
    try:
        print("Requesting cluster 1");
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" :tm}
        print(str(para_dict))
        resp = requests.get(EDGE, params=para_dict)
        #print("a4");
        return resp;
    except Exception as e:
        print(e)

def request_to_edge1(ml_type, client_id):
    try:
        print("Requesting cluster 2");
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" :tm}
        print(str(para_dict))
        resp = requests.get(EDGE1, params=para_dict)
        #print("y");
        return resp;
    except Exception as e:
        print(e)

async def scalar_connect(ws, port):
    async with websockets.connect(ws+":"+port) as websocket:
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
        print('Preparing the model...');
        if data == 'Model ready':
            #2. Each 1 line data is sent
            skiprow = 41
            res_all = 0
            cnt = 0;
            bnw = 0;
            start_time = time.time()
            while True:
                try:
                    #Data set
                    rx_f = open(rx_path, "r");
                    tx_f = open(tx_path, "r");
                    rx_bytes_before = int(rx_f.read());
                    tx_bytes_before = int(tx_f.read());
                    rx_f.close()
                    tx_f.close()
                    #Time set
                    res_start = time.time()
                    
                    #WS
                    df = pd.read_csv('full_data_test.csv',skiprows=range(1,skiprow), usecols=columns, nrows=40);
                    df_json = df.to_json(orient='records')
                    parsed = json.loads(df_json)
                    for i in range(0,40):
                        temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
                        parsed[i].update(temp)
                        stdata = json.dumps(parsed[i])
                        await websocket.send(stdata)
                    result = await websocket.recv()
                    
                    # Timer calculate
                    res_end = time.time()
                    inter_res = res_end - res_start
                    res_all = res_all + inter_res
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
                   # print("a7");

                    print("RECEIVE : {}\n End-to-End time : {}\t proceed time : {}".format(result, timer(res_start,res_end), timer(start_time, elapsed_time)))
                    print("Receive bytes : {}".format(all_byte));
                    
                    if (int(elapsed_time - start_time) >= 300):
                        print("Result time : {}, Bandwidth : {}, all request : {}".format(res_all/cnt, bnw/cnt, cnt));
                        break;
                except Exception as e:
                    print(e)

                # Before loop process
                skiprow = skiprow + 40
                if skiprow >= 18670:
                    skiprow = 41;




if __name__ == "__main__":
    try:
        #print("a11");
        start_time=time.time()
        resp = request_to_edge(sys.argv[1], sys.argv[2])
        if resp.json()['migration'] is not 1:
            print("migration is not 1 : processing in cluster 1");
            num_port = resp.json()['service_port']
            print("service port : {}".format(num_port))
            if sys.argv[1] == 'scalar':
                time.sleep(5)
                asyncio.get_event_loop().run_until_complete(scalar_connect(EDGE_WS, num_port))
            elif sys.argv[1] == 'image':
                time.sleep(16)
                asyncio.get_event_loop().run_until_complete(image_connect(EDGE_WS, num_port))
        elif resp.json()['migration'] is 1:
            print('migration is 1 :  Request to other cluster')
            resp = request_to_edge1(sys.argv[1], sys.argv[2])
            num_port = resp.json()['service_port']
            print("service port : {}".format(num_port))
            if sys.argv[1] == 'scalar':
                time.sleep(5)
                asyncio.get_event_loop().run_until_complete(scalar_connect(EDGE_WS, num_port))
            elif sys.argv[1] == 'image':
                time.sleep(16)
                asyncio.get_event_loop().run_until_complete(image_connect(EDGE_WS, num_port))

    except Exception as e:
        print(e)
