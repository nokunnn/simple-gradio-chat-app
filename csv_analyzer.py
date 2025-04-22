"""CSVファイルの分析と洞察抽出機能"""
import os
import pandas as pd
import json
import numpy as np
from utils import logger, log_error

def analyze_csv(csv_path):
    """CSVファイルを分析し、構造と統計情報を抽出する関数"""
    if not csv_path or not os.path.exists(csv_path):
        return {"success": False, "error": "CSVファイルが見つかりません"}
    
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # もし読み込みに失敗したら他のエンコーディングも試す
        if df.empty:
            for encoding in ['shift-jis', 'cp932', 'iso-2022-jp']:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    if not df.empty:
                        break
                except:
                    continue
        
        # 基本情報
        file_info = {
            "file_name": os.path.basename(csv_path),
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        # 最初の10行をサンプルとして取得
        sample_data = []
        for _, row in df.head(10).iterrows():
            sample_data.append(dict(row))
        
        # 統計情報の初期化
        statistics = {
            "numeric": {},
            "categorical": {}
        }
        
        # 各列の型と統計情報を分析
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                try:
                    # 数値型の列の統計
                    col_stats = {
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "std": float(df[col].std())
                    }
                    statistics["numeric"][col] = col_stats
                except Exception as e:
                    statistics["numeric"][col] = {"error": str(e)}
            else:
                try:
                    # カテゴリ型の列の統計
                    value_counts = df[col].value_counts()
                    col_stats = {}
                    
                    for val, count in value_counts.items():
                        if pd.notna(val):  # null値はスキップ
                            # 文字列に変換（数値も文字列として扱う）
                            val_str = str(val)
                            percentage = (count / len(df)) * 100
                            col_stats[val_str] = {
                                "count": int(count),
                                "percentage": round(percentage, 1)
                            }
                    
                    statistics["categorical"][col] = col_stats
                except Exception as e:
                    statistics["categorical"][col] = {"error": str(e)}
        
        # 職種別の選択傾向を分析
        job_type_analysis = analyze_job_type_trends(df)
        
        # 分析結果をまとめる
        analysis_result = {
            "file_info": file_info,
            "statistics": statistics,
            "sample_data": sample_data,
            "job_type_analysis": job_type_analysis
        }
        
        # 表示用のテキストを生成
        display_text = generate_display_text(analysis_result)
        
        return {
            "success": True,
            "analysis_result": analysis_result,
            "display_text": display_text
        }
        
    except Exception as e:
        error_msg = log_error("CSVファイルの分析中にエラーが発生しました", e)
        return {"success": False, "error": error_msg}

def analyze_job_type_trends(df):
    """職種別の選択傾向を分析し、各職種の特徴を抽出する関数"""
    try:
        # CSVの形式が想定通りかチェック
        if len(df.columns) < 3:
            return {"error": "CSVのフォーマットが期待と異なります。少なくとも3列以上が必要です。"}
        
        # 職種が1列目、回答者数が2列目、選択肢が3列目以降と想定
        job_types = df.iloc[:, 0]
        total_responses = df.iloc[:, 1]
        choices = df.iloc[:, 2:]
        
        # 結果を格納する辞書
        job_type_trends = {}
        
        # 各職種について分析
        for i, job_type in enumerate(job_types):
            if pd.isna(job_type) or str(job_type).strip() == "":
                continue
                
            # この職種の回答者数
            response_count = total_responses.iloc[i]
            if pd.isna(response_count) or response_count <= 0:
                continue
                
            # 各選択肢の割合を計算
            choice_percentages = {}
            for j, choice_col in enumerate(choices.columns):
                choice_count = choices.iloc[i, j]
                if pd.isna(choice_count):
                    continue
                    
                percentage = (choice_count / response_count) * 100
                choice_percentages[choice_col] = {
                    "count": choice_count,
                    "percentage": round(percentage, 1)
                }
            
            # 上位選択肢と下位選択肢を特定
            sorted_choices = sorted(choice_percentages.items(), key=lambda x: x[1]["percentage"], reverse=True)
            top_choices = sorted_choices[:2]  # 上位2つの選択肢
            bottom_choices = sorted_choices[-2:] if len(sorted_choices) > 2 else []  # 下位2つの選択肢
            
            # この職種の傾向を文章で表現
            trend_text = generate_job_type_trend_text(job_type, top_choices, bottom_choices, choice_percentages)
            
            # 結果を辞書に追加
            job_type_trends[str(job_type)] = trend_text
        
        return job_type_trends
        
    except Exception as e:
        logger.error(f"職種別選択傾向の分析中にエラーが発生しました: {str(e)}")
        return {"error": f"職種別選択傾向の分析中にエラーが発生しました: {str(e)}"}

def generate_job_type_trend_text(job_type, top_choices, bottom_choices, all_choices):
    """職種ごとの選択傾向を自然な日本語のテキストで表現する関数"""
    try:
        # 職種名を取得
        job_type_str = str(job_type)
        
        # 分析の初期化
        trend_parts = []
        
        # 最も選ばれた選択肢の特徴
        if top_choices:
            top1_name, top1_stats = top_choices[0]
            top1_percentage = top1_stats["percentage"]
            
            if top1_percentage > 50:
                trend_parts.append(f"{job_type_str}は「{top1_name}」を特に重視する傾向が強く（{top1_percentage}%）")
            elif top1_percentage > 30:
                trend_parts.append(f"{job_type_str}は「{top1_name}」を重視する傾向があり（{top1_percentage}%）")
            else:
                trend_parts.append(f"{job_type_str}は「{top1_name}」をある程度重視し（{top1_percentage}%）")
        
        # 2番目に選ばれた選択肢（あれば）
        if len(top_choices) > 1:
            top2_name, top2_stats = top_choices[1]
            top2_percentage = top2_stats["percentage"]
            
            # 1位との差が小さい場合は「同様に」、大きい場合は「次いで」などと表現
            if abs(top_choices[0][1]["percentage"] - top2_percentage) < 10:
                trend_parts.append(f"同様に「{top2_name}」も重視しています（{top2_percentage}%）")
            else:
                trend_parts.append(f"次いで「{top2_name}」を評価しています（{top2_percentage}%）")
        
        # 最も選ばれなかった選択肢の特徴（あれば）
        if bottom_choices and len(all_choices) > 3:  # 選択肢が十分にある場合のみ
            bottom1_name, bottom1_stats = bottom_choices[0]
            bottom1_percentage = bottom1_stats["percentage"]
            
            if bottom1_percentage < 10:
                trend_parts.append(f"一方で「{bottom1_name}」はあまり重視されていません（{bottom1_percentage}%）")
            elif bottom1_percentage < 20:
                trend_parts.append(f"「{bottom1_name}」については比較的関心が低い傾向にあります（{bottom1_percentage}%）")
        
        # 職種の特徴を示唆する追加コメント
        if top_choices and len(top_choices) > 0:
            top1_name = top_choices[0][0]
            
            # 選択肢の名前に基づいて、職種の特性を推測
            if "コスト" in top1_name or "価格" in top1_name or "費用" in top1_name:
                trend_parts.append("コスト意識が高い傾向にあります")
            elif "効率" in top1_name or "生産性" in top1_name:
                trend_parts.append("業務効率を重視する傾向にあります")
            elif "品質" in top1_name or "精度" in top1_name:
                trend_parts.append("品質や精度を最優先する特徴があります")
            elif "革新" in top1_name or "先進" in top1_name or "新技術" in top1_name:
                trend_parts.append("新しい技術や革新的なアプローチに関心が高いです")
            elif "安全" in top1_name or "セキュリティ" in top1_name:
                trend_parts.append("安全性やセキュリティを重視する傾向があります")
            elif "使いやすさ" in top1_name or "操作性" in top1_name:
                trend_parts.append("使いやすさやユーザビリティを重視しています")
        
        # 最終的なテキストを生成
        if trend_parts:
            return "、".join(trend_parts) + "。"
        else:
            return f"{job_type_str}の選択傾向に明確な特徴は見られませんでした。"
            
    except Exception as e:
        logger.error(f"職種別選択傾向のテキスト生成中にエラーが発生しました: {str(e)}")
        return f"{job_type}の選択傾向の分析中にエラーが発生しました。"

def generate_display_text(analysis_result):
    """分析結果を表示用のテキストに変換する"""
    file_info = analysis_result["file_info"]
    stats = analysis_result["statistics"]
    job_type_analysis = analysis_result.get("job_type_analysis", {})
    
    text_parts = []
    
    # ファイル情報
    text_parts.append(f"## CSVファイル分析: {file_info['file_name']}")
    text_parts.append(f"- 行数: {file_info['num_rows']}")
    text_parts.append(f"- 列数: {file_info['num_columns']}")
    text_parts.append(f"- 列名: {', '.join(file_info['column_names'])}")
    
    # 数値データの統計
    if stats["numeric"]:
        text_parts.append("\n### 数値データの統計")
        for col, col_stats in stats["numeric"].items():
            if "error" in col_stats:
                text_parts.append(f"- {col}: エラー - {col_stats['error']}")
            else:
                text_parts.append(f"- {col}:")
                text_parts.append(f"  - 最小値: {col_stats['min']}")
                text_parts.append(f"  - 最大値: {col_stats['max']}")
                text_parts.append(f"  - 平均値: {col_stats['mean']}")
                text_parts.append(f"  - 中央値: {col_stats['median']}")
                text_parts.append(f"  - 標準偏差: {col_stats['std']}")
    
    # カテゴリデータの統計
    if stats["categorical"]:
        text_parts.append("\n### カテゴリデータの統計")
        for col, col_stats in stats["categorical"].items():
            if "error" in col_stats:
                text_parts.append(f"- {col}: エラー - {col_stats['error']}")
            else:
                text_parts.append(f"- {col}:")
                # 上位5つのカテゴリのみ表示
                sorted_cats = sorted(col_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
                for cat, cat_stats in sorted_cats:
                    text_parts.append(f"  - {cat}: {cat_stats['count']}件 ({cat_stats['percentage']}%)")
    
    # 職種別選択傾向の分析
    if job_type_analysis and not isinstance(job_type_analysis, dict) or "error" in job_type_analysis:
        error_msg = job_type_analysis.get("error", "不明なエラー")
        text_parts.append(f"\n### 職種別選択傾向の分析: エラー\n{error_msg}")
    elif job_type_analysis:
        text_parts.append("\n### 職種別選択傾向の分析")
        for job_type, trend_text in job_type_analysis.items():
            text_parts.append(f"- **{job_type}**: {trend_text}")
    
    return "\n".join(text_parts)

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
