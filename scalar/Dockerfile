FROM nvcr.io/nvidia/l4t-ml:r32.4.3-py3

WORKDIR /

RUN pip3 install websockets

COPY Deployment_Driver_Profiling_rework.py .
COPY Proposed_LSTM_based.h5 .

CMD ["python3","Deployment_Driver_Profiling_rework.py"]
