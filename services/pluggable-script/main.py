import os
import argparse
from app.context import PipelineContext
from app.utils import load_config, read_file
from app.constants import SETTINGS_YAML
from app.plugins.script_generator import ScriptGeneratorPlugin
from app.plugins.script_formatter import ScriptFormatterPlugin
from app.plugins.subtitle_generator import SubtitleGeneratorPlugin

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="pluggable-script pipeline runner")
    parser.add_argument(
        "--step", "-s",
        type=str,
        default="all",
        choices=["setup", "question", "merge", "format", "subtitle", "all"],
        help="Specify the pipeline step to execute (default: all)"
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

    setup_file = os.path.join(context.output_dir, "setup.txt")
    question_file = os.path.join(context.output_dir, "question.txt")

    # 1. 各ジェネレータのロード（必要に応じて実行またはファイルから読み込み）
    # setup ステップまたは一括実行の場合
    if args.step in ["setup", "all"]:
        if os.path.exists(setup_file):
            print(f"[main] setup.txt already exists at {setup_file}. Loading from file...")
            context.set_script("setup", read_file(setup_file))
        else:
            setup_plugin = ScriptGeneratorPlugin(name="setup", prompt_template_path="prompts/setup.txt")
            setup_plugin.run(context)
    else:
        # 他のステップで前段のテキストが必要な場合はファイルからロード
        if os.path.exists(setup_file):
            context.set_script("setup", read_file(setup_file))

    # question ステップまたは一括実行の場合
    if args.step in ["question", "all"]:
        if os.path.exists(question_file):
            print(f"[main] question.txt already exists at {question_file}. Loading from file...")
            context.set_script("question", read_file(question_file))
        else:
            question_plugin = ScriptGeneratorPlugin(name="question", prompt_template_path="prompts/question.txt")
            question_plugin.run(context)
    else:
        # 他のステップで前段のテキストが必要な場合はファイルからロード
        if os.path.exists(question_file):
            context.set_script("question", read_file(question_file))

    # 2. 結合処理
    if args.step in ["merge", "all"]:
        print("[main] Merging script parts...")
        context.merge_scripts(
            parts=["setup", "question"], 
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

