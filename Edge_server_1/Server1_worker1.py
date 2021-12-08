import docker
from time import sleep
import datetime
from flask import Flask, render_template, json, request, jsonify, g
from datetime import datetime
from time import sleep

app = Flask("app-test")


@app.route('/app-service',methods=['GET','POST'])
def service_request():
    client = docker.from_env()

    ml_type = request.args.get('type', type = str)
    runtime = request.args.get('runtime',type = str)

    print(ml_type+'\t'+runtime+'\t')

    print("Last created container container = {}" .format(datetime.now()))
    container = client.containers.list(limit = 1)
    print(container)

    print("stopping the container = {}" .format(datetime.now()))
    for container in client.containers.list(limit=1):
        print(container.id)
        container.stop()
        print("commit the container = {}".format(datetime.now()))
        image = container.commit("sri2301/imagetest10")
        print(image.id)

    print("pushing the image to dockerHub = {}" .format(datetime.now()))
    client.login(username='sri2301', password='sri2301')
    for line in client.images.push('sri2301/imagetest10', stream=True, decode=True):
        print(line)

    print("push completion time = {}" .format(datetime.now()))

    return jsonify({'push' : 1})

#####main#####

if __name__ == '__main__':
    app.debug = True
    app.run(host = '192.168.1.21', port=5633)
