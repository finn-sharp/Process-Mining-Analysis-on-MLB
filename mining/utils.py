import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import re

def extract_stage_number(state):
    """상태(state) 문자열에서 단계 번호를 추출합니다."""
    if state == 'start': 
        return -1 
    if state == 'end': 
        return 999 
    match = re.search(r'\_(\d+)', state)
    if match: 
        return int(match.group(1))
    return 0



def load_data_from_bigquery(key_path="key.json", limit=None):
    """
    BigQuery에서 Josh Hader의 투구 데이터 로드
    
    Args:
        key_path: 서비스 계정 키 파일 경로
        limit: 데이터 제한 (None이면 전체)
    
    Returns:
        DataFrame: 투구 데이터
    """
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    
    query = """
    SELECT
      game_date,
      pitcher,
      batter,
      stand,
      p_throws,
      outs_when_up,
      on_1b, on_2b, on_3b,
      balls, strikes,
      type,
      hit_location, launch_speed, launch_angle, babip_value,
      pitch_type,
      release_speed,
      release_pos_x,
      release_pos_z,
      release_pos_y,
      plate_x,
      plate_z,
      description,
      events
    FROM
      `helpful-kit-473614-g8.Dugtrio_1.josh_hader_pitch_by_pitch_5yr`
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    df = client.query(query).to_dataframe()
    df['game_date'] = pd.to_datetime(df['game_date'])
    
    return df

