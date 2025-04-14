"""
法人向けLP企画設計チャットアプリ
このアプリは、GradioとLLM（Gemini API、Claude API）を使用して
法人向けランディングページの企画設計をサポートします。
"""
import gradio as gr
import traceback
from utils import (
    GOOGLE_API_KEY, 
    ANTHROPIC_API_KEY, 
    chat_history, 
    current_svg_code, 
    current_analysis, 
    current_theme,
    logger
)
from lp_planner import generate_lp_planning

def respond(message, history):
    """チャットメッセージに応答する関数"""
    # 入力が空の場合は何も返さない
    if not message.strip():
        return [], None, None
    
    # LP企画設計モード
    if "LP企画:" in message:
        product_theme = message.replace("LP企画:", "").strip()
        analysis, svg_code, download_link = generate_lp_planning(product_theme)
        
        response = f"### {product_theme} の法人向けLP企画分析\n\n{analysis}"
        
        # チャット履歴に追加
        chat_history.append((message, response))
        
        return [(message, response)], svg_code, download_link
    
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
        3. PowerPoint: SVG図が生成されると、その内容をPowerPointに変換してダウンロードできます
        
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
    
    return [(message, response)], None, None

def clear_chat():
    """チャット履歴をクリアする関数"""
    chat_history.clear()
    global current_svg_code, current_analysis, current_theme
    current_svg_code = None
    current_analysis = None
    current_theme = None
    return [], None, '<div class="svg-container">SVG図がここに表示されます</div>', None

# CSSスタイル
CSS = """
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
    .button-row {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    .download-link {
        display: inline-block;
        padding: 10px 20px;
        background-color: #28a745;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        transition: background-color 0.2s;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .download-link:hover {
        background-color: #218838;
        text-decoration: none;
    }
    .download-link:active {
        background-color: #1e7e34;
    }
"""

# Gradio インターフェースの作成
def create_app():
    """Gradioアプリケーションを作成する"""
    with gr.Blocks(css=CSS) as demo:
        with gr.Column(elem_classes="title-area"):
            gr.Markdown("# 💬 法人向けLP企画設計チャットアプリ")
            gr.Markdown("""
            このアプリは、商品やサービスのテーマに基づいて法人向けLPの企画設計をサポートします。
            
            **使い方**: 
            - 「LP企画: 商品名やテーマ」と入力すると、LP企画設計の分析とSVG図を生成します
            - テキスト分析はGoogle Gemini、SVG図はAnthropic Claudeで生成します
            - SVG図はGeminiの分析結果に基づいて生成されます
            - 生成したSVG図はPowerPointファイルとしてダウンロードできます
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
            
            # ダウンロードボタン/リンク表示エリア
            download_area = gr.HTML(
                value='', 
                elem_id="download-area"
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
        
        # イベントの設定
        # メッセージ送信イベント（テキストボックスからのEnter）
        txt_submit_event = txt.submit(respond, [txt, chatbot], [chatbot, svg_output, download_area], queue=False)
        txt_submit_event.then(lambda: "", None, txt)
        
        # メッセージ送信イベント（ボタンクリック）
        submit_click_event = submit_btn.click(respond, [txt, chatbot], [chatbot, svg_output, download_area], queue=False)
        submit_click_event.then(lambda: "", None, txt)
        
        # クリアボタンのイベント
        clear_btn.click(clear_chat, None, [chatbot, svg_output, svg_output, download_area])
    
    return demo

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("警告: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。")
    
    if not ANTHROPIC_API_KEY:
        print("警告: Anthropic API Keyが設定されていません。環境変数ANTHROPIC_API_KEYを設定してください。")
    
    try:
        app = create_app()
        app.launch(share=True)
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"アプリケーション起動中にエラーが発生しました: {str(e)}")
        print(f"詳細なエラー情報:\n{error_detail}")
