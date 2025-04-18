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

def generate_lp_planning(product_theme, csv_path=None, svg_path=None):
    """Gemini APIを使用してLP企画のための分析を生成する関数"""
    if not GOOGLE_API_KEY:
        return "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。", None, None
    
    try:
        # Geminiモデルの生成
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # CSVデータを読み込み
        csv_analysis = None
        csv_summary = ""
        csv_insights = ""
        
        if csv_path and os.path.exists(csv_path):
            csv_analysis = read_csv_data(csv_path)
            logger.info(f"CSVファイルを読み込みました: {csv_path}")
            
            # CSV分析のサマリーを作成
            if csv_analysis:
                # CSVデータの基本的な統計を計算
                df = csv_analysis.get('dataframe')
                if df is not None and isinstance(df, pd.DataFrame):
                    # 基本的な統計情報を取得
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    
                    stats_text = ""
                    # 数値列の場合は平均、最大値、最小値などを表示
                    if numeric_cols:
                        stats_text += "**数値データの統計:**\n"
                        for col in numeric_cols[:3]:  # 最初の3列のみ分析
                            stats_text += f"- {col}: 平均={df[col].mean():.2f}, 最大={df[col].max():.2f}, 最小={df[col].min():.2f}\n"
                    
                    # カテゴリ列の場合は上位値の分布を表示
                    if categorical_cols:
                        stats_text += "\n**カテゴリデータの分布:**\n"
                        for col in categorical_cols[:3]:  # 最初の3列のみ分析
                            value_counts = df[col].value_counts().head(3)
                            stats_text += f"- {col}の上位カテゴリ: "
                            for val, count in value_counts.items():
                                percentage = count / len(df) * 100
                                stats_text += f"{val}({percentage:.1f}%), "
                            stats_text = stats_text.rstrip(", ") + "\n"
                
                # CSVデータの概要サマリー
                csv_summary = f"""
                ## CSVデータ分析
                
                **アップロードされたCSVデータの概要:**
                - ファイル: {os.path.basename(csv_path)}
                - 行数: {csv_analysis['num_rows']}
                - 列数: {csv_analysis['num_columns']}
                - 列情報: {', '.join([f"{col}" for col in csv_analysis['columns'].keys()])}
                
                {stats_text}
                
                このCSVデータに基づいてターゲット分析を行います。
                """
                
                # CSVデータからの自動的な洞察生成を追加
                insights_prompt = f"""
                あなたはデータ分析の専門家です。以下のCSVデータの概要を分析して、主要な洞察を抽出してください。
                特に企業のターゲット層、課題、ニーズに関する洞察に焦点を当ててください。
                
                CSVデータの概要:
                - 行数: {csv_analysis['num_rows']}
                - 列数: {csv_analysis['num_columns']}
                - 列の情報: {', '.join([f"{col}" for col in csv_analysis['columns'].keys()])}
                
                サンプルデータ:
                {json.dumps(csv_analysis['sample_data'], ensure_ascii=False, indent=2)}
                
                このデータから得られる主要な洞察を3-5つ、箇条書きでまとめてください。
                結果は「### CSVデータからの主要な洞察」という見出しで始めてください。
                """
                
                try:
                    insights_response = model.generate_content(insights_prompt)
                    csv_insights = insights_response.text
                except Exception as e:
                    logger.error(f"CSV洞察生成中にエラーが発生しました: {str(e)}")
                    csv_insights = "### CSVデータからの主要な洞察\n- CSVデータの自動分析に失敗しました。手動で分析を行ってください。"
        
        # プロンプトテンプレート
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
        なお、検討結果については1000字以内でまとめてください。

        商品/サービステーマ: {product_theme}

        あなたのレポートは以下の構成で書いてください:
        1. 「## ターゲットの分析」: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
        2. 「## 訴求軸の検討」: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
        3. 「## 訴求シナリオの検討」: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

        詳細な分析について説明し、具体的な提案を含めてください。
        """
        
        # CSVデータが提供されている場合、プロンプトに追加
        if csv_analysis:
            # プロンプトにCSV分析情報を追加
            prompt = f"""
            あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
            以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
            なお、検討結果については1000字以内でまとめてください。

            商品/サービステーマ: {product_theme}

            あなたのレポートは以下の構成で書いてください:
            1. 「## CSVデータ分析に基づく洞察」: アップロードされたCSVデータから得られた主要な洞察（このセクションは必ず含めてください）
            2. 「## ターゲットの分析」: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
            3. 「## 訴求軸の検討」: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
            4. 「## 訴求シナリオの検討」: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

            また、以下の顧客アンケートデータを参考にして分析を行ってください。特にターゲット分析に活用してください。
            
            CSVデータの概要:
            - 行数: {csv_analysis['num_rows']}
            - 列数: {csv_analysis['num_columns']}
            - 列の情報: {', '.join([f"{col}" for col in csv_analysis['columns'].keys()])}
            
            サンプルデータ:
            {json.dumps(csv_analysis['sample_data'], ensure_ascii=False, indent=2)}
            
            このデータから読み取れる傾向や特徴を分析に組み込んでください。特に、ターゲット企業の特性や課題、ニーズに関する洞察を深めることに重点を置いてください。
            
            必ず「## CSVデータ分析に基づく洞察」というセクションをレポートの先頭に含め、CSVデータから得られた具体的な発見、パターン、顧客の特性などをまとめてください。
            """
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答から分析部分を取得
        analysis_text = response.text
        
        # CSV分析情報がGeminiの応答に含まれない場合は、自動生成した洞察を追加
        if csv_analysis and "CSVデータ分析に基づく洞察" not in analysis_text and csv_insights:
            analysis_text = f"{csv_insights}\n\n{analysis_text}"
        
        # CSVデータ分析のサマリーがある場合は、それを分析テキストの前に追加
        if csv_summary:
            analysis_text = f"{csv_summary}\n\n{analysis_text}"
        
        # Gemini 1.5 Proを使ってSVGを生成（Geminiの分析結果を渡す）
        svg_code, svg_error = generate_svg_with_gemini(product_theme, analysis_text, svg_path)
        
        # SVGに問題があった場合のバックアップSVG
        if not svg_code:
            svg_code = get_backup_svg()
            if svg_error:
                analysis_text += f"\n\n{svg_error}"
        
        # グローバル変数に保存
        utils.current_svg_code = svg_code
        utils.current_analysis = analysis_text
        utils.current_theme = product_theme
        
        # PowerPointファイルを生成
        pptx_data, filename = svg_to_pptx(svg_code, analysis_text, product_theme)
        
        # ダウンロードリンクの作成
        download_link = create_download_link(pptx_data, filename)
        
        return analysis_text, svg_code, download_link
        
    except Exception as e:
        return log_error("LP企画設計中にエラーが発生しました", e), None, None
