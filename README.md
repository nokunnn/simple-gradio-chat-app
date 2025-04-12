# 簡単なGradioチャットアプリ

このリポジトリは、Gradioを使用した簡単なチャットアプリケーションの実装例です。

## 機能

- テキストベースのチャットインターフェース
- 簡単な応答ロジック（キーワードベース）
- チャット履歴の表示
- チャット履歴のクリア機能

## セットアップ

### 必要条件

- Python 3.7以上

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/nokunnn/simple-gradio-chat-app.git
cd simple-gradio-chat-app
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

## 使用方法

アプリケーションを実行：
```bash
python app.py
```

ブラウザで `http://localhost:7860` を開くと、チャットインターフェースが表示されます。

## カスタマイズ

応答ロジックは `app.py` の `respond()` 関数で定義されています。必要に応じて、キーワードと応答を追加・変更してカスタマイズできます。

## ライセンス

MITライセンス
