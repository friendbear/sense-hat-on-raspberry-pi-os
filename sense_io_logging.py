import sqlite3
import time
from sense_hat import SenseHat
from signal import pause

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

# メニュー項目
menu_items = ["Start Logging", "Stop Logging", "Visitor Log"]
current_item = 0

logging = False
visitor_logging = False
entry_time = None

# メニューを表示する関数
def display_menu():
    global current_item
    sense.clear()
    for i, item in enumerate(menu_items):
        color = (0, 255, 0) if i == current_item else (255, 255, 255)
        sense.show_message(item, text_colour=color, scroll_speed=0.05)
    time.sleep(0.5)  # 少し待ってから次の表示

# センサーのデータをSQLiteに保存する関数
def log_sensor_data():
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) VALUES (?, ?, ?, ?)", 
              (timestamp, temp, humidity, pressure))
    conn.commit()

# 訪問者の入室時刻を記録する関数
def log_entry_time():
    global entry_time
    entry_time = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO visitor_log (entry_time) VALUES (?)", (entry_time,))
    conn.commit()

# 訪問者の退出時刻を記録する関数
def log_exit_time():
    global entry_time
    if entry_time:
        exit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE visitor_log SET exit_time = ? WHERE entry_time = ?", (exit_time, entry_time))
        conn.commit()
        entry_time = None

# ジョイスティックのイベントを処理する関数
def joystick_up(event):
    global current_item
    if event.action == "pressed":
        current_item = (current_item - 1) % len(menu_items)
        display_menu()

def joystick_down(event):
    global current_item
    if event.action == "pressed":
        current_item = (current_item + 1) % len(menu_items)
        display_menu()

def joystick_middle(event):
    global logging, visitor_logging
    if event.action == "pressed":
        if current_item == 0 and not logging:
            logging = True
            sense.show_message("Logging Started", text_colour=(0, 255, 0))
            while logging:
                log_sensor_data()
                time.sleep(10)  # 10秒ごとにデータをログ
                for event in sense.stick.get_events():
                    if event.action == "pressed" and event.direction == "middle":
                        logging = False
                        sense.show_message("Logging Stopped", text_colour=(255, 0, 0))
                        break
        elif current_item == 1 and logging:
            logging = False
            sense.show_message("Logging Stopped", text_colour=(255, 0, 0))
        elif current_item == 2:
            if not visitor_logging:
                log_entry_time()
                sense.show_message("Entry Logged", text_colour=(0, 255, 0))
                visitor_logging = True
            else:
                log_exit_time()
                sense.show_message("Exit Logged", text_colour=(255, 0, 0))
                visitor_logging = False

# ジョイスティックのイベントリスナーを設定
sense.stick.direction_up = joystick_up
sense.stick.direction_down = joystick_down
sense.stick.direction_middle = joystick_middle

# 初期メニュー表示
display_menu()

pause()  # プログラムを終了させずに待機

# プログラム終了時にリソースを解放
sense.clear()
conn.close()

