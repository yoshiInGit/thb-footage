import os
from app.context import PipelineContext
from app.utils import load_config
from app.constants import SETTINGS_YAML
from app.plugins.script_generator import ScriptGeneratorPlugin
from app.plugins.script_formatter import ScriptFormatterPlugin
from app.plugins.subtitle_generator import SubtitleGeneratorPlugin

def main():
    print("[main] Initializing pluggable-script pipeline...")
    # 設定ファイルの読み込み
    config = load_config(SETTINGS_YAML)

    # 共有コンテキストの初期化 (出力を output フォルダ直下にまとめる)
    context = PipelineContext(
        plan_file="input/plan.txt",
        output_dir="output",
        config=config
    )

    # 1. 各パートの台本を生成するプラグインを定義・実行
    # ここでは Pythonコードで自由に構成を記述できる
    print("[main] Step 1: Generating script parts...")
    
    setup_plugin = ScriptGeneratorPlugin(
        name="setup", 
        prompt_template_path="prompts/setup.txt"
    )
    question_plugin = ScriptGeneratorPlugin(
        name="question", 
        prompt_template_path="prompts/question.txt"
    )

    setup_plugin.run(context)
    question_plugin.run(context)

    # 2. 生成された台本をPythonコードでマージ処理
    print("[main] Step 2: Merging script parts...")
    context.merge_scripts(
        parts=["setup", "question"], 
        output_name="merged_script.txt"
    )

    # 3. 台本の整形プラグインを定義・実行
    print("[main] Step 3: Formatting merged script...")
    formatter = ScriptFormatterPlugin(
        name="script_formatter", 
        output_name="formatted_script.txt"
    )
    formatter.run(context)

    # 4. 字幕付き動画ファイルを生成するプラグインを定義・実行
    # ※ input/voice 内に音声ファイルが存在する場合に動作します
    print("[main] Step 4: Generating subtitle video...")
    subtitler = SubtitleGeneratorPlugin(
        name="subtitle_generator", 
        output_name="subtitle.mp4"
    )
    subtitler.run(context)

    print("[main] Pipeline finished successfully!")

if __name__ == "__main__":
    main()
