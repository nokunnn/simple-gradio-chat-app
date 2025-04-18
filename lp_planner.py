"""Gemini APIを使用したLP企画設計の分析機能"""
import os
import google.generativeai as genai
from utils import GOOGLE_API_KEY, log_error, logger, read_csv_data, read_svg_content
from svg_generator import generate_svg_with_gemini, get_backup_svg
from pptx_converter import svg_to_pptx, create_download_link
import utils
import json
import pandas as pd

# Gemini APIの設定
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_csv_analysis(csv_path):
    """CSVファイルの詳細な分析を行う関数"""
    if not csv_path or not os.path.exists(csv_path):
        return None, None
    
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_path)
        
        # 基本情報
        num_rows = len(df)
        num_cols = len(df.columns)
        column_names = list(df.columns)
        
        # 基本的な統計情報
        stats_text = ""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # 数値列の場合は平均、最大値、最小値などを表示
        if numeric_cols:
            stats_text += "**数値データの統計:**\n"
            for col in numeric_cols[:3]:  # 最初の3列のみ分析
                try:
                    stats_text += f"- {col}: 平均={df[col].mean():.2f}, 最大={df[col].max():.2f}, 最小={df[col].min():.2f}\n"
                except:
                    stats_text += f"- {col}: 統計計算できませんでした\n"
        
        # カテゴリ列の場合は上位値の分布を表示
        if categorical_cols:
            stats_text += "\n**カテゴリデータの分布:**\n"
            for col in categorical_cols[:3]:  # 最初の3列のみ分析
                try:
                    value_counts = df[col].value_counts().head(3)
                    stats_text += f"- {col}の上位カテゴリ: "
                    for val, count in value_counts.items():
                        percentage = count / len(df) * 100
                        stats_text += f"{val}({percentage:.1f}%), "
                    stats_text = stats_text.rstrip(", ") + "\n"
                except:
                    stats_text += f"- {col}: 分布計算できませんでした\n"
        
        # サンプルデータ
        sample_data = df.head(5).to_dict()
        
        # 分析情報をまとめる
        analysis = {
            "file_path": csv_path,
            "file_name": os.path.basename(csv_path),
            "num_rows": num_rows,
            "num_columns": num_cols,
            "column_names": column_names,
            "statistics": stats_text,
            "sample_data": sample_data,
            "dataframe": df
        }
        
        # CSVデータの概要サマリー
        csv_summary = f"""
## CSVデータ分析

**アップロードされたCSVデータの概要:**
- ファイル: {os.path.basename(csv_path)}
- 行数: {num_rows}
- 列数: {num_cols}
- 列情報: {', '.join(column_names)}

{stats_text}

このCSVデータに基づいてターゲット分析を行います。
"""
        
        return analysis, csv_summary
    
    except Exception as e:
        logger.error(f"CSVデータ分析中にエラーが発生しました: {str(e)}")
        return None, f"""
## CSVデータ分析

**アップロードされたCSVデータ:**
- ファイル: {os.path.basename(csv_path) if csv_path else "不明"}
- エラー: CSVファイルの分析中にエラーが発生しました。ファイル形式を確認してください。

"""

def generate_lp_planning(product_theme, csv_path=None, svg_path=None):
    """Gemini APIを使用してLP企画のための分析を生成する関数"""
    if not GOOGLE_API_KEY:
        return "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。", None, None
    
    try:
        # CSVデータの分析
        csv_analysis = None
        csv_summary = None
        csv_insights_text = None
        final_analysis_text = ""
        
        # 1. CSVデータの分析とサマリー生成
        if csv_path and os.path.exists(csv_path):
            csv_analysis, csv_summary = generate_csv_analysis(csv_path)
            if csv_analysis:
                logger.info(f"CSVファイルを分析しました: {csv_path}")
                final_analysis_text += csv_summary + "\n\n"
        
        # 2. CSVデータからの洞察生成
        if csv_analysis:
            # Geminiモデル初期化
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # CSVデータからの自動的な洞察生成
            insights_prompt = f"""
あなたはデータ分析の専門家です。以下のCSVデータの概要を分析して、主要な洞察を抽出してください。
特に企業のターゲット層、課題、ニーズに関する洞察に焦点を当ててください。

CSVデータの概要:
- ファイル: {csv_analysis['file_name']}
- 行数: {csv_analysis['num_rows']}
- 列数: {csv_analysis['num_columns']}
- 列の情報: {', '.join(csv_analysis['column_names'])}

{csv_analysis['statistics']}

サンプルデータ（最初の5行）:
{json.dumps(csv_analysis['sample_data'], ensure_ascii=False, indent=2)}

このデータから得られる主要な洞察を3-5つ、箇条書きでまとめてください。
結果は「## CSVデータからの主要な洞察」という見出しで始めてください。
"""
            
            try:
                insights_response = model.generate_content(insights_prompt)
                csv_insights_text = insights_response.text
                final_analysis_text += csv_insights_text + "\n\n"
                logger.info("CSVデータからの洞察を生成しました")
            except Exception as e:
                logger.error(f"CSV洞察生成中にエラーが発生しました: {str(e)}")
                csv_insights_text = "## CSVデータからの主要な洞察\n- CSVデータの自動分析に失敗しました。手動で分析を行ってください。"
                final_analysis_text += csv_insights_text + "\n\n"
        
        # 3. LP企画設計の分析
        # Geminiモデルの初期化
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # プロンプトの作成（CSVデータがある場合と無い場合で分ける）
        if csv_analysis:
            prompt = f"""
あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。

商品/サービステーマ: {product_theme}

CSVデータからの洞察:
{csv_insights_text}

この洞察を踏まえて、以下の3つの観点から分析を行ってください:

1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

分析内容は必ず以下の形式で出力してください:
```
## ターゲットの分析
（ターゲット分析の内容）

## 訴求軸の検討
（訴求軸の内容）

## 訴求シナリオの検討
（訴求シナリオの内容）
```

各セクションは具体的で、詳細な分析を含め、長さは合計で1000字程度にしてください。
CSVデータからの洞察を反映させた具体的な提案を含めてください。
"""
        else:
            prompt = f"""
あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。

商品/サービステーマ: {product_theme}

以下の3つの観点から分析を行ってください:

1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

分析内容は必ず以下の形式で出力してください:
```
## ターゲットの分析
（ターゲット分析の内容）

## 訴求軸の検討
（訴求軸の内容）

## 訴求シナリオの検討
（訴求シナリオの内容）
```

各セクションは具体的で、詳細な分析を含め、長さは合計で1000字程度にしてください。
"""
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答から分析部分を取得し、最終分析テキストに追加
        final_analysis_text += response.text
        
        # SVG生成（最終分析テキストを入力として）
        svg_code, svg_error = generate_svg_with_gemini(product_theme, final_analysis_text, svg_path)
        
        # SVGに問題があった場合のバックアップSVG
        if not svg_code:
            svg_code = get_backup_svg()
            if svg_error:
                final_analysis_text += f"\n\n{svg_error}"
        
        # グローバル変数に保存
        utils.current_svg_code = svg_code
        utils.current_analysis = final_analysis_text
        utils.current_theme = product_theme
        
        # PowerPointファイルを生成
        pptx_data, filename = svg_to_pptx(svg_code, final_analysis_text, product_theme)
        
        # ダウンロードリンクの作成
        download_link = create_download_link(pptx_data, filename)
        
        return final_analysis_text, svg_code, download_link
        
    except Exception as e:
        return log_error("LP企画設計中にエラーが発生しました", e), None, None
