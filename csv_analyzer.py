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
                        
                        cross_tabs_text += f"- 特徴的な傾向: \"{max_row}\" は \"{max_col}\" の選択率が最も高く ({max_val:.1f}%)、\"{min_row}\" は \"{min_col}\" の選択率が最も低い ({min_val:.1f}%)\n"
                        
                        # 平均との差が大きいセルを抽出
                        col_means = cross_tab.mean()
                        for idx in cross_tab.index:
                            notable_diffs = []
                            for col_name in cross_tab.columns:
                                diff = cross_tab.loc[idx, col_name] - col_means[col_name]
                                if abs(diff) > 15:  # 平均との差が15%ポイント以上ある場合
                                    direction = "高い" if diff > 0 else "低い"
                                    notable_diffs.append(f"\"{col_name}\" が平均より{abs(diff):.1f}%ポイント{direction}")
                            
                            if notable_diffs:
                                cross_tabs_text += f"- \"{idx}\" の特徴: {', '.join(notable_diffs)}\n"
                    except Exception as e:
                        logger.warning(f"列 {col} のクロス集計中にエラーが発生しました: {str(e)}")
            except Exception as e:
                logger.warning(f"クロス集計中にエラーが発生しました: {str(e)}")
                cross_tabs_text = f"クロス集計を実行できませんでした。エラー: {str(e)}"
        
        # 分析結果をまとめる
        analysis_result = {
            "success": True,
            "file_info": {
                "file_path": csv_path,
                "file_name": file_name,
                "encoding": encoding,
                "num_rows": num_rows,
                "num_columns": num_cols,
                "column_names": column_names
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
    file_info = csv_analysis["file_info"]
    stats = csv_analysis["statistics"]
    
    # 数値データの概要テキスト
    numeric_text = ""
    if stats["numeric"]:
        for col, col_stats in stats["numeric"].items():
            if "error" not in col_stats:
                numeric_text += f"- {col}の範囲: {col_stats['min']}～{col_stats['max']} (平均: {col_stats['mean']})\n"
    
    # カテゴリデータの概要テキスト
    category_text = ""
    if stats["categorical"]:
        for col, col_stats in stats["categorical"].items():
            if "error" not in col_stats:
                category_text += f"- {col}の主な値: "
                sorted_categories = sorted(col_stats.items(), key=lambda x: x[1]['count'], reverse=True)
                for val, val_stats in sorted_categories[:3]:  # 上位3つのカテゴリのみ
                    category_text += f"{val}({val_stats['percentage']}%), "
                category_text = category_text.rstrip(", ") + "\n"
    
    # クロス集計の洞察テキスト
    cross_tabs_text = ""
    if "cross_tabs_text" in csv_analysis["analysis_result"]:
        cross_tabs_lines = csv_analysis["analysis_result"]["cross_tabs_text"].split("\n")
        insight_lines = [line for line in cross_tabs_lines if line.startswith("- ")]
        if insight_lines:
            cross_tabs_text = "### 職種別の選択傾向の特徴:\n" + "\n".join(insight_lines)
    
    # サンプルデータをJSON形式でフォーマット
    sample_data_json = json.dumps(csv_analysis["sample_data"][:3], ensure_ascii=False, indent=2)
    
    insights_data = {
        "file_name": file_info["file_name"],
        "num_rows": file_info["num_rows"],
        "num_columns": file_info["num_columns"],
        "column_names": file_info["column_names"],
        "numeric_summary": numeric_text,
        "category_summary": category_text,
        "cross_tabs_insights": cross_tabs_text,
        "sample_data_json": sample_data_json
    }
    
    return insights_data
