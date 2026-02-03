# MLB 투수 구종 패턴 분석 프로젝트 요약

## **1. 연구 개요 및 목표**

- **주제:** Levenshtein 거리를 이용한 MLB 투수의 구종 시퀀스 패턴 분석 및 계층적 군집화.
- **목표:** 프로세스 마이닝 기법을 활용하여 투수의 구종 선택 전략을 **구조적으로 정량화**하고, 유사한 전략 패턴을 **군집화**하여 핵심 전략과 예외 전략을 식별합니다.
<br>

## **2. Contributors**

| **Members** | **Roles** |
| --- | --- |
|<img height="135" alt="image" src="https://github.com/user-attachments/assets/e3dc25ec-4919-418b-996f-8e90964b179f" /> <br> <p align="center"><a href="https://github.com/finn-sharp" target="_blank"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" height="16" style="vertical-align: middle;" />&nbsp;[김재현]</a></p>|• 데이터 분석 파이프라인 및 코드 템플릿 구조를 설계하여 프로젝트 전반의 분석 흐름을 정리함 <br>• 분석 결과 해석을 돕기 위한 데이터 시각화 작업을 수행함 <br>• 원천 데이터 정제 및 가공 등 데이터 전처리 전반을 담당함 <br>• 코드의 재사용성과 유지보수성을 고려한 모듈화 작업을 수행함 <br>• 프로젝트 결과를 종합하여 최종 발표 자료를 구성하고 발표를 진행함|
|<img height="135" alt="image" src="https://github.com/user-attachments/assets/66a1e01e-b57b-4b03-b3fb-09e4ef38f4da" /> <br> <p align="center"><a href="https://github.com/flt-feather" target="_blank"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" height="16" style="vertical-align: middle;" />&nbsp;[위훈성]</a></p>|• 프로젝트 전체 기획과 진행을 총괄하며 연구 방향과 일정을 관리함 <br>• 중간 발표를 기획·진행하며 연구 진행 상황을 공유함 <br>• 선행 연구 및 관련 논문 분석을 통해 연구의 이론적 기반을 정리함 <br>• 세이버메트릭스 지표 계산을 위한 분석 모듈을 설계·구현함 <br>• 분석 결과를 정리하여 연구 보고서를 작성함|
|<img height="135" alt="image" src="https://github.com/user-attachments/assets/29f62315-fb55-4d5f-988f-bcd03c98f171" /> <br> <p align="center"><a href="https://github.com/ben7094" target="_blank"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" height="16" style="vertical-align: middle;" />&nbsp;[김상훈]</a></p>|• 분석에 필요한 데이터를 수집하고 웹 스크래핑을 통해 원천 데이터를 확보함 <br>• 연구 주제 설정 및 분석 방향 수립 등 연구 기획 단계에 참여함 <br>• 중간 발표 및 최종 발표용 발표 자료(데크)를 제작함 <br>• 최종 발표 과정에 참여하여 프로젝트 결과 공유를 지원함|
<br>

### 2.1 프로젝트 초기 설정 및 환경 세팅 가이드

이 프로젝트는 **프로세스 마이닝(Process Mining)** 분석을 위해 특정 Python 패키지와 모듈 구조를 필요로 합니다. 아래 가이드를 따라 환경을 설정하면 즉시 실험을 시작할 수 있습니다.
<br>

## **3. 프로젝트 디렉토리 구조 (Tree Structure)**

프로젝트의 논리적 구성 요소를 명확히 파악할 수 있도록 트리 형태로 디렉토리 구조를 시각화했습니다.

```
.
├── cap/                      # [1] 가상 환경 폴더 (Project Virtual Environment)
├── clustering/               # [2] 군집 분석 모듈
│   ├── __init__.py
│   ├── distance.py           # - Levenshtein 거리 계산, ClusteredTraces 클래스
│   ├── visualizer.py         # - MDS, Dendrogram 시각화 기능
│   └── utils.py              # - 군집화 이후 cluster를 ProcessID를 기반으로 dataframe에 mapping하는 함수
├── lib/                      # [3] 라이브러리 및 공통 데이터 저장소 (Common Libs/Data)
├── data/                     # [4] 프로세스 마이닝 분석에 필요한 데이터( 2019 ~ 2024년도 투수의 투구 데이터)
│   └── pitcher_2019_2024.csv   # 분석에 사용한 실제 데이터셋
├── metrics/                  # [5] 프로세스 마이닝 분석에 필요한 데이터( 2019 ~ 2024년도 투수의 투구 데이터)
│   ├── __init__.py              
│   └── saber.py              # Sabermetrics에 사용하는 지표 함수 정의(p/pa, k/pa, fip)
├── mining/                   # [6] 프로세스 마이닝 분석 모듈 (Core Logic)
│   ├── __init__.py
│   ├── utils.py              # - load_data_from_bigquery 등 유틸리티 함수
│   ├── preprocessing.py      # - 전처리, 필터링, 노드 추가 함수
│   ├── probability.py        # - BasedTraces 등 확률 기반 계산 모듈
│   ├── visualizer.py         # - Sankey Diagram, Interactive Grpah 시각화 기능
│   └── exploratory.py        # - ProcessEDA 등 탐색적 분석 모듈
├── .git/
├── .gitignore                # Git 추적 제외 파일 명시 (key.json, cap 등)
├── key.json                  # BigQuery 접근 인증 파일
├── README.md
├── requirements.txt          # 패키지 의존성 목록
└── inference.ipynb           # [7] 메인 실험 및 분석 노트북
```
<br>

 #### 3.1 핵심 디렉토리 상세 설명

| **번호** | **디렉토리** | **역할 및 포함 내용** |
| --- | --- | --- |
| **[1]** | **`cap`** (`venv`) | **가상 환경:** 프로젝트의 Python 인터프리터와 설치된 의존성 패키지(`pm4py`, `pandas`, `Levenshtein` 등)를 격리 보관합니다. |
| **[2]** | **`clustering`** | **군집화 모듈:** 구종 시퀀스 간의 **구조적 유사성(Levenshtein Distance)**을 계산하고, 이를 기반으로 **계층적 군집화 및 MDS 시각화**를 수행하는 모듈이 포함됩니다. |
| **[3]** | **`lib`** | **공용 자원:** 프로젝트 전반에 걸쳐 사용되는 재사용 가능한 라이브러리 파일이나 공통 데이터셋을 저장합니다. |
| **[4]** | **`data`** | **수집 데이터:** 실제 Process Mining을 통한 Sabermetrics 개선 연구에 활용한 데이터셋을 저장합니다. |
| **[5]** | **`metrics`** | **평가 지표:** 군집화된 데이터 별 Sabermetrics을 평가하기위해 실제 공식에 기반하여 계산하기 위한 지표 함수를 정의했습니다. |
| **[6]** | **`mining`** | **프로세스 마이닝 핵심 로직:** 데이터 로드, **프로세스 이벤트 로그 변환**, EDA, **전이 확률 계산** 등 프로세스 마이닝을 위한 기본 분석 기능이 정의되어 있습니다. |
| **[7]** | **`inference.ipynb`** | **실험 코드:** 데이터를 로드하고 전처리한 후, `mining` 모듈로 EDA를 수행하고 `clustering` 모듈로 패턴 분류를 수행하는 **전체 연구 흐름이 순서대로 기록**된 메인 노트북입니다. |
<br>

## **4. 초기 환경 설정 (Quick Start)**

### **4.1. 가상 환경 설정 및 활성화**

프로젝트의 의존성 충돌을 방지하기 위해 가상 환경을 사용합니다.

**4.1.1 프로젝트 루트 디렉토리로 이동합니다. (Process-Mining-Analysis-on-MLB)**
```Bash
cd Process-Mining-Analysis-on-MLB
```

**4.1.2. 가상 환경 생성 (예: 'venv'라는 이름으로 생성)**
```Bash
python3 -m venv venv
```

**4.1.3. 가상 환경 활성화**
- **macOS/Linux**
```Bash
source venv/bin/activate
```

- **Windows (PowerShell)**

```Bash
.\venv\Scripts\Activate
```
<br>

### **4.2. 의존성 패키지 설치**

프로젝트에 필요한 모든 라이브러리를 `requirements.txt` 파일을 통해 설치합니다.

```Bash
pip install -r requirements.txt
```
<br>
또는 의존성 패키지 및 실제 본 Repository를 활용하여 데이터를 분석하기 위해서 아래 코드를 실행해도 됩니다.  
하지만 데이터 등을 활용하는 측면에서 가급적 clone 후 package를 활용하면 좋을 것 같습니다.

```Bash
pip install git+https://github.com/finn-sharp/Process-Mining-Analysis-on-MLB.git
pip install -r requirements.txt
```

### **4.3. 데이터 접근 설정**

Google Cloud BigQuery를 사용하므로, 프로젝트 루트 디렉토리에 **`key.json`** 파일을 배치하여 데이터베이스 접근 권한을 설정해야 합니다.
또는 실제 data 폴더에 저장된 csv파일을 활용하여 마무리 투수에 대한 연구를 진행합니다.
