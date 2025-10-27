"""
유틸리티 함수 모듈
한글 폰트 설정 등 공통 유틸리티 함수
"""

import matplotlib.pyplot as plt
import platform


def setup_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/AppleGothic.ttf',
            '/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        ]
        font_name = 'AppleGothic'
    elif system == 'Windows':
        font_name = 'Malgun Gothic'
    else:  # Linux
        font_name = 'NanumGothic'
    
    try:
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
        return font_name
    except:
        # 폰트 설정 실패 시 기본 폰트 사용
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        return 'DejaVu Sans'


# 모듈 로드 시 한글 폰트 설정
KOREAN_FONT = setup_korean_font()

