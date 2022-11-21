import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.applications import imagenet_utils
from tensorflow.keras.preprocessing import image
import time
import sys
import base64
import websockets
import asyncio
from PIL import Image
import io
#Need to change there get websocket image data

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
   try:
      tf.config.experimental.set_virtual_device_configuration(gpus[0],[tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2560)])
   except RuntimeError as e:
      print(e)

#file_name= 'ILSVRC2012_val_00004677.JPEG';
#img_resized = cv2.resize(img,(224,224))
'''
if (sys.argv[1] == 'pruned'):
    print('pruned');
    model_path = "mobilenet_0.h5"  ## pruned model with MobilenetV1 Bigdata Team
    model = tf.keras.models.load_model(model_path)
elif (sys.argv[1] == 'original'):
    print('original')
    model_path = "mobilenet_original.h5" ## mobilenet V1
    model = tf.keras.models.load_model(model_path)
elif (sys.argv[1] == 'mobile'):
    print('v2')
    model = tf.keras.applications.mobilenet_v2.MobileNetV2()  ## Mobilenet V2
else:
    print('error input arg')

#img = image.load_img(file_name, target_size=(224,224))
resized_img= image.img_to_array(img) #to client
## to server
final_image = np.expand_dims(resized_img,axis =0)
final_image=tf.keras.applications.mobilenet.preprocess_input(final_image)
# 10 samples

kk=0;
for x in range(11):
    st = time.time()
    predictions = model.predict(final_image) # MobilenetV2 original and Bigdata Team
    endt= time.time() - st;
    print(endt)
    if x != 0:
        kk=endt+kk;
    results = imagenet_utils.decode_predictions(predictions)
    print(results)
    print(kk/10)
'''

async def running_ml(websocket, path):
# 1. preset recieve data number and model
    model_path = "mobilenet_0.h5"
    model = tf.keras.models.load_model(model_path)
    while True:
        try:
            json_list = list()
            rcv_data = await websocket.recv()
            temp = json.loads(rcv_data)
            client_timestamp = temp['timestamp']
            del temp['timestamp']
# 2. set ml part
# important thing is hard to load image
# proceed is (client) file load -> encoded str -> (server)str -> decoded byte -> Image object
            base64_img_bytes = temp['data'].encode('utf-8')
            bin_image = base64.b64decode(base64_img_bytes)
            im = Image.open(io.BytesIO(bin_image))
            resized_img = im.resize((224,224))
            num_image = np.expand_dims(resized_img, axis = 0)
            final_image = tf.keras.applications.mobilenet.preprocess_input(num_image)
            predictions = model.predict(final_image)
            results = imagenet_utils.decode_predictions(predictions)
            await websocket.send(str(results))
        except Exception as e:
            print(e)
            asyncio.get_event_loop().stop();
            break;

########################################################################
#########################main start here################################
########################################################################
# start point
start_server = websockets.serve(running_ml, '0.0.0.0', 5700);
print('image_server_running')
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever();
