FROM python:3.6-slim
RUN pip3 install Flask kubernetes flask_restplus werkzeug==0.16.1 

WORKDIR /
COPY rcvserver.py .


ENTRYPOINT ["python3","rcvserver.py"]
