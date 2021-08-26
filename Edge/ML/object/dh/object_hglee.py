import cv2
import numpy as np

def model_setting(model_location, num_label):
    model_layer = model_location.getLayerNames()
    model_out = [model_layer[i[0] - 1] for i in model_location.getUnconnectedOutLayers()]
    rainbow = np.random.uniform(0, 255, size=(len(num_label), 3))
    return model_layer, model_out, rainbow

def photo_setting(photo_location, model_location, model_out):
    photo = cv2.resize(photo_location, None, fx=0.3, fy=0.3)
    height, width, channels = photo.shape
    blob = cv2.dnn.blobFromImage(photo, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    model_location.setInput(blob)
    outs = model_location.forward(model_out)
    return photo, height, width, channels, blob, outs
