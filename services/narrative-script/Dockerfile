FROM python:3.11-slim

WORKDIR /workspace

# パッケージの依存関係をインストール
COPY services/narrative-script/requirements.txt ./services/narrative-script/requirements.txt
RUN pip install --no-cache-dir -r services/narrative-script/requirements.txt

# プロジェクト全体をコピー（sharedモジュールを含めるためビルドコンテキストはルートにする）
COPY . .

WORKDIR /workspace/services/narrative-script
CMD ["python", "main.py"]
