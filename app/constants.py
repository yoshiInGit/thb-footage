import os

# Gemini モデル設定
DEFAULT_MODEL_NAME = "gemini-3-flash-preview"

# プロジェクトのルートディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ディレクトリ定義 ---
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PROMPT_DIR = os.path.join(BASE_DIR, "prompts")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# ログディレクトリ
LOG_DIR = os.path.join(OUTPUT_DIR, "logs")

# 各ステップの出力ディレクトリ名
STEP_01_SETUP = "01_setup"
STEP_02_QUESTION = "02_question"
STEP_03_CHRONICLE = "03_pressure"
STEP_04_SCHEMA = "04_schema"
STEP_05_MERGE = "05_merge"

# 各ステップの出力ディレクトリパス
SETUP_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_01_SETUP)
QUESTION_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_02_QUESTION)
CHRONICLE_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_03_CHRONICLE)
SCHEMA_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_04_SCHEMA)
MERGE_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_05_MERGE)

# --- 末端ファイル定義 ---

# 設定ファイル
SETTINGS_YAML = os.path.join(CONFIG_DIR, "settings.yaml")
CONTROL_FILE = os.path.join(CONFIG_DIR, "control.json")

# 入力ファイル
PLAN_FILE = os.path.join(INPUT_DIR, "plan.txt")

# プロンプトディレクトリ
SETUP_PROMPT_DIR = os.path.join(PROMPT_DIR, "setup")
QUESTION_PROMPT_DIR = os.path.join(PROMPT_DIR, "question")
CHRONICLE_PROMPT_DIR = os.path.join(PROMPT_DIR, "pressure")
SCHEMA_PROMPT_DIR = os.path.join(PROMPT_DIR, "schema")

# プロンプトファイル
SETUP_PROMPT_DRAFT = os.path.join(SETUP_PROMPT_DIR, "draft.txt")
QUESTION_PROMPT_DRAFT = os.path.join(QUESTION_PROMPT_DIR, "draft.txt")
CHRONICLE_PROMPT_DRAFT = os.path.join(CHRONICLE_PROMPT_DIR, "draft.txt")
SCHEMA_PROMPT_DRAFT = os.path.join(SCHEMA_PROMPT_DIR, "draft.txt")

# 成果物ファイル
SETUP_FILE = os.path.join(SETUP_OUT_DIR, "setup.txt")
QUESTION_FILE = os.path.join(QUESTION_OUT_DIR, "question.txt")
CHRONICLE_FILE = os.path.join(CHRONICLE_OUT_DIR, "pressure.txt")
SCHEMA_FILE = os.path.join(SCHEMA_OUT_DIR, "schema.txt")
FINAL_SCRIPT_FILE = os.path.join(MERGE_OUT_DIR, "final_script.txt")

def get_chronicle_file(part: str = None) -> str:
    """
    Chronicle of Discovery のファイルパスを返す。
    :param part: パート番号 (例: '1', '2')。None の場合はデフォルトのファイルパスを返す。
    """
    if part:
        return os.path.join(CHRONICLE_OUT_DIR, f"pressure-{part}.txt")
    return CHRONICLE_FILE
