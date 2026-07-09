import argparse
from app.context import PipelineContext
from app.utils import load_config
from app.constants import SETTINGS_YAML
from app.plugins.subtitle_generator import SubtitleGeneratorPlugin


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="pluggable-script subtitle generator")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="subtitle.mp4",
        help="出力する字幕付き動画ファイル名 (default: subtitle.mp4)"
    )
    args = parser.parse_args()

    print("[main] Initializing pluggable-script subtitle generator...")
    
    # 設定ファイルの読み込み
    config = load_config(SETTINGS_YAML)

    # 共有コンテキストの初期化
    context = PipelineContext(
        output_dir="output",
        config=config
    )

    # 字幕付き動画の生成
    print("[main] Generating subtitle video...")
    subtitler = SubtitleGeneratorPlugin(
        name="subtitle_generator",
        output_name=args.output
    )
    subtitler.run(context)

    print("[main] Subtitle generation finished successfully!")


if __name__ == "__main__":
    main()

