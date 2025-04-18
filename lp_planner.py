"""Gemini APIを使用したLP企画設計の分析機能"""
import os
import google.generativeai as genai
from utils import GOOGLE_API_KEY, log_error, logger, read_svg_content
from svg_generator import generate_svg_with_gemini, get_backup_svg
from pptx_converter import svg_to_pptx, create_download_link
import utils
import json

# Gemini APIの設定
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_lp_planning(product_theme, csv_insights=None, svg_path=None):
    """Gemini APIを使用してLP企画のための分析を生成する関数
    
    Args:
        product_theme (str): 商品/サービスのテーマ
        csv_insights (dict, optional): CSVデータからの洞察情報。csv_analyzer.pyから提供される。
        svg_path (str, optional): 参照SVGファイルのパス
        
    Returns:
        tuple: (分析テキスト, SVGコード, ダウンロードリンク)
    """
    if not GOOGLE_API_KEY:
        return "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。", None, None
    
    try:
        # Geminiモデルの生成
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # プロンプトテンプレート
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
        なお、検討結果については1000字以内でまとめてください。

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
        
        # CSVデータの洞察が提供されている場合、プロンプトに追加
        if csv_insights:
            prompt = f"""
            あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
            以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
            なお、検討結果については1000字以内でまとめてください。

            商品/サービステーマ: {product_theme}

            以下のCSVデータによる分析結果を参考にしてください：
            - ファイル名: {csv_insights.get('file_name', '不明')}
            - データ行数: {csv_insights.get('num_rows', 0)}
            - 列情報: {', '.join(csv_insights.get('column_names', []))}

            数値データの概要:
            {csv_insights.get('numeric_summary', '情報なし')}

            カテゴリデータの概要:
            {csv_insights.get('category_summary', '情報なし')}

            サンプルデータ:
            {csv_insights.get('sample_data_json', '{}')}

            上記のCSVデータの分析結果を参考にして、以下の3つの観点から分析を行ってください:

            1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
               - CSVデータから得られる顧客の特性や傾向を必ず考慮してください
            2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
               - CSVデータから見える課題やニーズを考慮してください
            3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

            分析内容は必ず以下の形式で出力してください:
            ```
            ## ターゲットの分析
            （ターゲット分析の内容 - CSVデータの分析結果を必ず活用してください）

            ## 訴求軸の検討
            （訴求軸の内容）

            ## 訴求シナリオの検討
            （訴求シナリオの内容）
            ```

            各セクションは具体的で、詳細な分析を含め、長さは合計で1000字程度にしてください。
            特にターゲット分析では、CSVデータから得られた洞察を具体的に言及してください。
            """
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答から分析部分を取得
        analysis_text = response.text
        
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
