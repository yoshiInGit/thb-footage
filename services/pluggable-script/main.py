import argparse
from app.context import PipelineContext
from app.utils import load_config
from app.constants import SETTINGS_YAML
from app.plugins.script_generator import ScriptGeneratorPlugin
from app.plugins.script_formatter import ScriptFormatterPlugin
from app.plugins.subtitle_generator import SubtitleGeneratorPlugin

# 全パート定義（生成順序順）
# 企画書「宇宙へ送られた最後の手紙」の幕構成に対応
SCRIPT_PARTS = [
    {"name": "hook",    "prompt": "prompts/hook.txt"},     # 冒頭フック（ナレーション単独）
    {"name": "you",     "prompt": "prompts/you.txt"},      # 幕① カール・セーガンとは何者か（YOU）
    {"name": "need",    "prompt": "prompts/need.txt"},     # 幕② NASAからの依頼（NEED）
    {"name": "go",      "prompt": "prompts/go.txt"},       # 幕③ 人類代表を選ぶ苦悩（GO）
    {"name": "search",  "prompt": "prompts/search.txt"},   # 幕④ 人類を1枚に圧縮する（SEARCH）
    {"name": "find",    "prompt": "prompts/find.txt"},     # 幕⑤ 48時間の恋（FIND）
    {"name": "take",    "prompt": "prompts/take.txt"},     # 幕⑥ 宛先のない手紙（TAKE）
    {"name": "return",  "prompt": "prompts/return.txt"},   # 幕⑦ 打ち上げ、そしてその後（RETURN）
    {"name": "change",  "prompt": "prompts/change.txt"},   # 幕⑧ 私たちは何者なのか（CHANGE）
    {"name": "ending",  "prompt": "prompts/ending.txt"},   # エンディング（着地・余韻）
]

# パート名のリスト（結合順序としても使用）
PART_NAMES = [p["name"] for p in SCRIPT_PARTS]

# --step 引数で指定可能なステップ一覧
VALID_STEPS = PART_NAMES + ["merge", "format", "subtitle", "all"]


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="pluggable-script pipeline runner")
    parser.add_argument(
        "--step", "-s",
        type=str,
        default="all",
        choices=VALID_STEPS,
        help="実行するパイプラインステップを指定 (default: all)"
    )
    args = parser.parse_args()

    print(f"[main] Initializing pluggable-script pipeline for step: '{args.step}'...")
    
    # 設定ファイルの読み込み
    config = load_config(SETTINGS_YAML)

    # 共有コンテキストの初期化
    context = PipelineContext(
        plan_file="input/plan.txt",
        output_dir="output",
        config=config
    )

    # 1. 各パートの台本生成（順次実行でコンテキストを蓄積）
    for part in SCRIPT_PARTS:
        if args.step in [part["name"], "all"]:
            ScriptGeneratorPlugin(
                name=part["name"],
                prompt_template_path=part["prompt"]
            ).run(context)

    # 2. 結合処理（全パートを幕順に結合）
    if args.step in ["merge", "all"]:
        print("[main] Merging script parts...")
        context.merge_scripts(
            parts=PART_NAMES,
            output_name="merged_script.txt"
        )

    # 3. 台本の整形
    if args.step in ["format", "all"]:
        print("[main] Formatting merged script...")
        formatter = ScriptFormatterPlugin(
            name="script_formatter",
            output_name="formatted_script.txt"
        )
        formatter.run(context)

    # 4. 字幕付き動画の生成
    if args.step in ["subtitle", "all"]:
        print("[main] Generating subtitle video...")
        subtitler = SubtitleGeneratorPlugin(
            name="subtitle_generator",
            output_name="subtitle.mp4"
        )
        subtitler.run(context)

    print(f"[main] Pipeline step '{args.step}' finished successfully!")


if __name__ == "__main__":
    main()
