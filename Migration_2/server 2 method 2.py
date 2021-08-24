#Flask
from flask import Flask, render_template, json, request, jsonify, g
from datetime import datetime
#Kubernetes API in python
from kubernetes import client, config
from time import sleep

app = Flask("app-test")

##kubernetes component create##

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
    xavier_weight = client.V1PreferredSchedulingTerm(weight=50, preference = client.V1NodeSelectorTerm(match_expressions=[client.V1NodeSelectorRequirement(key='machine',operator='In',values=['xavier',]),])) 
    tx2_weight = client.V1PreferredSchedulingTerm(weight=50, preference = client.V1NodeSelectorTerm(match_expressions=[client.V1NodeSelectorRequirement(key='machine',operator='In',values=['tx2',]),]))
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


#Flask Webserver#

#Request service for ml_type = {scalar, image}, nsp(username or already make)
@app.route('/app-service',methods=['GET','POST'])
def service_request(): 
    # config for kubernetes
    c = client.Configuration()
    c.debug = True

    # config.load_incluster_config() 
    config.load_kube_config()   

    # object in kubernetes API, this object call the function
    core_v1 = client.CoreV1Api() 
    app_v1 = client.AppsV1Api()
    service_port = {'scalar':'31600', 'image':'31602'}

    # read nodes list, node's count
    xavier_label = "machine=xavier"
    tx2_label="machine=tx2"
    xavier_nodelist_rsp = core_v1.list_node(label_selector=xavier_label)
    tx2_nodelist_rsp = core_v1.list_node(label_selector=tx2_label)
    xavier_count = len(list(xavier_nodelist_rsp.items))
    tx2_count = len(list(tx2_nodelist_rsp.items))
    print("\nKubernetes nodes Information for processing ML = \nXavier node = {}\ntx2 node = {}".format(xavier_count,tx2_count))
    ml_capacity = xavier_count+tx2_count;
    
    # Fetch the allocatable memory of the worker node
    node1 = core_v1.list_node(label_selector=xavier_label)
    for i in node1.items:
        resource = i.status.allocatable
        memory1 = resource.get('memory')
        print('Node 1 Allocatable memory = {}'.format(memory1))
    
    Allocatable_memory_node1 = int(memory1.strip('Ki'))
    print(Allocatable_memory_node1)

    node2 = core_v1.list_node(label_selector=tx2_label)
    for i in node2.items:
        resource = i.status.allocatable
        memory2 = resource.get('memory')
        print('Node 2 Allocatable memory = {}'.format(memory2))
    
    Allocatable_memory_node2 = int(memory2.strip('Ki'))
    print(Allocatable_memory_node2)

    # Step1. checking request message
    ml_type = request.args.get('type',type = str)
    client_id = request.args.get('clientID',type = str)
    tm = request.args.get('clienttime',type = str)
    print('\nRequest message')
    print(ml_type+'\t'+client_id+'\t'+tm+'\t')
    print("\nCurrent time = " + datetime.utcnow().isoformat(sep=' ',timespec='milliseconds'))
    nsp = (ml_type+'-test')
    nm = (ml_type+'-deploy')
    
    # Memory calculations
    if ml_type == 'scalar':
        required_memory_limit = "3906250Ki"

    elif ml_type == 'image':
        required_memory_limit = "5371094Ki"
    
    print("Memory needed for processing the request = " + required_memory_limit)
    resource_limit = required_memory_limit.strip('Ki')
    print("Required resource limit = " + resource_limit)
    
        
    #scalar_utilised_memory - node1
    scalar_pod_list_node1 = core_v1.list_namespaced_pod(namespace = "scalar-test" ,field_selector='spec.nodeName=cluster2worker2-desktop' )
    scalar_pod_count_node1 = len(scalar_pod_list_node1.items)
    print("\nscalar_pod_count_node1 = {}".format(scalar_pod_count_node1))
    scalar_utilised_memory_node1 = scalar_pod_count_node1 * 3906250
    print("scalar_utilised_memory_node1 = {}".format(scalar_utilised_memory_node1)) 
    #image_utilised_memory
    image_pod_list_node1 = core_v1.list_namespaced_pod(namespace = "image-test" , field_selector='spec.nodeName=cluster2worker2-desktop')
    image_pod_count_node1 = len(image_pod_list_node1.items)
    print("image_pod_count_node1 = {}".format(image_pod_count_node1))
    image_utilised_memory_node1 = image_pod_count_node1 * 5371094
    print("image_utilised_memory_node1 = {}".format(image_utilised_memory_node1))

    Total_memory_utilised_node1 = (scalar_utilised_memory_node1 + image_utilised_memory_node1)
    print("Total memory utilised_node1 = {}".format(Total_memory_utilised_node1))

    #calculating remaining available memory
    Remaining_memory_node1 = Allocatable_memory_node1 - Total_memory_utilised_node1
    print('remaining memory in node 1 = {}'.format(Remaining_memory_node1))  

    #scalar_utilised_memory - node2
    scalar_pod_list_node2 = core_v1.list_namespaced_pod(namespace = "scalar-test",field_selector='spec.nodeName=nvidia-desktop')
    scalar_pod_count_node2 = len(scalar_pod_list_node2.items)
    print("\nscalar_pod_count_node2 = {}".format(scalar_pod_count_node2))
    scalar_utilised_memory_node2 = scalar_pod_count_node2 * 3906250
    print("scalar_utilised_memory_node2 = {}".format(scalar_utilised_memory_node2))

    #image_utilised_memory
    image_pod_list_node2 = core_v1.list_namespaced_pod(namespace = "image-test",field_selector='spec.nodeName=nvidia-desktop')
    image_pod_count_node2 = len(image_pod_list_node2.items)
    print("image_pod_count_node2 = {}".format(image_pod_count_node2))
    image_utilised_memory_node2 = image_pod_count_node2 * 5371094
    print("image_utilised_memory_node2 = {}".format(image_utilised_memory_node2))

    Total_memory_utilised_node2 = (scalar_utilised_memory_node2 + image_utilised_memory_node2)
    print("Total memory utilised_node2 = {}".format(Total_memory_utilised_node2))

    #calculating remaining available memory
    Remaining_memory_node2 = Allocatable_memory_node2 - Total_memory_utilised_node2
    print('remaining memory in node 2 = {}'.format(Remaining_memory_node2))


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
            elif ml_type == 'image':
                image_deploy.spec.replicas = item.spec.replicas
                deploy_exist = 1
                break
    
     #Step3-1. checking migration conditions
    if deploy_exist == 1:
        if Remaining_memory_node1 < int(resource_limit) or Remaining_memory_node2 < int(resource_limit):
            print('\nNo sufficient Memory')
            return jsonify({'service_port': service_port[ml_type], 'migration1':1})

    #Doesn't have any target deploy...
    #Step3-2. Deployment create
    elif deploy_exist == 0:
        if ml_type == 'scalar':
            print('\nscalar create')
            #Before running to create deployment (scalar)
            scalar_dep_resp = app_v1.create_namespaced_deployment(namespace=nsp, body=scalar_deploy);
            scalar_deploy.spec.replicas = scalar_dep_resp.spec.replicas
            deploy_exist = 1;
        elif ml_type == 'image':
            print('\nimage create')
            #Before running to create deployment (image)
            image_dep_resp = app_v1.create_namespaced_deployment(namespace=nsp, body=image_deploy);
            image_deploy.spec.replicas = image_dep_resp.spec.replicas
            deploy_exist = 1;

    #Step4. Increasing replicas
    new_replicas = 0;
    if deploy_exist == 1:
        if ml_type == 'scalar':
            print('\nscalar patch')
            scalar_deploy.spec.replicas = scalar_deploy.spec.replicas + 1;
            scalar_dep_resp = app_v1.patch_namespaced_deployment_scale(name=(ml_type+'-deploy'), namespace=nsp, body=scalar_deploy)
            new_replicas = scalar_dep_resp.spec.replicas
        elif ml_type == 'image':
            print('\nimage patch')
            image_deploy.spec.replicas = image_deploy.spec.replicas + 1;
            image_dep_resp = app_v1.patch_namespaced_deployment_scale(name=(ml_type+'-deploy'), namespace=nsp, body=image_deploy)
            new_replicas = image_dep_resp.spec.replicas
    
    #Step5. new replicas wait
    dps = app_v1.read_namespaced_deployment(name = nm, namespace=nsp)
    wait_time = 0;

    while dps.status.available_replicas != new_replicas:
        wait_time = wait_time + 1;
        sleep(1);
        print("Wait for {} sec ready for replicas".format(wait_time));
        dps = app_v1.read_namespaced_deployment(name = nm, namespace = nsp)
    
    #Final, return service port
    return jsonify({'service_port' : service_port[ml_type],'migration1':0})

#main#

if __name__ == '__main__':
    app.debug = True
    app.run(host = '192.168.1.11', port=5611)


