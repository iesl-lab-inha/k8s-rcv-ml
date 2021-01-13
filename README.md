k8s-rcv-ml
=================
# 1. Goal
클러스터로 구성된 Edge Computing 환경 구성을 위한 서비스 요청과 
외부 Client의 요청을 proxy server의 역할을 하는 Router(고정IP)에서 받은 후 포트가 정해져 있는 Receive server의 Service로 전달한다. (Receive server는 pod로 구성되며 node들 중 임의로 한 node가 선택되어 구성된다. Receive server의 포트 번호는 외부 Client와의 연결을 위해 로드밸런서로 설정하여 외부에 노출된다.)
# 1. Example Environment
## 1.1 structure

### 1.1.1 Hardware

### 1.1.2 Software


이 소프트웨어는 2020년도 정부(과학기술정보통신부)의 재원으로 정보통신기술진흥센터의 지원을 받아 수행된 연구임
(No.2019-0-00064, 커넥티드 카를 위한 지능형 모바일 엣지 클라우드 솔루션 개발)
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIT)
(No.2019-0-00064, Intelligent Mobile Edge Cloud Solution for Connected Car)
