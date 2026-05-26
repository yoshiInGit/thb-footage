# thb-footage: マルチサービス自動生成システム

本プロジェクトは、YouTube動画制作における各種自動化タスク（解説動画の台本〜字幕生成、ランキング動画台本生成、映像製作支援など）を独立したコンテナサービスとして並行開発・運用できる、モノレポ（Monorepo）構成のシステムです。

---

## 全体ディレクトリ構成

システムは、共通ライブラリを格納する `shared/` と、個別の自動化タスクを実行する `services/` に分かれています。

```text
.
├── docker-compose.yml          # 全サービスを定義・管理するDocker Compose設定
├── .env                        # 共通の環境変数（Gemini APIキーなど）
├── .gitignore                  # マルチサービス対応の除外設定
├── README.md                   # 本ドキュメント
├── shared/                     # 各サービス間で共通利用するコアモジュール
│   ├── __init__.py
│   ├── gemini.py               # 共通のGemini APIクライアント
│   └── utils.py                # 共通のファイル操作ユーティリティ
└── services/                   # 各種独立サービス
    └── narrative-script/       # 解説動画の台本〜字幕生成サービス
        ├── Dockerfile          # サービス専用のDockerfile
        ├── app/                # 台本生成・結合・字幕化ロジック
        ├── assets/             # サービス専用アセット（フォントなど）
        ├── config/             # 各種設定（control.json, settings.yaml）
        ├── input/              # 入力データ（plan.txt, 音声素材）
        ├── output/             # 生成された成果物（テキスト、動画など）
        ├── prompts/            # 各ステップのシステムプロンプト
        ├── main.py             # サービス実行用エントリーポイント
        └── requirements.txt    # サービス固有の依存パッケージ
```

---

## 共通の環境設定

プロジェクトルート直下に環境変数ファイル `.env` を作成します。

1. `.env.example` をコピーして `.env` を作成します。
   ```bash
   cp .env.example .env
   ```
2. `.env` を開き、Gemini の API キーを設定します。
   ```text
   GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
   ```

---

## サービス1: 解説動画台本〜字幕生成 (`narrative-script`)

YouTubeの実話ストーリー解説系動画の台本制作を自動化し、音声データと字幕を組み合わせた動画（MP4）を出力するサービスです。

> [!NOTE]
> 4段階ナラティブ構成の定義、ナラティブ設計の原則（Show, don't tellのルールなど）、各ステップの処理フローや詳細な依存関係については、サービス個別のドキュメントである [services/narrative-script/README.md](file:///c:/Users/yoshi/OneDrive/デスクトップ/git/thb-footage/services/narrative-script/README.md) に整理されています。合わせてご参照ください。

### 1. サービスのビルド
ソースコードの変更や、`shared/` ディレクトリに変更があった場合は、以下のコマンドでDockerイメージを構築・更新します。
```bash
docker-compose build narrative-script
```

### 2. 実行の準備

実行に必要な設定ファイルや入力データを、`services/narrative-script/` 配下の適切なディレクトリに配置します。

#### ① 制御設定の編集 (`services/narrative-script/config/control.json`)
実行したいステップや、AIへの追加指示を設定します。
```json
{
    "next_step": "subtitle",
    "plan_file": "input/plan.txt",
    "request": "Bはあまりボイジャーに同情しすぎないで。"
}
```
- **`next_step`**: 実行したいステップ名、または一括実行の `"all"` を指定します。
  - `setup`: 導入部分（Set Up）の台本生成
  - `question`: 問い（Dramatic Question）の台本生成
  - `chronicle`: 探究（Chronicle of Discovery）の台本生成
  - `schema`: 解決（Schema Update）の台本生成
  - `merge`: 各ステップで生成された台本ファイルの結合
  - `format`: 結合台本を対話形式（A, B話者付与）かつ読点で改行するように整形
  - `subtitle`: 音声素材を結合し、テキストを合成した字幕動画（`.mp4`）の生成
  - `all`: 上記の全ステップを一括してシーケンシャルに実行

#### ② 入力データの配置
- **台本生成タスクを実行する場合**:
  `services/narrative-script/input/plan.txt` に、解説動画の企画書・プロットを記入します。
- **字幕動画生成タスクを実行する場合**:
  `services/narrative-script/input/voice/` 内に、以下の規則に従って音声ファイルと字幕原稿テキストファイルをペアで配置します。
  - 音声ファイル: `001_名前_タイトル.wav` (WAV形式)
  - 字幕テキスト: `001_名前_タイトル.txt` (TXT形式, UTF-8)
  ※冒頭の3桁の数字に基づいて、ペアリングおよび動画内での再生順序が決定されます。

---

### 3. サービスの実行コマンド

設定完了後、以下のいずれかの方法でサービスを実行します。

#### 方法A: 直接コマンドを指定して実行する（推奨）
コンテナを起動して、自動的に台本生成・字幕動画生成スクリプト（`main.py`）を実行します。
```bash
docker-compose run --rm narrative-script python main.py
```
- **`run`**: 新しいコンテナを作成してコマンドを実行します。
- **`--rm`**: コンテナの実行終了後に、不要になったコンテナを自動的に削除します（ディスク容量の圧迫を防ぐため、推奨されます）。
- **`narrative-script`**: 対象とするサービス名です。
- **`python main.py`**: コンテナ内で実行するコマンドです。

#### 方法B: コンテナ内のインタラクティブシェルに入って実行する
コンテナ内のターミナル（`bash`）に入り、内部から手動でコマンドを実行します。デバッグや対話的な操作を行う場合に便利です。
```bash
docker-compose run --rm narrative-script bash
```
1. 上記コマンドを実行すると、コンテナのシェル（ワーキングディレクトリ: `/workspace/services/narrative-script`）に入ります。
2. コンテナ内部で直接 Python スクリプトを実行します。
   ```bash
   python main.py
   ```
3. コンテナのシェルを抜けるには `exit` を実行します。

#### 実行結果の出力
- 生成された各種台本テキストおよび最終動画は、以下のディレクトリに出力されます。
  - 出力先: `services/narrative-script/output/`
- 音声結合・字幕動画（mp4）の出力先は以下の通りです。
  - 出力先: `services/narrative-script/output/07_subtitle/subtitle.mp4`

---

## 将来新しいサービスを追加する際の手順

別の用途（例: ランキング動画の台本作成 `ranking-script`）を追加する際は、以下の手順でシステムに組み込むことができます。

### 1. ディレクトリとファイルの作成
`services/` の下に新しいサービス用のディレクトリを作成し、必要なファイルを配置します。
```text
services/
└── ranking-script/
    ├── Dockerfile          # サービス専用のDockerfile
    ├── requirements.txt    # 必要なPythonライブラリ
    ├── main.py             # 実行エントリーポイント
    └── app/                # ロジックコード
```

### 2. Dockerfile の記述例
共通モジュール `shared/` をビルド時に同梱できるように、ビルドコンテキストをプロジェクトルート（`.`）に設定した `Dockerfile` を記述します。
```dockerfile
FROM python:3.11-slim

WORKDIR /workspace

# 依存パッケージのインストール
COPY services/ranking-script/requirements.txt ./services/ranking-script/requirements.txt
RUN pip install --no-cache-dir -r services/ranking-script/requirements.txt

# コード全体のコピー（共通モジュールsharedを含めるため）
COPY . .

WORKDIR /workspace/services/ranking-script
CMD ["python", "main.py"]
```

### 3. Docker Compose への登録
プロジェクトルート直下の `docker-compose.yml` に、新規サービスコンテナの定義を追加します。
```yaml
services:
  # 既存の解説動画生成サービス
  narrative-script:
    ...

  # 新規追加するランキング動画生成サービス
  ranking-script:
    build:
      context: .
      dockerfile: services/ranking-script/Dockerfile
    volumes:
      - .:/workspace
    working_dir: /workspace/services/ranking-script
    env_file:
      - .env
    stdin_open: true
    tty: true
```

### 4. 実行コマンド
追加した新規サービスは、以下のコマンドで同様にビルド・実行が可能です。
- **ビルド**:
  ```bash
  docker-compose build ranking-script
  ```
- **実行**:
  ```bash
  docker-compose run --rm ranking-script python main.py
  ```
