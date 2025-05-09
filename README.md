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
  - ビジネス文書/パワーポイントスタイルのSVG図表（Google Gemini 1.5 Proによる生成）
- **新機能**: CSVファイルとSVGファイルのアップロードと活用機能
  - **CSVファイルのアップロード**: 法人企業のアンケートデータなどをターゲット分析に活用
  - **SVGファイルのアップロード**: レイアウトやデザインの参考としてSVG生成に活用

## CSVとSVGファイルの活用機能

### CSVファイルの活用
このアプリケーションは、CSVファイルから顧客アンケートなどのデータを取り込み、ターゲット分析に活用することができます。

- **対応するCSVデータ**: 法人企業アンケート、顧客属性データ、市場調査データなど
- **データ活用方法**: アップロードされたCSVデータを解析し、ターゲット企業の特性や課題、ニーズに関する洞察を深めます
- **活用プロセス**:
  1. CSVファイルをアップロードエリアからアップロード
  2. 「LP企画: 〜」コマンドを入力
  3. CSVデータがGemini APIに分析用データとして送信され、分析に活用

### SVGファイルの活用
既存のSVGをアップロードすると、そのレイアウトやデザインを参考にして新しいSVGを生成することができます。

- **活用目的**: レイアウト、構成、デザイン要素、色彩などの参考として活用
- **活用プロセス**:
  1. 参考にしたいSVGファイルをアップロードエリアからアップロード
  2. 「LP企画: 〜」コマンドを入力
  3. アップロードされたSVGのデザイン要素を参考にした新しいSVGが生成

## データ連携型デュアルLLM統合
このアプリケーションでは、2つの異なるLLMを連携させて活用します：

- **テキスト分析**: Google Gemini 2.0 flash
  - 法人向けLP企画の詳細なテキスト分析を生成
  - アップロードされたCSVデータを参考に、より具体的なターゲット分析を実施

- **SVG図表生成**: Google Gemini 1.5 Pro
  - Gemini Flashが生成した分析テキストを入力として受け取る
  - 分析内容に基づいたプロフェッショナルなビジネス向けSVGスライドを生成
  - アップロードされたSVGファイルのレイアウトやデザインを参考に活用
  - 16:9比率のワイドスクリーンフォーマット
  - パワーポイント形式の体裁と構造を持つレイアウト

この連携型アプローチにより、テキスト分析とビジュアル表現の一貫性が保たれ、より質の高い企画設計資料が生成されます。

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
- **Gemini分析に基づく視覚化**: テキスト分析の内容がSVGに反映されるため、一貫性のある資料作成が可能
- **参照SVGの活用**: アップロードされたSVGファイルのデザイン要素を部分的に取り入れることが可能

## ユーザー体験の向上

- **逐次的なテキスト表示**: LLMの出力が文字単位でタイピング風に表示されるため、生成過程が視覚的に確認できます
- **コンパクトなレイアウト**: チャットエリアとSVG表示が画面内で最適に配置され、スクロールを最小限に抑えています
- **全体を一目で確認**: 分析テキストとSVG図表が一画面内で確認できます
- **一貫性のある出力**: テキスト分析とSVG図表が同じ分析内容に基づいているため、情報の一貫性が向上しています
- **ファイルアップロード機能**: CSVやSVGファイルを簡単にアップロードでき、分析やデザインに活用できます

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

3. API キーを環境変数に設定
```bash
# Linuxまたは Mac
export GOOGLE_API_KEY="あなたのGemini APIキー"

# Windows (コマンドプロンプト)
set GOOGLE_API_KEY=あなたのGemini APIキー

# Windows (PowerShell)
$env:GOOGLE_API_KEY="あなたのGemini APIキー"
```

またはapp.pyファイル内で直接設定することもできます（セキュリティ上推奨されません）：
```python
os.environ["GOOGLE_API_KEY"] = "あなたのGemini APIキー"
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
1. Gemini APIによるテキスト分析が逐次的に（タイピング風に）チャット欄に表示されます
2. Geminiの分析結果を入力としてSVG図が生成されます

### ファイルアップロード機能の使い方

1. メイン画面のファイルアップロードエリアから「CSVファイルをアップロード」または「SVGファイルをアップロード」を選択
2. 対応するファイルを選択してアップロード
3. 「LP企画: 商品名やテーマ」のように入力して企画設計を開始
4. アップロードされたファイルがLP企画設計プロセスに活用されます

**CSVファイル活用のヒント**:
- 顧客企業の属性や課題が含まれたCSVファイルが効果的です
- 列名と内容がわかりやすいCSVデータが最適です

**SVGファイル活用のヒント**:
- 参考にしたいレイアウトやデザインのSVGファイルを使用します
- 既存のプレゼンテーションスライドからエクスポートしたSVGも活用できます

## 処理フロー

LP企画設計機能の処理フローは以下の通りです：

1. ユーザーが「LP企画: テーマ名」と入力（オプションでCSV/SVGファイルをアップロード）
2. アップロードされたCSVファイルがある場合は分析
3. Gemini 2.0 flashが3つの観点からテーマを分析しテキスト結果を生成（CSVデータがある場合はそれを参考に）
4. 生成されたテキスト分析がGemini 1.5 Proに入力として渡される
5. Gemini 1.5 ProがSVG図表を生成（参考SVGがある場合はそのデザイン要素を参考に）
6. テキスト分析とSVG図表が画面に表示される

この連携により、テキスト分析の内容とSVG図表の内容に一貫性が保たれます。

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

# アプリを実行
!python app.py
```

実行後、Colabの出力に表示される「Public URL:」のリンクをクリックしてアプリにアクセスできます。

## エラー対処法

### API キー関連のエラー

アプリケーションがAPI キーの不足を検出した場合、エラーメッセージが表示されます：
- Google API キーが設定されていない場合: テキスト分析が行われません

API キーが正しく設定されていることを確認してください。

### ファイルアップロード関連のエラー

- **CSVファイルが正しく読み込めない場合**: CSVファイルの形式やエンコーディングを確認してください
- **SVGファイルが読み込めない場合**: SVGファイルの形式やXMLの妥当性をチェックしてください
- **大きすぎるファイル**: ファイルサイズが大きすぎる場合は、より小さいファイルを使用してください

### 「Data incompatible with tuples format」エラーが発生した場合

このエラーはGradioのチャットボットコンポーネントにデータを渡す際の形式の問題です。最新版のコードではこの問題を修正していますが、古いバージョンを使用している場合は以下のような修正が必要です：

1. `respond` 関数の戻り値を `[(message, response)]` の形式に変更
2. 空の応答の場合は `[]` を返すよう変更
3. イベント設定に `queue=False` を追加

### その他のエラー対応

アプリケーションには詳細なエラー表示機能が追加されています。エラーが発生した場合はコンソールに詳細情報が表示されますので、それを参考に対処してください。

## カスタマイズ

- LP企画設計のプロンプトは以下のファイル内で定義されています：
  - `lp_planner.py`: Geminiによるテキスト分析のプロンプト
  - `svg_generator.py`: SVG生成のプロンプト（Geminiの分析結果を受け取る）
- SVGの表示スタイルは `app.py` 内のCSSで調整できます。
- CSVデータの処理方法は `utils.py` の `read_csv_data()` 関数内で変更できます。
- SVGのビジネススタイルやカラースキームを変更するには、`svg_generator.py` 内のプロンプトを修正します。

## ライセンス

MITライセンス
