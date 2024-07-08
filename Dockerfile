# ベースイメージとしてRaspberry Pi OS用のPython 3.9イメージを使用
FROM balenalib/rpi-raspbian:stretch

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    sense-hat \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# sense-hatライブラリをインストール
RUN pip3 install sense-hat

# 作業ディレクトリを設定
WORKDIR /app

# アプリケーションファイルをコンテナにコピー
COPY . /app

# アプリケーションを実行
CMD ["python3", "app-sense-hat.py"]
