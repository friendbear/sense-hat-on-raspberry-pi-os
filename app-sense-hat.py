import sqlite3
import time
import random
from sense_hat import SenseHat
from threading import Thread

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
menu_layout = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (2, 1)]  # 2x2の格子位置
current_item = 0

visitor_logging = False
entry_time = None

# メニューを表示する関数
def display_menu():
    sense.clear()
    for i in range(4):
        x, y = menu_layout[i]
        color = menu_items[i] if i < len(menu_items) else (255, 255, 255)  # 空白の項目は白色
        sense.set_pixel(x, y, color if i != current_item else (255, 255, 255))  # 選択中の項目は白色で表示
    time.sleep(0.1)  # 少し待ってから次の表示

# センサーのデータをSQLiteに保存する関数
def log_sensor_data():
    while True:
        temp = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        conn_thread = sqlite3.connect('sensor_data.db')
        c_thread = conn_thread.cursor()
        c_thread.execute("INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) VALUES (?, ?, ?, ?)",
                         (timestamp, temp, humidity, pressure))
        conn_thread.commit()
        conn_thread.close()
        time.sleep(10)  # 10秒ごとにデータをログ

# 訪問者の入室時刻を記録する関数
def log_entry_time():
    global entry_time
    entry_time = time.strftime('%Y-%m-%d %H:%M:%S')
    conn_thread = sqlite3.connect('sensor_data.db')
    c_thread = conn_thread.cursor()
    c_thread.execute("INSERT INTO visitor_log (entry_time) VALUES (?)", (entry_time,))
    conn_thread.commit()
    conn_thread.close()

# 訪問者の退出時刻を記録する関数
def log_exit_time():
    global entry_time
    if entry_time:
        exit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        conn_thread = sqlite3.connect('sensor_data.db')
        c_thread = conn_thread.cursor()
        c_thread.execute("UPDATE visitor_log SET exit_time = ? WHERE entry_time = ?", (exit_time, entry_time))
        conn_thread.commit()
        conn_thread.close()
        entry_time = None

# ジョイスティックのイベントを処理する関数
def joystick_event(event):
    global current_item, visitor_logging
    if event.action == "pressed":
        if event.direction == "left":
            current_item = (current_item - 1) % len(menu_items)
        elif event.direction == "right":
            current_item = (current_item + 1) % len(menu_items)
        elif event.direction == "up":
            current_item = (current_item - 2) % len(menu_items)
        elif event.direction == "down":
            current_item = (current_item + 2) % len(menu_items)
        elif event.direction == "middle":
            if current_item == 2:
                if not visitor_logging:
                    log_entry_time()
                    sense.show_message("Entry Logged", text_colour=(0, 255, 0))
                    visitor_logging = True
                else:
                    log_exit_time()
                    sense.show_message("Exit Logged", text_colour=(255, 0, 0))
                    visitor_logging = False
        display_menu()

# ジョイスティックのイベントリスナーを設定
sense.stick.direction_left = joystick_event
sense.stick.direction_right = joystick_event
sense.stick.direction_up = joystick_event
sense.stick.direction_down = joystick_event
sense.stick.direction_middle = joystick_event

# 初期メニュー表示
display_menu()

# ディスコ風のキラキラ表示
def display_disco():
    while True:
        for x in range(8):
            for y in range(4):
                if (x, y) not in menu_layout:
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    sense.set_pixel(x, y, (r, g, b))
        time.sleep(0.1)
        sense.clear()
        time.sleep(0.1)

# スレッドを開始してディスコ風表示を実行
disco_thread = Thread(target=display_disco, daemon=True)
disco_thread.start()

# ジョイスティックのイベントハンドラを維持してプログラムを実行
while True:
    for event in sense.stick.get_events():
        joystick_event(event)

