import time
import random
import math
import sense_hat

sense = sense_hat.SenseHat()
sense.low_light = True

state = {
    "bug_x": 4,
    "bug_y": 4,
    "bug_rgb": (250, 250, 250),
    "food_x": 2,
    "food_y": 7,
    "food_rgb": (0, 255, 50),
    "level": 1,
    "enemies": [[4, 6], [0, 4]],
    "enemy_rgb": (255, 50, 0)
}

start_over_state = dict(state)

def setscreen():
    """画面を設定する関数"""
    bug_x = state["bug_x"]
    bug_y = state["bug_y"]
    bug_rgb = state["bug_rgb"]
    food_x = state["food_x"]
    food_y = state["food_y"]
    food_rgb = state["food_rgb"]
    enemies = state["enemies"]
    enemy_rgb = state["enemy_rgb"]

    if sense.low_light:
        zero = 8
    else:
        zero = 48
    brightness = 255 - zero
    sense.clear((50, 100, 150))
    sense.set_pixel(food_x, food_y, food_rgb)
    sense.set_pixel(bug_x, bug_y, bug_rgb)
    for e in enemies:
        sense.set_pixel(e[0], e[1], enemy_rgb)

def distance(x1, y1, x2, y2):
    """二点間の距離を計算する関数"""
    return math.hypot(x2 - x1, y2 - y1)

def clip(pixels, nmin=0, nmax=255):
    """RGB値が0〜255の範囲に収まるように調整する関数"""
    return tuple(max(min(nmax, n), nmin) for n in pixels)

def check_pos():
    """食べ物を食べたり敵にぶつかったりするかをチェックする関数"""
    global state
    bug_x = state["bug_x"]
    bug_y = state["bug_y"]
    food_x = state["food_x"]
    food_y = state["food_y"]
    level = state["level"]
    enemies = state["enemies"]

    weaker = int(10 * (level / 2))
    stronger = 10
    radius = 2.5
    fdist = distance(bug_x, bug_y, food_x, food_y)

    for e in enemies:
        edist = distance(bug_x, bug_y, e[0], e[1])
        if edist == 0:
            # 敵にぶつかったらゲームオーバー
            sense.show_message("Game Over, Level {0}".format(state["level"]))
            state = dict(start_over_state)
            return

    if fdist > radius:
        # 食べ物から遠い場合、弱くする
        state["bug_rgb"] = clip([abs(i - weaker) for i in state["bug_rgb"]])
    elif fdist == 0.0:
        # 食べ物を食べた場合、元気になる
        state["bug_rgb"] = (255, 255, 255)
        state["level"] += 1
        state["enemies"].append([random.randint(0, 7), random.randint(0, 7)])
        sense.show_message(str(state["level"]))
        time.sleep(1)
        # 新しい位置に食べ物を設定する（バグと同じ位置でないように）
        while True:
            state["food_x"] = random.randint(0, 7)
            if state["food_x"] != state["bug_x"]:
                break
        while True:
            state["food_y"] = random.randint(0, 7)
            if state["food_y"] != state["bug_y"]:
                break
    elif fdist < radius:
        # 食べ物に近づいた場合、少し強くする
        state["bug_rgb"] = clip([abs(i + stronger) for i in state["bug_rgb"]])

def rand_step(xy):
    """ランダムウォークの一歩を返す関数"""
    x, y = xy

    new_x = x + random.choice([-1, 0, 1])
    new_y = y + random.choice([-1, 0, 1])
    return [0 if new_x == 8 else 7 if new_x == -1 else new_x,
            0 if new_y == 8 else 7 if new_y == -1 else new_y]

def move_enemies():
    """敵を動かす関数"""
    global state
    enemies = state["enemies"]
    reserved = [[state["bug_x"], state["bug_y"]], [state["food_x"], state["food_y"]]]
    new_enemies = []
    for e in enemies:
        while True:
            new_e = rand_step(e)
            if new_e not in reserved:
                break
        new_enemies.append(new_e)
    state["enemies"] = new_enemies
    setscreen()

def draw_bug(event):
    """キープレスを受け取って画面を再描画する関数"""
    global state
    if event.action == sense_hat.ACTION_RELEASED:
        # リリースされたら無視する
        return
    elif event.direction == sense_hat.DIRECTION_UP:
        state["bug_x"] = state["bug_x"]
        state["bug_y"] = 7 if state["bug_y"] == 0 else state["bug_y"] - 1
    elif event.direction == sense_hat.DIRECTION_DOWN:
        state["bug_x"] = state["bug_x"]
        state["bug_y"] = 0 if state["bug_y"] == 7 else state["bug_y"] + 1
    elif event.direction == sense_hat.DIRECTION_RIGHT:
        state["bug_x"] = 0 if state["bug_x"] == 7 else state["bug_x"] + 1
        state["bug_y"] = state["bug_y"]
    elif event.direction == sense_hat.DIRECTION_LEFT:
        state["bug_x"] = 7 if state["bug_x"] == 0 else state["bug_x"] - 1
        state["bug_y"] = state["bug_y"]

    # イベント後に状態をチェックする
    setscreen()
    check_pos()
    setscreen()

def display_disco():
    """ディスコのようなフラッシュ効果を表示する関数"""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for _ in range(20):
        color = random.choice(colors)
        sense.clear(color)
        time.sleep(0.05)
    setscreen()

# 初期状態を設定
setscreen()
sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])

last_tick = round(time.time(), 1) * 10

while True:
    # 敵の動きはレベルが上がると速くなる
    timer = 20 - (state["level"] % 20)

    # 一定間隔で敵を動かす
    tick = round(time.time(), 1) * 10
    if (tick % timer == 0) and (tick > last_tick):
        move_enemies()
        last_tick = tick

    # ジョイスティックのイベントをポーリングして、画面を再描画する
    for event in sense.stick.get_events():
        draw_bug(event)

    # フラッシュ効果を表示する
    if state["level"] % 5 == 0:
        display_disco()

