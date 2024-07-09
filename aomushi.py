import os
import sys
import pygame as pg
from collections import deque

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 500  # ゲームウィンドウの幅
HEIGHT = 500  # ゲームウィンドウの高さ
SIZE = 20

class Snake:
    """
    メインで動かす青虫の定義
    """
    def __init__(self):
        """
        特定の変数に青虫の情報を入れる
        引数なし：
        """
        self.body = deque([(WIDTH//2, HEIGHT//2), (WIDTH//2-SIZE, HEIGHT//2), (WIDTH//2-2*SIZE, HEIGHT//2)])
        self.direction = (SIZE, 0)  # 初期の移動方向は右
        self.move = False  # 蛇が動くかどうかを示すフラグ
        self.body_image = pg.image.load("fig/body_L.png")  # 蛇の体の画像を読み込む

    def update(self):
        """
        青虫の座標の更新
        引数なし：
        """
        if self.move:  # moveがTrueのときだけ更新する
            # 新しいヘッドを作成
            new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
            # 体を更新
            self.body.appendleft(new_head)
            self.body.pop()
            self.move = False  # 連打で一マスずつ動くようになります

    def change_direction(self, direction:tuple):
        """
        青虫の移動する距離の設定
        引数１：移動する距離の座標tuple型
        """
        self.direction = direction

    def draw(self, screen:pg):
        """
        描画の更新
        引数:screenディスプレイの情報
        """
        for segment in self.body:
            screen.blit(self.body_image, segment)  # 各セグメントに画像を描画

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    img = pg.image.load(f"fig/bg.png")
    snake = Snake()

    while True:
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
                    snake.move = False  # キーが離されたら停止
            if move_direction:  # breakで高速処理
                break

        if move_direction :
            snake.change_direction(move_direction)
            snake.move = True  # キーが押されている間は移動

        snake.update()
        screen.blit(img, [0, 0])
        snake.draw(screen)
        pg.display.update()
        clock.tick(10)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
