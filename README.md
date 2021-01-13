k8s-rcv-ml
=================
# 1. Goal
클러스터로 구성된 Edge Computing 환경 구성을 위한 서비스 요청을 해결하고, container 환경의 DL 서비스를 지원하기 위해서 구성된 플랫폼을 목표로 한다.

# 2. Function
## 1.1 structure
### 1.1.1 Hardware
엣지 서버는 Master Node, Worker Node로 구성된 클러스터 서버로 kubernetes 플랫폼을 기반으로 한다.
**Master node**는 클러스터 전체를 컨트롤하는 역할을 한다. (상태 정보 관리, Worker node에 pod를 할당하고 pod 안에 컨테이너를 띄움 등)

### 1.1.2 Software


이 소프트웨어는 2020년도 정부(과학기술정보통신부)의 재원으로 정보통신기술진흥센터의 지원을 받아 수행된 연구임
(No.2019-0-00064, 커넥티드 카를 위한 지능형 모바일 엣지 클라우드 솔루션 개발)
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIT)
(No.2019-0-00064, Intelligent Mobile Edge Cloud Solution for Connected Car)
