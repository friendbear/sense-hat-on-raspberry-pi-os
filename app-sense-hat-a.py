import sqlite3
import time
from sense_hat import SenseHat
from signal import pause
from queue import Queue
from threading import Thread, Lock
import pyaudio
import numpy as np

sense = SenseHat()
sense.clear()

# SQLiteデータベースの設定
conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
             (timestamp TEXT, temperature REAL, humidity REAL, pressure REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS visitor_log
             (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_time TEXT, exit_time TEXT)''')
conn.commit()

# メニュー項目の設定（6つ）
menu_items = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
menu_layout = [(0, 0), (2, 0), (0, 2), (2, 2), (4, 0), (4, 2)]  # 2x2の格子位置
current_item = 0

visitor_logging = False
entry_time = None

# イベントキューとロック
event_queue = Queue()
lock = Lock()

# PyAudioの設定
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# 音の大きさに応じて明るさを調整する関数
def adjust_brightness():
    while True:
        data = np.frombuffer(stream.read(1024), dtype=np.int16)
        peak = np.average(np.abs(data)) * 2
        brightness = min(1.0, peak / 32767)  # 正規化して0.0から1.0の範囲にする
        adjusted_colors = [(int(brightness * r), int(brightness * g), int(brightness * b)) for r, g, b in menu_items]
        display_menu(adjusted_colors)
        time.sleep(0.1)

# メニューを表示する関数
def display_menu(adjusted_colors=None):
    sense.clear()
    colors = adjusted_colors if adjusted_colors else menu_items
    for i in range(6):
        x, y = menu_layout[i]
        color = colors[i] if i < len(colors) else (255, 255, 255)  # 空白の項目は白色
        for dx in range(2):
            for dy in range(2):
                sense.set_pixel(x + dx, y + dy, color if i != current_item else (255, 255, 255))  # 選択中の項目は白色で表示

# 現在の時間を表示する関数
def display_time():
    while True:
        current_time = time.strftime('%H:%M:%S')
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        for color in colors:
            for y in range(4, 8):
                for x in range(8):
                    sense.set_pixel(x, y, color)
            time.sleep(0.5)
            sense.show_message(current_time, text_colour=color, back_colour=(0, 0, 0))
            time.sleep(0.5)

# センサーのデータをSQLiteに保存する関数
def log_sensor_data():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    while True:
        temp = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with lock:
            c.execute("INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) VALUES (?, ?, ?, ?)", 
                      (timestamp, temp, humidity, pressure))
            conn.commit()
        time.sleep(10)  # 10秒ごとにデータをログ
    conn.close()

# 訪問者の入室時刻を記録する関数
def log_entry_time():
    global entry_time
    entry_time = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    with lock:
        c.execute("INSERT INTO visitor_log (entry_time) VALUES (?)", (entry_time,))
        conn.commit()
    conn.close()

# 訪問者の退出時刻を記録する関数
def log_exit_time():
    global entry_time
    if entry_time:
        exit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('sensor_data.db')
        c = conn.cursor()
        with lock:
            c.execute("UPDATE visitor_log SET exit_time = ? WHERE entry_time = ?", (exit_time, entry_time))
            conn.commit()
        conn.close()
        entry_time = None

# ジョイスティックのイベントを処理する関数
def joystick_left(event):
    if event.action == "pressed":
        event_queue.put("left")

def joystick_right(event):
    if event.action == "pressed":
        event_queue.put("right")

def joystick_up(event):
    if event.action == "pressed":
        event_queue.put("up")

def joystick_down(event):
    if event.action == "pressed":
        event_queue.put("down")

def joystick_middle(event):
    if event.action == "pressed":
        event_queue.put("middle")

# イベントを処理するスレッド
def event_handler():
    global current_item, visitor_logging
    while True:
        event = event_queue.get()
        with lock:
            if event == "left":
                current_item = (current_item - 1) % len(menu_items)
                display_menu()
            elif event == "right":
                current_item = (current_item + 1) % len(menu_items)
                display_menu()
            elif event == "up":
                current_item = (current_item - 2) % len(menu_items)
                display_menu()
            elif event == "down":
                current_item = (current_item + 2) % len(menu_items)
                display_menu()
            elif event == "middle":
                if current_item == 2:
                    if not visitor_logging:
                        log_entry_time()
                        sense.show_message("Entry Logged", text_colour=(0, 255, 0))
                        visitor_logging = True
                    else:
                        log_exit_time()
                        sense.show_message("Exit Logged", text_colour=(255, 0, 0))
                        visitor_logging = False

# ジョイスティックのイベントリスナーを設定
sense.stick.direction_left = joystick_left
sense.stick.direction_right = joystick_right
sense.stick.direction_up = joystick_up
sense.stick.direction_down = joystick_down
sense.stick.direction_middle = joystick_middle

# 初期メニュー表示
display_menu()

# イベントハンドラースレッドを開始
handler_thread = Thread(target=event_handler, daemon=True)
handler_thread.start()

# センサーデータを記録するスレッドを開始
sensor_thread = Thread(target=log_sensor_data, daemon=True)
sensor_thread.start()

# 現在時刻を表示するスレッドを開始
time_thread = Thread(target=display_time, daemon=True)
time_thread.start()

# 音の大きさに応じて明るさを調整するスレッドを開始
brightness_thread = Thread(target=adjust_brightness, daemon=True)
brightness_thread.start()

pause()  # プログラムを終了させずに待機

# プログラム終了時にリソースを解放
sense.clear()
stream.stop_stream()
stream.close()
p.terminate()

