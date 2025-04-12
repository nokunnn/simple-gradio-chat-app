# 法人向けLP企画設計チャットアプリ

このリポジトリは、Gradioを使用したチャットアプリケーションで、Google Gemini APIを活用して法人向けランディングページ（LP）の企画設計をサポートする機能を備えています。

## 機能

### 基本機能
- テキストベースのチャットインターフェース
- チャット履歴の表示
- チャット履歴のクリア機能

### LP企画設計機能
- ユーザーが指定した商品/サービステーマに基づいて法人向けLPの企画分析を生成
- 以下の3つの観点から詳細な分析を提供：
  1. ターゲットの分析
  2. 訴求軸の検討
  3. 訴求シナリオの検討
- 分析結果をパワーポイントスライド用のSVGとして出力

## セットアップ

### 必要条件

- Python 3.7以上
- Google Gemini API キー

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

3. Google Gemini API キーを環境変数に設定
```bash
# Linuxまたは Mac
export GOOGLE_API_KEY="あなたのAPIキー"

# Windows (コマンドプロンプト)
set GOOGLE_API_KEY=あなたのAPIキー

# Windows (PowerShell)
$env:GOOGLE_API_KEY="あなたのAPIキー"
```

または、app.pyファイル内で直接設定することもできます（セキュリティ上推奨されません）：
```python
os.environ["GOOGLE_API_KEY"] = "あなたのAPIキーをここに入力"
```

## 使用方法

1. アプリケーションを実行：
```bash
python app.py
```

2. ブラウザで `http://localhost:7860` を開くと、チャットインターフェースが表示されます。

### LP企画設計機能の使い方

「LP企画: 商品名やテーマ」のように入力することで、LP企画設計機能を使用できます。

例：
- 「LP企画: クラウドセキュリティサービス」
- 「LP企画: AI搭載データ分析ツール」
- 「LP企画: 企業向けコミュニケーションプラットフォーム」

入力後、アプリケーションはGoogle Gemini APIを使用して分析を行い、結果をテキストと共にSVGデータとして表示します。

## カスタマイズ

- LP企画設計のプロンプトは `app.py` の `generate_lp_planning()` 関数内で定義されています。必要に応じてカスタマイズできます。
- SVGの表示スタイルは `gr.Blocks()` 内のCSSで調整できます。

## ライセンス

MITライセンス
