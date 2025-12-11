import pygame, sys, pymunk,random,math,os

# 初期化
pygame.init()
pygame.mixer.init()

# フォント
big_font = pygame.font.SysFont("meiryo", 100)
font = pygame.font.SysFont("meiryo", 60)
small_font = pygame.font.SysFont("meiryo", 30)

# 画像と画面
sky_img = pygame.image.load("sky.png")
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("積みゲー：フルスクリーン")
sky_img = pygame.transform.scale(sky_img, (WIDTH, HEIGHT))

#画像一覧
#透過を保持したまま雲の画像を読み込み
cloud_imgs = [
    pygame.image.load("cloud.png").convert_alpha()
]

import os

TARGET_SIZE = (80, 80)

ball_imgs = []

filenames = [
    "ゴミ拾い.png",
    "お辞儀.png",
    "植林.png",
    "道案内.png",
    "席を譲る.png",
    "ヘルメットをする.png",
    "募金.png",
    "落とし物を届ける.png",
    "世界を救う.png"
]

for filename in filenames:
    img = pygame.image.load(filename).convert_alpha()
    img = pygame.transform.smoothscale(img, TARGET_SIZE)
    # 画像とファイル名をセットで保存
    ball_imgs.append({"image": img, "filename": filename})
clouds = [] #空のリストを生成
for i, img in enumerate(cloud_imgs):
    w, h = img.get_size()
    x = WIDTH // 4 + i * (WIDTH // 4)
    # 高さを上半分だけに制限
    y = random.randint(0, HEIGHT//4 )  
    speed = 0.5 + i * 0.3
    clouds.append({"img": img, "x": x, "y": y, "speed": speed})


# 物理空間
space = pymunk.Space()
space.gravity = 0, -1000
clock = pygame.time.Clock()
FPS = 60

# 色
SKY = (200, 230, 255)
BUTTON_COLOR = (255, 255, 25)
BLACK = (0,0,0)

#pymunkの座標をpygameの座標基準に変換
def convert_cordinates(point):
    return point[0], HEIGHT - point[1]

# 状態管理
STATE_TITLE, STATE_PLAY, STATE_RULE,STATE_BOOK = "title", "play", "rule","book"
game_state = STATE_TITLE

# ボタン
start_button = pygame.Rect(WIDTH//2-125, HEIGHT//2, 250, 100)
rule_button = pygame.Rect(WIDTH//2-125, int(HEIGHT/1.5), 250, 100)
back_button = pygame.Rect(WIDTH//2-125, int(HEIGHT/1.2), 250, 100)
temporary_button = pygame.Rect(WIDTH-70, 10, 60, 60)
temporary_one = pygame.Rect(WIDTH-55, 25, 8, 30)
temporary_two = pygame.Rect(WIDTH-33, 25, 8, 30)

#   形ごとの得点(dict)
POINTS = {
    "square": 40,
    "trapezoid": 40,
    "hex": 60,
    "circle": 100
}

#BGMを無限ループ
def play_music(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1)


#タイトル画面
def draw_title():
    global clouds
    screen.blit(sky_img, (0, 0))
    # 雲を流す（画面外に出たら右へリスポーン)
    for cloud in clouds:
        cloud["x"] -= cloud["speed"]
        if cloud["x"] < -cloud["img"].get_width():
            cloud["x"] = WIDTH + random.randint(0, 200)
            cloud["y"] = random.randint(0, HEIGHT//4)
        screen.blit(cloud["img"], (cloud["x"], cloud["y"]))

    # タイトルの表示
    title_text = big_font.render("善行を積め!!", True, BLACK)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))

    # タイトル画面に文字を表示
    for btn, text in [(start_button, "スタート"), (rule_button, "遊び方")]:
        pygame.draw.rect(screen, BUTTON_COLOR, btn, border_radius=20)
        t = font.render(text, True, BLACK)
        screen.blit(t, (btn.centerx - t.get_width()//2, btn.centery - t.get_height()//2))
        pygame.draw.rect(screen, BLACK, btn, 3, border_radius=20)

    # 本画像の読み込み（透過済み画像を使う）
    book_img = pygame.image.load("zukan.png").convert_alpha()
    book_img = pygame.transform.scale(book_img, (80, 80))  # サイズ調整

    # 右下に表示
    book_rect = book_img.get_rect(bottomright=(WIDTH - 30, HEIGHT - 30))
    screen.blit(book_img, book_rect)

    # ボタン領域として使う
    return book_rect


#ルール画面
def draw_rule():
    screen.fill((220, 220, 220)) #背景を塗りつぶし
    rules = ["【遊び方】","1. マウスでブロックを左右に動かします。",
             "2. クリックでブロックを落とします。",
             "3. 地面や積み上げたブロックに重ねて積みます。",
             "4. たくさん積んでスコアアップを目指そう"] #ルールの内容
    y = HEIGHT//4 #1行目の高さ
    for line in rules: #rulesのリストの数だけループ
        t = small_font.render(line, True, BLACK)
        screen.blit(t, (WIDTH//2-t.get_width()//2, y))
        y += 70 #高さを変更

    #戻るボタン
    t = font.render("戻る", True, BLACK)
    screen.blit(t, (back_button.centerx-t.get_width()//2, back_button.centery-t.get_height()//2))
    pygame.draw.rect(screen, BLACK, back_button, 3, border_radius=20)

def draw_book():
    screen.fill((230,230,230))
    title = big_font.render("ブロック図鑑", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    # 配置設定
    cols = 3                     # 1行に並べる数
    gap_x, gap_y = 300, 150      # 画像間隔
    start_y = 220                # タイトルより下に開始

    # グリッド全体の幅を計算して中央寄せ
    grid_width = cols * gap_x
    start_x = WIDTH//2 - grid_width//2 + 120

    for i, data in enumerate(ball_imgs):
        img = data["image"]
        filename = data["filename"]

        # 拡張子を除いた名前だけ表示
        name_only = os.path.splitext(filename)[0]

        rect = img.get_rect(topleft=(start_x + (i % cols) * gap_x,
                                     start_y + (i // cols) * gap_y))
        screen.blit(img, rect)

        # ←ここを追加：ラベル描画
        label = small_font.render(name_only, True, BLACK)
        screen.blit(label, (rect.centerx - label.get_width()//2, rect.bottom + 5))

    # 戻るボタン
    back_button = pygame.Rect(WIDTH//2 - 120, HEIGHT - 80, 240, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, back_button, border_radius=20)
    t = small_font.render("タイトルへ", True, BLACK)
    screen.blit(t, (back_button.centerx - t.get_width()//2, back_button.centery - t.get_height()//2))
    pygame.draw.rect(screen, BLACK, back_button, 3, border_radius=20)

    pygame.display.update()
    return back_button
#物理空間初期化
def reset_space():
    global space,field
    space = pymunk.Space() #物理シュミレーション空間を生成
    space.gravity = (0, -1000) #pymunkでは左下が原点なので負の値を入れる
    field = create_field(300,100,1000,100)

#積む物体の形についての情報
#ランダム生成
def create_random_block(x, y, add_to_space=True):
    # 画像インデックスと重みを指定
    indices = list(range(9))  # 0〜8
    weights = [
        2.5, 2.5, 2.5,   # 四角形 (ball1〜3)
        2.5, 2.5, 2.5,   # 台形 (ball4〜6)
        2, 2,            # 六角形 (ball7〜8)
        1                # 円 (ball9)
    ]

    idx = random.choices(indices, weights=weights, k=1)[0]
    data = ball_imgs[idx]      # ← dict を取り出す
    img = data["image"]        # ← Surface を取り出す

    if idx in [0, 1, 2]:   # 四角形
        return create_square(x, y, img, size=70, mass=70, add_to_space=add_to_space)
    elif idx in [3, 4, 5]: # 台形
        return create_trapezoid(x, y, img, top=60, bottom=80, height=70, mass=70, add_to_space=add_to_space)
    elif idx in [6, 7]:   # 六角形
        return create_hexball(x, y, img, radius=40, mass=50, add_to_space=add_to_space)
    else:                 # 円
        return create_circle(x, y, img, radius=40, mass=50, add_to_space=add_to_space)
def draw_block(block):
    if block["type"]=="square":
        draw_square(block)
    elif block["type"]=="trapezoid":
        draw_trapezoid(block)
    elif block["type"]=="hex":
        draw_hexball(block)
    else:
        draw_circle(block)

#四角形の情報
def create_square(x, y, img, size=60, mass=60, add_to_space=True):
    scaled_img = pygame.transform.scale(img, (size, size))
    moment = pymunk.moment_for_box(mass, (size, size))
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = (x, 700)  # 固定でOK
    half = size // 2
    vertices = [(-half, -half), (half, -half), (half, half), (-half, half)]
    shape = pymunk.Poly(body, vertices)
    shape.elasticity = 0.2
    shape.friction = 0.5
    if add_to_space:
        space.add(body, shape)
    return {"type": "square", "size": size, "img": scaled_img,
            "body": body, "shape": shape}

def draw_square(block):
    pos = convert_cordinates(block["body"].position)
    angle_deg = -math.degrees(block["body"].angle)  # pymunk角度をpygame用に変換

    # 画像を角度に合わせて回転
    rotated_img = pygame.transform.rotozoom(block["img"], angle_deg, 1.0)
    rect = rotated_img.get_rect(center=pos)
    screen.blit(rotated_img, rect)

    # 枠線も描画
    half = block["size"]//2
    verts = [(-half,-half),(half,-half),(half,half),(-half,half)]
    angle = block["body"].angle
    verts_rotated = [(vx*math.cos(angle)-vy*math.sin(angle),
                      vx*math.sin(angle)+vy*math.cos(angle)) for (vx,vy) in verts]
    verts_screen = [(pos[0]+vx,pos[1]-vy) for (vx,vy) in verts_rotated]
    pygame.draw.polygon(screen, BLACK, verts_screen, width=2)


def create_trapezoid(x, y, img, top, bottom, height, mass, add_to_space=True):
    scaled_img = pygame.transform.scale(img, (bottom, height))
    half_top, half_bottom, h = top//2, bottom//2, height//2
    vertices = [(-half_bottom,-h),(half_bottom,-h),(half_top,h),(-half_top,h)]
    moment = pymunk.moment_for_poly(mass, vertices)
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = (x, 700)
    shape = pymunk.Poly(body, vertices)
    shape.elasticity = 0.2
    shape.friction = 0.5
    if add_to_space:
        space.add(body, shape)
    return {"type":"trapezoid","top":top,"bottom":bottom,"height":height,
            "img":scaled_img,"body":body,"shape":shape}

def draw_trapezoid(block):
    pos = convert_cordinates(block["body"].position)
    angle_deg = -math.degrees(block["body"].angle)

    # 画像を角度に合わせて回転
    rotated_img = pygame.transform.rotozoom(block["img"], angle_deg, 1.0)
    rect = rotated_img.get_rect(center=pos)
    screen.blit(rotated_img, rect)

    # 枠線も描画
    half_top, half_bottom, h = block["top"]//2, block["bottom"]//2, block["height"]//2
    verts = [(-half_bottom,-h),(half_bottom,-h),(half_top,h),(-half_top,h)]
    angle = block["body"].angle
    verts_rotated = [(vx*math.cos(angle)-vy*math.sin(angle),
                      vx*math.sin(angle)+vy*math.cos(angle)) for (vx,vy) in verts]
    verts_screen = [(pos[0]+vx,pos[1]-vy) for (vx,vy) in verts_rotated]
    pygame.draw.polygon(screen, BLACK, verts_screen, width=2)
def hexagon_vertices(radius):
    return [(radius*math.cos(math.radians(60*i)),
             radius*math.sin(math.radians(60*i))) for i in range(6)]

def create_hexball(x, y, img, radius, mass, add_to_space=True):
    scaled_img = pygame.transform.scale(img, (radius*2, radius*2))
    vertices = hexagon_vertices(radius)
    moment = pymunk.moment_for_poly(mass, vertices)
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = (x, 700)
    shape = pymunk.Poly(body, vertices)
    shape.elasticity = 0.2
    shape.friction = 0.5
    if add_to_space:
        space.add(body, shape)
    return {"type":"hex","radius":radius,"img":scaled_img,"body":body,"shape":shape}

def draw_hexball(block):
    pos = convert_cordinates(block["body"].position)
    angle_deg = -math.degrees(block["body"].angle)

    # 画像を角度に合わせて回転
    rotated_img = pygame.transform.rotozoom(block["img"], angle_deg, 1.0)
    rect = rotated_img.get_rect(center=pos)
    screen.blit(rotated_img, rect)

    # 枠線も描画
    verts = hexagon_vertices(block["radius"])
    angle = block["body"].angle
    verts_rotated = [(vx*math.cos(angle)-vy*math.sin(angle),
                      vx*math.sin(angle)+vy*math.cos(angle)) for (vx,vy) in verts]
    verts_screen = [(pos[0]+vx,pos[1]-vy) for (vx,vy) in verts_rotated]
    pygame.draw.polygon(screen, BLACK, verts_screen, width=2)

# --- 円 ---
def create_circle(x, y, img, radius, mass,add_to_space=True):
    scaled_img = pygame.transform.scale(img, (radius*2, radius*2))
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = (x, 700)
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.1
    shape.friction = 0.7
    if add_to_space:
        space.add(body, shape)
    return {"type":"circle","radius":radius,"img":scaled_img,"body":body,"shape":shape}
def draw_circle(block):
    pos = convert_cordinates(block["body"].position)
    rect = block["img"].get_rect(center=pos)
    screen.blit(block["img"], rect)
    pygame.draw.circle(screen, BLACK, pos, block["radius"], width=2)




def create_field(tlx, tly, brx, bry):
    bl_start, bl_stop = (tlx, bry), (brx, bry)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, bl_start, bl_stop, 3)
    shape.elasticity, shape.friction = 0.75, 0.9
    space.add(shape, body)
    return {"bl_start": bl_start, "bl_stop": bl_stop, "ground_y": bry}
def draw_field(field):
    x1, y1 = convert_cordinates(field["bl_start"])
    x2, y2 = convert_cordinates(field["bl_stop"])
    pygame.draw.rect(screen, (80,60,40),
                     (min(x1,x2), min(y1,y2), abs(x2-x1), 100))


def draw_pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,150))
    screen.blit(overlay,(0,0))
    menu_rect = pygame.Rect(WIDTH//2-300, HEIGHT//2-200, 600, 400)
    pygame.draw.rect(screen,(240,240,240),menu_rect,border_radius=20)
    pygame.draw.rect(screen,BLACK,menu_rect,3,border_radius=20)
    pause_text = font.render("ポーズ中",True,BLACK)
    screen.blit(pause_text,(menu_rect.centerx-pause_text.get_width()//2, menu_rect.top+40))
    resume_button = pygame.Rect(menu_rect.centerx-120, menu_rect.centery-40, 240, 60)
    title_button = pygame.Rect(menu_rect.centerx-120, menu_rect.centery+40, 240, 60)
    for btn,text in [(resume_button,"再開"),(title_button,"タイトルへ戻る")]:
        pygame.draw.rect(screen,BUTTON_COLOR,btn,border_radius=15)
        t = small_font.render(text,True,BLACK)
        screen.blit(t,(btn.centerx-t.get_width()//2, btn.centery-t.get_height()//2))
        pygame.draw.rect(screen,BLACK,btn,2,border_radius=15)
    return resume_button,title_button

def draw_play():
    global paused, game_state,space
    paused = False
    reset_space()
    field = create_field(300,100,1000,100)
    ground_y = field["ground_y"]
    balls = []
    score = 0

    # 最初の保持ブロック（spaceに追加しない）
    current_block = create_random_block(WIDTH//2, 700, add_to_space=False)

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if temporary_button.collidepoint(event.pos): 
                    click_sound = pygame.mixer.Sound("pose.mp3"); click_sound.play()
                    paused=True
                elif paused and resume_button and resume_button.collidepoint(event.pos): 
                    click_sound = pygame.mixer.Sound("click.mp3"); click_sound.play()
                    paused=False
                elif paused and title_button and title_button.collidepoint(event.pos):
                    click_sound = pygame.mixer.Sound("click.mp3"); click_sound.play()
                    paused=False; game_state=STATE_TITLE; reset_space(); return score
                elif not paused:
                # 落とす処理（カーソルxに合わせる）
                    mouse_x, _ = pygame.mouse.get_pos()
                    x, _ = convert_cordinates((mouse_x, 700))
                    current_block["body"].position = (x, 700)
                    space.add(current_block["body"], current_block["shape"])
                    balls.append(current_block) 
                    score += POINTS[current_block["type"]]

                    drop_sound = pygame.mixer.Sound("drop.mp3")
                    drop_sound.play()

                # 次の保持ブロックを生成（spaceに追加しない）
                    current_block = create_random_block(WIDTH//2, 700, add_to_space=False)

        # --- 描画 ---
        screen.fill(SKY)
        draw_field(field)
        for b in balls:
            draw_block(b)

        pygame.draw.rect(screen, (0,0,0), temporary_button,3, border_radius=10)
        pygame.draw.rect(screen,(0,0,0),temporary_one, border_radius = 5)
        pygame.draw.rect(screen,(0,0,0),temporary_two, border_radius = 5)
        # --- プレビュー表示（カーソルxに連動、yは固定700） ---
        if not paused:
            mouse_x, _ = pygame.mouse.get_pos()
            current_block["body"].position = (mouse_x, 700)
        draw_block(current_block)

        score_text = small_font.render(f"スコア: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        if paused: resume_button,title_button=draw_pause_overlay()
        for b in balls:
            if b["body"].position.y < ground_y:
                game_state = "result"
                return score

        pygame.display.update()
        clock.tick(FPS)
        space.step(1/FPS)

def draw_result(final_score):
    screen.fill((220,220,220))
    result_text = big_font.render("リザルト", True, BLACK)
    screen.blit(result_text, (WIDTH//2-result_text.get_width()//2, HEIGHT//4))

    score_text = font.render(f"スコア: {final_score}", True, BLACK)
    screen.blit(score_text, (WIDTH//2-score_text.get_width()//2, HEIGHT//2))
    pygame.draw.rect(screen, BUTTON_COLOR, back_button, border_radius=20)
    t = small_font.render("タイトルへ", True, BLACK)
    screen.blit(t, (back_button.centerx-t.get_width()//2, back_button.centery-t.get_height()//2))
    pygame.draw.rect(screen, BLACK, back_button, 3, border_radius=20)

    pygame.display.update()
    return back_button

def main():
    global game_state,back_button
    current_music = None
    score = 0

    while True:
        if game_state == STATE_PLAY:
            # 音楽切り替え
            if current_music != "play.mp3":
                play_music("play.mp3")
                current_music = "play.mp3"
            score = draw_play()

        elif game_state == "result":
            if current_music != "result.mp3":
                play_music("result.mp3")
                current_music = "result.mp3"

            back_button = draw_result(score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                    click_sound = pygame.mixer.Sound("click.mp3")
                    click_sound.play()
                    game_state = STATE_TITLE

        elif game_state == STATE_TITLE:
            book_button = draw_title()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_sound = pygame.mixer.Sound("click.mp3")
                    click_sound.play()
                    if start_button.collidepoint(event.pos):
                        game_state = STATE_PLAY
                    elif rule_button.collidepoint(event.pos):
                        game_state = STATE_RULE
                    elif book_button.collidepoint(event.pos):   # ←ここを追加
                        game_state = STATE_BOOK

            # 音楽切り替え
            if current_music != "title.mp3":
                play_music("title.mp3")
                current_music = "title.mp3"
            draw_title()

        elif game_state == STATE_RULE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                    click_sound = pygame.mixer.Sound("click.mp3")
                    click_sound.play()
                    game_state = STATE_TITLE
            # 音楽切り替え
            if current_music != "title.mp3":
                play_music("title.mp3")
                current_music = "title.mp3"
            draw_rule()
        elif game_state == STATE_BOOK:
            back_button = draw_book()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                    click_sound = pygame.mixer.Sound("click.mp3")
                    click_sound.play()
                    game_state = STATE_TITLE

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()


