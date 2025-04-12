import gradio as gr
import os
import json
import google.generativeai as genai
from pathlib import Path
import io
import base64
import re
import traceback
import time

# Google Gemini API Key設定
# 実際に使用する際には環境変数から読み込むことをお勧めします
# os.environ["GOOGLE_API_KEY"] = "あなたのAPIキーをここに入力"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Gemini APIの設定
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# チャット履歴を保存するリスト
chat_history = []

def generate_lp_planning(product_theme):
    """Gemini APIを使用してLP企画のための分析を生成する関数"""
    if not GOOGLE_API_KEY:
        return "エラー: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。", None
    
    try:
        # Geminiモデルの生成
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # プロンプトテンプレート
        prompt = f"""
        あなたは法人向けのランディングページ(LP)の企画設計のエキスパートです。
        以下の商品/サービステーマに対して、法人向けLPの企画設計を行ってください。

        商品/サービステーマ: {product_theme}

        以下の3つの観点から分析してください:
        1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
        2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
        3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

        回答は2つの部分に分けてください:

        【パート1】詳細な分析
        各観点について詳細に説明し、具体的な提案を含めてください。
        
        【パート2】要約と視覚化
        分析内容の重要ポイントを簡潔に要約し、それを以下の条件でSVGデータとして表現してください:
        
        SVG要件:
        - サイズは16:9の比率で設定してください（例: width="800" height="450"）
        - ビジネス文書・プレゼンテーションとしての体裁を重視してください
        - 企業向けパワーポイントのスライドとしての活用を想定してください
        - プロフェッショナルなカラースキームを使用してください（青系のビジネスカラーが適切です）
        - 明確なタイトル、サブタイトル、箇条書きなどの階層構造を持たせてください
        - フォントはシンプルで読みやすいサンセリフフォントを使用してください
        - 適切なマージンとパディングを取り、余白を効果的に活用してください
        - 図表を使用する場合は、シンプルかつビジネス的な印象のデザインにしてください
        - テキストは必ず枠内に収まるように調整し、はみ出さないようにしてください
        - 情報量は適切に調整し、文字が小さくなり過ぎないようにしてください
        - パート１における３つの観点の検討結果を全て記載してください
        - フォントサイズは小さくても12px以上を維持してください
        - 必ず完全なSVGコード（<svg>タグから</svg>タグまで）を提供してください

        SVGのコードは<svg>タグで始まり</svg>タグで終わる完全な形式で必ず記述してください。
        """
        
        # Geminiからの応答を取得
        response = model.generate_content(prompt)
        
        # 応答から分析部分とSVGコードを分離
        full_response = response.text
        
        # SVGコードを抽出
        svg_match = re.search(r'<svg[\s\S]*?<\/svg>', full_response)
        svg_code = svg_match.group(0) if svg_match else None
        
        # SVGが見つからない場合の処理
        if not svg_code:
            analysis_text = full_response
            svg_code = '<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#f8f9fa"/><text x="50%" y="50%" text-anchor="middle" font-family="Arial" font-size="18" fill="#dc3545">SVGデータの生成に失敗しました。もう一度お試しください。</text></svg>'
        else:
            # SVGを除いた分析テキスト部分
            analysis_text = full_response.replace(svg_code, '')
            
            # SVGのサイズを800x450（16:9）に変更
            svg_code = re.sub(r'width="[0-9]+"', 'width="800"', svg_code)
            svg_code = re.sub(r'height="[0-9]+"', 'height="450"', svg_code)
            
            # viewBox属性を調整
            if 'viewBox' not in svg_code:
                svg_code = svg_code.replace('<svg', '<svg viewBox="0 0 800 450"')
            else:
                svg_code = re.sub(r'viewBox="[^"]+"', 'viewBox="0 0 800 450"', svg_code)
        
        return analysis_text, svg_code
        
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"詳細なエラー情報:\n{error_detail}")
        return f"エラーが発生しました: {str(e)}", None

def respond(message, history):
    """チャットメッセージに応答する関数"""
    # 入力が空の場合は何も返さない
    if not message.strip():
        return [], None
    
    # LP企画設計モード
    if "LP企画:" in message:
        product_theme = message.replace("LP企画:", "").strip()
        analysis, svg_code = generate_lp_planning(product_theme)
        
        response = f"### {product_theme} の法人向けLP企画分析\n\n{analysis}"
        
        # チャット履歴に追加
        chat_history.append((message, response))
        
        return [(message, response)], svg_code
    
    # 通常のチャットモード
    elif "こんにちは" in message or "hello" in message.lower():
        response = "こんにちは！どうぞお話しください。LP企画設計をご希望の場合は、「LP企画: 商品名やテーマ」のように入力してください。"
    elif "LP企画" in message or "lp" in message.lower():
        response = "LP企画設計機能を使うには「LP企画: あなたの商品やサービスのテーマ」のように入力してください。"
    elif "使い方" in message:
        response = """
        このチャットアプリの使い方:
        
        1. 通常のチャット: 質問や会話を入力すると応答します
        2. LP企画設計: 「LP企画: 商品名やテーマ」と入力すると、そのテーマについての法人向けLPの企画設計分析とSVG図を生成します
        
        例: 「LP企画: クラウドセキュリティサービス」
        """
    elif "元気" in message:
        response = "元気です！あなたはどうですか？"
    elif "さようなら" in message or "goodbye" in message.lower() or "バイバイ" in message:
        response = "さようなら！またお話しましょう。"
    else:
        response = "なるほど、もっと教えてください。LP企画設計をご希望の場合は、「LP企画: 商品名やテーマ」のように入力してください。"
    
    # チャット履歴に追加
    chat_history.append((message, response))
    
    return [(message, response)], None

def clear_chat():
    """チャット履歴をクリアする関数"""
    chat_history.clear()
    return [], None

# Gradio インターフェースの作成
with gr.Blocks(css="""
    .svg-container { 
        margin: 10px auto;
        border: 1px solid #ccc; 
        padding: 10px;
        background-color: white;
        width: 90%;
        max-width: 800px;
        text-align: center;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    .svg-container svg {
        width: 100%;
        height: auto;
        max-height: 450px;
        overflow: visible;
    }
    footer { visibility: hidden }
    .responsive-layout {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    .chat-area {
        min-height: 350px;
        max-height: 400px;
    }
    .title-area {
        margin-bottom: 5px;
    }
    .input-area {
        margin-top: 10px;
    }
""") as demo:
    with gr.Column(elem_classes="title-area"):
        gr.Markdown("# 💬 法人向けLP企画設計チャットアプリ")
        gr.Markdown("""
        このアプリは、商品やサービスのテーマに基づいて法人向けLPの企画設計をサポートします。
        
        **使い方**: 
        - 「LP企画: 商品名やテーマ」と入力すると、LP企画設計の分析とSVG図を生成します
        - 通常のチャットには、普通にメッセージを入力してください
        
        **例**: 「LP企画: クラウドセキュリティサービス」
        """)
    
    with gr.Column(elem_classes="responsive-layout"):
        # チャットエリア
        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            elem_classes="chat-area",
            bubble_full_width=False,
            avatar_images=(None, "https://api.dicebear.com/7.x/thumbs/svg?seed=Aneka"),
            height=350
        )
        
        # SVG出力エリア
        svg_output = gr.HTML(
            value='<div class="svg-container">SVG図がここに表示されます</div>', 
            elem_id="svg-output"
        )
    
        with gr.Row(elem_classes="input-area"):
            txt = gr.Textbox(
                scale=4,
                show_label=False,
                placeholder="メッセージを入力するか、「LP企画: テーマ」と入力してください...",
                container=False,
            )
            submit_btn = gr.Button("送信", scale=1)
    
        clear_btn = gr.Button("会話をクリア")
    
    # イベントの設定（ストリーミングを無効化し、通常の応答に戻す）
    txt_submit_event = txt.submit(respond, [txt, chatbot], [chatbot, svg_output], queue=False)
    txt_submit_event.then(lambda: "", None, [txt])
    
    submit_click_event = submit_btn.click(respond, [txt, chatbot], [chatbot, svg_output], queue=False)
    submit_click_event.then(lambda: "", None, [txt])
    
    clear_btn.click(clear_chat, None, [chatbot, svg_output])

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("警告: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。")
    
    try:
        demo.launch(share=True)
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"アプリケーション起動中にエラーが発生しました: {str(e)}")
        print(f"詳細なエラー情報:\n{error_detail}")
