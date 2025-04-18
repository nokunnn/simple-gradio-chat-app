"""共通のユーティリティ機能"""
import os
import logging
import re
import traceback
import time
import shutil
from datetime import datetime
import pandas as pd

# ロギングを設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API キー設定
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# グローバル変数
chat_history = []
current_svg_code = None
current_analysis = None
current_theme = None
uploaded_csv_path = None
uploaded_svg_path = None

# 一時ファイル用のディレクトリ
TEMP_DIR = "temp_files"

# 一時ファイルディレクトリの作成
os.makedirs(TEMP_DIR, exist_ok=True)

def clean_filename(theme):
    """ファイル名に使えない文字を除去し、適切なファイル名を生成する"""
    if not theme:
        return f"lp_planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # ファイル名に使用できない文字を除去
    theme_part = re.sub(r'[\\/*?:"<>|]', "", theme)
    theme_part = theme_part.replace(' ', '_').lower()[:30]
    return f"lp_planning_{theme_part}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def log_error(error_message, error=None):
    """エラーのログを記録する"""
    if error:
        error_detail = traceback.format_exc()
        logger.error(f"{error_message}:\n{error_detail}")
        return f"{error_message}: {str(error)}"
    else:
        logger.error(error_message)
        return error_message

def save_uploaded_file(filepath, file_type):
    """アップロードされたファイルを一時ディレクトリに保存する"""
    global uploaded_csv_path, uploaded_svg_path
    
    if not filepath:
        return None
    
    # ファイルのコピー先パスを生成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.basename(filepath)
    _, ext = os.path.splitext(base_name)
    new_filename = f"{file_type}_{timestamp}{ext}"
    new_path = os.path.join(TEMP_DIR, new_filename)
    
    # ファイルをコピー
    shutil.copy2(filepath, new_path)
    
    # グローバル変数を更新
    if file_type == "csv":
        # 前回のCSVがあれば削除
        if uploaded_csv_path and os.path.exists(uploaded_csv_path):
            try:
                os.remove(uploaded_csv_path)
            except:
                pass
        uploaded_csv_path = new_path
    elif file_type == "svg":
        # 前回のSVGがあれば削除
        if uploaded_svg_path and os.path.exists(uploaded_svg_path):
            try:
                os.remove(uploaded_svg_path)
            except:
                pass
        uploaded_svg_path = new_path
    
    return new_path

def read_csv_data(csv_path):
    """CSVファイルを読み込んで分析する"""
    if not csv_path or not os.path.exists(csv_path):
        return None
    
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_path)
        
        # 基本的な情報を収集
        num_rows = len(df)
        num_cols = len(df.columns)
        column_info = df.dtypes.to_dict()
        
        # 最初の5行をサンプルとして取得
        sample_data = df.head(5).to_dict()
        
        # 分析情報を返す
        analysis = {
            "file_path": csv_path,
            "num_rows": num_rows,
            "num_columns": num_cols,
            "columns": column_info,
            "sample_data": sample_data,
            "dataframe": df  # 必要に応じて使用
        }
        
        return analysis
    except Exception as e:
        log_error(f"CSVファイルの読み込み中にエラーが発生しました: {csv_path}", e)
        return None

def read_svg_content(svg_path):
    """SVGファイルを読み込む"""
    if not svg_path or not os.path.exists(svg_path):
        return None
    
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        return svg_content
    except Exception as e:
        log_error(f"SVGファイルの読み込み中にエラーが発生しました: {svg_path}", e)
        return None

def clean_temp_files():
    """一時ファイルを削除する"""
    global uploaded_csv_path, uploaded_svg_path
    
    # アップロードされたファイルを削除
    if uploaded_csv_path and os.path.exists(uploaded_csv_path):
        try:
            os.remove(uploaded_csv_path)
        except:
            pass
    
    if uploaded_svg_path and os.path.exists(uploaded_svg_path):
        try:
            os.remove(uploaded_svg_path)
        except:
            pass
    
    uploaded_csv_path = None
    uploaded_svg_path = None
    
    # 24時間以上前のファイルを削除（定期的なクリーンアップ）
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        # ファイルの最終更新時間をチェック
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 86400:  # 24時間 = 86400秒
            try:
                os.remove(file_path)
            except:
                pass
