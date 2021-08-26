'''
#import json
import base64
import websockets
import asyncio

async def accept(websocket, path):
    while True:
        try:
            #json_list = list()
            rcv_data = await websocket.recv()
            print("received:" + rcv_data)
            #await websocket.send("echo: " + rcv_data)
            await websocket.send("done")
 
        except Exception as e:
            print(e)
            asyncio.get_event_loop().stop();
            break;

#main start here
start_server = websockets.serve(accept, '0.0.0.0', 3004); #for test
print('**getting data from CARLA')
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever();
'''

import asyncio;
import websockets;
import json

async def accept(websocket, path):
   while True:
      data = await websocket.recv()
      #print(json.dumps(data,indent=4))
      print("receive : " + data)
      #print("type : ",type(data))
      await websocket.send("echo : " + data)
      
start_server = websockets.serve(accept, "0.0.0.0", 3004)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
