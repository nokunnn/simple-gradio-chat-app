# 法人向けLP企画設計チャットアプリ

このリポジトリは、Gradioを使用したチャットアプリケーションで、Google Gemini APIとAnthropic Claude 3.7 Sonnetを活用して法人向けランディングページ（LP）の企画設計をサポートする機能を備えています。

## 機能

### 基本機能
- テキストベースのチャットインターフェース
- 逐次的なテキスト表示（タイピング風の表示）
- チャット履歴の表示
- チャット履歴のクリア機能

### LP企画設計機能
- ユーザーが指定した商品/サービステーマに基づいて法人向けLPの企画分析を生成
- 以下の3つの観点から詳細な分析を提供：
  1. ターゲットの分析
  2. 訴求軸の検討
  3. 訴求シナリオの検討
- 分析内容を以下の形式で出力:
  - 詳細な分析テキスト（Google Gemini APIによる生成）
  - ビジネス文書/パワーポイントスタイルのSVG図表（Anthropic Claude 3.7 Sonnetによる生成）

## デュアルLLM統合
このアプリケーションでは、2つの異なるLLMを最適な用途に合わせて活用しています：

- **テキスト分析**: Google Gemini 1.5 Pro
  - 法人向けLP企画の詳細なテキスト分析を生成

- **SVG図表生成**: Anthropic Claude 3.7 Sonnet
  - プロフェッショナルなビジネス向けSVGスライドを生成
  - 16:9比率のワイドスクリーンフォーマット
  - パワーポイント形式の体裁と構造を持つレイアウト

## 最適化されたSVG出力

分析結果は以下の特徴を持つSVGで視覚化されます：

- **16:9のワイドスクリーン比率**: パワーポイントスライドに最適なサイズ設定（800×450ピクセル）
- **プロフェッショナルなビジネスデザイン**:
  - 企業向けプレゼンテーションに適した青系カラースキーム
  - 明確な階層構造（タイトル、サブタイトル、箇条書き）
  - 読みやすいサンセリフフォント
  - 適切な余白とレイアウト
- **コンパクトなサイズ**: スクロールなしで全体を閲覧可能
- **直接使用可能**: SVGをダウンロードして、そのままプレゼン資料に利用可能

## ユーザー体験の向上

- **逐次的なテキスト表示**: LLMの出力が文字単位でタイピング風に表示されるため、生成過程が視覚的に確認できます
- **コンパクトなレイアウト**: チャットエリアとSVG表示が画面内で最適に配置され、スクロールを最小限に抑えています
- **全体を一目で確認**: 分析テキストとSVG図表が一画面内で確認できます

## セットアップ

### 必要条件

- Python 3.7以上
- Google Gemini API キー
- Anthropic Claude API キー

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

3. API キーを環境変数に設定
```bash
# Linuxまたは Mac
export GOOGLE_API_KEY="あなたのGemini APIキー"
export ANTHROPIC_API_KEY="あなたのClaude APIキー"

# Windows (コマンドプロンプト)
set GOOGLE_API_KEY=あなたのGemini APIキー
set ANTHROPIC_API_KEY=あなたのClaude APIキー

# Windows (PowerShell)
$env:GOOGLE_API_KEY="あなたのGemini APIキー"
$env:ANTHROPIC_API_KEY="あなたのClaude APIキー"
```

またはapp.pyファイル内で直接設定することもできます（セキュリティ上推奨されません）：
```python
os.environ["GOOGLE_API_KEY"] = "あなたのGemini APIキー"
os.environ["ANTHROPIC_API_KEY"] = "あなたのClaude APIキー"
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

入力後、アプリケーションは以下のように結果を表示します：
1. テキスト分析が逐次的に（タイピング風に）チャット欄に表示されます（Gemini APIによる生成）
2. ビジネス向けのパワーポイントスタイルのSVG図が生成されます（Claude 3.7 Sonnetによる生成）

## Google Colabでの実行方法

Google Colabを使用して以下の手順でアプリケーションを実行できます：

```python
# リポジトリをクローン
!git clone https://github.com/nokunnn/simple-gradio-chat-app.git
%cd simple-gradio-chat-app

# 必要なパッケージをインストール
!pip install -r requirements.txt

# API キーを設定
import os
os.environ["GOOGLE_API_KEY"] = "あなたのGemini APIキー"
os.environ["ANTHROPIC_API_KEY"] = "あなたのClaude APIキー"

# アプリを実行
!python app.py
```

実行後、Colabの出力に表示される「Public URL:」のリンクをクリックしてアプリにアクセスできます。

## エラー対処法

### API キー関連のエラー

アプリケーションがAPI キーの不足を検出した場合、エラーメッセージが表示されます：
- Google API キーが設定されていない場合: テキスト分析が行われません
- Anthropic API キーが設定されていない場合: SVG図が生成されません

両方のAPIキーが正しく設定されていることを確認してください。

### 「Data incompatible with tuples format」エラーが発生した場合

このエラーはGradioのチャットボットコンポーネントにデータを渡す際の形式の問題です。最新版のコードではこの問題を修正していますが、古いバージョンを使用している場合は以下のような修正が必要です：

1. `respond` 関数の戻り値を `[(message, response)]` の形式に変更
2. 空の応答の場合は `[]` を返すよう変更
3. イベント設定に `queue=False` を追加

### ストリーミング出力に関するエラー

逐次的なテキスト表示（ストリーミング出力）の速度は `time.sleep(0.01)` の値を調整することで変更できます。遅延が大きすぎる場合は、この値を小さくしてみてください。

### その他のエラー対応

アプリケーションには詳細なエラー表示機能が追加されています。エラーが発生した場合はコンソールに詳細情報が表示されますので、それを参考に対処してください。

## カスタマイズ

- LP企画設計のプロンプトは `app.py` の以下の関数内で定義されています：
  - `generate_lp_planning()`: Geminiによるテキスト分析のプロンプト
  - `generate_svg_with_claude()`: Claudeによるビジュアル生成のプロンプト
- SVGの表示スタイルは `gr.Blocks()` 内のCSSで調整できます。
- SVGのビジネススタイルやカラースキームを変更するには、プロンプト内の指示を修正します。
- 逐次的なテキスト表示の速度は `time.sleep()` の値を調整して変更できます。

## ライセンス

MITライセンス
