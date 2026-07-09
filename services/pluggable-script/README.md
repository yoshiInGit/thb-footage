# 音声字幕動画生成サービス (`pluggable-script`)

本サービスは、音声ファイル（`.wav`）と字幕テキスト（`.txt`）を `input/voice/` に配置するだけで、字幕テロップ付きの動画（`.mp4`）を自動生成するサービスです。

映像は `moviepy` によってレンダリングされ、話者ごとの字幕カラーやフォント・レイアウトは `config/settings.yaml` で一元管理されています。

---

## 1. ディレクトリ構造

```text
services/pluggable-script/
├── Dockerfile          # サービス専用のDockerfile
├── requirements.txt    # サービス固有の依存パッケージ
├── main.py             # 実行エントリーポイント
├── app/
│   ├── constants.py    # デフォルトの各種パス定数
│   ├── context.py      # 共有コンテキスト (PipelineContext)
│   ├── utils.py        # ユーティリティ関数群
│   └── plugins/        # プラグインモジュール群
│       ├── base.py                 # 全プラグインの基底抽象クラス (BasePlugin)
│       └── subtitle_generator.py   # 字幕付き動画生成プラグイン
├── assets/
│   └── font/           # 字幕用 TrueType フォントの格納先
├── config/
│   └── settings.yaml   # サービスの動作・装飾設定ファイル
├── input/
│   └── voice/          # 音声ファイル (.wav) と字幕テキスト (.txt) を配置
└── output/             # 生成された字幕動画が出力されます
```

---

## 2. 入力ファイルの配置規則

`input/voice/` ディレクトリ内に、音声ファイルと字幕テキストをペアで配置します。

### ファイル命名規則

```
{連番}_{話者名}_{任意の識別子}.wav
{連番}_{話者名}_{任意の識別子}.txt
```

- **連番** (例: `001`, `002`, ...): WAVファイルを昇順にソートして結合するための番号。
- **話者名**: `config/settings.yaml` の `subtitle.speakers` に設定した話者ラベルと一致する必要があります。
- **任意の識別子**: 管理用の任意の文字列。

### 配置例

```text
input/voice/
├── 001_アメノちゃん_opening.wav
├── 001_アメノちゃん_opening.txt    ← 同名のテキストが字幕テキストになります
├── 002_ディアちゃん_question.wav
├── 002_ディアちゃん_question.txt
└── ...
```

各 `.txt` ファイルには、対応する音声で読み上げられる字幕テキストのみを記述します。

---

## 3. 設定ファイル (`config/settings.yaml`)

字幕動画のレイアウトや話者カラーを設定します。

```yaml
# 出力・音声データのパス設定
paths:
  output_dir: "output"
  voice_dir: "input/voice"  # 音声・テキストファイルのソースディレクトリ

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
  width: 1920                   # 動画の横幅 (px)
  height: 150                   # 字幕クリップ単体の高さ (px)
  padding_x: 250                # 左右のパディング幅 (px)
  silent_duration: 0.25         # 文末が句読点（、。！？）の際の音声後無音期間（秒）
```

---

## 4. 実行方法

### 基本的な実行コマンド

```bash
# デフォルト設定で実行（output/subtitle.mp4 に出力）
python main.py

# 出力ファイル名を指定して実行
python main.py --output my_video.mp4
python main.py -o my_video.mp4
```

### `--output` / `-o` 引数

| 引数 | デフォルト値 | 説明 |
|---|---|---|
| `--output` / `-o` | `subtitle.mp4` | 出力先のファイル名（`output/` ディレクトリ以下に作成されます） |

---

## 5. `SubtitleGeneratorPlugin` の動作仕様

`SubtitleGeneratorPlugin` は `input/voice/` 内のファイルを読み込んで動画を生成します。

### 処理フロー

1. `voice_dir` 内の `.wav` ファイルをファイル名の昇順でソートします。
2. 各 `.wav` に対応する同名の `.txt` ファイルを読み込み、字幕テキストとして使用します。
3. ファイル名から話者名（`{連番}_{話者名}_{識別子}` の中間部分）を抽出し、`settings.yaml` の `speakers` 設定を元に字幕カラーを決定します。
4. `moviepy` を使って音声クリップと字幕テロップを合成した動画クリップを生成します。
5. すべてのクリップを連結して、最終的な1本の動画ファイルを出力します。

### テキストファイルが見つからない場合

対応する `.txt` ファイルが存在しない `.wav` は警告を表示してスキップされます。

---

## 6. 依存パッケージ

```
python-dotenv
pyyaml
moviepy
Pillow
```

インストール:

```bash
pip install -r requirements.txt
```

---

## 7. Dockerでの実行

```bash
# イメージのビルド
docker build -t pluggable-script .

# コンテナの実行（ローカルの input/voice/ と output/ をマウント）
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pluggable-script
```
