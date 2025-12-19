import pandas as pd

def clustered_dataframe(final_results, df_filtered):
    
    df_filtered = df_filtered.copy()
    cluster_map = final_results['cluster_map']
    mapping_to_cluster = {}

    for cluster_label, pid_list in cluster_map.items():
        for pid in pid_list:
            mapping_to_cluster[pid] = cluster_label

    df_filtered['cluster'] = df_filtered['case:concept:name'].map(mapping_to_cluster)
    return df_filtered