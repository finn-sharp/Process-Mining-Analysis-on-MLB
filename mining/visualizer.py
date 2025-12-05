import os
import pandas as pd
import webbrowser

import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network


def sankey_visualizer(data, length):

    # Visualization
    all_nodes = list(pd.unique(data[['Source', 'Target']].values.ravel('K')))
    node_map = {node: i for i, node in enumerate(all_nodes)}

    node_colors = []
    for node in all_nodes:
        if 'SI' in node:
            node_colors.append('rgba(40, 167, 69, 0.8)')  # Green for SI
        elif 'SL' in node:
            node_colors.append('rgba(0, 123, 255, 0.8)') # Blue for SL
        else:
            node_colors.append('rgba(108, 117, 125, 0.8)') # Gray for others

    flow_values = {'start': 1.0}

    source_indices = []
    target_indices = []
    link_values = []
    link_colors = []

    def get_link_color(target_node):
        if 'SI' in target_node:
            return 'rgba(40, 167, 69, 0.4)'  # Green for SI
        elif 'SL' in target_node:
            return 'rgba(0, 123, 255, 0.4)' # Blue for SL
        return 'rgba(108, 117, 125, 0.4)' # Gray for others

    for _, row in data.iterrows():
        source = row['Source']
        target = row['Target']
        variable = row['Variable']
        

        current_flow = flow_values.get(source, 0)    
        link_flow = current_flow * variable
        flow_values[target] = flow_values.get(target, 0) + link_flow
        
        source_indices.append(node_map[source])
        target_indices.append(node_map[target])
        link_values.append(link_flow)
        link_colors.append(get_link_color(target))

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors,
        ),

        link=dict(
            source=source_indices,
            target=target_indices,
            value=link_values,
            color=link_colors,
            hovertemplate='Source: %{source.label}<br>' +
                        'Target: %{target.label}<br>' +
                        'variable: %{value:.2%})'
        ))])

    fig.update_layout(
        title_text=f"Multi-Layer State Transition ({length})",
        font_size=20,
        width=800,
        height=600
    )

    fig.show()


def interactive_graph(df_preprocessing):

    flow_values = {'start' : 1.0}
    all_node = list(pd.unique(df_preprocessing[['Source', 'Target']].values.ravel("K")))
    


    # 그래프 생성
    G = nx.DiGraph()

    # Node  & Edge 생성
    for node in all_node : G.add_node(node)
    for from_act, to_act, val in zip(df_preprocessing['Source'], df_preprocessing['Target'], df_preprocessing['Variable']):        
        
        if df_preprocessing['Variable'].dtype == 'int64':
            label = f"{val}"
        else :
            label = f"{val:.2f}"

        G.add_edge(from_act, to_act, weight=val, label=f"{val:.2f}")


    # 네트워크 생성
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)

    # 네트워크 그래프 : Node Parameter
    node_dict = {}
    node_dict['size'] = 40
    node_dict['shape'] = "dot"
    node_dict['font'] = {"size": 16, "face": "Arial", "color": "black"}
    node_dict['borderWidth'] = 2
    node_dict['borderColor'] = "#000000"
    node_dict['color'] = "#4A90E2"

    for idx, node in enumerate(G.nodes()): 
        if idx == 0: 
            node_dict['color'] = "#E3F2FD"
            net.add_node(node, label=node, **node_dict)
        if idx == len(G.nodes)-1:
            node_dict['color'] = "#1565C0"
            net.add_node(node, label=node, **node_dict)
        
        node_dict['color'] = "#4A90E2"
        net.add_node(node, label=node, **node_dict)
        

    # 모든 확률 값 가져오기 (두께 정규화용)
    all_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(all_weights) if all_weights else 1.0
    min_weight = min(all_weights) if all_weights else 0.0    

    # 네트워크 그래프에 엣지 추가
    # edge_color = "rgba(74, 144, 226, 0.8)"  
    for u, v in G.edges():
        weight = G[u][v]['weight']
        label = G[u][v].get('label', f'{weight:.2f}')
        
        # 두께 정규화 (최소 1, 최대 10)
        if max_weight > min_weight:
            normalized_weight = 1 + (weight - min_weight) / (max_weight - min_weight) * 9
        else:
            normalized_weight = 5

        net.add_edge(u, v, 
                    label=label, 
                    # color=edge_color,
                    width=normalized_weight,
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
    output_file = 'test.html'
    file_path = os.path.abspath(output_file)
    net.save_graph(output_file)

    print(f"\n인터랙티브 그래프가 다음 위치에 저장되었습니다:")
    print(f"  {file_path}")
    print(f"브라우저에서 열어보세요!")

    # 자동으로 브라우저 열기
    webbrowser.open(f'file://{file_path}')

# import networkx as nx
# import matplotlib.pyplot as plt
# import pandas as pd
# import os
# import numpy as np
# # (참고: webbrowser와 pyvis.network는 더 이상 필요하지 않습니다.)

# def InteractiveGraph(df_preprocessing: pd.DataFrame):
#     """
#     Pandas DataFrame을 기반으로 NetworkX와 Matplotlib를 사용하여
#     투구 전이 확률 네트워크를 시각화합니다.
    
#     Args:
#         df_preprocessing (pd.DataFrame): 'Source', 'Target', 'Variable'(확률)을 
#                                          포함하는 전이 확률 데이터프레임.
#     """
#     # 1. 그래프 객체 생성 및 데이터 로드
#     # 방향성이 있는 그래프 (투구 순서는 방향성이 있음)
#     G = nx.DiGraph()

#     # 모든 노드 추출
#     all_node = list(pd.unique(df_preprocessing[['Source', 'Target']].values.ravel("K")))

#     # 노드 추가
#     for node in all_node: 
#         G.add_node(node)

#     # 엣지 추가 (가중치로 확률 값 사용)
#     for from_act, to_act, val in zip(df_preprocessing['Source'], df_preprocessing['Target'], df_preprocessing['Variable']):
#         # 확률 값이 문자열일 경우 숫자형으로 변환 시도
#         try:
#             weight_val = float(val)
#         except (ValueError, TypeError):
#             weight_val = 0.0 # 변환 실패 시 기본값 설정
            
#         G.add_edge(from_act, to_act, weight=weight_val) 


#     # 2. 레이아웃 결정 및 노드/엣지 스타일 설정
    
#     # 2-1. 레이아웃: k 값 증가로 노드 간 간격을 넓혀 겹침을 최소화 (k=0.8)
#     # seed=42 고정으로 실행할 때마다 같은 위치에 그려지도록 설정
#     pos = nx.spring_layout(G, seed=42, k=0.8, iterations=50) 
    
#     # 2-2. 엣지 두께 정규화: (pyvis 코드의 논리를 Matplotlib에 적용)
#     all_weights = [G[u][v]['weight'] for u, v in G.edges()]
#     max_weight = max(all_weights) if all_weights else 1.0
#     min_weight = min(all_weights) if all_weights else 0.0
    
#     # 엣지 두께를 최소 0.5, 최대 5 범위로 정규화
#     if max_weight > min_weight:
#         edge_widths = [0.5 + (weight - min_weight) / (max_weight - min_weight) * 4.5 for weight in all_weights]
#     else:
#         edge_widths = [2.5] * len(all_weights)

#     # 2-3. 노드 색상 지정 (시작/끝 노드 색상 분리)
#     COLOR_START = "#E3F2FD"   # 연한 파랑
#     COLOR_END = "#1565C0"     # 진한 파랑
#     COLOR_DEFAULT = "#4A90E2" # 기본 파랑
    
#     node_colors = []
#     # 노드 리스트는 G.nodes() 순서를 따름
    
#     # 시작 노드와 끝 노드를 구분하기 위해 노드 리스트를 활용합니다.
#     try:
#         start_node = all_node[0]
#         end_node = all_node[-1]
#     except IndexError:
#         start_node, end_node = None, None

#     for node in G.nodes():
#         if node == start_node:
#             node_colors.append(COLOR_START)
#         elif node == end_node:
#             node_colors.append(COLOR_END)
#         else:
#             node_colors.append(COLOR_DEFAULT)

#     # 3. Matplotlib 플롯 설정 및 그리기
#     plt.figure(figsize=(15, 10))
    
#     # 3-1. 엣지 그리기 (connectionstyle 옵션으로 간선을 곡선 처리)
#     nx.draw_networkx_edges(
#         G, pos,
#         width=edge_widths,
#         edge_color="#4A90E2",
#         alpha=0.6,
#         arrowsize=20,
#         arrowstyle='->',
#         connectionstyle='arc3, rad=0.1' # <-- 간선을 휘어지게 만듭니다.
#     )

#     # 3-2. 노드 그리기
#     nx.draw_networkx_nodes(
#         G, pos,
#         node_size=2000,
#         node_color=node_colors,
#         edgecolors='black', # 테두리 색상
#         linewidths=1.5
#     )

#     # 3-3. 노드 라벨 그리기 (텍스트)
#     nx.draw_networkx_labels(
#         G, pos,
#         font_size=12,
#         font_color="black",
#         font_weight="bold"
#     )

#     # 3-4. 엣지 라벨 그리기 (확률/가중치 값)
#     edge_labels = {
#         (u, v): f"{G[u][v]['weight']:.2f}"
#         for u, v in G.edges()
#     }
#     # 곡선 엣지에서도 라벨이 엣지 근처에 표시되도록 설정
#     nx.draw_networkx_edge_labels(
#         G, pos, 
#         edge_labels=edge_labels,
#         font_size=10, 
#         font_color='black',
#         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'),
#         rotate=False # 텍스트가 회전하지 않도록 설정
#     )

#     # 4. 최종 출력 설정 및 저장
#     plt.title("Pitch Type Transition Probability Network (Matplotlib)", fontsize=16)
#     plt.axis('off') # 축(x, y 눈금) 제거
#     plt.tight_layout() # 여백 조정

#     # 파일 저장 (PNG 파일로 저장)
#     output_file_png = 'pitch_network_curved.png'
#     plt.savefig(output_file_png)
#     print(f"\n정적 그래프가 다음 위치에 PNG 파일로 저장되었습니다: {os.path.abspath(output_file_png)}")
    
#     # Jupyter Notebook에 바로 출력
#     plt.show()