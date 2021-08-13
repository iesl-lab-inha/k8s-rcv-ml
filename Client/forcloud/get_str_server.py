#from tensorflow import keras
import pandas as pd
import json
import numpy as np
import time
#import asyncio
#import websockets
#import tensorflow as tf
import csv
from datetime import datetime


# preprocessing
columns=["Long_Term_Fuel_Trim_Bank1","Intake_air_pressure","Accelerator_Pedal_value","Fuel_consumption","Torque_of_friction","Maximum_indicated_engine_torque","Engine_torque","Calculated_LOAD_value", "Activation_of_Air_compressor","Engine_coolant_temperature","Transmission_oil_temperature","Wheel_velocity_front_left-hand","Wheel_velocity_front_right-hand","Wheel_velocity_rear_left-hand", "Torque_converter_speed","Class"]

'''columns = ["Long_Term_Fuel_Trim_Bank1", "Intake_air_pressure", "Accelerator_Pedal_value", "Fuel_consumption",
                    "Torque_of_friction", "Maximum_indicated_engine_torque", "Engine_torque", "Calculated_LOAD_value",
                    "Activation_of_Air_compressor", "Engine_coolant_temperature", "Transmission_oil_temperature",
                    "Wheel_velocity_front_left-hand", "Wheel_velocity_front_right-hand",
                    "Wheel_velocity_rear_left-hand",
                    "Torque_converter_speed"]
'''
classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
dx = 6  ## shift, opposite of overlap
Wx = 40  ## window size
'''
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
   try:
      tf.config.experimental.set_virtual_device_configuration(gpus[0],[tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
   except RuntimeError as e:
      print(e)

def Preprocessing(classes,columns,Wx,dx,df):
    new_df = df[columns]
    from sklearn.preprocessing import StandardScaler
    scaler=StandardScaler()
    scaler.fit(new_df)
    pre_df = scaler.transform(new_df)
    dTest = np.expand_dims(pre_df, axis = 0)
    return dTest

def Labels_Transform(labels):
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    le.fit(labels)
    labels=le.transform(labels)
    return labels
'''
'''
def Testing_model(X_test,model):
    st =time.time()
    Predictions = model.predict(X_test)
    Confidence =  (Predictions[0][np.argmax(Predictions[0])])*100;
    predicted = np.argmax(Predictions, axis=1)
    endtime = time.time()-st
    return predicted, endtime, Confidence
'''

if __name__ == "__main__":
    try:
        skiprow = 0
        df1 = pd.read_csv('full_data_test.csv',nrows=40,usecols=columns)
        result = df1.to_json(orient='records')
        parsed = json.loads(result)

        temp1 = {'timestamp' : datetime.utcnow().isoformat(sep=' ',timespec='milliseconds')}
        parsed[skiprow].update(temp1)
        stdata1 = json.dumps(parsed[skiprow])
        print(stdata1)
        
        json_list = list()
        #Trained_model = keras.models.load_model('Proposed_LSTM_based.h5')
        

        for i in range(0,40):
            temp = json.loads(stdata1)
            client_timestmap = temp['timestamp']
            del temp['timestamp']
            #del temp["Class"]
            #print(temp['Long_Term_Fuel_Trim_Bank1'])
            #temp_copy = temp.copy()
            #print(temp_copy)
            json_list.append(temp)
            #print(temp)
            ##del json_list[0]
            #print(json_list[0])

        print(json_list)
        np_df = pd.DataFrame(json_list)
        #print(json_list)
        #print('np_df = pd.DataFrame(json_list) --> result')
        #print(np_df)
        df = np_df[columns]
        del df['Class']
        #print('df = np_df[columns] --> result')
        #print(df)
        test_data = np.expand_dims(df, axis=0)
        print('test_data = np.expand_dims(df, axis=0) --> result')
        print(test_data)
        #test_data = np.reshape(test_data,(40,16))
        print(test_data.shape)
        #ascii_string, endtime, confidence = Testing_model(test_data, Trained_model)
        #Results = "[ Output result : {}, Execution_Time : {}, confidence : {} ]".format(ascii_string, endtime, confidence)

    except Exception as e:
        print(e)