"""
法人向けLP企画設計チャットアプリ
このアプリは、GradioとGemini APIを使用して
法人向けランディングページの企画設計をサポートします。
"""
import gradio as gr
import traceback
import os
from utils import (
    GOOGLE_API_KEY, 
    chat_history, 
    current_svg_code, 
    current_analysis, 
    current_theme,
    uploaded_csv_path,
    uploaded_svg_path,
    logger,
    save_uploaded_file,
    clean_temp_files
)
from lp_planner import generate_lp_planning
from csv_analyzer import analyze_csv, get_csv_insights_for_lp_planning

def analyze_uploaded_csv(csv_file):
    """アップロードされたCSVファイルを分析する関数"""
    if not csv_file:
        return "CSVファイルがアップロードされていません。"
    
    # CSVファイルを分析
    csv_analysis = analyze_csv(csv_file)
    
    if not csv_analysis.get("success", False):
        error_msg = csv_analysis.get("error", "不明なエラー")
        return f"CSVファイルの分析中にエラーが発生しました: {error_msg}"
    
    # 分析結果を表示用のテキストとして返す
    return csv_analysis.get("display_text", "分析結果がありません。")

def respond(message, history, csv_file=None, svg_file=None):
    """チャットメッセージに応答する関数"""
    # 入力が空の場合は何も返さない
    if not message.strip():
        return [], None, None, None
    
    # ファイルがアップロードされた場合は保存
    csv_path = None
    svg_path = None
    csv_analysis = None
    csv_insights = None
    csv_analysis_text = None
    
    if csv_file is not None:
        csv_path = csv_file  # すでにパスが得られている
        logger.info(f"CSVファイルが保存されました: {csv_path}")
        
        # CSVファイルを分析
        csv_analysis = analyze_csv(csv_path)
        if csv_analysis.get("success", False):
            csv_analysis_text = csv_analysis.get("display_text", "")
            csv_insights = get_csv_insights_for_lp_planning(csv_analysis)
            logger.info("CSVファイルの分析が完了しました")
        else:
            csv_analysis_text = f"CSVファイルの分析中にエラーが発生しました: {csv_analysis.get('error', '不明なエラー')}"
            logger.error(f"CSVファイルの分析中にエラーが発生しました: {csv_analysis.get('error', '不明なエラー')}")
    
    if svg_file is not None:
        svg_path = svg_file  # すでにパスが得られている
        logger.info(f"SVGファイルが保存されました: {svg_path}")
    
    # LP企画設計モード
    if "LP企画:" in message:
        product_theme = message.replace("LP企画:", "").strip()
        analysis, svg_code, download_link = generate_lp_planning(product_theme, csv_insights, svg_path)
        
        response = f"### {product_theme} の法人向けLP企画分析\n\n{analysis}"
        
        # チャット履歴に追加
        chat_history.append((message, response))
        
        return [(message, response)], svg_code, download_link, csv_analysis_text
    
    # 通常のチャットモード
    elif "こんにちは" in message or "hello" in message.lower():
        response = "こんにちは！どうぞお話しください。LP企画設計をご希望の場合は、「LP企画: 商品名やテーマ」のように入力してください。CSVファイルとSVGファイルをアップロードすることもできます。"
    elif "LP企画" in message or "lp" in message.lower():
        response = "LP企画設計機能を使うには「LP企画: あなたの商品やサービスのテーマ」のように入力してください。"
    elif "使い方" in message:
        response = """
        このチャットアプリの使い方:
        
        1. 通常のチャット: 質問や会話を入力すると応答します
        2. LP企画設計: 「LP企画: 商品名やテーマ」と入力すると、そのテーマについての法人向けLPの企画設計分析とSVG図を生成します
        3. ファイルアップロード: CSVファイル（ターゲット分析データ）やSVGファイル（レイアウト参考）をアップロードして、LP企画設計に活用できます
        4. PowerPoint: SVG図が生成されると、その内容をPowerPointに変換してダウンロードできます
        
        例: 「LP企画: クラウドセキュリティサービス」（オプションでファイルをアップロード）
        """
    elif "元気" in message:
        response = "元気です！あなたはどうですか？"
    elif "さようなら" in message or "goodbye" in message.lower() or "バイバイ" in message:
        response = "さようなら！またお話しましょう。"
    elif "csv" in message.lower() or "ファイル" in message:
        response = "CSVファイルは法人企業のアンケートデータなどを分析に活用できます。SVGファイルはレイアウトの参考として活用できます。ファイルアップロード欄からアップロードしてください。"
    else:
        response = "なるほど、もっと教えてください。LP企画設計をご希望の場合は、「LP企画: 商品名やテーマ」のように入力してください。"
    
    # チャット履歴に追加
    chat_history.append((message, response))
    
    return [(message, response)], None, None, csv_analysis_text

def clear_chat():
    """チャット履歴をクリアする関数"""
    chat_history.clear()
    global current_svg_code, current_analysis, current_theme
    current_svg_code = None
    current_analysis = None
    current_theme = None
    clean_temp_files()  # 一時ファイルを削除
    return [], None, '<div class="svg-container">SVG図がここに表示されます</div>', None, None, None

def on_csv_upload(csv_file):
    """CSVファイルがアップロードされたときの処理"""
    if not csv_file:
        return None, "CSVファイルがアップロードされていません。"
    
    csv_analysis = analyze_csv(csv_file)
    
    if not csv_analysis.get("success", False):
        error_msg = csv_analysis.get("error", "不明なエラー")
        return csv_file, f"CSVファイルの分析中にエラーが発生しました: {error_msg}"
    
    return csv_file, csv_analysis.get("display_text", "分析結果がありません。")

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
        min-height: 600px !important;
        max-height: 800px !important;
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
    .file-upload-area {
        margin-top: 10px;
        padding: 10px;
        border: 1px solid #eee;
        border-radius: 5px;
        background-color: #f9f9f9;
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
    .csv-analysis-area {
        margin-top: 15px;
        padding: 15px;
        border: 1px solid #d0e3ff;
        border-radius: 5px;
        background-color: #f0f7ff;
        overflow-y: auto;
        max-height: 600px;
    }
    .csv-analysis-area h2 {
        color: #0056b3;
        font-size: 1.2rem;
        margin-top: 0;
    }
    .csv-analysis-area h3 {
        color: #0069d9;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    .csv-analysis-area ul {
        margin-top: 5px;
    }
    /* チャット吹き出しのスタイル改善 */
    .chatbot-container .user-message, .chatbot-container .bot-message {
        max-width: 90% !important;
        padding: 12px 16px !important;
    }
    .chatbot-container .bot-message {
        background-color: #f0f7ff !important;
    }
    /* スクロールバーのスタイル */
    .chat-area::-webkit-scrollbar {
        width: 8px;
    }
    .chat-area::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    .chat-area::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    .chat-area::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* Markdownの表示を改善 */
    .bot-message h2 {
        font-size: 1.35rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        color: #0056b3 !important;
        border-bottom: 1px solid #dee2e6 !important;
        padding-bottom: 0.3rem !important;
    }
    .bot-message h3 {
        font-size: 1.2rem !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.7rem !important;
        color: #0069d9 !important;
    }
    .bot-message p {
        margin-bottom: 0.7rem !important;
        line-height: 1.5 !important;
    }
    .bot-message ul, .bot-message ol {
        margin-top: 0.5rem !important;
        margin-bottom: 0.7rem !important;
        padding-left: 1.5rem !important;
    }
    .bot-message li {
        margin-bottom: 0.3rem !important;
    }
    .bot-message hr {
        margin: 1.5rem 0 !important;
        border: 0 !important;
        border-top: 1px solid #dee2e6 !important;
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
            - CSVファイル（ターゲット分析データ）とSVGファイル（レイアウト参考）をアップロードすることができます
            - LP分析にはGemini Flash、SVG図にはGemini 1.5 Proを使用します
            - 生成したSVG図はPowerPointファイルとしてダウンロードできます
            - 通常のチャットには、普通にメッセージを入力してください
            
            **例**: 「LP企画: クラウドセキュリティサービス」
            """)
        
        with gr.Row():
            # 左側カラム（チャットエリアとファイルアップロード）
            with gr.Column(scale=3):  # 幅を拡大
                # チャットエリア
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    elem_classes="chat-area chatbot-container",
                    bubble_full_width=False,
                    avatar_images=(None, "https://api.dicebear.com/7.x/thumbs/svg?seed=Aneka"),
                    height=700  # 高さを増加
                )
                
                # ファイルアップロードエリア
                with gr.Row(elem_classes="file-upload-area"):
                    csv_file = gr.File(
                        label="CSVファイルをアップロード（オプション）",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    svg_file = gr.File(
                        label="SVGファイルをアップロード（オプション）",
                        file_types=[".svg"],
                        type="filepath"
                    )
                
                # チャット入力エリア
                with gr.Row(elem_classes="input-area"):
                    txt = gr.Textbox(
                        scale=4,
                        show_label=False,
                        placeholder="メッセージを入力するか、「LP企画: テーマ」と入力してください...",
                        container=False,
                        lines=2  # 入力エリアを2行に
                    )
                    submit_btn = gr.Button("送信", scale=1)
                
                clear_btn = gr.Button("会話をクリア")
            
            # 右側カラム（結果表示部分）
            with gr.Column(scale=2):
                with gr.Tab("SVG出力"):
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
                
                with gr.Tab("CSVデータ分析"):
                    # CSVデータ分析結果表示エリア
                    csv_analysis_output = gr.Markdown(
                        value="CSVファイルをアップロードすると、ここに分析結果が表示されます。",
                        elem_classes="csv-analysis-area"
                    )
        
        # イベントの設定
        # CSVファイルアップロード時の処理
        csv_file.change(
            on_csv_upload, 
            inputs=[csv_file], 
            outputs=[csv_file, csv_analysis_output]
        )
        
        # メッセージ送信イベント（テキストボックスからのEnter）
        txt_submit_event = txt.submit(respond, [txt, chatbot, csv_file, svg_file], [chatbot, svg_output, download_area, csv_analysis_output], queue=False)
        txt_submit_event.then(lambda: "", None, txt)
        
        # メッセージ送信イベント（ボタンクリック）
        submit_click_event = submit_btn.click(respond, [txt, chatbot, csv_file, svg_file], [chatbot, svg_output, download_area, csv_analysis_output], queue=False)
        submit_click_event.then(lambda: "", None, txt)
        
        # クリアボタンのイベント
        clear_btn.click(clear_chat, None, [chatbot, svg_output, svg_output, download_area, csv_file, svg_file])
    
    return demo

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("警告: Google API Keyが設定されていません。環境変数GOOGLE_API_KEYを設定してください。")
    
    try:
        app = create_app()
        app.launch(share=True)
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"アプリケーション起動中にエラーが発生しました: {str(e)}")
        print(f"詳細なエラー情報:\n{error_detail}")
