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
            # 新しく追加した自然文のターゲット分析を使用する
            target_analysis_text = csv_insights.get('target_analysis', '')
            
            # 職種別選択傾向の分析結果を取得
            job_type_analysis = csv_insights.get('job_type_analysis', '')
            
            prompt = f"""
            あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
            以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
            なお、検討結果については1000字以内でまとめてください。

            商品/サービステーマ: {product_theme}

            以下のターゲット分析の結果を参考にしてください：

            <<< ターゲット分析 >>>
            {target_analysis_text}
            <<< ターゲット分析おわり >>>

            以下の職種別選択傾向の分析も参考にしてください：

            <<< 職種別選択傾向分析 >>>
            {job_type_analysis}
            <<< 職種別選択傾向分析おわり >>>

            以下の3つの観点から分析を行ってください:

            1. ターゲットの分析: 
               - 上記のターゲット分析と職種別選択傾向分析を踏まえて、このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのかを詳細に分析してください。
               - 特に、職種ごとの選択傾向から見える特徴（効率性重視、コスト意識、品質重視など）を考慮し、各職種が抱える課題や関心事を具体的に分析してください。
               - ターゲット企業内の主要な意思決定者の職種や、彼らが何を重視するかに着目してください。
               
            2. 訴求軸の検討: 
               - 上記のターゲット分析と職種別選択傾向分析を踏まえて、商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題を検討してください。
               - 各職種の特性に合わせた訴求ポイントを具体的に提案してください。例えば、コスト意識が高い職種には投資対効果や費用削減効果を、品質重視の職種には精度や信頼性を強調するなど。
               
            3. 訴求シナリオの検討: 
               - 職種ごとの選択傾向を踏まえて、LPで情報を伝達する最適な順序、各セクションで伝えるべき内容を具体的に検討してください。
               - 主要な意思決定者の職種（経営層、管理職、専門職など）に向けたメッセージの配置順序や強調方法を提案してください。
               - 各職種が重視する要素（効率性、コスト、品質、革新性など）をLPのどのセクションで、どのように訴求すべきかを具体的に提案してください。

            分析内容は必ず以下の形式で出力してください:
            ```
            ## ターゲットの分析
            （ターゲット分析の内容 - 職種ごとの選択傾向から見える特徴を活かした具体的な考察）

            ## 訴求軸の検討
            （訴求軸の内容 - 各職種の特性に合わせた訴求ポイントを含む）

            ## 訴求シナリオの検討
            （訴求シナリオの内容 - 職種ごとの重視要素を考慮したLP構成）
            ```

            各セクションは具体的で、詳細な分析を含め、長さは合計で1000字程度にしてください。
            ターゲット分析では、CSVデータから得られた洞察と職種別選択傾向を踏まえた具体的な考察を行ってください。
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
