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

