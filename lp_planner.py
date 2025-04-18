"""Gemini APIを使用したLP企画設計の分析機能"""
import google.generativeai as genai
from utils import GOOGLE_API_KEY, log_error, logger, read_csv_data, read_svg_content
from svg_generator import generate_svg_with_gemini, get_backup_svg
from pptx_converter import svg_to_pptx, create_download_link
import utils
import json

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
        if csv_path:
            csv_analysis = read_csv_data(csv_path)
            logger.info(f"CSVファイルを読み込みました: {csv_path}")
        
        # プロンプトテンプレート
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。
        なお、検討結果については1000字以内でまとめてください。

        商品/サービステーマ: {product_theme}

        以下の3つの観点から分析してください:
        1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
        2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
        3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

        詳細な分析について説明し、具体的な提案を含めてください。
        """
        
        # CSVデータが提供されている場合、プロンプトに追加
        if csv_analysis:
            # プロンプトにCSV分析情報を追加
            prompt += f"""
            
            また、以下の顧客アンケートデータを参考にして分析を行ってください。特にターゲット分析に活用してください。
            
            CSVデータの概要:
            - 行数: {csv_analysis['num_rows']}
            - 列数: {csv_analysis['num_columns']}
            - 列の情報: {', '.join([f"{col}" for col in csv_analysis['columns'].keys()])}
            
            サンプルデータ:
            {json.dumps(csv_analysis['sample_data'], ensure_ascii=False, indent=2)}
            
            このデータから読み取れる傾向や特徴を分析に組み込んでください。特に、ターゲット企業の特性や課題、ニーズに関する洞察を深めることに重点を置いてください。
            """
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答から分析部分を取得
        analysis_text = response.text
        
        # Gemini 2.5 Proを使ってSVGを生成（Geminiの分析結果を渡す）
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
