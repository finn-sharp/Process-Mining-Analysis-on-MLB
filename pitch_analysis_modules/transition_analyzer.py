"""
전이 확률 분석 모듈
투구 타입 간 전이 확률을 계산하는 함수들
"""

from collections import defaultdict


def calculate_transition_probabilities(event_log):
    """
    전이 확률 계산
    
    Args:
        event_log: PM4Py 이벤트 로그
    
    Returns:
        dict: 전이 확률 딕셔너리 {from_activity: {to_activity: probability}}
    """
    transition_counts = defaultdict(lambda: defaultdict(int))
    
    for case in event_log:
        activities = [event['concept:name'] for event in case]
        for i in range(len(activities) - 1):
            from_activity = activities[i]
            to_activity = activities[i + 1]
            transition_counts[from_activity][to_activity] += 1
    
    # 전이 확률 계산
    transition_probs = {}
    for from_activity, to_dict in transition_counts.items():
        total = sum(to_dict.values())
        transition_probs[from_activity] = {
            to_activity: count / total 
            for to_activity, count in to_dict.items()
        }
    
    return transition_probs, transition_counts

