import os
import random
import sys
import pygame as pg
import time


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), #上
    pg.K_DOWN: (0, +5), #下
    pg.K_LEFT: (-5, 0), #左
    pg.K_RIGHT: (+5, 0), #右
}


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面内か画面外かを判定する関数
    引数：こうかとんRect or 爆弾Rect
    戻り値：横方向・縦方向判定結果（True：画面内, False：画面外）
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数：screen（メイン画面のSurface）
    """
    go_img = pg.Surface((WIDTH, HEIGHT)) 
    pg.draw.rect(go_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    go_img.set_alpha(210)
    
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = (WIDTH / 2, HEIGHT / 2)
    go_img.blit(txt, txt_rct)
    
    kk_sad_img = pg.image.load("fig/8.png")
    kk_sad_rct_1 = kk_sad_img.get_rect()
    kk_sad_rct_1.center = (WIDTH / 2 - 200, HEIGHT / 2)
    kk_sad_rct_2 = kk_sad_img.get_rect()
    kk_sad_rct_2.center = (WIDTH / 2 + 200, HEIGHT / 2)
    go_img.blit(kk_sad_img, kk_sad_rct_1)
    go_img.blit(kk_sad_img, kk_sad_rct_2)
    
    screen.blit(go_img, [0, 0])
    pg.display.update()
    
    time.sleep(5)
    

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズと加速度が異なる爆弾のリストを生成する関数
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)

    bb_accs = [a for a in range(1, 11)]
    
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルに応じたこうかとん画像の辞書を返す
    """
    kk_img_l = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_img_r = pg.transform.flip(kk_img_l, True, False)

    kk_dict = {
        ( 0,  0): kk_img_l,                            
        (+5,  0): kk_img_r,                            # 右
        (+5, -5): pg.transform.rotozoom(kk_img_r, 45, 1.0),  # 右上
        ( 0, -5): pg.transform.rotozoom(kk_img_r, 90, 1.0),  # 上
        (-5, -5): pg.transform.rotozoom(kk_img_l, -45, 1.0), # 左上
        (-5,  0): kk_img_l,                            # 左
        (-5, +5): pg.transform.rotozoom(kk_img_l, 45, 1.0),  # 左下
        ( 0, +5): pg.transform.rotozoom(kk_img_r, -90, 1.0), # 下
        (+5, +5): pg.transform.rotozoom(kk_img_r, -45, 1.0), # 右下
    }
    return kk_dict


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20)) # 爆弾用の空のSurfaceを作る
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH) # 爆弾の初期座標を設定する
    bb_rct.centery = random.randint(0, HEIGHT) # 爆弾の初期座標を設定する
    vx,vy = +2,+2

    bb_imgs, bb_accs = init_bb_imgs()
    idx = 0
    bb_img = bb_imgs[idx]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        if kk_rct.colliderect(bb_rct): # 衝突判定
            gameover(screen)
            return # ゲームオーバーの意味でmain関数から出る
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True): # 画面外だったら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy) # 爆弾を移動させる
        yoko, tate = check_bound(bb_rct)
        if not yoko: # 横方向の判定
            vx *= -1
        if not tate: # 縦方向の判定
            vy *= -1
        screen.blit(bb_img, bb_rct) # 爆弾を表示

        idx = min(tmr // 500, 9)
        
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        
        if tuple(sum_mv) in kk_imgs:
            kk_img = kk_imgs[tuple(sum_mv)]

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()