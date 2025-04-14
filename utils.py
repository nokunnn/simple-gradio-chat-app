"""共通のユーティリティ機能"""
import os
import logging
import re
import traceback
import time
from datetime import datetime

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
