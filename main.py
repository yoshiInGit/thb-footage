import argparse
import sys
from app.pipeline import Pipeline
from app.utils import load_config
import os

from app.constants import PLAN_FILE, SETTINGS_YAML

def main():
    parser = argparse.ArgumentParser(description="YouTube動画台本自動生成システム")
    parser.add_argument("--step", type=str, choices=["all", "intro", "outline", "body", "outro", "merge"], default="all",
                        help="実行する工程を指定 (default: all)")
    parser.add_argument("--input", type=str, default=PLAN_FILE,
                        help="入力ファイルまたは中間データのパス")
    parser.add_argument("--config", type=str, default=SETTINGS_YAML,
                        help="設定ファイルのパス")
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    pipeline = Pipeline(config)
    
    if args.step == "all":
        pipeline.run_all(args.input)
    else:
        pipeline.run_step(args.step, args.input)

if __name__ == "__main__":
    main()
