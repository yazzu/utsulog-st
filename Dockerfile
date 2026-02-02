# cuDNN 9 を含む NVIDIA 公式イメージを使用
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# タイムゾーンの設定などを非対話的に行うための設定
ENV DEBIAN_FRONTEND=noninteractive

# 必要なシステムパッケージとPythonのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# python3 コマンドを python として使えるようにシンボリックリンクを作成
RUN ln -s /usr/bin/python3 /usr/bin/python

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 作業ディレクトリの設定
WORKDIR /app

# Pythonライブラリのインストール
# --system フラグを使用してベースのPython環境に直接インストールします
# Whisper関連: faster-whisper, stable-ts
# Gemini関連: google-genai
# Ginaz関連: ginza
# その他: webvtt-py (VTT操作用)
RUN uv pip install --system --no-cache \
    faster-whisper \
    stable-ts \
    google-genai \
    pathvalidate \
    webvtt-py \
    ginza \
    ja_ginza

# コンテナ起動時のデフォルトコマンド
CMD ["bash"]
