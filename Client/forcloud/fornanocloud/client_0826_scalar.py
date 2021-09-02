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

#logging for websockets
import logging

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

#EDGE = 'http://165.246.41.45:5601/app-service' #for rcv pod running
#EDGE = 'http://165.246.41.45:31111/app-service' #for rcv pod running
EDGE = 'http://0.0.0.0:31111/app-service'
#EDGE = 'http://192.168.1.20:5601/app-service' #for rcv host running
#CENTER = 'http://ec2-3-23-18-37.us-east-2.compute.amazonaws.com'

CENTER = 'http://ec2-18-191-225-96.us-east-2.compute.amazonaws.com'
#CENTER_WS = 'ws://172.31.7.139'
CENTER_WS = 'ws://3.142.133.220'

EDGE_WS = "ws://165.246.41.45"

columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value", "Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand", "Torque_converter_speed","Class"]

classes= ['A','B','C','D','E','F','G','H','I','J']
tx_path = "/sys/class/net/wlan0/statistics/tx_bytes"
rx_path = "/sys/class/net/wlan0/statistics/rx_bytes"

def timer(start, end):
    seconds = end - start;
    return str("{:08.5f}".format(seconds))

def request_to_edge(ml_type, client_id):
    try:
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" :tm}
        print(str(para_dict))
        resp = requests.get(EDGE, params=para_dict)
        return resp;
    except Exception as e:
        print(e)

def request_to_center(ml_type, client_id):
    print('Call the Center API')    
    if ml_type == 'scalar':
        resp = requests.post((CENTER+'/driver-class-predict/'+client_id))
    return resp;
    print(response.json())

async def scalar_connect(ws, port):
    async with websockets.connect(ws+":"+port) as websocket:
        print('ws connect')
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
        print(data)
        print('Preparing the model...');
        if data == 'Model ready':
            #a = await websocket.recv()
            #print(a)
            print('model ready get')
            #2. Each 1 line data is sent
            skiprow = 41
            res_all = 0
            cnt = 0;
            bnw = 0;
            start_time = time.time()

            #while 시작
            while True:
                print('start while loop')
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
                    print('Data, time setting end')
                    
                    #WS
                    df = pd.read_csv('full_data_test.csv',skiprows=range(1,skiprow), usecols=columns, nrows=40);
                    df_json = df.to_json(orient='records')
                    parsed = json.loads(df_json)


                    for i in range(0,40):
                        ##print('in for loop')
                        temp = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
                        parsed[i].update(temp)
                        stdata = json.dumps(parsed[i])
                        ##print('**before send') 
                        await websocket.send(stdata) 
                        ##print('**after await send')
                    result = await websocket.recv()
                    #print('result: {}'.format(result))
                    
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

                    print("RECEVIE : {}\n End-to-End time : {}\t proceed time : {}".format(result, timer(res_start,res_end), timer(start_time, elapsed_time)))
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
        #resp = request_to_edge(sys.argv[1], sys.argv[2])
        #if resp.json()['offloading'] is not 1:
        #    num_port = resp.json()['service_port']
        #    print("service port : {}".format(num_port))
        #    if sys.argv[1] == 'scalar':
        #        time.sleep(5)
        #        asyncio.get_event_loop().run_until_complete(scalar_connect(EDGE_WS, num_port))
        #elif resp.json()['offloading'] is 1:
        print('Offloading, Request to Datacenter')
            #thread_api = threading.Thread(target = request_to_center, args=(sys.argv[1],sys.argv[2]))
            #thread_api.start()
        if sys.argv[1] == 'scalar':
            time.sleep(4)
            asyncio.get_event_loop().run_until_complete(scalar_connect(CENTER_WS, '5702')) #nodeport
            #thread_api.join()
    except Exception as e:
        print(e)
