import os
import sys
import pygame as pg
from collections import deque

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 500  # ゲームウィンドウの幅
HEIGHT = 500  # ゲームウィンドウの高さ
SIZE = 20


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

    def update(self, key_lst: list[bool]):
        sum_mv = [0, 0]
        move_keys = [k for k in __class__.delta if key_lst[k]]

        if len(move_keys) == 1:  # 1つの方向キーが押されている場合のみ移動
            k = move_keys[0]
            sum_mv[0] += __class__.delta[k][0]
            sum_mv[1] += __class__.delta[k][1]
        
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
    ScoreとTimer連連携
    """
    def __init__(self, timer:Timer):
        self.font = pg.font.Font(None, 25)
        self.color = (0, 0, 255)
        self.value = timer.time*2
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 50, HEIGHT-25

    def update(self, timer:Timer, screen: pg.Surface):
        self.value = timer.time*2
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

    

    

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    img = pg.image.load(f"fig/bg.png")
    insect = Insect()  # 虫
    timer = Timer()  # 時間 
    score = Score(timer)

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            
        screen.blit(img, [0, 0])
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
