'''
    mosaic_letter.py

    Created by 堀 哲也 on 2018/01/04.
    Copyright © 2018年 堀 哲也. All rights reserved.

    モザイク文字画像の情報を持つクラス

    - フィールド
        - colors 整数リスト：使用するカラーコード（背景，色1，色2）
        - gridSize  整数：モザイクのグリッドの大きさ
        - grid_parameter  np配列：背景の部分を0，色ありの部分を1で表現
        - grid_pattern   np配列：gridの各部分の色を指定
    - メソッド
        - __init__  フィールドへ代入
        - input     標準入力から色とグリッドの大きさとパターンを入力
        - mask      parameterが0でない部分は，patternの色を保持
                    parameterが0の部分は，patternに背景色を入れる
        - output    bmp形式で出力
'''

import struct
import numpy as np

class MosaicLetter:

    def __init__(self):

        self.colors = list()
        self.gridSize = None
        self.grid_parameter = list()
        self.grid_pattern = list()

        self.input() # 入力を受ける

    def input(self):
        print("First, input 3 colorcodes.")
        for i in range(3):
            self.colors.append(int(input(), base=16))

        print("Second, input size of grid.")
        self.gridSize = int(input())

        print("Third, input grid parameter.")
        for i in range(self.gridSize):
            self.grid_parameter.append([int(j) for j in input()])
        self.grid_parameter = np.array(self.grid_parameter)

        print("Finally, input grid pattern.")
        for i in range(self.gridSize):
            self.grid_pattern.append([int(j) for j in input()])
        self.grid_pattern = np.array(self.grid_pattern)

    def mask(self):
        # grid_parameterに基づいてgrid_patternを編集する
        # grid_parameter[i][j]が0ならgrid_pattern[i][j]も0
        # grid_parameter[i][j]が1ならgrid_pattern[i][j]はそのまま
        self.grid_pattern *= self.grid_parameter

    def output(self, name="output.bmp"):

        # 定数
        FILEHEADER = 14 # ファイルヘッダの大きさ
        INFOHEADER = 12 # 情報ヘッダの大きさ
        SQUARESIZE = 32 # 小さな正方形の一辺の長さ
        FRAMETHICK = 1  # 縁取りの線の厚さ
        IMAGE_LEN = SQUARESIZE * self.gridSize  # 画像の1辺の長さ

        # 書き込み
        with open(name, "wb") as f:
            # 符号なし4byte整数を書き込む関数
            writeInt = (lambda x: f.write(struct.pack("I", x)))
            writeShort = (lambda x: f.write(struct.pack("H", x)))
            writeByte = (lambda x: f.write(struct.pack("B", x)))

            # ファイルヘッダ ----------------
            f.write(struct.pack("BB", ord("B"), ord("M")))  # ファイルヘッダ
            # ファイルサイズ（4bit=1/2byteの画像であるので画素数を1/2する）
            writeInt(FILEHEADER + INFOHEADER+ 3*16 + IMAGE_LEN**2 // 2)
            writeInt(0) # 予約領域
            # 先頭から画像までのオフセット = ファイルヘッダ + 情報ヘッダ + パレットデータ
            writeInt(FILEHEADER + INFOHEADER + 3*16)

            # 情報ヘッダ ----------------
            writeInt(INFOHEADER) # 情報ヘッダの大きさ
            writeShort(IMAGE_LEN) # 縦横の長さ
            writeShort(IMAGE_LEN) # 正方形なので同じ数値を2つ
            writeShort(1) # bcプレーン数（？）は常に1
            writeShort(4) # 画像の色数（4bit）

            # パレットデータ ----------------
            # 最初の3色にcolorsのデータを入れ、残りは0に設定
            for color in self.colors:
                # リトルエンディアンで1byteずつ書き込む
                writeByte(color & 0x0000FF)
                writeByte((color & 0x00FF00) >> 8)
                writeByte((color & 0xFF0000) >> 16)

            for i in range(16 - len(self.colors)):
                for j in range(3):
                    writeByte(0)

            # 画像データ ----------------
            # 1Byteに2pixelのデータが入ることに注意
            # 画像データは左下から右上に記録される
            
            # 縁の内外を判定して書き込み -------------------------------------
            def checkAndWrite(v_i, v_j, h_i, h_j):
                if FRAMETHICK <= v_j < SQUARESIZE-FRAMETHICK \
                and FRAMETHICK <= h_j < SQUARESIZE-FRAMETHICK:
                    # 縁の内側
                    data = self.grid_pattern[self.gridSize - v_i - 1][h_i] \
                    + (self.grid_pattern[self.gridSize - v_i - 1][h_i] << 4)
                else:
                    # 縁
                    data = 0
                # 書き込み
                writeByte(data)
            # -----------------------------------------------------------

            for v_i in range(self.gridSize): # 縦のパターンの数だけループ
                for v_j in range(SQUARESIZE): # 小さい正方形の縦の長さだけループ
                    for h_i in range(self.gridSize): # 横のパターンの数だけループ
                        for h_j in range(SQUARESIZE // 2):
                            # 小さい正方形の横の長さ/2だけループ
                            # 1byteに2画素書き込むためループ数を1/2とする
                            checkAndWrite(v_i, v_j, h_i, h_j)

if __name__ == '__main__':
    ml = MosaicLetter()
    ml.mask()
    ml.output()
