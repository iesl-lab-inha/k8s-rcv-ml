from tensorflow import keras
import pandas as pd
import json
import numpy as np
import time
import asyncio
import websockets
import tensorflow as tf

# preprocessing
columns = ["Long_Term_Fuel_Trim_Bank1", "Intake_air_pressure", "Accelerator_Pedal_value", "Fuel_consumption",
                    "Torque_of_friction", "Maximum_indicated_engine_torque", "Engine_torque", "Calculated_LOAD_value",
                    "Activation_of_Air_compressor", "Engine_coolant_temperature", "Transmission_oil_temperature",
                    "Wheel_velocity_front_left-hand", "Wheel_velocity_front_right-hand",
                    "Wheel_velocity_rear_left-hand",
                    "Torque_converter_speed"]
classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
dx = 6  ## shift, opposite of overlap
Wx = 40  ## window size

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
   try:
      tf.config.experimental.set_virtual_device_configuration(gpus[0],[tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
   except RuntimeError as e:
      print(e)

def Preprocessing(classes,columns2,Wx,dx,df):
    del df['Class']
    
    from sklearn.preprocessing import StandardScaler
    scaler=StandardScaler()
    scaler.fit(df)
    pre_df = scaler.transform(df)
    dTest = np.expand_dims(pre_df, axis = 0)
    return dTest


def Labels_Transform(labels):
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    le.fit(labels)
    labels=le.transform(labels)
    return labels

def Testing_model(X_test,model):
    st =time.time()
    
    Predictions = model.predict(X_test)
    Confidence =  (Predictions[0][np.argmax(Predictions[0])])*100;
    predicted = np.argmax(Predictions, axis=1)
 
    endtime = time.time()-st

    return predicted, endtime, Confidence

async def running_ml(websocket, path):
    # 1. Preset part for Learning model 40 data is received
    json_list = list()
    rcv_data = str()
    for i in range(0,40):
        rcv_data = await websocket.recv()
        temp = json.loads(rcv_data)
        client_timestmap = temp['timestamp']
        del temp['timestamp']
        json_list.append(temp)
    await websocket.send('Model ready')
    Trained_model = keras.models.load_model('Proposed_LSTM_based.h5')
    #2. inf loop working
    while True:
        # 2. 40 line data is received
        for i in range(0,40):
            rcv_data = await websocket.recv()
            temp = json.loads(rcv_data)
            client_timestmap = temp['timestamp']
            del temp['timestamp']
            json_list.append(temp)
            del json_list[0]
        df = pd.DataFrame(json_list)
        #pre_data = Preprocessing(classes,columns,Wx,dx,df)
        del df['Class']
        test_data = np.expand_dims(df, axis=0)
        ascii_string, endtime, confidence = Testing_model(test_data, Trained_model)
        Results = "[ Output result : {}, Execution_Time : {}, confidence : {} ]".format(ascii_string, endtime, confidence)
        await websocket.send(Results)

##########################################################################
################################## Main started here #####################
##########################################################################
start_server = websockets.serve(running_ml, '0.0.0.0', 5700);
print('scalar_server_running')
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever();
