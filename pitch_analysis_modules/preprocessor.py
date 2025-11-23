"""
데이터 전처리 모듈
타임스탬프 생성, 시작 노드 추가, 데이터 정리 함수들
"""

import pandas as pd
from datetime import timedelta


def deleteNullPitchType(df_event):
    """
    pitch_type이 'nan'(문자열) 또는 None인 행 제거
    """
    p_index = set(df_event[df_event['pitch_type'].isna()]['processID'])
    condition = ~df_event['processID'].isin(p_index)
    
    df_event = df_event[condition]
    df_event = df_event.sort_values(by=['processID'], ascending=True).reset_index(drop=True)
    return df_event

def checkNullPitchType(df_event):
    """
    pitch_type이 'nan'(문자열) 또는 None인 행 확인
    """
    p_index = set(df_event[df_event['pitch_type'].isna()]['processID'])
    df_check_null = df_event[df_event['processID'].isin(p_index)]

    return df_check_null




# 시작 노드 끝 노드 설정하는 걸로 변경하기 (Labeling으로 도식화)
def addNodeAndTimestamp(df_event, start_name, end_name):
 
    # [1] 행 제거(PitchType is Null)
    acept_data = deleteNullPitchType(df_event)

    # [2] Time Stamp 추가
    acept_data['time:timestamp'] = acept_data.apply(lambda row: row['game_date'] + timedelta(seconds=row['pitchOrder']),axis=1)

    # [3] 시작/종료 노드 추가
    start_name = start_name
    end_name = end_name


    add_node_list = []
    for process in acept_data['processID'].unique():
        case_df = acept_data[acept_data['processID'] == process]
        if len(case_df) > 0:
            # 첫 번째 행을 복사하여 "In" 노드 생성
            first_row = case_df.iloc[-1].copy()
            first_row['pitch_type'] = start_name
            first_row['pitchOrder'] = -1  # 시작 노드는 -1로 설정
            first_row['time:timestamp'] = first_row['time:timestamp'] - timedelta(seconds=1)
        
            last_row = case_df.iloc[0].copy()
            last_row['pitch_type'] = end_name
            last_row['pitchOrder'] = len(case_df)
            last_row['time:timestamp'] = last_row['time:timestamp'] + timedelta(seconds=1)
            
            add_node_list.extend([first_row, last_row])

    # [4] 결과 저장
    node_df = pd.DataFrame(add_node_list)
    acept_data = pd.concat([acept_data, node_df], ignore_index=True)
    acept_data = acept_data.sort_values(by=['processID', 'pitchOrder'], ascending=[True, False]).reset_index(drop=True)

    return acept_data


#######
#######
#######
####### pm4py에서 제공하는 패턴으로 변경해야할 부분
#######
#######
def attach_case_result_to_pitch_type(df_event): 
    """
    각 투구의 pitch_type에 해당 타석의 최종 결과(out / reach / other)를 붙임
    예: SL → SL_out, SI → SI_reach
    """
    # case_id별 마지막 이벤트 기반으로 결과 분류
    case_results = df_event.groupby('case_id')['events'].apply(
        lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else None
    )

    def classify_result(event):
        if event in ['strikeout', 'out', 'field_out', 'force_out', 'double_play', 'triple_play',
                     'strikeout_double_play', 'sac_fly', 'sac_bunt']:
            return 'out'
        elif event in ['single', 'double', 'triple', 'home_run', 'walk', 'hit_by_pitch',
                       'catcher_interf', 'field_error', 'fielders_choice']:
            return 'reach'
        else:
            return 'other'

    case_results = case_results.apply(classify_result)

    # 원본 DataFrame에 결과 병합
    df_event = df_event.merge(case_results.rename('case_result'), on='case_id', how='left')

    # pitch_type + 결과 결합
    df_event['pitch_type'] = df_event['pitch_type'] + '_' + df_event['case_result']

    return df_event


def clean_dataframe(df_event):
    """
    DataFrame에서 None 값 완전히 제거
    
    Args:
        df_event: 원본 DataFrame (이미 FF가 제외된 상태)
    
    Returns:
        DataFrame: 정리된 DataFrame
    """
    # pm4py 포맷으로 컬럼 이름 맞추기
   # 1. description 그룹화
    df_event = map_description_to_category(df_event)

    # 2. pitch_type + description_group 조합으로 concept:name 생성
    df_event['concept:name'] = df_event['pitch_type'].astype(str) + " - " + df_event['description_group']

    # 3. pm4py용 컬럼 이름 통일
    df_clean = df_event.rename(columns={
        'case_id': 'case:concept:name'
    })
    
    # 필요한 컬럼만 선택
    df_clean = df_clean[['case:concept:name', 'concept:name', 'time:timestamp']].copy()
    
    # None, 빈 문자열, NaN 모두 제거
    df_clean = df_clean.dropna(subset=['concept:name'])
    df_clean = df_clean[df_clean['concept:name'].notna()]
    df_clean = df_clean[df_clean['concept:name'] != '']
    df_clean = df_clean[df_clean['concept:name'].astype(str) != 'nan']
    df_clean['concept:name'] = df_clean['concept:name'].astype(str)
    
    return df_clean

def map_description_to_category(df):
    """description을 5개 범주로 그룹화"""
    mapping = {
        'hit_into_play': '공을 침',
        'ball': '볼',
        'blocked_ball': '볼',
        'called_strike': '스트라이크',
        'swinging_strike': '스트라이크',
        'swinging_strike_blocked': '스트라이크',
        'foul_tip': '스트라이크',
        'foul_bunt': '스트라이크',
        'missed_bunt': '스트라이크',
        'foul': '파울',
        'hit_by_pitch': '데드볼'
    }
    df['description_group'] = df['description'].map(mapping).fillna('result')
    return df

