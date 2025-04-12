import gradio as gr

# チャット履歴を保存するリスト
chat_history = []

def respond(message, history):
    """チャットメッセージに応答する関数"""
    # 入力が空の場合は何も返さない
    if not message.strip():
        return ""
    
    # 簡単な応答ロジック
    if "こんにちは" in message or "hello" in message.lower():
        response = "こんにちは！どうぞお話しください。"
    elif "元気" in message:
        response = "元気です！あなたはどうですか？"
    elif "天気" in message:
        response = "今日はいい天気ですね！"
    elif "名前" in message:
        response = "私はGradioで作られたシンプルなチャットボットです。"
    elif "さようなら" in message or "goodbye" in message.lower() or "バイバイ" in message:
        response = "さようなら！またお話しましょう。"
    else:
        response = "なるほど、もっと教えてください。"
    
    # チャット履歴に追加
    chat_history.append((message, response))
    
    return response

def clear_chat():
    """チャット履歴をクリアする関数"""
    chat_history.clear()
    return None

# Gradio インターフェースの作成
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 💬 簡単なチャットアプリ")
    gr.Markdown("こんにちは、質問や会話を入力してみてください！")
    
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, "https://api.dicebear.com/7.x/thumbs/svg?seed=Aneka"),
    )
    
    with gr.Row():
        txt = gr.Textbox(
            scale=3,
            show_label=False,
            placeholder="メッセージを入力してください...",
            container=False,
        )
        submit_btn = gr.Button("送信", scale=1)
    
    clear_btn = gr.Button("会話をクリア")
    
    # イベントの設定
    txt.submit(respond, [txt, chatbot], [chatbot])
    txt.submit(lambda: "", None, [txt])
    
    submit_btn.click(respond, [txt, chatbot], [chatbot])
    submit_btn.click(lambda: "", None, [txt])
    
    clear_btn.click(clear_chat, None, [chatbot])

if __name__ == "__main__":
    demo.launch(share=True)
