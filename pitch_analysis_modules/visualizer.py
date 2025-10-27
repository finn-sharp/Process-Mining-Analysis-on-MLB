"""
시각화 모듈
전이 확률 그래프를 시각화하는 함수들
"""

import networkx as nx
from collections import defaultdict
import os
import webbrowser

# Pyvis를 사용한 인터랙티브 시각화
try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False


def visualize_transition_graph_pyvis(transition_probs, transition_counts, min_prob=0.01, output_file="transition_graph.html", case_type='out'):
    """
    Pyvis를 사용한 인터랙티브 전이 확률 그래프 시각화
    
    Args:
        transition_probs: 전이 확률 딕셔너리
        transition_counts: 전이 카운트 딕셔너리
        min_prob: 최소 확률 임계값
        output_file: 출력 HTML 파일명
        case_type: 케이스 타입 ('out' 또는 'reach') - 색상 결정용
    """
    if not PYVIS_AVAILABLE:
        print("Pyvis가 설치되지 않았습니다. 'pip install pyvis'로 설치해주세요.")
        return
    
    # NetworkX 그래프 생성
    G = nx.DiGraph()
    
    # 시작 노드와 종료 노드 추가
    START_NODE = "Start"
    END_NODE = "Out"
    G.add_node(START_NODE)
    G.add_node(END_NODE)
    
    # 투구 타입 노드 추가
    all_activities = set()
    for from_activity in transition_probs.keys():
        all_activities.add(from_activity)
        for to_activity in transition_probs[from_activity].keys():
            all_activities.add(to_activity)
    
    for activity in all_activities:
        G.add_node(activity)
    
    # 시작 → 첫 투구 전이 추가
    # 각 투구 타입으로 시작하는 확률 계산
    start_counts = defaultdict(int)
    total_starts = 0
    for from_activity, to_dict in transition_probs.items():
        for count in transition_counts[from_activity].values():
            start_counts[from_activity] += count
            total_starts += count
    
    if total_starts > 0:
        for activity, count in start_counts.items():
            start_prob = count / total_starts
            G.add_edge(START_NODE, activity, weight=start_prob, label=f'{start_prob:.2f}')
    
    # 투구 간 전이 추가
    for from_activity, to_dict in transition_probs.items():
        for to_activity, prob in to_dict.items():
            if prob >= min_prob:
                G.add_edge(from_activity, to_activity, weight=prob, label=f'{prob:.2f}')
    
    # 각 투구 타입 → 종료 전이 추가
    # 마지막 투구가 각 타입일 확률 계산
    end_counts = defaultdict(int)
    total_ends = 0
    for from_activity, to_dict in transition_probs.items():
        for to_activity, count in transition_counts[from_activity].items():
            # to_activity가 최종 투구인 경우 계산
            end_counts[to_activity] += count
            total_ends += count
    
    if total_ends > 0:
        for activity, count in end_counts.items():
            end_prob = count / total_ends
            G.add_edge(activity, END_NODE, weight=end_prob, label=f'{end_prob:.2f}')
    
    # 케이스 타입에 따른 색상 설정
    if case_type == 'reach':
        # 출루 케이스: 파란색 계열
        node_color = "#4A90E2"  # 파란색
        start_color = "#E3F2FD"  # 밝은 파란색 (시작)
        end_color = "#1565C0"  # 진한 파란색 (종료)
        edge_color_base = "rgba(74, 144, 226, 0.8)"  # 파란색 엣지
    else:
        # 아웃 케이스: 빨간색 계열
        node_color = "#E74C3C"  # 빨간색
        start_color = "#FFEBEE"  # 밝은 빨간색 (시작)
        end_color = "#C62828"  # 진한 빨간색 (종료)
        edge_color_base = "rgba(231, 76, 60, 0.8)"  # 빨간색 엣지
    
    # Pyvis 네트워크 생성
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
    # 노드 추가 (케이스 타입에 따라 색상 설정)
    for node in G.nodes():
        if node == START_NODE:
            node_color_use = start_color
        elif node == END_NODE:
            node_color_use = end_color
        else:
            node_color_use = node_color
            
        net.add_node(node, 
                    label=node, 
                    color=node_color_use,
                    size=40,  # 노드 크기
                    shape="dot",  # 원형 노드
                    font={"size": 16, "face": "Arial", "color": "black"},
                    borderWidth=2,  # 테두리 두께
                    borderColor="#000000")  # 검은색 테두리
    
    # 모든 확률 값 가져오기 (두께 정규화용)
    all_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(all_weights) if all_weights else 1.0
    min_weight = min(all_weights) if all_weights else 0.0
    
    # 엣지 추가
    for u, v in G.edges():
        weight = G[u][v]['weight']
        label = G[u][v].get('label', f'{weight:.2f}')
        
        # 두께 정규화 (최소 1, 최대 10)
        if max_weight > min_weight:
            normalized_weight = 1 + (weight - min_weight) / (max_weight - min_weight) * 9
        else:
            normalized_weight = 5
        
        # 색상 (케이스 타입에 따라)
        if weight >= (max_weight + min_weight) / 2:
            color = edge_color_base
        else:
            # 투명도 조정
            color = edge_color_base.replace("0.8", "0.5")
        
        net.add_edge(u, v, 
                    label=label, 
                    width=normalized_weight,
                    color=color,
                    arrows="to",
                    arrowStrikethrough=False)
    
    # 네트워크 설정 (노드 간 간격 증가)
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -5000,
          "centralGravity": 0.1,
          "springLength": 400,
          "springConstant": 0.02,
          "damping": 0.15
        },
        "minVelocity": 0.75,
        "solver": "barnesHut"
      },
      "nodes": {
        "font": {
          "size": 16,
          "color": "black",
          "face": "Arial",
          "align": "center",
          "vadjust": 0,
          "multi": false
        },
        "shape": "dot",
        "margin": 10,
        "labelHighlightBold": true,
        "shadow": {
          "enabled": true
        }
      },
      "edges": {
        "font": {
          "size": 10,
          "color": "black",
          "align": "middle"
        },
        "labelHighlightBold": true
      }
    }
    """)
    
    # HTML 파일로 저장
    file_path = os.path.abspath(output_file)
    net.save_graph(output_file)
    
    print(f"\n인터랙티브 그래프가 다음 위치에 저장되었습니다:")
    print(f"  {file_path}")
    print(f"브라우저에서 열어보세요!")
    
    # 자동으로 브라우저 열기
    webbrowser.open(f'file://{file_path}')

