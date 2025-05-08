"""Gemini 1.5 Proを使用したSVG生成機能"""
import re
import time
import random
import google.generativeai as genai
from utils import GOOGLE_API_KEY, log_error, logger, read_svg_content

# Gemini APIの設定
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_svg_with_gemini(product_theme, analysis_text, svg_path=None):
    """Gemini 1.5 ProにGeminiの分析結果を渡してSVGを生成する関数"""
    if not GOOGLE_API_KEY:
        return None, "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。"
    
    # 最大再試行回数と初期カウンタ
    max_retries = 3
    retry_count = 0
    
    # 参考SVGが提供されている場合、そのコンテンツを読み込む
    reference_svg = None
    if svg_path:
        reference_svg = read_svg_content(svg_path)
        logger.info(f"参考SVGファイルを読み込みました: {svg_path}")
    
    # 再試行ロジックを実装
    while retry_count < max_retries:
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

            SVGスライドを作成する上では以下に示す順序で検討してください。

            ##検討１：分析結果の要約
            -上記の分析結果に基づいて、以下の3つの観点を含むSVGスライドを作成してください
             1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
             2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
             3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

             ##検討２：分析結果のレイアウトとSVGの生成
             -検討１における分析結果の要約内容を下記のSVG要件を踏まえて適切にレイアウトしてください
             -レイアウトに基づきSVGを生成してください。その際下記の留意事項の内容も反映してください

             #SVG要件:
             - 読み込んだ参考SVGのレイアウトを参照してください
             - サイズは16:9の比率で設定してください（width="800" height="450"）
             - ビジネス文書・プレゼンテーションとしての体裁を重視してください
             - 企業向けパワーポイントのスライドとしての活用を想定してください
             - 明確なタイトル、サブタイトル、箇条書きなどの階層構造を持たせてください
             - フォントはシンプルで読みやすいサンセリフフォントを使用してください（例: Arial, Helvetica, sans-serif）
             - 適切なマージンとパディングを取り、余白を効果的に活用してください
             - 図表を使用する場合は、シンプルかつビジネス的な印象のデザインにしてください
             - テキストは必ず枠内に収まるように調整し、はみ出さないようにしてください
             - 情報量は適切に調整し、文字が小さくなり過ぎないようにしてください
             - フォントサイズは小さくても10px以上を維持してください
             - 3つの観点を全て1つのSVGに包含してください
             - 提供された分析結果の重要なポイントを活用してください
             - 日本語を含む場合は、文字化けしないように適切なフォントやエンコーディングを指定してください

             #留意事項
             - 上記の分析結果の内容を要約して、SVG形式の１枚のスライドにまとめて。
             - サイズは16:9の比率で設定してください（width="800" height="450"）
             - SVGのコードだけを出力してください。必ず<svg>タグで始まり</svg>タグで終わる完全な形式で記述してください。
             - コードの前後に説明文やマークダウンなどは不要です。SVGコード以外は一切出力しないでください。
            """
            
            # 参考SVGがある場合、プロンプトに追加
            if reference_svg:
                prompt += f"""
                
                #参考SVGの活用:
                以下に参考としてSVGファイルが提供されています。このSVGのレイアウト、デザイン、構成要素の配置方法などを参考にして、新しいSVGを作成してください。参考SVGの良い部分（構成、配色、レイアウト、視覚的なバランスなど）を取り入れつつ、上記の分析結果に適合するようにコンテンツを調整してください。
                
                参考SVGコード:
                {reference_svg}
                
                ただし、参考SVGのデザインをそのまま模倣するのではなく、参考SVGのレイアウトやデザインの良い点を取り入れながら、上記のテーマと分析結果に合わせて新しいSVGを作成してください。
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
            error_message = str(e)
            # レート制限エラー(429)をチェック
            if "429" in error_message and "exceeded your current quota" in error_message and retry_count < max_retries - 1:
                # エラーメッセージから推奨される遅延時間を抽出しようとする
                retry_delay_match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', error_message)
                
                if retry_delay_match:
                    # APIから提案された遅延時間を使用
                    delay_seconds = int(retry_delay_match.group(1))
                else:
                    # 指数バックオフ + ジッター（ランダム化）
                    delay_seconds = (2 ** retry_count) + random.uniform(0, 1)
                
                # 安全のために最大遅延を設定
                delay_seconds = min(delay_seconds, 60)  # 最大1分
                
                logger.warning(f"APIレート制限に達しました。{delay_seconds}秒後に再試行します（{retry_count + 1}/{max_retries}）")
                time.sleep(delay_seconds)
                retry_count += 1
                
                # フォールバック：再試行回数が多い場合は、gemini-2.0-flashモデルを試す
                if retry_count >= 2:
                    try:
                        logger.info("Gemini 1.5 Proでのレート制限により、代替としてGemini 2.0 Flashでの生成を試みます")
                        return generate_basic_svg_with_flash(product_theme, analysis_text), None
                    except Exception as flash_error:
                        logger.warning(f"Gemini 2.0 Flashでの生成も失敗しました: {str(flash_error)}")
            else:
                # その他のエラーまたは最大再試行回数に達した場合
                error_msg = log_error("SVG生成中にエラーが発生しました", e)
                # 簡易版のSVGを生成
                return generate_fallback_svg(product_theme, analysis_text), error_msg
    
    # 最大再試行回数に達した場合
    return generate_fallback_svg(product_theme, analysis_text), "APIレート制限のため、SVGの生成に失敗しました。簡易版のSVGを表示します。"

def generate_basic_svg_with_flash(product_theme, analysis_text):
    """Gemini 2.0 Flashを使った簡易版SVG生成（APIレート制限時のフォールバック）"""
    try:
        # Gemini 2.0 Flash モデルの初期化（より低いクォータ）
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # より短い簡略化したプロンプト
        prompt = f"""
        以下の内容に基づいて、シンプルなSVGスライドを作成してください。
        
        テーマ: {product_theme}
        
        内容:
        {analysis_text[:2000]}  <!-- 長すぎる場合は切り詰め -->
        
        要件:
        - サイズは800x450ピクセル（16:9比率）
        - シンプルなビジネス向けデザイン
        - 3つのセクション：ターゲット分析、訴求軸、訴求シナリオ
        - 読みやすいフォント、適切な余白
        - SVGコードのみを出力（説明なし）
        """
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答からSVGコードを抽出
        svg_text = response.text
        svg_match = re.search(r'<svg[\s\S]*?<\/svg>', svg_text)
        svg_code = svg_match.group(0) if svg_match else svg_text
        
        # SVGコードの調整
        svg_code = re.sub(r'width="[0-9]+"', 'width="800"', svg_code)
        svg_code = re.sub(r'height="[0-9]+"', 'height="450"', svg_code)
        
        if 'viewBox' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg viewBox="0 0 800 450"', 1)
        
        if 'encoding=' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg encoding="UTF-8"', 1)
        
        logger.info("Gemini 2.0 Flashを使用した代替SVG生成に成功しました")
        return svg_code
        
    except Exception as e:
        logger.error(f"代替SVG生成中にエラー: {str(e)}")
        return get_backup_svg()

def generate_fallback_svg(product_theme, analysis_text):
    """APIを使わない独自のフォールバックSVG生成機能"""
    try:
        # 分析テキストから主要ポイントを抽出
        # マークダウン見出しを検索して主要セクションを見つける
        target_section = ""
        appeal_section = ""
        scenario_section = ""
        
        # 簡易的なテキスト解析で主要ポイントを抽出
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "ターゲット" in line and ("##" in line or "#" in line):
                current_section = "target"
                continue
            elif "訴求軸" in line and ("##" in line or "#" in line):
                current_section = "appeal"
                continue
            elif "シナリオ" in line and ("##" in line or "#" in line):
                current_section = "scenario"
                continue
                
            if current_section == "target" and line and not line.startswith('#'):
                target_section += line + " "
                if len(target_section) > 200:  # 適当な長さで切る
                    break
            elif current_section == "appeal" and line and not line.startswith('#'):
                appeal_section += line + " "
                if len(appeal_section) > 200:
                    break
            elif current_section == "scenario" and line and not line.startswith('#'):
                scenario_section += line + " "
                if len(scenario_section) > 200:
                    break
        
        # 文字列が長すぎる場合は適切に切り詰める
        def truncate_text(text, max_length=200):
            if len(text) <= max_length:
                return text
            # 最後の文の途中で切れないように調整
            truncated = text[:max_length]
            last_period = truncated.rfind('。')
            if last_period > max_length * 0.7:  # 十分な長さがある場合
                return truncated[:last_period+1]
            return truncated + "..."
        
        target_section = truncate_text(target_section)
        appeal_section = truncate_text(appeal_section)
        scenario_section = truncate_text(scenario_section)
        
        # 簡易的なSVGを生成
        svg_code = f'''<svg width="800" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg" encoding="UTF-8">
            <!-- 背景 -->
            <rect width="800" height="450" fill="#f8f9fa"/>
            
            <!-- タイトル -->
            <rect x="0" y="0" width="800" height="60" fill="#1a73e8"/>
            <text x="400" y="38" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">{product_theme} - LP企画設計</text>
            
            <!-- セクション1: ターゲット分析 -->
            <rect x="40" y="80" width="220" height="320" fill="#e8f0fe" rx="5" ry="5"/>
            <text x="150" y="110" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="#1a73e8" text-anchor="middle">ターゲットの分析</text>
            <foreignObject x="50" y="120" width="200" height="270">
                <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #333; padding: 10px;">
                    {target_section}
                </div>
            </foreignObject>
            
            <!-- セクション2: 訴求軸 -->
            <rect x="290" y="80" width="220" height="320" fill="#e8f0fe" rx="5" ry="5"/>
            <text x="400" y="110" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="#1a73e8" text-anchor="middle">訴求軸の検討</text>
            <foreignObject x="300" y="120" width="200" height="270">
                <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #333; padding: 10px;">
                    {appeal_section}
                </div>
            </foreignObject>
            
            <!-- セクション3: 訴求シナリオ -->
            <rect x="540" y="80" width="220" height="320" fill="#e8f0fe" rx="5" ry="5"/>
            <text x="650" y="110" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="#1a73e8" text-anchor="middle">訴求シナリオ</text>
            <foreignObject x="550" y="120" width="200" height="270">
                <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #333; padding: 10px;">
                    {scenario_section}
                </div>
            </foreignObject>
            
            <!-- フッター -->
            <rect x="0" y="420" width="800" height="30" fill="#f1f3f4"/>
            <text x="400" y="440" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#666" text-anchor="middle">APIレート制限により簡易表示モードで生成されました</text>
        </svg>'''
        
        logger.info("フォールバックSVGを独自生成しました")
        return svg_code
        
    except Exception as e:
        logger.error(f"フォールバックSVG生成中にエラー: {str(e)}")
        return get_backup_svg()

def get_backup_svg():
    """SVG生成に失敗した場合のバックアップSVGを返す"""
    return '<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg" encoding="UTF-8"><rect width="100%" height="100%" fill="#f8f9fa"/><text x="50%" y="50%" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" fill="#dc3545">SVGデータの生成に失敗しました。もう一度お試しください。</text></svg>'
