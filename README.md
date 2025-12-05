#  Chaos GitOps Lab (인프라 & 운영 저장소)

이곳은 K3s 인프라, Argo CD(Manifest), Ansible(Chaos), Monitoring을 통합 관리하는 메인 컨트롤 타워입니다.

##  1. 업로드 가이드 (이곳에 올릴 것)
* **`k8s-manifests/online-boutique/`**: 백엔드 팀이 작성한 **Deployment, Service YAML 파일**.
* **`k8s-manifests/monitoring/`**: 모니터링 팀이 작성한 **Helm Chart (values.yaml)** 파일.
* **`ansible/playbooks/chaos/`**: 카오스 팀이 작성한 **공격 스크립트(.yml)** 파일.

---

##  2. 개발 공통 표준 (Namespace & Label)
**백엔드/인프라 팀 필독:** YAML 파일 작성 시 아래 라벨 표준을 반드시 준수해야 합니다. (Chaos 스크립트 타겟팅용)

###  기본 Namespace
* 모든 Online Boutique 서비스: `online-boutique`

###  공통 라벨 표준 (Key: Value)
* `app`: 서비스 식별자 (예: `frontend`, `cartservice`) **[절대 변경 금지]**
* `app.kubernetes.io/name`: 서비스 이름
* `app.kubernetes.io/part-of`: `online-boutique-chaos-lab`
* `app.kubernetes.io/tier`: `frontend`, `backend`, `data`
* `app.kubernetes.io/component`: `cart`, `payment`, `cache` 등

###  서비스별 라벨 상세 (복사해서 사용하세요)
**(1) frontend**
`app: frontend` / `tier: frontend`

**(2) productcatalogservice**
`app: productcatalogservice` / `tier: backend`

**(3) cartservice**
`app: cartservice` / `tier: backend`

**(4) checkoutservice**
`app: checkoutservice` / `tier: backend`

**(5) paymentservice**
`app: paymentservice` / `tier: backend`

**(6) shippingservice**
`app: shippingservice` / `tier: backend`

**(7) emailservice**
`app: emailservice` / `tier: backend`

**(8) redis-cart**
`app: redis-cart` / `tier: data`

---

##  3. Chaos Engineering 프로젝트 운영 규칙

###  (1) 운영 서버 접근 규칙
1. 모든 접속은 **devuser** 계정으로만 한다. (root 금지)
2. SSH 포트는 **2222**를 사용한다. (`ssh -p 2222 devuser@...`)
3. **서버 내 직접 수정 금지:** `vi`로 설정 수정하거나 `kubectl`로 리소스 변경 절대 금지. (무조건 Git/Ansible로만)

###  (2) Git 관리 규칙
1. **작업 흐름:** 로컬 개발 → GitHub Push → 서버 Pull.
2. **브랜치 전략:**
    * `main`: 안정 버전 (팀장만 Merge 가능).
    * `chaos/*`, `infra/*` 등 개인 브랜치 사용 후 PR 필수.

###  (3) K3s 운영 규칙
1. **라벨 불변:** `app=서비스명` 라벨은 Chaos 스크립트가 바라보므로 절대 바꾸지 않는다.
2. **리소스 제한:** Request/Limit 임의 변경 금지 (팀장 승인 필요).
3. **위험 명령 금지:** 노드 전체 CPU를 잡거나 네트워크를 끊는 명령어는 사전 승인 필수.

###  (4) Chaos 테스트 진행 규칙
1. **사전 공유:** "오늘 cartservice 죽입니다" 등 팀 간 공유 필수.
2. **단독 실행:** 한 번에 하나의 시나리오만 실행 (동시 실행 금지).
3. **Ansible Only:** 수동 `pod kill` 금지, 반드시 `ansible-playbook`으로 실행하여 기록 남김.
4. **복구 원칙:** 테스트 후 `restore_all.yml`로 클러스터 정상화 필수.

###  (5) 모니터링/알람 규칙
1. **Grafana:** 패널 추가는 자유, 삭제는 협의.
2. **Alertmanager:** 설정 변경은 반드시 PR로 진행.

###  (6) 기록 규칙
1. Chaos 테스트 전후로 [실행 플레이북, 지표 변화, 복구 여부, 시간]을 **Notion**에 반드시 기록한다.

### 기본 구조
chaos-gitops-lab/

├── ansible/

│      ├── inventory/

│      │   └── hosts.ini         # 미니 PC 접속 정보 (devuser 계정)

│      ├── playbooks/

│      │   ├── setup/

│      │   │   └── install_argocd.yml  # Argo CD 초기 설치용

│      │   └── chaos/

│      │       ├── run_chaos_test.yml  # Role을 조합하여 실행하는 카오스 시나리오
   
│      │       └── restore_all.yml     # 장애 복구용 플레이북

│      └── roles/                # 카오스 기능별 모듈 (Tasks)

│          ├── chaos_cpu/        # CPU 부하 주입 역할

│          │   └── tasks/main.yml

│          ├── chaos_kill/       # 프로세스 강제 종료 역할

│          │   └── tasks/main.yml

│          ├── chaos_network/    # 네트워크 지연(Latency) 주입 역할

│          │   └── tasks/main.yml

│          └── chaos_pod/        # 팟(Pod) 삭제 역할

   │           └── tasks/main.yml

│

├── k8s-manifests/            # Argo CD가 바라보는 배포 상태(State)

│      ├── online-boutique/      # 웹 애플리케이션 리소스

│      │   ├── deployment.yaml

│      │   ├── service.yaml

│      │   └── redis.yaml

│      ├── monitoring/           # 모니터링 스택 (Prometheus/Grafana)

│      │   ├── Chart.yaml        # Helm Umbrella Chart 정의

│      │   └── values.yaml       # Helm 설정값 (NodePort 등)

│      └── bootstrap.yaml        # (옵션) App of Apps 패턴 정의 파일

│

└── README.md      # 운영 규칙 및 아키텍처 설명
