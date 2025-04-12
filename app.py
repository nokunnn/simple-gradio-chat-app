import gradio as gr
import os
import json
import google.generativeai as genai
from pathlib import Path
import io
import base64
import re
import traceback

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

        以下の3つの観点から分析し、詳細に説明してください:
        1. ターゲットの分析: このサービス/商品の理想的な法人顧客はどのような企業か、どのような課題を持っているのか
        2. 訴求軸の検討: 商品/サービスの最も魅力的な特徴と、それによって解決される顧客の課題
        3. 訴求シナリオの検討: LPで情報を伝達する最適な順序、各セクションで伝えるべき内容

        回答は分析的かつ実用的な内容にし、各セクションで具体的な提案をしてください。
        最後に、これらの分析をパワーポイントスライドに変換するためのSVGデータとして、
        簡潔なフローチャートか図解を提案してください。SVGコードを含めてください。

        SVGのコードは<svg>タグで始まり</svg>タグで終わる完全な形式で提供してください。
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
            svg_code = None
        else:
            # SVGを除いた分析テキスト部分
            analysis_text = full_response.replace(svg_code, '')
        
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
    .svg-container { margin-top: 20px; border: 1px solid #ccc; padding: 10px; }
    footer { visibility: hidden }
""") as demo:
    gr.Markdown("# 💬 法人向けLP企画設計チャットアプリ")
    gr.Markdown("""
    このアプリは、商品やサービスのテーマに基づいて法人向けLPの企画設計をサポートします。
    
    **使い方**: 
    - 「LP企画: 商品名やテーマ」と入力すると、LP企画設計の分析とSVG図を生成します
    - 通常のチャットには、普通にメッセージを入力してください
    
    **例**: 「LP企画: クラウドセキュリティサービス」
    """)
    
    with gr.Row():
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                bubble_full_width=False,
                avatar_images=(None, "https://api.dicebear.com/7.x/thumbs/svg?seed=Aneka"),
                height=400
            )
        
        with gr.Column(scale=3):
            svg_output = gr.HTML(
                value='<div class="svg-container">SVG図がここに表示されます</div>', 
                elem_id="svg-output"
            )
    
    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="メッセージを入力するか、「LP企画: テーマ」と入力してください...",
            container=False,
        )
        submit_btn = gr.Button("送信", scale=1)
    
    clear_btn = gr.Button("会話をクリア")
    
    # イベントの設定
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
