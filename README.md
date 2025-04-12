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
- 分析内容を以下の形式で出力:
  - 詳細な分析テキスト
  - 要約を含む16:9比率のSVG図表（パワーポイントスライド向け）

## 最適化されたSVG出力

分析結果は以下の特徴を持つSVGで視覚化されます：

- **16:9のワイドスクリーン比率**: パワーポイントスライドに最適なサイズ設定（1600×900ピクセル）
- **内容の要約**: 詳細分析の要点をまとめた視覚的な表現
- **適切なレイアウト**: 情報が見やすく配置されたデザイン
- **フローチャートや図表**: 関連性や流れを視覚的に表現
- **直接使用可能**: SVGをダウンロードしてそのままプレゼン資料に利用可能

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

入力後、アプリケーションはGoogle Gemini APIを使用して分析を行い、結果をテキストと共にSVGデータとして表示します。SVGは16:9比率で生成され、パワーポイントスライドとして利用しやすい形式になっています。

## Google Colabでの実行方法

Google Colabを使用して以下の手順でアプリケーションを実行できます：

```python
# リポジトリをクローン
!git clone https://github.com/nokunnn/simple-gradio-chat-app.git
%cd simple-gradio-chat-app

# 必要なパッケージをインストール
!pip install -r requirements.txt

# Google Gemini APIキーを設定
import os
os.environ["GOOGLE_API_KEY"] = "あなたのGemini APIキーをここに入力"

# アプリを実行
!python app.py
```

実行後、Colabの出力に表示される「Public URL:」のリンクをクリックしてアプリにアクセスできます。

## エラー対処法

### 「Data incompatible with tuples format」エラーが発生した場合

このエラーはGradioのチャットボットコンポーネントにデータを渡す際の形式の問題です。最新版のコードではこの問題を修正していますが、古いバージョンを使用している場合は以下のような修正が必要です：

1. `respond` 関数の戻り値を `[(message, response)]` の形式に変更
2. 空の応答の場合は `[]` を返すよう変更
3. イベント設定に `queue=False` を追加

### その他のエラー対応

アプリケーションには詳細なエラー表示機能が追加されています。エラーが発生した場合はコンソールに詳細情報が表示されますので、それを参考に対処してください。

## カスタマイズ

- LP企画設計のプロンプトは `app.py` の `generate_lp_planning()` 関数内で定義されています。必要に応じてカスタマイズできます。
- SVGの表示スタイルは `gr.Blocks()` 内のCSSで調整できます。
- SVG生成の品質を調整するには、プロンプト内の指示を修正することで変更できます。

## ライセンス

MITライセンス
