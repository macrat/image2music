""" 木琴風

たのしい。


# 特徴

- RGB空間を使う
  変化が大きいのでよりたのしい。

- フェードアウトを入れて、フェードインを入れない
  木琴っぽくなる。

- 倍音を入れる
  電子音っぽさを減らすことが目的。
  基音が10/12の音量、1オクターブ上下に10/12/12の音量、2オクターブ上下に2/12/12の音量で配置している。


# やってない

- 前後の音を重ねる
  音の長さを4分から2分に変えて、半分づつ重ねるようにした。
  なんとなく微妙なのでやめた。ポテンシャルは感じる。
"""

import sys

import cv2
import numpy

import gensound


def color2sound(color: int) -> gensound.Sound:
    """ 色(というか輝度)を音に変換する

    color    -- 0から255の範囲で表わされる色。

    return -- 色から生成した音。
    """

    temperament = [
        261.626,
        293.665,
        329.628,
        349.228,
        391.995,
        440.000,
        493.883,
        523.251,
    ]

    sound = gensound.overlay(
        gensound.Sound.from_sinwave(temperament[color%8],
                                    duration=1/4,
                                    volume=10/12),
        gensound.Sound.from_sinwave(temperament[color%8]*2,
                                    duration=1/4,
                                    volume=10/12/12),
        gensound.Sound.from_sinwave(temperament[color%8]*4,
                                    duration=1/4,
                                    volume=2/12/12),
        gensound.Sound.from_sinwave(temperament[color%8]/2,
                                    duration=1/4,
                                    volume=10/12/12),
        gensound.Sound.from_sinwave(temperament[color%8]/4,
                                    duration=1/4,
                                    volume=2/12/12),
    )
    sound = gensound.LinearFadeOut().apply(sound)

    return sound


def pixel2sound(pixel: numpy.array) -> gensound.Sound:
    """ 画像のピクセルを音に変換する。

    pixel -- B, G, Rの各色が入ったnumpyの配列。

    return -- 生成した音。
    """

    return gensound.overlay(*(
        color2sound(color).volume(1/3) for color in pixel
    ))


def image2sound(image: numpy.array) -> gensound.Sound:
    """ OpenCV形式の画像を音に変換する。

    image -- OpenCVで読み込んだ画像。1チャンネルの画像は想定していないので注意。
    """

    # image[y, x, 色] だと使いづらいので、 data[index, 色] みたいにする。
    data = image.reshape(-1, 3)

    results = []
    for i, pixel in enumerate(data):
        print('\rcalc... {0}/{1}: {2:.2%}'.format(i+1,
                                          len(data),
                                          (i+1)/len(data)), end='')
        results.append(pixel2sound(pixel))

    print('\rcalc... {0}/{0}: 100.00%'.format(len(data)))

    print('concat...')
    return gensound.concat(*results)  # 結合して完成。


if __name__ == '__main__':
    input_name = sys.argv[1]
    
    sound = image2sound(cv2.imread(input_name))

    print('write...')
    sound.write(sys.argv[2])

    print('done')
