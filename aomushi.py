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

# class Bird(pg.sprite.Sprite):
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
        # super().__init__()
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
        self.speed=10
        
    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.8)
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



class Insect(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.body = deque([(WIDTH//2, HEIGHT//2), (WIDTH//2-SIZE, HEIGHT//2), (WIDTH//2-2*SIZE, HEIGHT//2)])
        # self.body = ([(WIDTH//2, HEIGHT//2), (WIDTH//2-SIZE, HEIGHT//2), (WIDTH//2-2*SIZE, HEIGHT//2)])
        self.direction = (SIZE, 0)  # 初期の移動方向は右
        self.move = False  # 蛇が動くかどうかを示すフラグ
        self.body_image = pg.image.load("fig/body_L.png")  # 蛇の体の画像を読み込む
        self.body_rects=[self.body_image.get_rect(topleft=segment)for segment in self.body]

    def update(self):
        if self.move:  # moveがTrueのときだけ更新する
            # 新しいヘッドを作成
            new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
            # 体を更新
            self.body.appendleft(new_head)
            self.body.pop()
            # 座標の更新
            self.body_rects=[self.body_image.get_rect(topleft=segment)for segment in self.body]


    def change_direction(self, direction):
        self.direction = direction

    def draw(self, screen):
        for segment in self.body:
            screen.blit(self.body_image, segment)  # 各セグメントに画像を描画

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    img = pg.image.load(f"fig/bg.png")
    insect = Insect()
    bird = Bird(3, (100,100))
    
    while True:
        # print(insect.body)
        key_lst = pg.key.get_pressed()
        move_direction = None  # キーが押されている場合の移動方向
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    move_direction = (0, -SIZE)
                elif event.key == pg.K_a:
                    move_direction = (-SIZE, 0)
                elif event.key == pg.K_s:
                    move_direction = (0, SIZE)
                elif event.key == pg.K_d:
                    move_direction = (SIZE, 0)
            elif event.type == pg.KEYUP:
                if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                    insect.move = False  # キーが離されたら停止

        if move_direction:
            insect.change_direction(move_direction)
            insect.move = True  # キーが押されている間は移動

        # 青虫とこうかとんの衝突判定
        for insect_b in insect.body_rects:
            # print(insect_b)
            if bird.rect.colliderect(insect_b):                
                screen.blit(img, [0, 0])
                bird.change_img(6,screen)               
                fonto = pg.font.Font(None,80)
                txt = fonto.render("EAT AOMUSHI!!",True,(255,255,0))
                screen.blit(txt,[WIDTH/2-220,HEIGHT/2])
                pg.display.update()
                time.sleep(5)
                return

        
        insect.update()
        screen.blit(img, [0, 0])
        bird.update(key_lst, screen)
        insect.draw(screen)
                
        pg.display.update()
        clock.tick(10)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
  