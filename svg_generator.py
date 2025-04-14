"""Gemini 1.5 Proを使用したSVG生成機能"""
import re
import google.generativeai as genai
from utils import GOOGLE_API_KEY, log_error, logger

# Gemini APIの設定
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_svg_with_gemini(product_theme, analysis_text):
    """Gemini 1.5 ProにGeminiの分析結果を渡してSVGを生成する関数"""
    if not GOOGLE_API_KEY:
        return None, "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。"
    
    try:
        # Gemini 1.5 Pro モデルの初期化
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Gemini 1.5 Proへのプロンプト
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマとその分析に基づいて、法人向けLPの企画設計のためのSVGスライドを作成してください。

        商品/サービステーマ: {product_theme}

        Gemini AIによる分析結果:
        {analysis_text}

        上記の分析結果に基づいて、以下の3つの観点を含むSVGスライドを作成してください:
         1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
         2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
         3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容
 
         SVG要件:
         - サイズは16:9の比率で設定してください（width="800" height="450"）
         - ビジネス文書・プレゼンテーションとしての体裁を重視してください
         - 企業向けパワーポイントのスライドとしての活用を想定してください
         - プロフェッショナルなカラースキームを使用してください（青系のビジネスカラーが適切です）
         - 明確なタイトル、サブタイトル、箇条書きなどの階層構造を持たせてください
         - フォントはシンプルで読みやすいサンセリフフォントを使用してください（例: Arial, Helvetica, sans-serif）
         - 適切なマージンとパディングを取り、余白を効果的に活用してください
         - 図表を使用する場合は、シンプルかつビジネス的な印象のデザインにしてください
         - テキストは必ず枠内に収まるように調整し、はみ出さないようにしてください
         - 情報量は適切に調整し、文字が小さくなり過ぎないようにしてください
         - フォントサイズは小さくても12px以上を維持してください
         - 3つの観点を全て1つのSVGに包含してください
         - 提供された分析結果の重要なポイントを活用してください
         - 日本語を含む場合は、文字化けしないように適切なフォントやエンコーディングを指定してください
 
         上記の分析結果の内容を要約して、SVG形式の１枚のスライドにまとめて。
         サイズは16:9の比率で設定してください（width="800" height="450"）
         
         SVGのコードだけを出力してください。必ず<svg>タグで始まり</svg>タグで終わる完全な形式で記述してください。
         コードの前後に説明文やマークダウンなどは不要です。SVGコード以外は一切出力しないでください。
        """
        
        # Gemini 1.5 Proからの応答を取得
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 8192,
            }
        )
        
        # 応答からSVGコードを抽出
        svg_text = response.text
        
        # SVGコードを抽出（必要に応じて）
        svg_match = re.search(r'<svg[\s\S]*?<\/svg>', svg_text)
        svg_code = svg_match.group(0) if svg_match else svg_text
        
        # SVGのサイズを800x450（16:9）に変更
        svg_code = re.sub(r'width="[0-9]+"', 'width="800"', svg_code)
        svg_code = re.sub(r'height="[0-9]+"', 'height="450"', svg_code)
        
        # viewBox属性を調整
        if 'viewBox' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg viewBox="0 0 800 450"', 1)
        else:
            svg_code = re.sub(r'viewBox="[^"]+"', 'viewBox="0 0 800 450"', svg_code)
        
        # UTF-8エンコーディングを明示的に指定
        if 'encoding=' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg encoding="UTF-8"', 1)
        
        # フォントファミリーを明示的に指定
        svg_code = re.sub(r'font-family="([^"]*)"', r'font-family="Arial, Helvetica, sans-serif"', svg_code)
        
        logger.info(f"SVG生成完了: 長さ {len(svg_code)} 文字のSVGコードを生成")
        return svg_code, None
        
    except Exception as e:
        return None, log_error("SVG生成中にエラーが発生しました", e)

def get_backup_svg():
    """SVG生成に失敗した場合のバックアップSVGを返す"""
    return '<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg" encoding="UTF-8"><rect width="100%" height="100%" fill="#f8f9fa"/><text x="50%" y="50%" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="#dc3545">SVGデータの生成に失敗しました。もう一度お試しください。</text></svg>'
