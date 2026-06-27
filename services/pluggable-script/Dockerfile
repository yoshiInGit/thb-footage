FROM python:3.11-slim

WORKDIR /workspace

# パッケージの依存関係をインストール
COPY services/pluggable-script/requirements.txt ./services/pluggable-script/requirements.txt
RUN pip install --no-cache-dir -r services/pluggable-script/requirements.txt

# プロジェクト全体をコピー
COPY . .

WORKDIR /workspace/services/pluggable-script
CMD ["python", "main.py"]
