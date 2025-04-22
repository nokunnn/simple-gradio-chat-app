def get_csv_insights_for_lp_planning(csv_analysis):
    """LP企画設計のためのCSV洞察をフォーマットする"""
    if not csv_analysis or not csv_analysis.get("success", False):
        return None
    
    # LP企画設計で使用するCSVデータの洞察情報をまとめる
    analysis_result = csv_analysis["analysis_result"]
    file_info = analysis_result["file_info"]
    stats = analysis_result["statistics"]
    
    # 新しい分析結果を活用
    job_type_analysis = analysis_result.get("job_type_analysis", {})
    
    # データの特徴を自然な文章で表現するための変数
    target_insights = []
    demographic_insights = []
    preference_insights = []
    behavioral_insights = []
    
    # 1. ターゲット全体の概要 (行数 = 回答者/顧客数)
    respondents_count = file_info["num_rows"]
    target_insights.append(f"アンケートデータには{respondents_count}人の回答が含まれており、十分な母集団サイズでターゲットの傾向を分析できます。")
    
    # 2. 主要な属性情報の抽出 (カテゴリ変数から)
    if stats["categorical"]:
        # 最初の2つのカテゴリ列は通常、重要な属性情報を含む（職種、年齢層、性別など）
        primary_categories = list(stats["categorical"].items())[:2]
        
        for col_name, col_stats in primary_categories:
            if "error" not in col_stats:
                # 上位2つのカテゴリを抽出
                top_categories = sorted(col_stats.items(), key=lambda x: x[1]['percentage'], reverse=True)[:2]
                if top_categories:
                    cat1, stats1 = top_categories[0]
                    percentage1 = stats1['percentage']
                    
                    if len(top_categories) > 1:
                        cat2, stats2 = top_categories[1]
                        percentage2 = stats2['percentage']
                        demographic_insights.append(f"{col_name}は「{cat1}」が{percentage1}%と最も多く、次いで「{cat2}」が{percentage2}%を占めています。")
                    else:
                        demographic_insights.append(f"{col_name}は「{cat1}」が{percentage1}%と大半を占めています。")
    
    # 3. 数値データからの洞察
    if stats["numeric"]:
        for col_name, col_stats in stats["numeric"].items():
            if "error" not in col_stats:
                # 平均値と分布の広がりから洞察を生成
                mean = col_stats["mean"]
                spread = col_stats["max"] - col_stats["min"]
                std = col_stats.get("std", 0)
                
                if "年齢" in col_name or "age" in col_name.lower():
                    behavioral_insights.append(f"回答者の平均{col_name}は{mean}で、{col_stats['min']}歳から{col_stats['max']}歳まで分布しています。")
                elif "収入" in col_name or "所得" in col_name or "income" in col_name.lower():
                    behavioral_insights.append(f"ターゲットの平均{col_name}は{mean}万円で、最小{col_stats['min']}万円から最大{col_stats['max']}万円まで分布しています。")
                elif "満足度" in col_name or "評価" in col_name or "score" in col_name.lower() or "rating" in col_name.lower():
                    if col_stats["max"] <= 5:  # 5点満点の評価と仮定
                        if mean > 3.5:
                            preference_insights.append(f"{col_name}の平均は{mean}点と高く、概ね好評価です。")
                        else:
                            preference_insights.append(f"{col_name}の平均は{mean}点と中程度で、改善の余地があります。")
    
    # 4. 職種ごとの選択傾向からの洞察を追加
    job_type_insights = []
    
    # 最も特徴的な職種のみ（最大3つ）をハイライト
    highlighted_job_types = list(job_type_analysis.keys())[:3]
    
    for job_type in highlighted_job_types:
        if job_type in job_type_analysis:
            job_type_insights.append(job_type_analysis[job_type])
    
    # 5. すべての洞察を組み合わせて自然な文章を生成
    summary_paragraphs = []
    
    # ターゲット全体の概要
    if target_insights:
        target_summary = " ".join(target_insights)
        summary_paragraphs.append(target_summary)
    
    # 属性の特徴
    if demographic_insights:
        demo_summary = "ターゲットの属性としては、" + " ".join(demographic_insights)
        summary_paragraphs.append(demo_summary)
    
    # 職種ごとの選択傾向
    if job_type_insights:
        job_summary = "アンケートデータから得られた職種ごとの特徴的な傾向として、" + " ".join(job_type_insights)
        summary_paragraphs.append(job_summary)
    
    # 行動や嗜好の特徴
    combined_insights = preference_insights + behavioral_insights
    if combined_insights:
        behavior_summary = "ターゲットの行動特性として、" + " ".join(combined_insights)
        summary_paragraphs.append(behavior_summary)
    
    # LP企画への示唆
    implications = "これらの職種別特性を踏まえると、各職種が持つ課題や関心事に焦点を当て、それぞれが重視する観点（効率性、コスト、品質など）に対応した価値提案をLPで訴求することが効果的です。特に主要な職種である" + "、".join(highlighted_job_types[:2]) + "向けのメッセージを優先的に配置することで、コンバージョン率を高められる可能性があります。"
    summary_paragraphs.append(implications)
    
    # 最終的な自然文テキスト
    target_analysis_text = "\n\n".join(summary_paragraphs)
    
    # 元の統計情報も保持（必要に応じて参照できるように）
    numeric_text = ""
    if stats["numeric"]:
        for col, col_stats in stats["numeric"].items():
            if "error" not in col_stats:
                numeric_text += f"- {col}の範囲: {col_stats['min']}～{col_stats['max']} (平均: {col_stats['mean']})\n"
    
    category_text = ""
    if stats["categorical"]:
        for col, col_stats in stats["categorical"].items():
            if "error" not in col_stats:
                category_text += f"- {col}の主な値: "
                sorted_categories = sorted(col_stats.items(), key=lambda x: x[1]['count'], reverse=True)
                for val, val_stats in sorted_categories[:3]:  # 上位3つのカテゴリのみ
                    category_text += f"{val}({val_stats['percentage']}%), "
                category_text = category_text.rstrip(", ") + "\n"
    
    # 職種ごとの選択傾向
    job_type_text = ""
    for job_type, analysis in job_type_analysis.items():
        job_type_text += f"- {job_type}: {analysis}\n\n"
    
    # サンプルデータをJSON形式でフォーマット
    sample_data = analysis_result.get("sample_data", [])
    sample_data_json = json.dumps(sample_data[:3] if sample_data else [], ensure_ascii=False, indent=2)
    
    insights_data = {
        "file_name": file_info["file_name"],
        "num_rows": file_info["num_rows"],
        "num_columns": file_info["num_columns"],
        "column_names": file_info["column_names"],
        "target_analysis": target_analysis_text,  # 新たに追加した自然文の分析テキスト
        "numeric_summary": numeric_text,
        "category_summary": category_text,
        "job_type_analysis": job_type_text,  # 新たに追加した職種別選択傾向
        "sample_data_json": sample_data_json
    }
    
    return insights_data
