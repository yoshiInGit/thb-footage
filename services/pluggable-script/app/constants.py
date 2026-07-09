import os

# プロジェクトのルートディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ディレクトリ定義 ---
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# ログディレクトリ
LOG_DIR = os.path.join(OUTPUT_DIR, "logs")

# 設定ファイル
SETTINGS_YAML = os.path.join(CONFIG_DIR, "settings.yaml")

# 入力ファイル・ディレクトリのデフォルト
VOICE_DIR = os.path.join(INPUT_DIR, "voice")

