import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

# プロジェクトルートディレクトリを sys.path に追加して、sharedパッケージをインポート可能にする
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.editor import generate_patch
from app.patcher import apply_patches
from app.utils import load_config

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="Content Editor Service")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="使用するGeminiモデル名 (指定しない場合は設定ファイルの値を使用)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="使用する設定ファイルのパス (デフォルト: config/settings.yaml)"
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="指定した場合、差分適用の失敗を無視して続行します (非推奨)"
    )
    return parser.parse_args()

def read_file_or_exit(filepath: str, description: str) -> str:
    """ファイルを読み込み、存在しない場合はエラー終了する"""
    if not os.path.exists(filepath):
        logger.error(f"{description}が見つかりません: {filepath}")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filepath: str, content: Any, is_json: bool = False) -> None:
    """ファイルにコンテンツを書き込む"""
    with open(filepath, "w", encoding="utf-8") as f:
        if is_json:
            json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            f.write(content)

def load_references(ref_config_path: str) -> List[Dict[str, str]]:
    """reference.jsonから参考資料を動的に読み込む"""
    references = []
    if not os.path.exists(ref_config_path):
        logger.info("参考資料設定 (reference.json) は存在しません。参考資料なしで進めます。")
        return references

    logger.info(f"参考資料設定を読み込んでいます: {ref_config_path}")
    try:
        with open(ref_config_path, "r", encoding="utf-8") as f:
            ref_config = json.load(f)
        
        for ref_file in ref_config.get("references", []):
            if os.path.exists(ref_file):
                logger.info(f"参考資料ファイルをロードしました: {ref_file}")
                references.append({
                    "name": os.path.basename(ref_file),
                    "content": read_file_or_exit(ref_file, "参考資料ファイル")
                })
            else:
                logger.warning(f"参考資料ファイルが見つかりません: {ref_file}")
    except Exception as e:
        logger.error(f"reference.json の解析中にエラーが発生しました: {e}")
        sys.exit(1)
        
    return references

def main():
    args = parse_args()
    strict = not args.no_strict

    # 設定ファイルの読み込み
    try:
        config = load_config(args.config)
    except Exception:
        sys.exit(1)

    model_config = config.get("model", {})
    paths_config = config.get("paths", {})

    # モデル名の決定（引数優先、次に設定ファイル、最後にデフォルト）
    model_name = args.model or model_config.get("name", "gemini-2.5-flash")

    # パスの定義
    input_dir       = paths_config.get("input_dir", "input")
    output_dir      = paths_config.get("output_dir", "output")
    
    content_path    = paths_config.get("content_file", "content.txt")
    task_path       = os.path.join(input_dir, paths_config.get("task_file", "task.txt"))
    ref_config_path = os.path.join(input_dir, paths_config.get("reference_config", "reference.json"))
    
    patch_output_path   = os.path.join(output_dir, paths_config.get("patch_output", "patch.json"))
    archive_dir         = os.path.join(output_dir, paths_config.get("archive_dir", "archives"))
    log_dir             = os.path.join(output_dir, paths_config.get("log_dir", "logs"))
    
    # アーカイブファイルのパスを生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(archive_dir, f"content_{timestamp}.txt")

    # 1. 入力ファイルの読み込み
    logger.info("入力ファイルを読み込んでいます...")
    content_data = read_file_or_exit(content_path, "編集対象ファイル")
    task_data    = read_file_or_exit(task_path, "指示ファイル")
    references   = load_references(ref_config_path)

    # 2. 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(log_dir,    exist_ok=True)

    # 3. AIを呼び出してパッチJSONを生成
    logger.info("AIに差分データの生成を依頼中...")
    try:
        patches = generate_patch(
            content    = content_data,
            task       = task_data,
            references = references,
            model_name = model_name,
            log_dir    = log_dir
        )
    except Exception as e:
        logger.error(f"AIによる差分データ生成中にエラーが発生しました: {e}")
        sys.exit(1)

    # 4. パッチJSONの書き出し
    logger.info(f"差分データを保存中 -> {patch_output_path}")
    write_file(patch_output_path, patches, is_json=True)

    # 5. パッチの適用
    logger.info("差分データを適用中...")
    try:
        new_content = apply_patches(content_data, patches, strict=strict)
    except Exception as e:
        logger.error(f"差分データの適用中にエラーが発生しました: {e}")
        sys.exit(1)

    # 6. 編集後コンテンツをアーカイブとして保存
    logger.info(f"編集結果をアーカイブに保存中 -> {archive_path}")
    write_file(archive_path, new_content)

    # 7. 元ファイルを上書き更新
    logger.info(f"元のファイルを更新中 -> {content_path}")
    write_file(content_path, new_content)

    logger.info("すべての処理が正常に完了しました！")

if __name__ == "__main__":
    main()

