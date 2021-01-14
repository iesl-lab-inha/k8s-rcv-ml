k8s-rcv-ml
=================
# 1. Goal
클러스터로 구성된 Edge Computing 환경 구성을 위한 서비스 요청을 해결하고, container 환경의 DL 서비스를 지원하기 위해서 구성된 플랫폼을 목표로 한다.   

## 2. 실행 환경
### 2.1 Hardware
엣지 서버는 Master Node, Worker Node로 구성된 클러스터 서버로 kubernetes 플랫폼을 기반으로 한다. 프로그램은 다음과 같은 구조에서 실행되도록 구성되었다.   

<p align="center"><img src="/readme_thumbnail/Hardware env.png" width="30%" height="30%" alt="env"></img></p><br/>   

#### 2.1.1 MasterNode   
**Master node**는 클러스터 전체를 컨트롤하는 역할을 한다. (상태 정보 관리, Worker node에 pod를 할당하고 pod 안에 컨테이너를 띄움 등)   
   
<p align="center"><img src="/readme_thumbnail/master.png" width="30%" height="25%" alt="master"></img></p><br/>   
   
Master node의 구조는 위의 그림과 같다. Master node는 Docker, Controller manager, kube-Scheduler, etcd, API server로 구성된다.   
+ **Docker**: Docker는 어플리케이션을 패키징, 배포, 실행하기 위한 플랫폼이다. Docker는 애플리케이션을 전체 환경과 함께 패키지화 되기 때문에 가상머신을 사용하여 가상머신 이미지를 만드는 것보다 훨씬 작은 컨테이너 이미지를 사용하므로 훨씬 가볍다. 또한 Docker 기반 컨테이너 이미지는 재사용이 쉬운 레이어로 구성되어 있어 배포 속도가 빠르고 이미지 스토리지 공간을 줄이는 데 효율적이다. Master node에서 Docker는 이런 이점들을 가지고 컨테이너 안에 리눅스 응용 프로그램들을 자동적으로 배치시켜준다.    
+ **API server**: Kubernetes의 라이프사이클을 정의, 배포, 관리하기 위해 Kubernetes API를 노출하는 컨트롤 플레인 컴포넌트이다. API 서버는 최종 사용자, 클러스터의 다른 부분 그리고 외부 컴포넌트가 서로 통신할 수 있도록 HTTP API를 제공한다. Kubernetes의 모든 기능을 REST API로 제공하고 그에 대한 명령을 처리한다.   
+ **etcd**: 분산 시스템을 계속 실행하는 데 필요한 중요한 정보를 보관하고 관리하는 데 사용되는 오픈소스 분산 key-value 저장소이다. 모든 클러스터 데이터(Kubernetes의 구성 데이터, 상태 데이터 및 메타 데이터)를 관리한다.       
+ **kube-scheduler**: 스케줄링은 kubelet이 pod를 실행할 수 있도록 pod가 노드에 적합한지 확인하고, pod, 서비스 등의 리소스를 적절한 노드에 할당하는 것이다. (노드가 배정되지 않은 새로 생성된 pod를 감지하고 해당 pod가 실행될 최상의 노드를 선택) 
+ **kube-controller-manager**: 컨트롤러를 생성하고 이를 각 노드에 배포하며 관리하는 역할을 한다.    
#### 2.1.2 WorkerNode   
**Worker node**는 Master node에 의해 명령을 받고 pod를 호스트한다.     
   
<p align="center"><img src="/readme_thumbnail/worker.png" width="20%" height="10%" alt="worker"></img></p><br/>   
   
Worker node의 구조는 위의 그림과 같다. Linux OS, Nvidia-runtime, pod로 구성된다.   
+ **Nvidia-runtime**: Nvidia-runtime은 컨테이너 런타임의 하나로 컨테이너 실행을 담당하는 소프트웨어이다. 컨테이너 런타임은 pod를 통해서 배포된 컨테이너를 실행한다. Nvidia 컨테이너 런타임은 OCI(Open Containers Initiative) 사양과 호환되는 GPU 인식 컨테이너 런타임이므로, 컨테이너화 된 GPU 가속 애플리케이션을 구축하고 배포 프로세스를 단순화한다. (Docker에서도 OCI를 사용하므로 호환됨)   
+ **Pod**: pod는 함께 배치된 컨테이너의 그룹이며 Kubernetes의 기본 빌딩 블록이다. 컨테이너를 배포할 때는 컨테이너를 개별 배포하지 않고 컨테이너를 가진 pod를 배포, 운영한다. Kubernetes에서 생성하고 관리할 수 있는 배포 가능한 가장 작은 컴퓨팅 단위이다.    
  - - -
### 2.2 Software   
#### 2.2.1 Overall   
1. 외부 Client의 요청을 proxy server의 역할을 하는 Router(고정IP)에서 받은 후 포트가 정해져 있는 Receive server의 Service로 전달한다. (Receive server는 pod로 구성되며 node들 중 임의로 한 node가 선택되어 구성된다. Receive server의 포트 번호는 외부 Client와의 연결을 위해 로드밸런서로 설정하여 외부에 노출된다.)   
2. Receive server의 Service는 Client의 요청을 Master node 내의 API server에 보낸 후 요청에 맞게 Worker node에 pod를 구성한다. (pod 구성은 Kubernetes가 자동적으로 함)   
(만약 자원이 부족한 경우 중앙 데이터 센터로 서비스를 재요청하는 오프로딩을 실행한다.)
3. 스칼라ML, 이미지ML에 대한 동작을 하는 pod가 생성되면 그 pod에 대한 Service(scalar 혹은 image)를 생성하고, Receive server는 그 Service의 포트 번호를 Client에게 제공한다.    
4. 이후, Client는 스칼라ML, 이미지ML에 대한 동작을 하는 pod에 연결하기 위해 Receive server를 통해 받은 포트번호를 사용하여 접속할 수 있고 1대1로 연결되어 데이터를 주고받는다. (ML 결과값은 웹소켓을 통해 Client로 전송)   
  
#### 2.2.2 Function specification    
(1) **Receive Server(rcvserver.py)**   
Client에서 받은 요청을 기반으로 가용성 확인 및 Edge 서버 Deployment의 전반적인 관리 수행      
   + **create_deployment_object(ml_type)** : ML Type에 따라 Container Resource Requirement를 별도로 설정.   

<pre><code>
   # Scalar Type Resource Setting
   Request = 3417969 KiB (Memory)
   Maximum Limit = 3906250 KiB (Memory)

   # Image Type Resource Setting
   Request = 4394531 KiB (Memory)
   Maximum Limit = 4882812 KiB (Memory)
</code></pre>

이후에 Kubernetes Pod 내에서의 node selector 설정과 Edge 서버에 있는 Xavier, tx2 H/W의 Scheduling 설정을 진행   
기본 설정이 끝난 후 Container와 Pod Template를 생성하고 이를 기반으로 Deployment 객체를 생성 및 반환   
   + **service_request** : Kubernetes 기본 설정을 처리한 후 Xavier, tx2 H/W의 ML 가용 용량을 설정   
create_deployment_object를 통해 생성된 Deployment를 기존 Namespace에 생성된 Deployment 유무를 통해 처리를 결정   

**기존 Deployment가 없는 경우**: Namespace 생성 및 생성된 Deployment를 추가   
**기존 Deployment가 있는 경우**: 사전에 설정된 ML 가용 용량을 확인 후 허용 범위 내이면 생성된 Deployment를 추가. 만약에 ML 가용 용량을 벗어난다면 생성된 Deployment를 기존 Namespace에 추가하지 않고 offloading값을 1로 설정하여 결과 반환. 이 경우 Client에서는 Edge 서버 대신 Center 서버 사용.    

   + **main** : Flask 서버를 초기화하고 동작시킴.   
(2) **Client(testclient_final.py)**   
서버 상태를 확인하고 서버에서 처리할 데이터를 사전 처리한 후 전송하여 결과값을 수신   
   + **timer (start, end)** : 입력으로 들어온 start, end 간 시간 간격을 계산하여 반환함   
   + **request_to_edge (ml_type, client_id)** : Edge Server에 가용이 가능한지 Request를 보내고 Response를 받아 JSON 형식으로 반환함   
   + **request_to_center (ml_type, client_id)** : 외부 Center Server에 가용이 가능한지 Request를 보내고 Response를 받아 JSON 형식으로 반환함
   + **scalar_connect (ws, port)** : ML Type이 Scalar인 데이터들을 Server ML 작업을 위한 과정을 수행함   
Server와 통신을 위한 Websocket을 연결한 후 Scalar data 초기 40개를 Model Ready Test를 위해 전송 및 결과값 수신   
이후 Model Ready 상태이면 초기 40개 이후의 data들을 40개씩 나누어 보내 Server에서 ML 작업을 수행한 결과를 받아 처리함   
2번째 송신부터는 각 40개씩 처리하는 과정에서의 End-to-End 소요시간, 데이터 처리 소요시간, 대역폭을 계산하여 출력   
   + **image_connect (ws, port)** : ML Type이 Image인 데이터를 Server ML 작업을 위한 과정을 수행함   
Scalar 데이터 처리 이후에 연속적으로 시행되기 때문에 사전 Model Test 과정 생략   
그 외에는 scalar_connect와 동일하게 Image data를 Websocket을 통해 Server로 보내고 작업된 결과를 수신   
또한 해당 과정에서의 End-to-End 소요시간, 데이터 처리 소요시간, 대역폭을 계산하여 출력   
   + **main**: 전체적인 Client 과정을 수행   
request_to_edge를 통해 Edge Server의 가용성을 확인한 후 ML 처리를 Edge, Center 둘 중 어디서 처리할 지 결정   
처리 장소를 결정한 후에는 Scalar, Image 순으로 데이터를 처리   
   
(3) **Scalar(Deployment_Driver_Profiling_rework.py)**   
Driver Profile에 관한 정보를 입력으로 Machine Learning을 통해 저장된 Data 중에서 가장 유사한 Profile을 찾아 반환   
   + **Preprocessing (classes, column2, Wx, dx, df)- deprecated** : 입력으로 들어온 df 데이터 중 필요없는 부분을 일부 제거하고 ML 입력 형식에 맞도록 가공, 현재 사용되지 않음   
   + **Labels_Transform (labels) - deprecated** : scikit-learn 라이브러리를 통해 입력으로 들어온 labels 데이터를 정규화함, 현재 사용되지 않음   
   + **Testing_model (X_test, model)**: 입력으로 들어온 40개의 X_test 데이터를 사전에 Train된 model을 기준으로 예측 값을 찾고 반환함.
그 외에 예측값들을 통해 산출된 신뢰도와 이 과정을 수행하는 데 걸린 소요 시간을 측정하고 같이 반환함.   
   + **running_ml (websocket, path)**: 실제 Client와 Websocket을 통해 40개씩 데이터를 받고 ML을 통한 결과값을 다시 Client에게 반환함. 초기 40개의 데이터는 ML을 위한 model 데이터 준비에 확인하는 용도이며, 이후 40개부터 실제 예측이 진행됨.   
   + **main**: Client와의 통신을 위한 Websocket을 초기화하고 시작하는 과정을 수행   

(4) **Image(ImageRecognition_original.py)**   


### Acknowledgement
이 소프트웨어는 2020년도 정부(과학기술정보통신부)의 재원으로 정보통신기술진흥센터의 지원을 받아 수행된 연구임   
(No.2019-0-00064, 커넥티드 카를 위한 지능형 모바일 엣지 클라우드 솔루션 개발)   
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIT)   
(No.2019-0-00064, Intelligent Mobile Edge Cloud Solution for Connected Car)   
