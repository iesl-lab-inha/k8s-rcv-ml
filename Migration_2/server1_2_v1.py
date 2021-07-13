#Flask
from flask import Flask, render_template, json, request, jsonify, g
#from flask_restplus import Resource, Api
from datetime import datetime
#Kubernetes API in python
from kubernetes import client, config
from time import sleep
import requests
import threading
from datetime import datetime
import time
import os
import sys
import asyncio
import websockets
import base64
import pandas as pd
import json
import csv

EDGE2 = 'http://192.168.1.11:5613/app-service'
EDGE_WS = "ws://165.246.41.45"

def request_to_edge2(ml_type, client_id):
    try:
        tm = str(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'))
        para_dict={"type" : ml_type, "clientID" : client_id, "clienttime" : tm}
        print(str(para_dict))
        resp2 = requests.get(EDGE2, params=para_dict)
        print(resp2)
        return resp2;
    except Exception as e:
        print(e)

app = Flask("app-test")
###############################
##kubernetes component create##
###############################
def create_deployment_object(ml_type):
    #resource
    if ml_type == 'scalar':
        res = client.V1ResourceRequirements(requests={"memory":"3417969Ki"},limits={"memory":"3906250Ki"})
    if ml_type == 'image':
        res = client.V1ResourceRequirements(requests={"memory":"4882812Ki"},limits={"memory":"5371094Ki"})
    #node required affinity(Hard)
    match_express = [client.V1NodeSelectorRequirement(key='machine',operator='NotIn',values=['nano',]),]
    node_selector = client.V1NodeSelector(node_selector_terms = [client.V1NodeSelectorTerm(match_expressions=match_express),])
    #node preferred affinity(Soft)
    xavier_weight = client.V1PreferredSchedulingTerm(weight=70, preference = client.V1NodeSelectorTerm(match_expressions=[client.V1NodeSelectorRequirement(key='machine',operator='In',values=['xavier',]),])) 
    tx2_weight = client.V1PreferredSchedulingTerm(weight=30, preference = client.V1NodeSelectorTerm(match_expressions=[client.V1NodeSelectorRequirement(key='machine',operator='In',values=['tx2',]),]))
    preferred_scheduling = [xavier_weight,tx2_weight]

    #Affinity obj
    affinity = client.V1Affinity(node_affinity = client.V1NodeAffinity(preferred_during_scheduling_ignored_during_execution= preferred_scheduling, required_during_scheduling_ignored_during_execution= node_selector))
    
    #Container obj
    container = client.V1Container(name = ml_type, image=('wnghks3030/'+ ml_type +':finalv2'), ports=[client.V1ContainerPort(container_port=5700)],resources=res)
    #Pod obj
    template = client.V1PodTemplateSpec(metadata=client.V1ObjectMeta(labels={"app": ml_type}), spec=client.V1PodSpec(containers=[container], affinity=affinity))
    #Deployment obj
    spec = client.V1DeploymentSpec(replicas=0, selector={'matchLabels':{'app':ml_type}}, template = template)
    deployment = client.V1Deployment(api_version="apps/v1", kind="Deployment", metadata=client.V1ObjectMeta(name=(ml_type+"-deploy"), labels={"app":ml_type}), spec=spec )
    return deployment;

################################
######Flask Webserver###########
################################


#Request service for ml_type = {scalar, image}, nsp(username or already make)
@app.route('/app-service',methods=['GET','POST'])
def service_request(): 
    #config for kubernetes
    c = client.Configuration()
    c.debug = True

    #config.load_incluster_config() #may code run on pods
    config.load_kube_config()   #may code run on host

    #object in kubernetes API, this object call the function
    core_v1 = client.CoreV1Api() #api_client=client.ApiClient(configuration = c))
    app_v1 = client.AppsV1Api()
    service_port = {'scalar':'31600', 'image':'xxxxx'}

    #read nodes list, node's count
    xavier_label = "machine=xavier"
    tx2_label = "machine=tx2"
    xavier_nodelist_rsp = core_v1.list_node(label_selector=xavier_label)
    tx2_nodelist_rsp = core_v1.list_node(label_selector=tx2_label)
    xavier_count = len(list(xavier_nodelist_rsp.items))
    tx2_count = len(list(tx2_nodelist_rsp.items))

    #[important] Edge capacity for ml
    #For example Kubernetes's has more nodes can caught up the capacity
    ml_capacity = xavier_count*2 + tx2_count;

    print("Kubernetes nodes Information for ML\n Xavier node : {}\n Tx2 node : {}\n".format(xavier_count, tx2_count))
    #Step1. checking request message
    ml_type = request.args.get('type',type = str)
    client_id = request.args.get('clientID',type = str)
    tm = request.args.get('clienttime',type = str)
    print(ml_type+'\t'+client_id+'\t'+tm+'\t')
    print(datetime.utcnow().isoformat(sep=' ',timespec='milliseconds'))
    nsp = (ml_type+'-test')
    nm = (ml_type+'-deploy')
    
    #Step2. checking initialize deployment
    scalar_deploy = create_deployment_object('scalar')
    image_deploy = create_deployment_object('image')
    dps = app_v1.list_namespaced_deployment(namespace = nsp)
    deploy_exist = 0;
    for item in list(dps.items):
        if item.metadata.name == nm:
            if ml_type == 'scalar':
                scalar_deploy.spec.replicas = item.spec.replicas
                deploy_exist = 1
                break

    # Step3-1. checking migration conditions
    # If over the spec, then migrate(re-direct) to the other cluster
    if deploy_exist == 1:
        print("scalar available replica count = {}".format(scalar_deploy.spec.replicas))
        print("ml_capacity = {}".format(ml_capacity))
        if scalar_deploy.spec.replicas >= ml_capacity:
            print("\n PROCESSING IN THE OTHER CLUSTER \n");
            try:
                resp2 = request_to_edge2(ml_type, client_id)
                if resp2.json()['migration2'] is not 1:     
                    num_port_2 = resp2.json()['service_port']
                    print("\nservice port for edge 2 : {}".format(num_port_2))
                elif resp2.json()['migration2'] is 1:
                    print('Offloading')
            except Exception as e: 
                print(e)
            return jsonify({'service_port': num_port_2, 'migration1':1})        
        elif scalar_deploy.spec.replicas < ml_capacity:
            print("\n PROCESSING IN THE SAME CLUSTER \n");

    #Doesn't have any target deploy...
    #Step3-2. Deployment create
    elif deploy_exist == 0:
        if ml_type == 'scalar':
            print('scalar create\n')
            #Before running to create deployment (scalar)
            scalar_dep_resp = app_v1.create_namespaced_deployment(namespace=nsp, body=scalar_deploy);
            scalar_deploy.spec.replicas = scalar_dep_resp.spec.replicas
            deploy_exist = 1;

    #Step4. Increasing replicas
    new_replicas = 0;
    if deploy_exist == 1:
        if ml_type == 'scalar':
            print('scalar patch\n')
            scalar_deploy.spec.replicas = scalar_deploy.spec.replicas + 1;
            scalar_dep_resp = app_v1.patch_namespaced_deployment_scale(name=(ml_type+'-deploy'), namespace=nsp, body=scalar_deploy)
            new_replicas = scalar_dep_resp.spec.replicas
    
    #Step5. new replicas wait
    dps = app_v1.read_namespaced_deployment(name = nm, namespace=nsp)
    wait_time = 0;

    while dps.status.available_replicas != new_replicas:
        wait_time = wait_time + 1;
        sleep(1);
        print("Wait for {} sec ready for replicas".format(wait_time));
        dps = app_v1.read_namespaced_deployment(name = nm, namespace = nsp)
    #Final, return service port
    return jsonify({'service_port' : service_port[ml_type],'migration1' : 0})

#####main#####
if __name__ == '__main__':
    app.debug = True
    app.run(host = '192.168.1.11', port=5611)
