# プラグイン構成台本・字幕生成サービス (`pluggable-script`)

本サービスは、動画の構成（パート構成）や実行順序を Python コードで柔軟に変更し、共有コンテキストを通じて「台本生成」「台本整形」「字幕動画生成」を実行できるプラグインアーキテクチャ型のサービスです。

---

## 1. ディレクトリ構造

```text
services/pluggable-script/
├── Dockerfile          # サービス専用のDockerfile
├── requirements.txt    # サービス固有の依存パッケージ
├── main.py             # 実行エントリーポイント（Pythonでフローを定義）
├── app/
│   ├── constants.py    # デフォルトの各種パスやモデルの定数定義
│   ├── context.py      # 共有コンテキスト (PipelineContext)
│   ├── gemini.py       # Gemini APIクライアント
│   ├── utils.py        # ユーティリティ関数群
│   └── plugins/        # プラグインモジュール群
│       ├── base.py                 # 全プラグインの基底抽象クラス (BasePlugin)
│       ├── script_generator.py     # 台本生成プラグイン
│       ├── script_formatter.py     # 台本整形プラグイン
│       └── subtitle_generator.py   # 字幕付き動画生成プラグイン
├── assets/
│   └── font/           # 字幕用 TrueType フォントの格納先
├── config/
│   └── settings.yaml   # サービスの動作・装飾設定ファイル
├── input/              # 入力データ（企画書 plan.txt、音声素材 voice/）
└── output/             # 各プラグインの成果物（1つのフォルダにフラットに出力されます）
```

---

## 2. 設定について

設定は主に `config/settings.yaml` と、パイプライン初期化時の `PipelineContext` で制御されます。

### ① 設定ファイル (`config/settings.yaml`)

サービスの基本的な振る舞いや、字幕動画生成時の各種パラメータを設定します。

```yaml
# Gemini API のモデル設定
model:
  name: "gemini-3.1-flash-lite" # 使用するモデル
  temperature: 0.7              # 創造性 (0.0〜2.0)
  top_p: 0.95                   # 核サンプリング閾値
  top_k: 40                     # トップkサンプリング
  max_output_tokens: 8192       # 最大出力トークン数

# 内部ディレクトリのデフォルト相対パス
paths:
  input_dir: "input"
  output_dir: "output"
  prompt_dir: "prompts"

# 再生成ループの最大リトライ数（拡張用）
refinement:
  max_retries: 2

# 字幕・動画レンダリング設定 (moviepy で使用)
subtitle:
  # 話者ラベルごとの字幕テキストカラー (HEX値で指定)
  speakers:
    "アメノちゃん": "#9D0C0C"   # 赤
    "ディアちゃん": "#004F6E"   # 青
  # 字幕に使用するフォントのパス (プロジェクトルートからの相対パス、または絶対パス)
  font: "assets/font/MPLUSRounded1c-Medium.ttf"
  font_size: 40                 # フォントサイズ (px)
  bg_color: "white"             # 字幕テロップ枠の背景色
  width: 1920                   # 動画の横幅
  height: 150                   # 字幕クリップ単体の高さ
  padding_x: 250                # 左右のパディング幅
  silent_duration: 0.25         # 文末が句読点（、。！？）の際の音声後無音期間（秒）
```

### ② 共有コンテキスト (`PipelineContext`) による実行時制御

`PipelineContext` インスタンス化の際に、Pythonコード側から入力・出力のパスや設定オブジェクトを動的に注入できます。

* **引数**:
  - `plan_file` (str): 企画書プロットテキストファイルのパス。デフォルトは `input/plan.txt`。
  - `output_dir` (str): 成果物をまとめて出力するディレクトリ。デフォルトは `output`。
  - `config` (dict): `settings.yaml` をパースした辞書データ。

---

## 3. パイプライン構築のサンプルコード (`main.py`)

Python コード上で引数（`--step`）を受け取り、特定の処理のみを選択して実行する実装例です。

```python
import os
import argparse
from app.context import PipelineContext
from app.utils import load_config, read_file
from app.constants import SETTINGS_YAML
from app.plugins.script_generator import ScriptGeneratorPlugin
from app.plugins.script_formatter import ScriptFormatterPlugin
from app.plugins.subtitle_generator import SubtitleGeneratorPlugin

def main():
    # 引数の解析
    parser = argparse.ArgumentParser(description="pluggable-script pipeline runner")
    parser.add_argument(
        "--step", "-s",
        type=str,
        default="all",
        choices=["setup", "question", "merge", "format", "subtitle", "all"],
        help="Specify the pipeline step to execute (default: all)"
    )
    args = parser.parse_args()

    # 1. 設定のロード
    config = load_config(SETTINGS_YAML)

    # 2. 共有コンテキストの初期化
    context = PipelineContext(
        plan_file="input/plan.txt",
        output_dir="output",
        config=config
    )

    setup_file = os.path.join(context.output_dir, "setup.txt")
    question_file = os.path.join(context.output_dir, "question.txt")

    # setup ステップまたは一括実行の場合
    if args.step in ["setup", "all"]:
        if os.path.exists(setup_file):
            print(f"[main] setup.txt already exists. Loading...")
            context.set_script("setup", read_file(setup_file))
        else:
            setup_plugin = ScriptGeneratorPlugin("setup", "prompts/setup.txt")
            setup_plugin.run(context)
    else:
        if os.path.exists(setup_file):
            context.set_script("setup", read_file(setup_file))

    # question ステップまたは一括実行の場合
    if args.step in ["question", "all"]:
        if os.path.exists(question_file):
            print(f"[main] question.txt already exists. Loading...")
            context.set_script("question", read_file(question_file))
        else:
            question_plugin = ScriptGeneratorPlugin("question", "prompts/question.txt")
            question_plugin.run(context)
    else:
        if os.path.exists(question_file):
            context.set_script("question", read_file(question_file))

    # 結合処理
    if args.step in ["merge", "all"]:
        context.merge_scripts(parts=["setup", "question"], output_name="merged_script.txt")

    # 整形処理
    if args.step in ["format", "all"]:
        formatter = ScriptFormatterPlugin("script_formatter", "formatted_script.txt")
        formatter.run(context)

    # 字幕動画の生成
    if args.step in ["subtitle", "all"]:
        subtitler = SubtitleGeneratorPlugin("subtitle_generator", "subtitle.mp4")
        subtitler.run(context)

if __name__ == "__main__":
    main()
```

---

## 4. 各プラグインモジュールの解説

### `ScriptGeneratorPlugin(name, prompt_template_path)`
- **役割**: Geminiを利用し、企画書から特定のパートの台本を生成します。
- **入力**: `context.plan_content`、およびこれまでに生成された台本コンテキスト。
- **出力**: `{context.output_dir}/{name}.txt` にテキスト保存、および `context.scripts` 辞書にキャッシュ。

### `ScriptFormatterPlugin(name, output_name)`
- **役割**: 結合された台本テキストを「、」による改行および話者 `A:` / `B:` のラベル付与をした対話用台本へ整形します。
- **入力**: `context.merged_script_path` （マージ済みテキスト）。
- **出力**: `{context.output_dir}/{output_name}`。

### `SubtitleGeneratorPlugin(name, output_name)`
- **役割**: `input/voice` (設定変更可) 内の `WAV` 音声ファイル群と `TXT` 字幕原稿群を結合し、`moviepy` で字幕テロップを合成した動画を出力します。
- **入力**: `voice/` ディレクトリ。
- **出力**: `{context.output_dir}/{output_name}` (mp4動画)。

---

## 5. プロンプトと共有コンテキストの連携フロー

`ScriptGeneratorPlugin` が Gemini（LLM）を用いて台本を生成する際、プロンプトテンプレートに対して共有コンテキスト（`PipelineContext`）から以下の情報が自動的にマッピングされます。

### ① プロンプト内でのプレースホルダーの指定

プロンプトファイル（例: `prompts/setup.txt`, `prompts/question.txt`）の中に、以下のプレースホルダーを記述しておくことで、実行時にコンテキスト情報が動的に埋め込まれます。

* **`{plan}`**: `input/plan.txt`（企画書プロット）の内容がそのまま展開されます。
* **`{context}`**: それまでに生成された**前段の全パートの生成台本**が結合された状態で展開されます。

### ② パイプライン実行時のコンテキストの遷移例

`main.py` で以下のように実行した場合の連携イメージです。

1. **`setup_plugin.run(context)` の実行**
   - `{plan}` $\rightarrow$ `plan.txt` の中身をマッピング。
   - `{context}` $\rightarrow$ まだ他のパートが生成されていないため、空の文字列。
   - 生成完了後、結果テキストがコンテキストの `context.scripts["setup"]` に保存されます（および `output/setup.txt` へ出力）。

2. **`question_plugin.run(context)` の実行**
   - `{plan}` $\rightarrow$ `plan.txt` の中身をマッピング。
   - `{context}` $\rightarrow$ コンテキストに保存されている `setup` の台本が自動的にフォーマットされて埋め込まれます。
     ```text
     --- (Previous Part: setup) ---
     [setup パートで生成された実際の台本内容]
     ```
   - これにより、Geminiは「導入（setup）でどのような話し方やストーリー展開が行われたか」を完全に把握した状態で、それに続く自然な課題提示（question）の台本を生成できます。
   - 生成結果は `context.scripts["question"]` に保存されます。

3. **マージ処理: `context.merge_scripts(["setup", "question"])`**
   - コンテキストに蓄積された `scripts` から指定したキー順（`setup` $\rightarrow$ `question`）で結合し、ファイルとして `output/merged_script.txt` に出力します。

このような連携構造により、後段の生成処理ほど前段のストーリー文脈や表現スタイルを強く意識した一貫性のある台本生成が可能となっています。

