"""CSVファイルの分析機能を提供するモジュール"""
import os
import pandas as pd
import json
from utils import logger, log_error
import chardet
import numpy as np

def detect_encoding(file_path):
    """ファイルのエンコーディングを自動検出する"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def analyze_csv(csv_path):
    """CSVファイルを分析し、基本的な統計情報と洞察を提供する"""
    if not csv_path or not os.path.exists(csv_path):
        return {
            "success": False,
            "error": "CSVファイルが見つかりません",
            "file_path": csv_path
        }
    
    try:
        # ファイルのエンコーディングを自動検出
        encoding = detect_encoding(csv_path)
        logger.info(f"CSVファイルのエンコーディングを検出: {encoding}")
        
        # 複数のエンコーディングを試す
        try:
            # 検出したエンコーディングで試す
            df = pd.read_csv(csv_path, encoding=encoding)
        except UnicodeDecodeError:
            # 代表的な日本語エンコーディングを順に試す
            encodings = ['utf-8', 'shift-jis', 'cp932', 'euc-jp', 'iso-2022-jp']
            success = False
            
            for enc in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=enc)
                    logger.info(f"エンコーディング {enc} で読み込み成功")
                    success = True
                    break
                except UnicodeDecodeError:
                    continue
            
            if not success:
                # 最後の手段としてエラー無視モードで読み込む
                df = pd.read_csv(csv_path, encoding='utf-8', errors='ignore')
                logger.warning("エラーを無視してCSVを読み込みました。一部のデータが欠損している可能性があります。")
        
        # 基本情報
        file_name = os.path.basename(csv_path)
        num_rows = len(df)
        num_cols = len(df.columns)
        column_names = list(df.columns)
        
        # 欠損値の確認
        missing_values = df.isnull().sum().to_dict()
        has_missing = any(value > 0 for value in missing_values.values())
        
        # 基本的な統計情報
        stats_info = {}
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # 数値列の統計
        numeric_stats = {}
        for col in numeric_cols:
            try:
                numeric_stats[col] = {
                    "mean": round(df[col].mean(), 2),
                    "median": round(df[col].median(), 2),
                    "min": round(df[col].min(), 2),
                    "max": round(df[col].max(), 2),
                    "std": round(df[col].std(), 2)
                }
            except:
                numeric_stats[col] = {"error": "統計計算できませんでした"}
        
        # カテゴリ列の分布
        category_stats = {}
        for col in categorical_cols:
            try:
                value_counts = df[col].value_counts().head(5).to_dict()  # 上位5カテゴリ
                total = sum(value_counts.values())
                
                # 各カテゴリの割合を計算
                percentages = {}
                for val, count in value_counts.items():
                    percentages[str(val)] = {
                        "count": int(count),
                        "percentage": round(count / total * 100, 1)
                    }
                
                category_stats[col] = percentages
            except:
                category_stats[col] = {"error": "分布計算できませんでした"}
        
        # サンプルデータ（最初の5行）
        sample_rows = df.head(5).to_dict('records')
        
        # クロス集計分析
        cross_tabs = {}
        cross_tabs_text = ""
        column_insights = {}
        job_preference_insights = {}
        
        # 最初の列をインデックス（職種カテゴリなど）として使用
        if len(column_names) > 1:
            try:
                index_col = column_names[0]
                # 各選択肢に対するクロス集計を実施
                for col in column_names[1:]:
                    try:
                        # クロス集計表を作成
                        cross_tab = pd.crosstab(df[index_col], df[col], normalize='index') * 100
                        cross_tab = cross_tab.round(1)  # パーセント表示で小数点1桁に丸める
                        
                        # クロス集計結果をdict形式で保持
                        cross_tabs[col] = cross_tab.to_dict()
                        
                        # テキスト形式でもクロス集計結果を保持
                        cross_tabs_text += f"\n### 「{index_col}」と「{col}」のクロス集計 (%):\n"
                        cross_tabs_text += cross_tab.to_string() + "\n\n"
                        
                        # 特徴的な傾向を分析
                        # 最大値と最小値を持つセルを特定
                        max_indices = np.unravel_index(cross_tab.values.argmax(), cross_tab.shape)
                        min_indices = np.unravel_index(cross_tab.values.argmin(), cross_tab.shape)
                        
                        # 最も高い比率と最も低い比率を持つカテゴリを特定
                        max_row = cross_tab.index[max_indices[0]]
                        max_col = cross_tab.columns[max_indices[1]]
                        max_val = cross_tab.iloc[max_indices]
                        
                        min_row = cross_tab.index[min_indices[0]]
                        min_col = cross_tab.columns[min_indices[1]]
                        min_val = cross_tab.iloc[min_indices]
                        
                        # 列名（選択肢）の意味を考慮した洞察を追加
                        column_insights[col] = {
                            "description": f"「{col}」選択肢の傾向分析",
                            "highest": {
                                "job_type": max_row, 
                                "option": max_col, 
                                "percentage": float(max_val)
                            },
                            "lowest": {
                                "job_type": min_row, 
                                "option": min_col, 
                                "percentage": float(min_val)
                            }
                        }
                        
                        cross_tabs_text += f"- 特徴的な傾向: \"{max_row}\" は \"{col}\" において \"{max_col}\" の選択率が最も高く ({max_val:.1f}%)、\"{min_row}\" は \"{min_col}\" の選択率が最も低い ({min_val:.1f}%)\n"
                        
                        # 平均との差が大きいセルを抽出
                        col_means = cross_tab.mean()
                        for idx in cross_tab.index:
                            if idx not in job_preference_insights:
                                job_preference_insights[idx] = []
                            
                            notable_diffs = []
                            significant_choices = []
                            
                            for col_name in cross_tab.columns:
                                diff = cross_tab.loc[idx, col_name] - col_means[col_name]
                                if abs(diff) > 15:  # 平均との差が15%ポイント以上ある場合
                                    direction = "高い" if diff > 0 else "低い"
                                    notable_diffs.append(f"\"{col}\" の \"{col_name}\" が平均より{abs(diff):.1f}%ポイント{direction}")
                                    
                                    # 職種ごとの選択傾向として記録
                                    significant_choices.append({
                                        "question": col,
                                        "choice": col_name,
                                        "difference": float(diff),
                                        "above_average": diff > 0,
                                        "percentage": float(cross_tab.loc[idx, col_name])
                                    })
                            
                            # 有意な選択肢があればジョブタイプの特徴として追加
                            if significant_choices:
                                job_preference_insights[idx].extend(significant_choices)
                            
                            if notable_diffs:
                                cross_tabs_text += f"- \"{idx}\" の特徴: {', '.join(notable_diffs)}\n"
                    except Exception as e:
                        logger.warning(f"列 {col} のクロス集計中にエラーが発生しました: {str(e)}")
            except Exception as e:
                logger.warning(f"クロス集計中にエラーが発生しました: {str(e)}")
                cross_tabs_text = f"クロス集計を実行できませんでした。エラー: {str(e)}"
        
        # 列名（選択肢）の意味を考慮した職種ごとの傾向分析テキストを生成
        job_type_analysis = generate_job_type_analysis(job_preference_insights, column_names)
        
        # 分析結果をまとめる
        analysis_result = {
            "success": True,
            "file_info": {
                "file_path": csv_path,
                "file_name": file_name,
                "encoding": encoding,
                "num_rows": num_rows,
                "num_columns": num_cols,
                "column_names": file_info["column_names"],
        "target_analysis": target_analysis_text,  # 新たに追加した自然文の分析テキスト
        "numeric_summary": numeric_text,
        "category_summary": category_text,
        "job_type_analysis": job_type_text,  # 新たに追加した職種別選択傾向
        "sample_data_json": sample_data_json
    }
    
    return insights_data": column_names
            },
            "data_quality": {
                "has_missing_values": has_missing,
                "missing_values": missing_values
            },
            "statistics": {
                "numeric": numeric_stats,
                "categorical": category_stats
            },
            "cross_tabs": cross_tabs,
            "cross_tabs_text": cross_tabs_text,
            "column_insights": column_insights,
            "job_preference_insights": job_preference_insights,
            "job_type_analysis": job_type_analysis,
            "sample_data": sample_rows
        }
        
        # UI表示用のテキスト生成
        display_text = generate_display_text(analysis_result)
        
        return {
            "success": True,
            "analysis_result": analysis_result,
            "display_text": display_text,
            "dataframe": df  # 元のDataFrameも返す（必要に応じて使用）
        }
        
    except Exception as e:
        error_msg = log_error(f"CSVファイル分析中にエラーが発生しました: {csv_path}", e)
        return {
            "success": False,
            "error": error_msg,
            "file_path": csv_path
        }

def generate_job_type_analysis(job_preference_insights, column_names):
    """職種ごとの選択傾向を分析し、テキストにまとめる"""
    job_type_analysis = {}
    
    # 各職種の特徴をテキストにまとめる
    for job_type, preferences in job_preference_insights.items():
        # 傾向が強い選択肢（差が大きい順）
        sorted_preferences = sorted(preferences, key=lambda x: abs(x['difference']), reverse=True)
        
        # 各職種の特徴をテキスト化
        insights = []
        
        # 選択肢を項目ごとにグループ化
        grouped_by_question = {}
        for pref in sorted_preferences:
            question = pref['question']
            if question not in grouped_by_question:
                grouped_by_question[question] = []
            grouped_by_question[question].append(pref)
        
        # 各質問項目について特徴をまとめる
        for question, prefs in grouped_by_question.items():
            positive_prefs = [p for p in prefs if p['above_average']]
            negative_prefs = [p for p in prefs if not p['above_average']]
            
            if positive_prefs:
                top_positive = positive_prefs[0]
                insights.append(f"「{question}」において「{top_positive['choice']}」の選択率が{top_positive['percentage']:.1f}%と平均より{abs(top_positive['difference']):.1f}%ポイント高い")
            
            if negative_prefs:
                top_negative = negative_prefs[0]
                insights.append(f"「{question}」において「{top_negative['choice']}」の選択率が{top_negative['percentage']:.1f}%と平均より{abs(top_negative['difference']):.1f}%ポイント低い")
        
        # 職種の総合的な傾向を記述
        if insights:
            summary = f"{job_type}は、" + "、また".join(insights) + "という特徴があります。"
            
            # 傾向の解釈を追加
            interpretation = interpret_job_type_preferences(job_type, sorted_preferences, column_names)
            if interpretation:
                summary += f" {interpretation}"
            
            job_type_analysis[job_type] = summary
        else:
            job_type_analysis[job_type] = f"{job_type}は特徴的な選択傾向が見られませんでした。"
    
    return job_type_analysis

def interpret_job_type_preferences(job_type, preferences, column_names):
    """職種の選択傾向から意味を解釈する"""
    if not preferences:
        return ""
    
    # 肯定的な選択と否定的な選択を分ける
    positive_prefs = [p for p in preferences if p['above_average']]
    negative_prefs = [p for p in preferences if not p['above_average']]
    
    interpretation = []
    
    # 肯定的な選択から傾向を解釈
    if positive_prefs:
        positive_keywords = [p['choice'] for p in positive_prefs[:3]]
        positive_questions = set([p['question'] for p in positive_prefs[:3]])
        
        # キーワードに基づいた解釈
        if any("コスト" in k for k in positive_keywords) or any("予算" in k for k in positive_keywords):
            interpretation.append("コスト意識が高い傾向にあります")
        if any("効率" in k for k in positive_keywords) or any("生産性" in k for k in positive_keywords):
            interpretation.append("効率性を重視する傾向にあります")
        if any("品質" in k for k in positive_keywords) or any("精度" in k for k in positive_keywords):
            interpretation.append("品質重視の姿勢が強い傾向にあります")
        if any("革新" in k for k in positive_keywords) or any("新しい" in k for k in positive_keywords) or any("新技術" in k for k in positive_keywords):
            interpretation.append("新しい技術や革新に積極的な傾向にあります")
        if any("安全" in k for k in positive_keywords) or any("セキュリティ" in k for k in positive_keywords):
            interpretation.append("安全性やセキュリティを重視する傾向にあります")
    
    # 否定的な選択から傾向を解釈
    if negative_prefs:
        negative_keywords = [p['choice'] for p in negative_prefs[:3]]
        negative_questions = set([p['question'] for p in negative_prefs[:3]])
        
        # キーワードに基づいた解釈
        if any("リスク" in k for k in negative_keywords):
            interpretation.append("リスク回避の傾向が低いです")
        if any("変化" in k for k in negative_keywords) or any("柔軟" in k for k in negative_keywords):
            interpretation.append("変化への適応に課題がある可能性があります")
    
    # 職種に基づいた特別な解釈
    if "経営" in job_type or "管理" in job_type:
        if positive_prefs and any("戦略" in p['choice'] or "長期" in p['choice'] for p in positive_prefs):
            interpretation.append("戦略的な視点を持ち、長期的な成果を重視しています")
    
    if "技術" in job_type or "エンジニア" in job_type:
        if positive_prefs and any("専門" in p['choice'] or "技術" in p['choice'] for p in positive_prefs):
            interpretation.append("専門的な技術への関心が高い傾向にあります")
    
    if "営業" in job_type:
        if positive_prefs and any("顧客" in p['choice'] or "関係" in p['choice'] for p in positive_prefs):
            interpretation.append("顧客関係を重視する傾向にあります")
    
    # 解釈をテキストとして結合
    if interpretation:
        return "これは" + "、".join(interpretation) + "ことを示唆しています。"
    else:
        return ""

def generate_display_text(analysis_result):
    """分析結果をUI表示用のテキストに変換する"""
    if not analysis_result.get("success", False):
        return f"## CSVファイル分析エラー\n\nファイル: {analysis_result.get('file_path', '不明')}\nエラー: {analysis_result.get('error', '不明なエラー')}"
    
    file_info = analysis_result["file_info"]
    data_quality = analysis_result["data_quality"]
    stats = analysis_result["statistics"]
    
    text = f"""## CSVデータ分析結果

### 基本情報
- **ファイル名**: {file_info["file_name"]}
- **エンコーディング**: {file_info.get("encoding", "不明")}
- **行数**: {file_info["num_rows"]}
- **列数**: {file_info["num_columns"]}
- **列名**: {', '.join(file_info["column_names"])}

### データ品質
- **欠損値の有無**: {"あり" if data_quality["has_missing_values"] else "なし"}
"""

    # 数値データの統計情報
    if stats["numeric"]:
        text += "\n### 数値データの統計\n"
        for col, col_stats in stats["numeric"].items():
            if "error" in col_stats:
                text += f"- **{col}**: {col_stats['error']}\n"
            else:
                text += f"- **{col}**: 平均={col_stats['mean']}, 中央値={col_stats['median']}, 最小={col_stats['min']}, 最大={col_stats['max']}\n"
    
    # カテゴリデータの分布
    if stats["categorical"]:
        text += "\n### カテゴリデータの分布\n"
        for col, col_stats in stats["categorical"].items():
            if "error" in col_stats:
                text += f"- **{col}**: {col_stats['error']}\n"
            else:
                text += f"- **{col}の上位カテゴリ**: "
                for val, val_stats in col_stats.items():
                    text += f"{val}({val_stats['percentage']}%), "
                text = text.rstrip(", ") + "\n"
    
    # 職種ごとの選択傾向分析
    if "job_type_analysis" in analysis_result and analysis_result["job_type_analysis"]:
        text += "\n## 職種ごとの選択傾向分析\n"
        job_type_analysis = analysis_result["job_type_analysis"]
        for job_type, analysis in job_type_analysis.items():
            text += f"### {job_type}の特徴\n"
            text += f"{analysis}\n\n"
    
    # クロス集計結果
    if "cross_tabs_text" in analysis_result and analysis_result["cross_tabs_text"]:
        text += "\n## クロス集計分析\n"
        text += analysis_result["cross_tabs_text"]
    
    # サンプルデータは複雑になりすぎるので省略
    text += "\n### サンプルデータ\n最初の数行のデータは分析に使用されます。\n"
    
    return text

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
        "column_names
