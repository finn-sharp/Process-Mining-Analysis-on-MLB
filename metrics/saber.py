import pandas as pd

def p_per_pa(df_filtered):
    results = []

    c = 'all'
    pitches = len(df_filtered)
    pa = df_filtered['processID'].nunique()
    p_pa = pitches/pa
    
    results.append({
                "unit": c,
                "pitches": pitches,
                "PA": pa,
                "P/PA": p_pa
            })

    if ('cluster' in df_filtered.columns):
        for c, group in df_filtered.groupby("cluster"):
            pitches = len(group)                     # 총 투구 수(P)
            pa = group["processID"].nunique()        # 고유 타석 수(PA)
            p_pa = pitches / pa                      # P/PA

            results.append({
                "unit": c,
                "pitches": pitches,
                "PA": pa,
                "P/PA": p_pa
            })

    df_result = pd.DataFrame(results)
    p_pa_dict = {row["unit"]: row["P/PA"] for row in results}
    return p_pa_dict, df_result



def k_per_pa(df_filtered):
    df_end = df_filtered[df_filtered["pitch_type"] == "end"]

    results = []
    c = 'all'
    pa = df_end["processID"].nunique()
    strikeouts = (df_end["events"] == "strikeout").sum()
    kpa = strikeouts / pa

    results.append({
        "cluster": c,
        "PA": pa,
        "K": strikeouts,
        "K/PA": kpa
    })

    if ('cluster' in df_filtered.columns):
        for c, group in df_end.groupby("cluster"):
            pa = group["processID"].nunique()
            strikeouts = (group["events"] == "strikeout").sum()
            
            kpa = strikeouts / pa

            results.append({
                "cluster": c,
                "PA": pa,
                "K": strikeouts,
                "K/PA": kpa
            })

    df_result = pd.DataFrame(results)
    kpa_dict = {row["cluster"]: row["K/PA"] for row in results}
    return kpa_dict, df_result



def fip(df_filtered, constant=3.1):

    # 아웃으로 잡을 이벤트들
    IP_criteria = [
        "strikeout",
        "field_out",
        "force_out",
        "grounded_into_double_play",
        "double_play",
        "sac_fly",
        "sac_bunt",
    ]

    # cluster 컬럼 유무에 따라 그룹핑 대상 결정
    group_cols = "cluster" if "cluster" in df_filtered.columns else "pitcher"

    # 기본 카운트들
    cluster_stats = (
        df_filtered.groupby(group_cols, dropna=False)
        .agg(
            PA=("processID", "nunique"),
            K=("events", lambda x: (x == "strikeout").sum()),
            BB=("events", lambda x: (x == "walk").sum()),
            HBP=("events", lambda x: (x == "hit_by_pitch").sum()),
            HR=("events", lambda x: (x == "home_run").sum()),
            OUTS=("events", lambda x: x.isin(IP_criteria).sum()),
        )
    )

    # 클러스터별 IP = OUTS / 3
    cluster_stats["IP"] = cluster_stats["OUTS"] / 3.0

    # IP가 0인 경우 분모 0 방지
    cluster_stats = cluster_stats[cluster_stats["IP"] > 0].copy()

    # FIP 계산
    cluster_stats["FIP"] = (
        (13 * cluster_stats["HR"]
         + 3 * (cluster_stats["BB"] + cluster_stats["HBP"])
         - 2 * cluster_stats["K"]) / cluster_stats["IP"]
         + constant
    )

    return cluster_stats
