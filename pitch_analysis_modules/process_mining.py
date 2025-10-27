"""
프로세스 마이닝 모듈
PM4Py를 사용한 프로세스 모델 생성 함수들
"""

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter as pt_converter


def create_process_model(event_log):
    """
    Inductive Miner로 프로세스 모델 생성
    
    Args:
        event_log: PM4Py 이벤트 로그
    
    Returns:
        tuple: (net, im, fm) - Petri net, initial marking, final marking
    """
    if len(event_log) == 0:
        raise ValueError("이벤트 로그가 비어있습니다!")
    
    process_tree = inductive_miner.apply(event_log)
    net, im, fm = pt_converter.apply(process_tree)
    
    return net, im, fm

