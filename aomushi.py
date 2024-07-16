import os
import sys
import pygame as pg
from collections import deque
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 500  # ゲームウィンドウの幅
HEIGHT = 500  # ゲームウィンドウの高さ
SIZE = 20

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird():
    """
    こうかとんに関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed=3
        
    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.5)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        
        screen.blit(self.image, self.rect)

class Timer():
    def __init__(self):
        self.start_time = pg.time.get_ticks()  # ゲーム開始時の時間を取得
        self.font = pg.font.Font(None, 25)  # フォントの設定
        self.color = (0, 0, 0)  # 文字の色
        self.rect = pg.Rect(WIDTH - 120, HEIGHT - 50, 100, 30)  # タイマーの位置とサイズの設定
        self.time = 0

    def update(self, screen):
        self.time = (pg.time.get_ticks() - self.start_time) // 1000  # 経過時間の計算（秒単位）
        timer_str = f"Timer: {self.time} sec"  # 表示する文字列の作成
        timer_surface = self.font.render(timer_str, True, self.color)  # 文字列を描画するSurfaceを作成
        screen.blit(timer_surface, self.rect)  # 画面に描画
                    
class Score:
    """
    Scoreに関するクラス
    Score_valueは、Timer_timeと連携している。
    """
    def __init__(self, timer:Timer):
        self.font = pg.font.Font(None, 25)
        self.color = (0, 0, 255)
        self.value = timer.time*2
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 50, HEIGHT-25
        self.miss = 0

    def update(self, timer:Timer, screen: pg.Surface):
        self.value = timer.time*2 +self.miss
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class Insect(pg.sprite.Sprite):
    """
    青虫に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_w: (0, -SIZE),
        pg.K_s: (0, SIZE),
        pg.K_a: (-SIZE, 0),
        pg.K_d: (SIZE, 0),        
    }
    jump_height = -25  # ジャンプの高さ
    gravity = 5  # 重力の強さ
    
    def __init__(self):
        super().__init__()
        self.body = deque([[WIDTH//2, HEIGHT-50], [WIDTH//2-SIZE, HEIGHT-50], [WIDTH//2-2*SIZE, HEIGHT-50]])  # 初期青虫
        self.direction = (0, 0)  # 初期の移動方向
        self.body_image = pg.image.load("fig/body_L.png")  # 虫の体の画像を読み込む
        self.jump_velocity = 0  # ジャンプの速度
        self.is_jumping = False  # ジャンプ中かどうかのフラグ
        self.start_y = HEIGHT - 50  # ジャンプ開始時の初期位置
        self.rect = pg.Rect(self.body[0], (SIZE, SIZE))  # 初期の位置とサイズで矩形を作成
        self.body_rects=[self.body_image.get_rect(topleft=segment)for segment in self.body]

    def update(self, key_lst: list[bool]):
        sum_mv = [0, 0]
        move_keys = [k for k in __class__.delta if key_lst[k]]
        self.body_rects=[self.body_image.get_rect(topleft=segment)for segment in self.body]

        if len(move_keys) == 1:  # 1つの方向キーが押されている場合のみ移動
            k = move_keys[0]
            sum_mv[0] += __class__.delta[k][0]//2
            sum_mv[1] += __class__.delta[k][1]//2
        
        if key_lst[pg.K_SPACE] and not self.is_jumping:
            self.jump_velocity = __class__.jump_height
            self.is_jumping = True
            self.start_y = self.body[0][1]  # ジャンプ開始時の初期位置を記憶
        
        if self.is_jumping:
            self.jump_velocity += __class__.gravity
            sum_mv[1] += self.jump_velocity
        
        # 新しいヘッドを作成
        new_head = [self.body[0][0] + sum_mv[0], self.body[0][1] + sum_mv[1]]
        
        # ジャンプが元の位置に戻ったらジャンプを止める
        if self.is_jumping and new_head[1] >= self.start_y:
            new_head = [new_head[0], self.start_y]
            self.is_jumping = False
            self.jump_velocity = 0
        
        # 体を更新
        self.body.appendleft(new_head)
        self.body.pop()
        
        # 画面外に行かないようにする
        if 0 > self.body[0][0]:
            self.body[0][0] = 0
        if self.body[0][0] > WIDTH - SIZE:
            self.body[0][0] = WIDTH - SIZE
        if 0 > self.body[0][1]:
            self.body[0][1] = 0
        if self.body[0][1] > HEIGHT - SIZE:
            self.body[0][1] = HEIGHT - SIZE
        
        # 矩形の位置を更新
        self.rect.topleft = self.body[0]
        
    def draw(self, screen):
        for segment in self.body:
            screen.blit(self.body_image, segment)  # 各セグメントに画像を描画
    
    def dash(self, key_lst:list[bool], score:Score):
        """
        引数１：移動のリスト
        引数２：スコア
        青虫緊急回避プログラム
        戻り値:無し
        """ 
        sum_mv = [0, 0]
        move_keys = [k for k in __class__.delta if key_lst[k]]

        if len(move_keys) == 1:  # 1つの方向キーが押されている場合のみ移動
            k = move_keys[0]
            sum_mv[0] += __class__.delta[k][0]*4
            sum_mv[1] += __class__.delta[k][1]*4
        if self.is_jumping:
            self.jump_velocity += __class__.gravity
            sum_mv[1] += self.jump_velocity
        
        # 新しいヘッドを作成
        new_head = (self.body[0][0] + sum_mv[0], self.body[0][1] + sum_mv[1])

        score.miss -= 10
        self.body.appendleft(new_head)
        self.body.pop()

def draw_menu(screen):
    """
    特定のキーが押されると黒い画面からゲームがスタートされる
    """
    screen.fill((0, 0, 0))  # 黒で塗りつぶす
    font = pg.font.Font(None, 36)
    text_start = font.render("Press SPACE", True, (255, 255, 255))
    text_rect = text_start.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_start, text_rect)

class Die(pg.sprite.Sprite):
    """
    Dieに関するクラス
    """
    def __init__(self, obj: "Insect", life: int):
        """
        虫が死ぬエフェクトを生成する
        引数1 虫のインスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        self.imgs = [ pg.transform.rotozoom(pg.image.load(f"fig/die.PNG"), 0, 1.5)]  # 例として4フレームの爆発画像
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.rect.centery -= 10
        if self.life < 0:
            self.kill()

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    img = pg.image.load(f"fig/bg.png")
    insect = Insect()  # 虫
    timer = Timer()  # 時間 
    bird = Bird(3,(WIDTH/2,HEIGHT/2))
    score = Score(timer)
    dies = pg.sprite.Group()
    menu = True
    running = True
    pg.mixer.music.load("music/nature.mp3")
    pg.mixer.music.play(loops=5,start=0.0)
    
    while running:
        if menu:
            draw_menu(screen)
            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        menu = False

        else:
            key_lst = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB and score.value >= 10:
                        insect.dash(key_lst, score)
                elif event.type == pg.KEYUP:
                    if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                        insect.move = False  # キーが離されたら停止

            # 青虫とこうかとんの衝突判定
            for insect_b in insect.body_rects:
                # print(insect_b)
                if bird.rect.colliderect(insect_b):                
                    screen.blit(img, [0, 0])
                    bird.change_img(6,screen)               
                    fonto = pg.font.Font(None,80)
                    txt = fonto.render("EAT AOMUSHI!!",True,(255,255,0))
                    screen.blit(txt,[WIDTH/2-220,HEIGHT/2])
                    dies.add(Die(insect, 50)) 
                    dies.update()
                    dies.draw(screen)
                    pg.display.update()
                    pg.mixer.music.load("music/die_voice.mp3")
                    pg.mixer.music.play(loops=0,start=0.0)
                    time.sleep(5)
                    return
            
            screen.blit(img, [0, 0])
            bird.update(key_lst,screen)  # こうかとん
            insect.update(key_lst)  # 青虫
            insect.draw(screen)  # 青虫
            timer.update(screen)  # 時間
            score.update(timer, screen)
            pg.display.update()
            clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()