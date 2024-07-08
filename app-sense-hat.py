import sqlite3
import time
from sense_hat import SenseHat
from signal import pause
from queue import Queue
from threading import Thread, Lock

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

# メニュー項目の設定（12個）
menu_items = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
              (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 128)]
current_item = 0

visitor_logging = False
entry_time = None

# イベントキューとロック
event_queue = Queue()
lock = Lock()

# メニューを表示する関数
def display_menu():
    sense.clear()
    for i in range(12):
        x = i % 4
        y = i // 4
        if i == current_item:
            sense.set_pixel(x, y, 255, 255, 255)  # 選択中の項目は白色で表示
        else:
            sense.set_pixel(x, y, menu_items[i])
    time.sleep(0.1)  # 少し待ってから次の表示

# センサーのデータをSQLiteに保存する関数
def log_sensor_data():
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

# 訪問者の入室時刻を記録する関数
def log_entry_time():
    global entry_time
    entry_time = time.strftime('%Y-%m-%d %H:%M:%S')
    with lock:
        c.execute("INSERT INTO visitor_log (entry_time) VALUES (?)", (entry_time,))
        conn.commit()

# 訪問者の退出時刻を記録する関数
def log_exit_time():
    global entry_time
    if entry_time:
        exit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with lock:
            c.execute("UPDATE visitor_log SET exit_time = ? WHERE entry_time = ?", (exit_time, entry_time))
            conn.commit()
        entry_time = None

# ジョイスティックのイベントを処理する関数
def joystick_left(event):
    if event.action == "pressed":
        event_queue.put("left")

def joystick_right(event):
    if event.action == "pressed":
        event_queue.put("right")

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
sense.stick.direction_middle = joystick_middle

# 初期メニュー表示
display_menu()

# イベントハンドラースレッドを開始
handler_thread = Thread(target=event_handler, daemon=True)
handler_thread.start()

# センサーデータを記録するスレッドを開始
sensor_thread = Thread(target=log_sensor_data, daemon=True)
sensor_thread.start()

pause()  # プログラムを終了させずに待機

# プログラム終了時にリソースを解放
sense.clear()
conn.close()

