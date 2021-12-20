SERVICE MIGRATION
=================
# 1. Goal

Development of service Migration Technology that complements the stability of the edge cloud.
Provides solution for handling user requests in the edge plane without the requirement of the central cloud.

# 2. Hardware and software specifications
```
Device              NVIDIA Jetson Xavier AGX (Jetpack 4.4.1 L4T 32.4.4)
GPU                 512-core Volta GPU with Tensor Cores
CPU                 8-core ARM v8.2 64-bit CPU, 8 MB L2 + 4 MB L3
Network Module      Intel AC9560, AGW 200
OS/Kernel           Linux Ubuntu 18.04, Tegra 4.9
Kubernetes          Kubernetes 1.18
Docker              19.03.6
TensorFlow          1.15.0
```
For service migration, two edge clusters were developed. Each edge cluster has one master node and one worker node with similar configurations.

# 3. Deep learning Applications Used

1. Driver Behaviour Profiling Application
2. Image Recognition

# 4. Methodology

## Assumptions

* Involves multiple edge clusters and movement of user services from one edge cluster to another edge cluster.
* Each edge cluster has a coverage point upto which it can provide its service.
* Migration scenarios : Insufficient resources & Client mobility

##  Migration due to insufficient resources
* Edge resources should possess enough computing resources to process the request sent by the client. In particular to our scenario, evaluation is performed on memory availability. If there are insufficient memory, then the service requests are migrated to the nearby edge clusters. 
* Provides load balancing of requests and efficient resource utilisation on the edge plane.
* Prevents service request waiting time for processing.

##  Migration due to client mobility
* Service containers are migrtated during runtime from the source to destination edge cluster.
* Blockchain is used to find the right destination edge cluster
* When client moves out of range, container metadata information(source_ip, container_id, size, cpu, gpu) of the running container is shared to the blockchain network.
* The destination node self evaluates itself to handle the container 
* It is done by comparing the container information with the current edge cluster if it can handle the migration container.








### Acknowledgement
이 소프트웨어는 2020년도 정부(과학기술정보통신부)의 재원으로 정보통신기술진흥센터의 지원을 받아 수행된 연구임   
(No.2019-0-00064, 커넥티드 카를 위한 지능형 모바일 엣지 클라우드 솔루션 개발)   
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIT)   
(No.2019-0-00064, Intelligent Mobile Edge Cloud Solution for Connected Car)   
