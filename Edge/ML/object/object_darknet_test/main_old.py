import cv2
import numpy as np
import time
import asyncio;
import websockets;
import json
import argparse
import os
import glob
import random
import cv2
import darknet
import base64

def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default="",
                        help="image source. It can be a single image, a"
                        "txt with paths to them, or a folder. Image valid"
                        " formats are jpg, jpeg or png."
                        "If no input is given, ")
    parser.add_argument("--batch_size", default=1, type=int,
                        help="number of images to be processed at the same time")
    parser.add_argument("--weights", default="/jetson-inference/darknet/cfg/yolov3.weights",
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--save_labels", action='store_true',
                        help="save detections bbox for each image in yolo format")#/media/yong2/nvme1/darknet/hg_data
    parser.add_argument("--config_file", default="/jetson-inference/darknet/cfg/yolov3.cfg",
                        help="path to config file")
    parser.add_argument("--data_file", default="/jetson-inference/darknet/cfg/coco.data",
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.40, #25
                        help="remove detections with lower confidence")
    return parser.parse_args()

def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if args.input and not os.path.exists(args.input):
        raise(ValueError("Invalid image path {}".format(os.path.abspath(args.input))))


#class_num = []
#num_2 = []
#box = []

def image_detection(image, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    #f = open("/media/yong2/nvme1/darknet/data/test_base64.txt", 'r', encoding='utf-8')
    #image = cv2.imread("/media/yong2/nvme1/darknet/data/hi.jpg")
    #hex_hg = f.readline()
    #hex_byte=base64.b64decode(hex_hg)

    #i= np.frombuffer(hex_byte, dtype=np.uint8)
    #i2 = i.reshape((576,1024,3))
    #image = i2[:, :, :3]
    image_resized = cv2.resize(image, (width, height))
    #image_resized = cv2.resize(image, (1024, 576))
    #print(image_resized.shape)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)

    image = darknet.draw_boxes(detections, image_resized, class_colors)

    return image, detections

args = parser()
check_arguments_errors(args)
network, class_names, class_colors = darknet.load_network(
    args.config_file,
    args.data_file,
    args.weights,
    batch_size=args.batch_size
)


async def accept(websocket, path):


    while True:
        data = await websocket.recv()
        if len(data) != 0:
            r= base64.b64decode(data) # byte 248832
            #print('s',data)
            hg_qi = np.frombuffer(r, dtype=np.uint8)
            hg_q = hg_qi.reshape((288,512,3))
            hg_image=hg_q[:, :, :3]

            box = []
            class_num = []
            num_2 = []

            prev_time = time.time()
            image, detections = image_detection(
                hg_image, network, class_names, class_colors, args.thresh
                )
            #fps = int(1/(time.time() - prev_time))
            #print("FPS: {}".format(fps))
            #cv2.imshow('Inference', )
            #cv2.waitKey(1)
            #indexes = cv2.dnn.NMSBoxes(box, num_2, 0.5, 0.4)
            #indexes_str = str(indexes.T)
            #indexes = np.transpose(indexes)
            #indexes = indexes.tolist()
            #dic = {'indexes': indexes, 'box': box, 'class_num': class_num}
            #dic = str(dic)
            #await websocket.send(dic)
            print('type',type(image))
            #i=np.array(image)
            print(image.shape)
            i3data = base64.b64encode(image)
            #print()
            await websocket.send(i3data)
        else :
            await websocket.send("no")
        await websocket.send("endbye")

start_server = websockets.serve(accept, "0.0.0.0", 5666)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
