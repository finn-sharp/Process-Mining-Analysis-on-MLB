# 야구 투구 패턴 분석 (Pitch Pattern Analysis)

Josh Hader의 투구 패턴을 프로세스 마이닝 기법으로 분석하는 모듈입니다.

## 📊 분석 목적

이 프로젝트는 투수의 투구 패턴을 프로세스 마이닝으로 분석하여:
- **아웃으로 끝나는 타석**과 **출루로 끝나는 타석**의 투구 패턴 차이를 발견
- 어떤 투구 타입 전환이 아웃/출루를 유도하는지 파악
- 통계적 검정을 통해 패턴 차이의 유의성을 확인

## 🔄 전체 분석 흐름

1. **데이터 수집**: BigQuery에서 투구 데이터 로드 (투구 타입, 이벤트 등)
2. **타석 케이스 정의**: 각 타석을 하나의 프로세스 케이스로 정의, 투구 순서를 이벤트 시퀀스로 변환
3. **케이스 분류**: 
   - 아웃 케이스: strikeout, out, field_out 등으로 끝나는 타석
   - 출루 케이스: single, double, home_run, walk 등으로 끝나는 타석
4. **프로세스 마이닝**: PM4Py Inductive Miner로 각 케이스별 투구 패턴 모델 생성
5. **전이 확률 계산**: 각 투구 타입 간 전이 확률 계산 (FF → SL, SL → CH 등)
6. **시각화**: 
   - 아웃 케이스: 빨간색 그래프 (`transition_graph_out.html`)
   - 출루 케이스: 파란색 그래프 (`transition_graph_reach.html`)
7. **차이 분석**: 다양한 메트릭으로 두 케이스 간 차이 측정 및 통계적 검정

## 🔬 상세 파이프라인 설명

### 1단계: 데이터 수집

- **함수**: `load_data_from_bigquery()`
- **작업**: BigQuery에서 Josh Hader의 투구 데이터 로드
- **수집 데이터**: 투구 타입(`pitch_type`), 이벤트(`events`), 게임 날짜, 타자 정보 등
- **출력**: pandas DataFrame

### 2단계: 타석 케이스 정의

- **함수**: `define_at_bat_cases()`
- **작업**: 각 타석을 하나의 프로세스 케이스로 정의
- **케이스 ID 생성**: `case_id = game_date + batter` (같은 게임의 같은 타자 = 하나의 케이스)
- **투구 순서**: `pitch_order` 컬럼으로 각 타석 내 투구 순서 부여
- **출력**: `case_id`와 `pitch_order`가 추가된 DataFrame

### 3단계: 케이스 분류

- **함수**: `filter_out_cases()` / `filter_reach_cases()`
- **작업**: 타석의 마지막 이벤트를 기준으로 케이스 분류
- **아웃 케이스**: `strikeout`, `out`, `field_out`, `force_out`, `double_play`, `triple_play`, `strikeout_double_play`, `sac_fly`, `sac_bunt` 등
- **출루 케이스**: `single`, `double`, `triple`, `home_run`, `walk`, `hit_by_pitch`, `catcher_interf`, `field_error`, `fielders_choice` 등
- **출력**: 필터링된 DataFrame과 결과 분포 통계

### 4단계: 데이터 전처리

- **함수**: `prepare_timestamps()`, `add_start_node()`, `clean_dataframe()`
- **작업**:
  - 타임스탬프 생성: 각 투구에 `time:timestamp` 부여
  - 시작 노드 추가: 각 타석 시작에 "In" 노드 추가 (선택사항)
  - 데이터 정리: None 값 제거, PM4Py 포맷으로 컬럼명 변환 (`case_id` → `case:concept:name`, `pitch_type` → `concept:name`)
  - **투구 타입 필터링**: FF(포심) 투구 타입 제외 (전체 데이터에서 4개만 존재하여 통계적 신뢰도가 낮음)
- **출력**: 정리된 DataFrame
- **참고**: 실제 데이터에는 SI(싱커), SL(슬라이더), CH(체인지업), FF(포심) 등이 포함되지만, 분석에서는 SI, SL, CH만 사용

### 5단계: 이벤트 로그 생성

- **함수**: `create_event_log()`
- **작업**: DataFrame을 PM4Py `EventLog`로 변환
- **데이터 구조**:
  - 각 케이스 = `Trace` 객체
  - 각 투구 = `Event` 객체
  - 이벤트 속성: `concept:name` (투구 타입), `time:timestamp` (시간)
- **출력**: PM4Py EventLog 객체

### 6단계: 프로세스 마이닝

- **함수**: `create_process_model()`
- **작업**: PM4Py Inductive Miner 알고리즘으로 프로세스 모델 생성
- **출력**: Petri Net (`net`), 초기 마킹 (`im`), 최종 마킹 (`fm`)

### 7단계: 전이 확률 계산

- **함수**: `calculate_transition_probabilities()`
- **작업**: 각 투구 타입 간 전이 확률 계산
- **계산 방법**:
  - 각 케이스 내 인접한 투구 쌍을 추출
  - 전이 빈도수 카운트: `transition_counts[from_activity][to_activity]`
  - 전이 확률 계산: `transition_probs[from_activity][to_activity] = count / total`
- **예시**: SI → SL (70%), SL → CH (30%) 등
- **참고**: 실제 데이터에는 FF(포심)도 있지만 샘플 수가 매우 적어 분석에서 제외됨
- **출력**: 전이 확률 딕셔너리와 전이 카운트 딕셔너리

### 8단계: 시각화

- **함수**: `visualize_transition_graph_pyvis()`
- **작업**: Pyvis를 사용한 인터랙티브 전이 그래프 생성
- **특징**:
  - 네트워크 그래프 형태 (노드 = 투구 타입, 엣지 = 전이 확률)
  - 아웃 케이스: 빨간색 계열 (`transition_graph_out.html`)
  - 출루 케이스: 파란색 계열 (`transition_graph_reach.html`)
  - 엣지 두께와 색상으로 확률 강도 표현
  - 드래그 앤 드롭으로 노드 위치 조정 가능
- **출력**: HTML 파일 (자동으로 브라우저에서 열림)

### 9단계: 비교 분석 및 통계적 검정

- **함수**: `compare_transition_probabilities()`, `print_comparison_summary()`
- **작업**: 아웃 케이스와 출루 케이스 간 전이 확률 차이 분석
- **계산 메트릭**:
  - **MSE/MAE**: 노드별 및 전체 평균 제곱/절대 오차
  - **KL Divergence**: 정보 이론적 관점의 분포 차이 (비대칭)
  - **JS Divergence**: KL Divergence의 대칭 버전 (0~1 범위)
  - **Total Variation Distance**: 분포 간 최대 차이 (0~1 범위)
  - **Chi-square 검정**: 통계적 유의성 검정 (p-value 계산)
- **출력**: 비교 결과 딕셔너리 및 요약 리포트

## 📊 핵심 함수 흐름도

```text
analyze_pitching_patterns()  # 전체 파이프라인 메인 함수
  ↓
load_data_from_bigquery()     # 1. BigQuery에서 데이터 로드
  ↓
define_at_bat_cases()         # 2. 타석 케이스 정의 (case_id 생성)
  ↓
filter_out_cases() / filter_reach_cases()  # 3. 케이스 분류 및 필터링
  ↓
prepare_timestamps()          # 4. 타임스탬프 준비
  ↓
clean_dataframe()             # 5. 데이터 정리 및 PM4Py 포맷 변환
  ↓
create_event_log()            # 6. DataFrame → PM4Py EventLog 변환
  ↓
calculate_transition_probabilities()  # 7. 전이 확률 계산
  ↓
visualize_transition_graph_pyvis()    # 8. 인터랙티브 그래프 시각화
  ↓
create_process_model()        # 9. 프로세스 모델 생성 (선택사항)
```

**비교 분석 흐름**:

```text
analyze_pitching_patterns(case_type='out')   # 아웃 케이스 분석
analyze_pitching_patterns(case_type='reach') # 출루 케이스 분석
  ↓
compare_transition_probabilities()            # 두 케이스 비교
  ↓
print_comparison_summary()                    # 결과 요약 출력
```

## 🎯 분석 결과로 얻을 수 있는 인사이트

- 어떤 투구 타입 전환이 아웃을 유도하는가?
- 어떤 투구 타입 전환이 출루를 허용하는가?
- 아웃과 출루 케이스 간 투구 패턴 차이는 통계적으로 유의한가?
- 투구 전략 개선을 위한 방향성 제시

## 📦 설치

필요한 패키지:

```bash
pip install pandas numpy google-cloud-bigquery google-auth google-cloud-bigquery-storage pm4py matplotlib networkx pyvis db-dtypes
```

또는 `requirements.txt`가 있다면:

```bash
pip install -r requirements.txt
```

## 🚀 사용 방법

### 방법 1: 전체 파이프라인 실행 (아웃 + 출루 비교)

```python
from pitch_analysis_modules import analyze_pitching_patterns, compare_transition_probabilities, print_comparison_summary

# 아웃 케이스 분석
results_out = analyze_pitching_patterns(
    key_path="key.json",
    limit=None,  # 전체 데이터 사용
    min_prob=0.05,
    case_type='out'
)

# 출루 케이스 분석
results_reach = analyze_pitching_patterns(
    key_path="key.json",
    limit=None,
    min_prob=0.05,
    case_type='reach'
)

# 두 케이스 비교 및 통계적 검정
comparison = compare_transition_probabilities(
    results_out['transition_probs'],
    results_reach['transition_probs'],
    results_out['transition_counts'],
    results_reach['transition_counts']
)

print_comparison_summary(comparison)
```

### 방법 2: 단계별 실행

```python
from pitch_analysis_modules import (
    load_data_from_bigquery,
    define_at_bat_cases,
    filter_out_cases,
    filter_reach_cases,
    add_start_node,
    clean_dataframe,
    create_event_log,
    create_process_model,
    calculate_transition_probabilities,
    visualize_transition_graph_pyvis
)

# 1. 데이터 로드
df = load_data_from_bigquery(key_path="key.json", limit=1000)

# 2. 타석 케이스 정의
df_event = define_at_bat_cases(df)

# 3. 케이스 필터링 (아웃 또는 출루)
df_filtered, result_counts = filter_out_cases(df_event)  # 또는 filter_reach_cases()

# 4. 시작 노드 추가
df_with_start = add_start_node(df_filtered)

# 5. 데이터 정리
df_clean = clean_dataframe(df_with_start)

# 6. 이벤트 로그 생성
event_log = create_event_log(df_clean)

# 7. 전이 확률 계산
transition_probs, transition_counts = calculate_transition_probabilities(event_log)

# 8. 전이 확률 그래프 시각화
visualize_transition_graph_pyvis(transition_probs, transition_counts, min_prob=0.05)
```

## 📚 주요 함수 설명

### 데이터 로드
- `load_data_from_bigquery(key_path, limit=None)`: BigQuery에서 데이터 로드

### 타석 케이스 정의
- `define_at_bat_cases(df)`: 각 타석을 케이스로 정의
- `filter_out_cases(df_event)`: 아웃 케이스만 필터링
- `filter_reach_cases(df_event)`: 출루 케이스만 필터링
- `add_start_node(df_event)`: 각 타석 시작에 "In" 노드 추가

### 이벤트 로그 생성
- `clean_dataframe(df_event, exclude_pitch_types=None)`: DataFrame에서 None 값 제거 및 특정 투구 타입 제외
  - 기본적으로 FF(포심) 투구 타입 제외 (샘플 수가 매우 적어 통계적 신뢰도가 낮음)
- `create_event_log(df_clean)`: DataFrame을 PM4Py 이벤트 로그로 변환

### 프로세스 마이닝
- `create_process_model(event_log)`: Inductive Miner로 프로세스 모델 생성

### 전이 확률 분석
- `calculate_transition_probabilities(event_log)`: 전이 확률 계산
- `visualize_transition_graph_pyvis(...)`: 전이 확률 그래프 시각화 (Pyvis 사용)

### 비교 분석 및 통계적 검정
- `compare_transition_probabilities(...)`: 두 케이스 간 전이 확률 차이 분석
  - **MSE/MAE**: 평균 제곱/절대 오차
  - **KL Divergence**: 정보 이론적 차이
  - **JS Divergence**: KL의 대칭 버전
  - **Total Variation Distance**: 분포 간 최대 차이
  - **Chi-square 검정**: 통계적 유의성 검정
- `print_comparison_summary(...)`: 비교 결과 요약 출력

## 📈 분석 결과 형태

```python
{
    'df': DataFrame,                    # 원본 데이터
    'df_filtered': DataFrame,           # 필터링된 데이터
    'event_log': EventLog,             # PM4Py 이벤트 로그
    'net': PetriNet,                    # Petri Net
    'im': InitialMarking,               # 초기 마킹
    'fm': FinalMarking,                 # 최종 마킹
    'transition_probs': dict,           # 전이 확률
    'transition_counts': dict,          # 전이 카운트
    'case_type': str,                   # 'out' 또는 'reach'
    'result_counts': Series              # 케이스 결과 분포
}
```

## 📊 비교 분석 결과 형태

```python
{
    'transition_diffs': dict,           # 각 전이별 상세 차이
    'mse_by_node': dict,                # 노드별 MSE
    'mae_by_node': dict,                # 노드별 MAE
    'overall_mse': float,               # 전체 MSE
    'avg_kl_divergence': float,         # 평균 KL Divergence
    'avg_js_divergence': float,         # 평균 JS Divergence
    'avg_tv_distance': float,           # 평균 Total Variation Distance
    'chi_square_stats': dict,           # Chi-square 통계량
    'chi_square_pvalues': dict,         # Chi-square 검정 결과
    'total_nodes': int,                 # 총 노드 수
    'nodes_with_transitions': int       # 전이가 있는 노드 수
}
```

## 💡 예시

`inference.py` 파일을 참고하세요.

```bash
python inference.py
```

이 스크립트는 아웃 케이스와 출루 케이스를 모두 분석하고 비교 결과를 출력합니다.

## ⚠️ 주의사항

1. **키 파일**: BigQuery 인증을 위해 `key.json` 파일이 필요합니다.
2. **데이터 크기**: 전체 데이터를 사용하면 시간이 오래 걸릴 수 있습니다. 테스트 시에는 `limit` 파라미터를 사용하세요.
3. **시각화**: 시각화 결과는 HTML 파일로 저장되며 자동으로 브라우저에서 열립니다.
4. **투구 타입**: 분석에는 SI(싱커), SL(슬라이더), CH(체인지업)만 포함됩니다. FF(포심)는 전체 데이터에서 4개만 존재하여 통계적 신뢰도가 낮아 기본적으로 제외됩니다.

## 📦 모듈 구조

프로젝트는 기능별로 모듈화되어 있습니다:

```text
pitch_analysis_modules/
├── __init__.py                 # 패키지 초기화 및 모든 함수 export
├── utils.py                    # 유틸리티 함수 (한글 폰트 설정)
├── data_loader.py              # BigQuery 데이터 로드
├── case_definer.py             # 타석 케이스 정의 및 필터링
├── preprocessor.py             # 데이터 전처리 (타임스탬프, 정리)
├── event_log.py                # PM4Py 이벤트 로그 생성
├── process_mining.py           # 프로세스 마이닝 (Inductive Miner)
├── transition_analyzer.py      # 전이 확률 계산
├── visualizer.py               # Pyvis 시각화
├── comparison.py               # 비교 분석 및 통계적 검정
└── pipeline.py                 # 메인 파이프라인
```

### 모듈별 역할

- **utils.py**: 한글 폰트 설정 등 공통 유틸리티
- **data_loader.py**: BigQuery에서 투구 데이터 로드
- **case_definer.py**: 타석을 프로세스 케이스로 정의하고 아웃/출루 분류
- **preprocessor.py**: 타임스탬프 생성, 시작 노드 추가, 데이터 정리
- **event_log.py**: DataFrame을 PM4Py EventLog로 변환
- **process_mining.py**: Inductive Miner로 프로세스 모델 생성
- **transition_analyzer.py**: 투구 타입 간 전이 확률 계산
- **visualizer.py**: 인터랙티브 네트워크 그래프 시각화
- **comparison.py**: 아웃/출루 케이스 비교 및 통계적 검정
- **pipeline.py**: 전체 분석 파이프라인 실행

### 모듈 사용 방법

```python
# 방법 1: 패키지에서 직접 import (권장)
from pitch_analysis_modules import analyze_pitching_patterns

# 방법 2: 기존 방식도 지원 (pitch_analysis.py가 있다면)
# from pitch_analysis import analyze_pitching_patterns

# 방법 3: 특정 모듈만 사용
from pitch_analysis_modules.data_loader import load_data_from_bigquery
from pitch_analysis_modules.transition_analyzer import calculate_transition_probabilities

# 방법 4: 여러 모듈에서 함수 import
from pitch_analysis_modules import (
    load_data_from_bigquery,
    define_at_bat_cases,
    filter_out_cases,
    calculate_transition_probabilities,
    visualize_transition_graph_pyvis
)
```

## 📁 파일 구조

```text
.
├── pitch_analysis_modules/    # 모듈화된 분석 패키지
│   ├── __init__.py
│   ├── utils.py
│   ├── data_loader.py
│   ├── case_definer.py
│   ├── preprocessor.py
│   ├── event_log.py
│   ├── process_mining.py
│   ├── transition_analyzer.py
│   ├── visualizer.py
│   ├── comparison.py
│   └── pipeline.py
├── inference.py                # 추론 스크립트
├── README_PITCH_ANALYSIS.md    # 이 파일
├── requirements.txt            # 필요한 패키지 목록
└── key.json                    # BigQuery 인증 키 (직접 생성 필요)
```

## 🔍 메트릭 설명

### MSE (Mean Squared Error)
- 두 확률 분포 간 평균 제곱 오차
- 값이 작을수록 두 분포가 유사함

### KL Divergence (Kullback-Leibler Divergence)
- 정보 이론적 관점에서 두 확률 분포의 차이 측정
- 비대칭 메트릭 (P에서 Q로의 분산)
- 값이 작을수록 두 분포가 유사함

### JS Divergence (Jensen-Shannon Divergence)
- KL Divergence의 대칭 버전
- 범위: 0~1
- 값이 작을수록 두 분포가 유사함

### Total Variation Distance
- 두 확률 분포의 최대 차이 측정
- 범위: 0~1
- 값이 작을수록 두 분포가 유사함

### Chi-square 검정
- 통계적 유의성 검정
- 두 분포가 다른지 확인
- p-value < 0.05이면 통계적으로 유의한 차이 존재
