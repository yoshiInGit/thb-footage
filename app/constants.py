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
STEP_01_INTRO = "01_intro"
STEP_02_OUTLINE = "02_outline"
STEP_03_BODY = "03_body"
STEP_04_OUTRO = "04_outro"
STEP_05_MERGE = "05_merge"

# 各ステップの出力ディレクトリパス
INTRO_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_01_INTRO)
OUTLINE_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_02_OUTLINE)
BODY_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_03_BODY)
OUTRO_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_04_OUTRO)
MERGE_OUT_DIR = os.path.join(OUTPUT_DIR, STEP_05_MERGE)

# --- 末端ファイル定義 ---

# 設定ファイル
SETTINGS_YAML = os.path.join(CONFIG_DIR, "settings.yaml")

# 入力ファイル
PLAN_FILE = os.path.join(INPUT_DIR, "plan.txt")

# プロンプトファイル: イントロ
INTRO_PROMPT_DIR = os.path.join(PROMPT_DIR, "intro")
INTRO_PROMPT_DRAFT = os.path.join(INTRO_PROMPT_DIR, "draft.txt")

# プロンプトファイル: アウトライン
OUTLINE_PROMPT_DIR = os.path.join(PROMPT_DIR, "outline")
OUTLINE_PROMPT_DRAFT = os.path.join(OUTLINE_PROMPT_DIR, "draft.txt")
OUTLINE_PROMPT_REVIEW = os.path.join(OUTLINE_PROMPT_DIR, "review.txt")
OUTLINE_PROMPT_FINALIZE = os.path.join(OUTLINE_PROMPT_DIR, "finalize.txt")

# プロンプトファイル: 本文
BODY_PROMPT_DIR = os.path.join(PROMPT_DIR, "body")
BODY_PROMPT_DRAFT = os.path.join(BODY_PROMPT_DIR, "draft.txt")
BODY_PROMPT_REVIEW = os.path.join(BODY_PROMPT_DIR, "review.txt")
BODY_PROMPT_FINALIZE = os.path.join(BODY_PROMPT_DIR, "finalize.txt")

# プロンプトファイル: アウトロ
OUTRO_PROMPT_DIR = os.path.join(PROMPT_DIR, "outro")
OUTRO_PROMPT_DRAFT = os.path.join(OUTRO_PROMPT_DIR, "draft.txt")
OUTRO_PROMPT_REVIEW = os.path.join(OUTRO_PROMPT_DIR, "review.txt")
OUTRO_PROMPT_FINALIZE = os.path.join(OUTRO_PROMPT_DIR, "finalize.txt")

# 成果物ファイル
INTRO_FILE = os.path.join(INTRO_OUT_DIR, "intro.txt")
OUTLINE_FILE = os.path.join(OUTLINE_OUT_DIR, "outline.json")
OUTRO_FILE = os.path.join(OUTRO_OUT_DIR, "outro.txt")
FINAL_SCRIPT_FILE = os.path.join(MERGE_OUT_DIR, "final_script.txt")
