import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import imagenet_utils
import time
from PIL import Image
import sys

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_virtual_device_configuration(gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
    except RuntimeError as e:
        print(e)

file_name= 'ILSVRC2012_val_00004677.JPEG';
##img_resized = cv2.resize(img,(224,224))

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

img = Image.open(file_name);
resized_img= img.resize((224,224)) #to client

#### to server
final_image =  np.expand_dims(resized_img,axis =0)
# 10 samples
kk=0;
for x in range(100):
    st = time.time()
    predictions = model.predict(final_image) # MobilenetV2 original and Bigdata Team
    endt= time.time() - st;
    print(endt)
    if x != 0:
        kk=endt+kk;
    results = imagenet_utils.decode_predictions(predictions)
    print(results)
print(kk/10)
