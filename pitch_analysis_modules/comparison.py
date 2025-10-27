"""
비교 분석 모듈
아웃 케이스와 출루 케이스 간 전이 확률 차이 분석 및 통계적 검정 함수들
"""

from collections import defaultdict
import numpy as np


def compare_transition_probabilities(transition_probs_out, transition_probs_reach, transition_counts_out=None, transition_counts_reach=None):
    """
    아웃 케이스와 출루 케이스 간 전이 확률 차이 분석 및 Loss 계산
    
    Args:
        transition_probs_out: 아웃 케이스의 전이 확률 딕셔너리
        transition_probs_reach: 출루 케이스의 전이 확률 딕셔너리
        transition_counts_out: 아웃 케이스의 전이 카운트 (선택사항)
        transition_counts_reach: 출루 케이스의 전이 카운트 (선택사항)
    
    Returns:
        dict: 비교 결과 및 loss 값들
    """
    # 모든 노드 수집
    all_nodes = set(transition_probs_out.keys()) | set(transition_probs_reach.keys())
    
    # 전이 확률 차이 계산
    transition_diffs = defaultdict(dict)
    transition_diffs_mse = defaultdict(float)  # 노드별 MSE
    transition_diffs_mae = defaultdict(float)  # 노드별 MAE
    
    total_diff = 0
    total_nodes_with_transitions = 0
    
    for node in all_nodes:
        out_probs = transition_probs_out.get(node, {})
        reach_probs = transition_probs_reach.get(node, {})
        
        # 모든 타겟 노드 수집
        all_targets = set(out_probs.keys()) | set(reach_probs.keys())
        
        node_mse = 0
        node_mae = 0
        node_transition_count = 0
        
        for target in all_targets:
            out_prob = out_probs.get(target, 0.0)
            reach_prob = reach_probs.get(target, 0.0)
            diff = reach_prob - out_prob
            
            transition_diffs[node][target] = {
                'out': out_prob,
                'reach': reach_prob,
                'diff': diff,
                'abs_diff': abs(diff)
            }
            
            # MSE 및 MAE 계산
            node_mse += diff ** 2
            node_mae += abs(diff)
            node_transition_count += 1
        
        if node_transition_count > 0:
            transition_diffs_mse[node] = node_mse / node_transition_count
            transition_diffs_mae[node] = node_mae / node_transition_count
            total_diff += node_mse
            total_nodes_with_transitions += 1
    
    # 전체 MSE (전체 전이 확률 차이의 평균 제곱 오차)
    overall_mse = total_diff / total_nodes_with_transitions if total_nodes_with_transitions > 0 else 0
    
    # KL Divergence 계산 (아웃을 기준으로 출루의 분포 차이)
    kl_divergence = 0
    kl_nodes = 0
    for node in all_nodes:
        out_probs = transition_probs_out.get(node, {})
        reach_probs = transition_probs_reach.get(node, {})
        
        if not out_probs or not reach_probs:
            continue
        
        # 모든 타겟 노드 수집
        all_targets = set(out_probs.keys()) | set(reach_probs.keys())
        
        node_kl = 0
        has_valid_kl = False
        
        for target in all_targets:
            out_prob = out_probs.get(target, 1e-10)  # 0을 피하기 위해 작은 값 추가
            reach_prob = reach_probs.get(target, 1e-10)
            
            if out_prob > 1e-10:  # out_prob가 0이 아닐 때만 계산
                node_kl += reach_prob * np.log(reach_prob / out_prob)
                has_valid_kl = True
        
        if has_valid_kl:
            kl_divergence += node_kl
            kl_nodes += 1
    
    avg_kl_divergence = kl_divergence / kl_nodes if kl_nodes > 0 else 0
    
    # JS Divergence 계산 (Jensen-Shannon Divergence - 대칭 버전)
    js_divergence = 0
    js_nodes = 0
    for node in all_nodes:
        out_probs = transition_probs_out.get(node, {})
        reach_probs = transition_probs_reach.get(node, {})
        
        if not out_probs or not reach_probs:
            continue
        
        all_targets = set(out_probs.keys()) | set(reach_probs.keys())
        
        node_js = 0
        has_valid_js = False
        
        for target in all_targets:
            out_prob = out_probs.get(target, 1e-10)
            reach_prob = reach_probs.get(target, 1e-10)
            m_prob = (out_prob + reach_prob) / 2  # 평균 분포
            
            if m_prob > 1e-10:
                node_js += (out_prob * np.log(out_prob / m_prob) + 
                           reach_prob * np.log(reach_prob / m_prob)) / 2
                has_valid_js = True
        
        if has_valid_js:
            js_divergence += node_js
            js_nodes += 1
    
    avg_js_divergence = js_divergence / js_nodes if js_nodes > 0 else 0
    
    # Total Variation Distance 계산
    tv_distance = 0
    tv_nodes = 0
    for node in all_nodes:
        out_probs = transition_probs_out.get(node, {})
        reach_probs = transition_probs_reach.get(node, {})
        
        if not out_probs or not reach_probs:
            continue
        
        all_targets = set(out_probs.keys()) | set(reach_probs.keys())
        
        node_tv = 0
        for target in all_targets:
            out_prob = out_probs.get(target, 0.0)
            reach_prob = reach_probs.get(target, 0.0)
            node_tv += abs(out_prob - reach_prob)
        
        tv_distance += node_tv / 2  # Total Variation Distance는 절대값의 합을 2로 나눔
        tv_nodes += 1
    
    avg_tv_distance = tv_distance / tv_nodes if tv_nodes > 0 else 0
    
    # Chi-square 검정 (카이제곱 검정) - 통계적 유의성 검정
    chi_square_stats = {}
    chi_square_pvalues = {}
    
    if transition_counts_out and transition_counts_reach:
        for node in all_nodes:
            out_counts = transition_counts_out.get(node, {})
            reach_counts = transition_counts_reach.get(node, {})
            
            if not out_counts or not reach_counts:
                continue
            
            all_targets = set(out_counts.keys()) | set(reach_counts.keys())
            
            # 관찰값과 기대값 계산
            observed = []
            expected = []
            total_out = sum(out_counts.values())
            total_reach = sum(reach_counts.values())
            total_combined = total_out + total_reach
            
            if total_combined == 0:
                continue
            
            for target in all_targets:
                out_count = out_counts.get(target, 0)
                reach_count = reach_counts.get(target, 0)
                
                if out_count == 0 and reach_count == 0:
                    continue
                
                observed.extend([out_count, reach_count])
                
                # 기대값 계산 (전체 비율에 따른 기대값)
                expected_out = (out_count + reach_count) * (total_out / total_combined) if total_combined > 0 else 0
                expected_reach = (out_count + reach_count) * (total_reach / total_combined) if total_combined > 0 else 0
                expected.extend([expected_out, expected_reach])
            
            # Chi-square 통계량 계산
            if len(observed) > 0 and any(e > 0 for e in expected):
                chi_square = sum((o - e) ** 2 / e if e > 0 else 0 
                                for o, e in zip(observed, expected))
                
                # 자유도 (카테고리 수 - 1)
                df = len(observed) // 2 - 1
                
                if df > 0:
                    # p-value 계산 (근사치, scipy가 없을 경우)
                    # 정확한 p-value는 scipy.stats.chi2 사용 권장
                    chi_square_stats[node] = chi_square
                    # p-value는 간단한 근사: chi-square 값이 크면 p-value가 작음
                    # 정확한 계산을 위해서는 scipy.stats.chi2.sf(chi_square, df) 사용 권장
                    chi_square_pvalues[node] = {
                        'chi_square': chi_square,
                        'df': df,
                        'significant': chi_square > 3.84  # df=1일 때 0.05 유의수준
                    }
    
    # 결과 요약
    result = {
        'transition_diffs': dict(transition_diffs),
        'mse_by_node': dict(transition_diffs_mse),
        'mae_by_node': dict(transition_diffs_mae),
        'overall_mse': overall_mse,
        'avg_kl_divergence': avg_kl_divergence,
        'avg_js_divergence': avg_js_divergence,
        'avg_tv_distance': avg_tv_distance,
        'chi_square_stats': chi_square_stats,
        'chi_square_pvalues': chi_square_pvalues,
        'total_nodes': len(all_nodes),
        'nodes_with_transitions': total_nodes_with_transitions
    }
    
    return result


def print_comparison_summary(comparison_result, num_out_cases=None, num_reach_cases=None):
    """
    비교 결과 요약 출력
    
    Args:
        comparison_result: compare_transition_probabilities의 결과
        num_out_cases: 아웃 케이스 데이터 개수
        num_reach_cases: 출루 케이스 데이터 개수
    """
    print("\n" + "="*60)
    print("전이 확률 비교 분석 결과")
    print("="*60)
    
    # 데이터 개수 정보
    if num_out_cases is not None and num_reach_cases is not None:
        print(f"\n[데이터 개수]")
        print(f"  - 아웃 케이스: {num_out_cases:,}개")
        print(f"  - 출루 케이스: {num_reach_cases:,}개")
        print(f"  - 전체 케이스: {num_out_cases + num_reach_cases:,}개")
    
    print(f"\n[1] 전체 통계:")
    print(f"  - 총 노드 수: {comparison_result['total_nodes']}")
    print(f"  - 전이가 있는 노드 수: {comparison_result['nodes_with_transitions']}")
    print(f"  - 전체 MSE (Mean Squared Error): {comparison_result['overall_mse']:.6f}")
    print(f"  - 평균 KL Divergence: {comparison_result['avg_kl_divergence']:.6f}")
    print(f"  - 평균 JS Divergence: {comparison_result['avg_js_divergence']:.6f}")
    print(f"  - 평균 Total Variation Distance: {comparison_result['avg_tv_distance']:.6f}")
    
    # Chi-square 검정 결과 요약
    if comparison_result['chi_square_pvalues']:
        significant_nodes = [node for node, stats in comparison_result['chi_square_pvalues'].items() 
                           if stats['significant']]
        print(f"\n[2] 통계적 유의성 검정 (Chi-square):")
        print(f"  - 검정 수행된 노드 수: {len(comparison_result['chi_square_pvalues'])}")
        print(f"  - 유의미한 차이가 있는 노드 수: {len(significant_nodes)} ({len(significant_nodes)/len(comparison_result['chi_square_pvalues'])*100:.1f}%)")
        
        if significant_nodes:
            print(f"\n  [2-1] 유의미한 차이가 있는 노드 (상위 10개):")
            sig_nodes_sorted = sorted(
                [(node, comparison_result['chi_square_pvalues'][node]) for node in significant_nodes],
                key=lambda x: x[1]['chi_square'],
                reverse=True
            )
            for i, (node, stats) in enumerate(sig_nodes_sorted[:10], 1):
                print(f"    {i}. {node}: chi-square={stats['chi_square']:.4f}, df={stats['df']}, significant=True")
        
        print(f"\n  [2-2] 유의미한 차이가 없는 노드 (하위 10개):")
        non_sig_nodes = [node for node, stats in comparison_result['chi_square_pvalues'].items() 
                        if not stats['significant']]
        if non_sig_nodes:
            non_sig_sorted = sorted(
                [(node, comparison_result['chi_square_pvalues'][node]) for node in non_sig_nodes],
                key=lambda x: x[1]['chi_square'],
                reverse=False
            )
            for i, (node, stats) in enumerate(non_sig_sorted[:10], 1):
                print(f"    {i}. {node}: chi-square={stats['chi_square']:.4f}, df={stats['df']}, significant=False")
        
        print(f"\n  [2-3] Chi-square 통계량 상위 10개:")
        sorted_chi2 = sorted(comparison_result['chi_square_pvalues'].items(), 
                            key=lambda x: x[1]['chi_square'], reverse=True)
        for i, (node, stats) in enumerate(sorted_chi2[:10], 1):
            sig_mark = "[SIGNIFICANT]" if stats['significant'] else "[NOT SIGNIFICANT]"
            print(f"    {i}. {node}: chi-square={stats['chi_square']:.4f}, df={stats['df']} {sig_mark}")
    
    print(f"\n[3] 노드별 MSE (상위 10개):")
    sorted_mse = sorted(comparison_result['mse_by_node'].items(), 
                       key=lambda x: x[1], reverse=True)
    for node, mse in sorted_mse[:10]:
        print(f"  - {node}: {mse:.6f}")
    
    print(f"\n[4] 노드별 MAE (상위 10개):")
    sorted_mae = sorted(comparison_result['mae_by_node'].items(), 
                       key=lambda x: x[1], reverse=True)
    for node, mae in sorted_mae[:10]:
        print(f"  - {node}: {mae:.6f}")
    
    print(f"\n[5] 큰 차이가 있는 전이 (상위 10개):")
    all_diffs = []
    for node, targets in comparison_result['transition_diffs'].items():
        for target, data in targets.items():
            all_diffs.append({
                'from': node,
                'to': target,
                'out': data['out'],
                'reach': data['reach'],
                'diff': data['diff'],
                'abs_diff': data['abs_diff']
            })
    
    sorted_diffs = sorted(all_diffs, key=lambda x: x['abs_diff'], reverse=True)
    for i, diff in enumerate(sorted_diffs[:10], 1):
        print(f"  {i}. {diff['from']} -> {diff['to']}:")
        print(f"     Out: {diff['out']:.4f}, Reach: {diff['reach']:.4f}, Diff: {diff['diff']:+.4f}")

