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

EDGE = 'http://165.246.41.45:31111/app-service'

EDGE_WS = "ws://165.246.41.45"
num_port = "5705"

async def connect(ws, port):
    async with websockets.connect((ws+":"+port)) as websocket:
        cnt=1
        while True:
            cnt=cnt+1
            data = "data" + str(cnt)
            await websocket.send(data)
            result = await websocket.recv()
            print(result)

if __name__ == "__main__":
    try:
        #cnt=1
        asyncio.get_event_loop().run_until_complete(connect(EDGE_WS, num_port))
    except Exception as e:
        print(e)
