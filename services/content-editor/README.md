# Content Editor サービス

このサービスは、AI（Gemini）を利用して `content.txt` の編集用差分データ（JSON形式のパッチ）を生成し、その差分をプログラムによって安全に `content.txt` に適用して編集するシステムです。

## ディレクトリ構造

```text
services/content-editor/
├── app/
│   ├── editor.py       # AIプロンプトの構築、Geminiの呼び出し
│   └── patcher.py      # 差分データの適用プログラム
├── config/             # 設定ファイルを配置するディレクトリ
│   └── settings.yaml   # サービス全体の設定ファイル（パスやモデル設定）
├── input/              # 入力ファイルを配置するディレクトリ（手動で作成）
│   ├── task.txt        # AIに対する指示（必須）
│   ├── reference.json  # 動的に読み込む参考資料のリスト（任意）
│   └── (その他参考資料テキストファイル...)
├── output/             # 出力ファイルが生成されるディレクトリ
│   ├── content.txt     # 編集適用後のテキストファイル
│   ├── patch.json      # AIが生成した差分データ
│   └── logs/           # Gemini APIの通信ログ
├── content.txt         # 編集対象のテキストファイル（直下に配置、必須）
├── main.py             # サービスのエントリーポイント
├── requirements.txt    # 依存パッケージ
└── README.md           # 本ファイル
```

## セットアップ

サービスのディレクトリに移動し、依存関係をインストールします。

```bash
cd services/content-editor
pip install -r requirements.txt
```

また、環境変数 `GOOGLE_API_KEY` が設定されていることを確認してください（プロジェクトルートの `.env` ファイルに定義されていれば自動で読み込まれます）。

## 使用方法

### 1. 入力ファイルの準備

#### `services/content-editor/content.txt`
編集したいオリジナルのテキストを記述します。サービス実行時に直接上書き編集されます。

#### `services/content-editor/input/task.txt`
どのように編集したいかの指示を記述します。
例：
```text
「宇宙へ送られた最後の手紙」という文章に、カール・セーガン博士の言葉である「私たちは星の屑でできている」という名言を引用文として追加してください。
また、イントロダクション部分の表現をよりドラマチックに書き換えてください。
```

#### `services/content-editor/input/reference.json` (任意)
編集の参考にさせたい資料ファイルを指定します。
例：
```json
{
  "references": [
    "input/ref1.txt",
    "input/ref2.txt"
  ]
}
```
※指定されたファイル（例: `input/ref1.txt` など）も `input/` ディレクトリに用意してください。

### 2. 実行

#### Pythonで直接実行する場合
コマンドプロンプトやPowerShellで以下のコマンドを実行します。
```bash
python main.py
```

#### Dockerで実行する場合
プロジェクトルートに用意されている `docker-compose.yml` を利用して実行できます。
```bash
# プロジェクトルートディレクトリで実行
docker compose run --rm content-editor
```
※ 必要に応じて、末尾にオプション引数（例: `--config config/settings.yaml`）を追加できます。

#### オプション引数
- `--config <ファイルパス>`: 使用する設定ファイルのパスを変更します（デフォルト: `config/settings.yaml`）。
- `--model <モデル名>`: 使用するGeminiモデルを変更します（指定しない場合は設定ファイルの値を使用）。
- `--no-strict`: 置換対象が重複または存在しない場合でも、エラーにせずスキップして処理を続行します（基本的には指定せず strict モードで動かすことを推奨します）。

### 3. 出力の確認

- `content.txt`: 編集後のテキスト（常に自動で上書き更新されます）
- `output/patch.json`: AIが作成した差分パッチデータ
- `output/archives/content_YYYYMMDD_HHMMSS.txt`: 編集結果のバックアップアーカイブ

