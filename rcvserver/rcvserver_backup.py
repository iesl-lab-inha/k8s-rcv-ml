#Flask
from flask import Flask, render_template, json, request,jsonify
#from flask_restplus import Resource, Api
from datetime import datetime
#Kubernetes API in python
from kubernetes import client, config

#config for kubernetes
c = client.Configuration()
c.debug = True

#may code run on pods
config.load_incluster_config()
#may code run on host
#config.load_inkube_config()

#object in kubernetes API, this object call the function
core_v1 = client.CoreV1Api(api_client=client.ApiClient(configuration=c)) 
app_v1 = client.AppsV1Api()

app = Flask("app-test")

def create_deployment_object(ml_type, namespace):
	container = client.V1Container( name = ml_type,
                                   image=('wnghks3030/test'+ ml_type +':v1.4'),
                                   ports=[client.V1ContainerPort(container_port=5700)],
                                   args =['-p','5700'],)
	template = client.V1PodTemplateSpec(metadata=client.V1ObjectMeta(labels={"app": ml_type}),
                                        spec=client.V1PodSpec(containers=[container]))
	spec = client.V1DeploymentSpec(replicas=1,
                                   selector={'matchLabels':{'app':ml_type}},
                                  template = template)
	deployment = client.V1Deployment(api_version="apps/v1",
                                     kind="Deployment",
                                     metadata=client.V1ObjectMeta(namespace=namespace,
                                                                  name= (ml_type+'-deploy'),
                                                                  labels={"app":(ml_type+'-deploy')}), spec=spec)
	return deployment

def create_service(ml_type, namesapce):
    port1 = client.V1ServicePort(ptotocol='TCP',port= '81',nodePort='31001',
                                 target_port=5700)

    spec = client.V1ServiceSpec(session_affinity='ClusterIP',cluster_ip='10.110.194.2',
                               external_i_ps='168.246.1.45',external_traffic_policy='Cluster',
                               ports = [port1],selector = {'app':(ml_type+'-deploy')},
                               type = 'LoadBalancer'
                               )
    service = client.V1Service(api_version="v1",
                              kind="Service",
                              metadata=client.V1ObjectMeta(name=(ml_type+'-service'),
                                                           labels={"app":(ml_type+'-service')},
                                                           namespace=namespace),
                              spec=spec)
    return service

#Request service for ml_type = {scalar, image}, nsp(username or already make)
@app.route('/app-service',methods=['GET','POST'])
def service_request():
	#check svc_type
	#if not existing then, creating new deployment and service for type has edge server
    #if existing then, checking replicaSet.
	ml_type = request.args.get('type',type = str)
	nsp = request.args.get('clientID',type = str)
	tm = request.args.get('clienttime',type = str)
	print(ml_type+'\n'+nsp+'\n'+tm+'\n')
	print(datetime.utcnow().isoformat(sep=' ',timespec='milliseconds'))
	dps=app_v1.list_namespaced_deployment(namespace=nsp)
	type_replicas = dict()
	for item in list(dps.items):
		if item.metadata.name != (ml_type+"-deploy") :
			deployment = create_deployment_object(ml_type, nsp)
			res_dp = app_v1.create_namespaced_deployment(namespace = nsp, body = deployment)
		else:
			res_dp = app_v1.read_namespaced_deployment(name=(ml_type+"-deploy") ,namespace = nsp)
            #type_replicas stores 2type's replicas
	type_replicas[ml_type] = res_dp.status.replicas
 
    #Extra functional for Caching/Offloading functions
    #we need to caculate new model for how much popular in image, scalar with central data center
    #considering 4 part gpu, cpu, ram, time
    #How caculate 4 parts? gpu = plugin, cpu/ram = default, time = timestamp
    
    #Final, return service port
	if ml_type == 'scalar':
		return jsonify({'service_port' : '31001', 'offloading' : 0})
	elif ml_type =='image':
		return jsonify({'service_port' : '31002', 'offloading' : 0})
'''
    #2. check service
    #if not existing then, creating new service for type
    svc = core_v1.read_namespaced_service(name=(ml_type+"-service"),namespace=nsp)
    if svc in none:
        service = create_service(ml_type, nsp)
        service_port = core_v1.create_namespaced_service(namespace = nsp, body = service)
    return service_port.sepc.ports[0]
'''

def page_not_found(error):
    return render_template('page_not_found.html',404)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port=5600)
