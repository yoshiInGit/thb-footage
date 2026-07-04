FROM python:3.11-slim

WORKDIR /workspace

# パッケージの依存関係をインストール
COPY services/content-editor/requirements.txt ./services/content-editor/requirements.txt
RUN pip install --no-cache-dir -r services/content-editor/requirements.txt

# プロジェクト全体をコピー
COPY . .

WORKDIR /workspace/services/content-editor
CMD ["python", "main.py"]
