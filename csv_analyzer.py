"""CSVファイルの分析と洞察抽出機能"""
import os
import pandas as pd
import json
import numpy as np
import chardet
from utils import logger, log_error
from job_type_analyzer import (
    analyze_job_type_preferences,
    generate_job_type_insights,
    analyze_choice_patterns,
    interpret_choice_patterns
)

def detect_encoding(file_path):
    """ファイルのエンコーディングを検出する関数"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def analyze_csv(csv_path):
    """CSVファイルを分析し、構造と統計情報を抽出する関数"""
    if not csv_path or not os.path.exists(csv_path):
        return {"success": False, "error": "CSVファイルが見つかりません"}
    
    try:
        # ファイルのエンコーディングを自動検出
        detected_encoding = detect_encoding(csv_path)
        logger.info(f"検出されたエンコーディング: {detected_encoding}")
        
        # 検出されたエンコーディングでCSVファイルを読み込む
        try:
            df = pd.read_csv(csv_path, encoding=detected_encoding)
        except Exception as e:
            logger.warning(f"検出されたエンコーディング {detected_encoding} での読み込みに失敗: {str(e)}")
            # 一般的な日本語エンコーディングを試す
            encodings_to_try = ['utf-8', 'shift-jis', 'cp932', 'euc-jp', 'iso-2022-jp']
            for encoding in encodings_to_try:
                try:
                    logger.info(f"エンコーディング {encoding} で試行中...")
                    df = pd.read_csv(csv_path, encoding=encoding)
                    logger.info(f"エンコーディング {encoding} で成功")
                    break
                except Exception as e:
                    logger.warning(f"エンコーディング {encoding} での読み込みに失敗: {str(e)}")
                    continue
            else:
                # すべてのエンコーディングで失敗した場合
                return {"success": False, "error": "CSVファイルのエンコーディングを特定できませんでした"}
        
        # 基本情報
        file_info = {
            "file_name": os.path.basename(csv_path),
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        # データフレームのデバッグ出力
        logger.info(f"CSVデータ読み込み成功: {file_info['num_rows']}行 × {file_info['num_columns']}列")
        logger.info(f"列名: {file_info['column_names']}")
        logger.info(f"最初の5行のサンプル:\n{df.head().to_string()}")
        
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
                    logger.error(f"列 {col} の数値統計計算中にエラー: {str(e)}")
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
                    logger.error(f"列 {col} のカテゴリ統計計算中にエラー: {str(e)}")
        
        # 職種別の選択傾向を詳細に分析
        job_type_preferences = analyze_job_type_preferences(df)
        job_type_insights = generate_job_type_insights(job_type_preferences)
        
        # 選択肢パターンの分析
        choice_patterns = analyze_choice_patterns(df)
        choice_pattern_insights = interpret_choice_patterns(choice_patterns)
        
        # 分析結果をまとめる
        analysis_result = {
            "file_info": file_info,
            "statistics": statistics,
            "sample_data": sample_data,
            "job_type_analysis": job_type_insights,
            "job_type_preferences": job_type_preferences,
            "choice_patterns": choice_patterns,
            "choice_pattern_insights": choice_pattern_insights
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

def generate_display_text(analysis_result):
    """分析結果を表示用のテキストに変換する"""
    file_info = analysis_result["file_info"]
    stats = analysis_result["statistics"]
    job_type_analysis = analysis_result.get("job_type_analysis", {})
    choice_pattern_insights = analysis_result.get("choice_pattern_insights", "")
    
    text_parts = []
    
    # ファイル情報
    text_parts.append(f"## CSVファイル分析: {file_info['file_name']}")
    text_parts.append(f"- 行数: {file_info['num_rows']}")
    text_parts.append(f"- 列数: {file_info['num_columns']}")
    text_parts.append(f"- 列名: {', '.join(file_info['column_names'])}")
    
    # 職種別選択傾向の分析（最重要部分なので最初に表示）
    if job_type_analysis and not isinstance(job_type_analysis, dict) or "error" in job_type_analysis:
        error_msg = job_type_analysis.get("error", "不明なエラー")
        text_parts.append(f"\n### 職種別選択傾向の分析: エラー\n{error_msg}")
    elif job_type_analysis:
        text_parts.append("\n### 職種別選択傾向の分析")
        for job_type, trend_text in job_type_analysis.items():
            text_parts.append(f"- **{job_type}**: {trend_text}")
    
    # 選択肢パターンの洞察
    if choice_pattern_insights:
        text_parts.append("\n### 選択肢の関連パターン分析")
        text_parts.append(choice_pattern_insights)
    
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
    choice_pattern_insights = analysis_result.get("choice_pattern_insights", "")
    
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
    
    # 選択肢の関連パターン
    if choice_pattern_insights:
        summary_paragraphs.append(choice_pattern_insights)
    
    # 行動や嗜好の特徴
    combined_insights = preference_insights + behavioral_insights
    if combined_insights:
        behavior_summary = "ターゲットの行動特性として、" + " ".join(combined_insights)
        summary_paragraphs.append(behavior_summary)
    
    # LP企画への示唆
    if highlighted_job_types and len(highlighted_job_types) >= 2:
        implications = "これらの職種別特性と選択パターンを踏まえると、各職種が持つ課題や関心事に焦点を当て、それぞれが重視する観点（効率性、コスト、品質など）に対応した価値提案をLPで訴求することが効果的です。特に主要な職種である" + "、".join(highlighted_job_types[:2]) + "向けのメッセージを優先的に配置することで、コンバージョン率を高められる可能性があります。"
    else:
        implications = "これらの職種別特性と選択パターンを踏まえると、各職種が持つ課題や関心事に焦点を当て、それぞれが重視する観点（効率性、コスト、品質など）に対応した価値提案をLPで訴求することが効果的です。"
    
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
        "choice_pattern_insights": choice_pattern_insights,  # 選択肢の関連パターン分析
        "sample_data_json": sample_data_json
    }
    
    return insights_data
