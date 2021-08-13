FROM nvcr.io/nvidia/l4t-tensorflow:r32.4.3-tf1.15-py3

RUN pip3 install pillow 
RUN pip3 install websockets

COPY ILSVRC2012_val_00004677.JPEG  .
COPY ImageRecognition_testing.py .
COPY mobilenet_0.h5 .
COPY mobilenet_original.h5 .

CMD ["python3","ImageRecognition_testing.py","pruned"]
