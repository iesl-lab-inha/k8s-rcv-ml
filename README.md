k8s-rcv-ml
=================
# 1. Goal
클러스터로 구성된 Edge Computing 환경 구성을 위한 서비스 요청을 해결하고, container 환경의 DL 서비스를 지원하기 위해서 구성된 플랫폼을 목표로 한다.   
   
# 2. Function
## 1.1 structure
### 1.1.1 Hardware
엣지 서버는 Master Node, Worker Node로 구성된 클러스터 서버로 kubernetes 플랫폼을 기반으로 한다.   
#### MasterNode   
**Master node**는 클러스터 전체를 컨트롤하는 역할을 한다. (상태 정보 관리, Worker node에 pod를 할당하고 pod 안에 컨테이너를 띄움 등)   
   
<img src="/readme_thumbnail/master.png" width="20%" height="20%" alt="master"></img><br/>   
   
Master node의 구조는 위의 그림과 같다. Master node는 Docker, Controller manager, kube-Scheduler, etcd, API server로 구성된다.   
+ **Docker**: Docker는 어플리케이션을 패키징, 배포, 실행하기 위한 플랫폼이다. Docker는 애플리케이션을 전체 환경과 함께 패키지화 되기 때문에 가상머신을 사용하여 가상머신 이미지를 만드는 것보다 훨씬 작은 컨테이너 이미지를 사용하므로 훨씬 가볍다. 또한 Docker 기반 컨테이너 이미지는 재사용이 쉬운 레이어로 구성되어 있어 배포 속도가 빠르고 이미지 스토리지 공간을 줄이는 데 효율적이다. Master node에서 Docker는 이런 이점들을 가지고 컨테이너 안에 리눅스 응용 프로그램들을 자동적으로 배치시켜준다.    
+ **API server**: Kubernetes의 라이프사이클을 정의, 배포, 관리하기 위해 Kubernetes API를 노출하는 컨트롤 플레인 컴포넌트이다. API 서버는 최종 사용자, 클러스터의 다른 부분 그리고 외부 컴포넌트가 서로 통신할 수 있도록 HTTP API를 제공한다. Kubernetes의 모든 기능을 REST API로 제공하고 그에 대한 명령을 처리한다.   
+ **etcd**: 분산 시스템을 계속 실행하는 데 필요한 중요한 정보를 보관하고 관리하는 데 사용되는 오픈소스 분산 key-value 저장소이다. 모든 클러스터 데이터(Kubernetes의 구성 데이터, 상태 데이터 및 메타 데이터)를 관리한다.       
+ **kube-scheduler**: 스케줄링은 kubelet이 pod를 실행할 수 있도록 pod가 노드에 적합한지 확인하고, pod, 서비스 등의 리소스를 적절한 노드에 할당하는 것이다. (노드가 배정되지 않은 새로 생성된 pod를 감지하고 해당 pod가 실행될 최상의 노드를 선택) 
+ **kube-controller-manager**: 컨트롤러를 생성하고 이를 각 노드에 배포하며 관리하는 역할을 한다.    
#### WorkerNode   
**Worker node**는 Master node에 의해 명령을 받고 pod를 호스트한다.     
   
<img src="/readme_thumbnail/worker.png" width="20%" height="20%" alt="worker"></img><br/>    
   
Worker node의 구조는 위의 그림과 같다. Linux OS, Nvidia-runtime, pod로 구성된다.   
+ **Nvidia-runtime**: Nvidia-runtime은 컨테이너 런타임의 하나로 컨테이너 실행을 담당하는 소프트웨어이다. 컨테이너 런타임은 pod를 통해서 배포된 컨테이너를 실행한다. Nvidia 컨테이너 런타임은 OCI(Open Containers Initiative) 사양과 호환되는 GPU 인식 컨테이너 런타임이므로, 컨테이너화 된 GPU 가속 애플리케이션을 구축하고 배포 프로세스를 단순화한다. (Docker에서도 OCI를 사용하므로 호환됨)   
+ **Pod**: pod는 함께 배치된 컨테이너의 그룹이며 Kubernetes의 기본 빌딩 블록이다. 컨테이너를 배포할 때는 컨테이너를 개별 배포하지 않고 컨테이너를 가진 pod를 배포, 운영한다. Kubernetes에서 생성하고 관리할 수 있는 배포 가능한 가장 작은 컴퓨팅 단위이다.    
  - - -
### 1.1.2 Software
외부 Client의 요청을 proxy server의 역할을 하는 Router(고정IP)에서 받은 후 포트가 정해져 있는 Receive server의 Service로 전달한다. (Receive server는 pod로 구성되며 node들 중 임의로 한 node가 선택되어 구성된다. Receive server의 포트 번호는 외부 Client와의 연결을 위해 로드밸런서로 설정하여 외부에 노출된다.)   
Receive server의 Service는 Client의 요청을 Master node 내의 API server에 보낸 후 요청에 맞게 Worker node에 pod를 구성한다. (pod 구성은 Kubernetes가 자동적으로 함)   
(만약 자원이 부족한 경우 중앙 데이터 센터로 서비스를 재요청하는 오프로딩을 실행한다.)
스칼라ML, 이미지ML에 대한 동작을 하는 pod가 생성되면 그 pod에 대한 Service(scalar 혹은 image)를 생성하고, Receive server는 그 Service의 포트 번호를 Client에게 제공한다.    
이제 Client는 스칼라ML, 이미지ML에 대한 동작을 하는 pod에 연결하기 위해 Receive server를 통해 받은 포트번호를 사용하여 접속할 수 있고 1대1로 연결되어 데이터를 주고받는다. (ML 결과값은 웹소켓을 통해 Client로 전송)   
   
이 소프트웨어는 2020년도 정부(과학기술정보통신부)의 재원으로 정보통신기술진흥센터의 지원을 받아 수행된 연구임   
(No.2019-0-00064, 커넥티드 카를 위한 지능형 모바일 엣지 클라우드 솔루션 개발)   
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIT)   
(No.2019-0-00064, Intelligent Mobile Edge Cloud Solution for Connected Car)   
