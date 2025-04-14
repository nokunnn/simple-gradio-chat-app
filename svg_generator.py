"""Claude 3.7 Sonnetを使用したSVG生成機能"""
import re
import anthropic
from utils import ANTHROPIC_API_KEY, log_error, logger

# Claude APIの設定
claude_client = None
if ANTHROPIC_API_KEY:
    claude_client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        # ベータヘッダーをここでクライアント初期化時に追加
        default_headers={"anthropic-beta": "output-128k-2025-02-19"}
    )

def generate_svg_with_claude(product_theme, analysis_text):
    """Claude 3.7 SonnetにGeminiの分析結果を渡してSVGを生成する関数"""
    if not ANTHROPIC_API_KEY or not claude_client:
        return None, "エラー: Anthropic API Keyが設定されていません。環境変数ANTHROPIC_API_KEYを設定してください。"
    
    try:
        # Claude 3.7 Sonnetへのプロンプト
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマとその分析に基づいて、法人向けLPの企画設計のためのSVGスライドを作成してください。

        商品/サービステーマ: {product_theme}

        Gemini AIによる分析結果:
        {analysis_text}

        上記の分析結果に基づいて、以下の流れで検討を行いSVGスライドを作成してください:
         1. 「ターゲットの分析」、「訴求軸の検討」、「訴求シナリオの検討」の３つの内容を要約する
         2.下記のsvg要件を考慮し見やすやを考慮して全体のレイアウトを検討する
         3.レイアウトにうまく収まるように要約内容のテキストを配置する（必ず３つの内容を盛り込んでください）。また適宜アイコン等を配置してください。
         4.上記の検討内容をSVG形式の１枚のスライドにまとめる。サイズは16:9の比率で設定する（width="800" height="450"）。その際下記の留意事項の内容も反映する。
 
         SVG要件:
         - サイズは16:9の比率で設定してください（width="800" height="450"）
         - ビジネス文書・プレゼンテーションとしての体裁を重視してください
         - 青系のビジネスカラーを貴重色としてください
         - 明確なタイトル、サブタイトル、箇条書きなどの階層構造を持たせてください
         - フォントはシンプルで読みやすいサンセリフフォントを使用してください（例: Arial, Helvetica, sans-serif）
         - 図表を使用する場合は、シンプルかつビジネス的な印象のデザインにしてください
         - テキストは必ず枠内に収まるように調整し、はみ出さないようにしてください
         - 情報量は適切に調整し、文字が小さくなり過ぎないようにしてください
         - フォントサイズは小さくても10px以上を維持してください
         - 日本語を含む場合は、文字化けしないように適切なフォントやエンコーディングを指定してください
         
         留意事項:
         - SVGのコードだけを出力してください。必ず<svg>タグで始まり</svg>タグで終わる完全な形式で記述してください。
         - コードの前後に説明文やマークダウンなどは不要です。SVGコード以外は一切出力しないでください。
        """
        
        # Claude 3.7 Sonnetからの応答を取得（ストリーミングAPIを使用し、最大出力トークン数を128kに拡張）
        svg_text = ""
        with claude_client.messages.stream(
            model="claude-3-7-sonnet-20250219",
            max_tokens=128000,  # 最大トークン長を128kに拡張
            temperature=0.1,
            system="あなたは、SVGフォーマットの高品質なビジネスプレゼンテーションスライドを作成する専門家です。提供された分析結果に基づいて、法人向けLPの企画設計のためのSVGを作成してください。日本語を含むテキストが文字化けしないよう注意してください。",
            messages=[
                {"role": "user", "content": prompt}
            ]
            # beta_headersはクライアント初期化時に設定
        ) as stream:
            # ストリーミングレスポンスを集約
            for text in stream.text_stream:
                svg_text += text
        
        # SVGコードを抽出（Claude 3.7はほぼ確実に正確なSVGを返すはずですが、念のため）
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
