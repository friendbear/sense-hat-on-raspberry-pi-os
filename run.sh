#!/bin/bash

# 定義: スクリプトのディレクトリを保存
SCRIPT_DIR="/home/pi/Develop/sense-hat"

# 仮想環境を使用する場合の設定
# VENV_DIR="/home/pi/venv"
# source $VENV_DIR/bin/activate

# Pythonの依存関係をインストール
echo "インストールの準備中です..."

# 必要なパッケージをアップグレード
pip install --upgrade pip setuptools

# 必要なパッケージをインストール
pip install numpy pygame

# RTIMUをクローンしてインストール
if [ ! -d "$SCRIPT_DIR/RTIMU" ]; then
  echo "RTIMUが見つからないため、クローンしています..."
  git clone https://github.com/RPi-Distro/RTIMULib.git "$SCRIPT_DIR/RTIMU"
fi

# RTIMUのビルドとインストール
echo "RTIMUのビルドとインストールを開始します..."
cd "$SCRIPT_DIR/RTIMU"
./build.sh

# 環境変数にRTIMUのパスを追加
export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/RTIMU/python

# スクリプトの実行
echo "スクリプトを実行しています..."
python3 "$SCRIPT_DIR/hanabi_v5.py"

