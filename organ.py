""" オルガン風

かなり曲っぽくなれそうなポテンシャルを感じる。


# 特徴

- HSV空間を使う
  人間の感覚に近い色になることを期待している。効果はあんまり無さそう。
  寒色か暖色かで音程や音色を変えると良いかもしれない？

- 同じトラック(チャンネル)で同じ音程を続けて出すときは繋げる
  1/4拍を基準として、同じ色が続いた場合は最大で1拍になるまで音を繋げる。
  ただし、1拍の長さを跨いで音を鳴らさない。
  かなり演奏してるっぽくなる。

- フェードイン・フェードアウトを入れる
  電子音っぽさを減らすことと、前後の音を明確に分離することが目的。

- 倍音を入れる
  電子音っぽさを減らすことが目的。ついでになんとなくベースとメロディが分かれた気がする。
  基音が1/2、1オクターブ上下に1/4の音量の倍音を配置している。
"""

import sys

import cv2
import numpy

import gensound


def pixel2notes(pixel: numpy.array) -> numpy.array:
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

    return numpy.array([temperament[x] for x in pixel%8])


def image2notes(image: numpy.array) -> numpy.array:
    data = image.reshape(-1, 3)

    result = []
    for i, pixel in enumerate(data):
        print('\rscan... {0}/{1}: {2:.2%}'.format(i+1, len(data), (i+1)/len(data)), end='')
        result.append(pixel2notes(pixel))

    print('\rscan... {0}/{0}: 100.00%'.format(len(data)))

    return numpy.array(result).T


def notes2sound(notes: numpy.array) -> gensound.Sound:
    tracks = [[], [], []]

    for i, (ns, track) in enumerate(zip(notes, tracks)):
        for j, n in enumerate(ns):
            print('\rjoin notes {0}/3... {1}/{2}: {3:.2%}'.format(i+1, j+1, len(ns), (j+1)/len(ns)), end='')

            if len(track) > 0 and track[-1]['freq'] == n and j%4 != 0:
                track[-1]['duration'] += 1/4
            else:
                track.append({'freq': n, 'duration': 1/4})

        print('\rjoin notes {0}/3... {1}/{1}: 100.00%'.format(i+1, len(ns), end=''))

    sound_tracks = [[], [], []]
    for i, (in_, out) in enumerate(zip(tracks, sound_tracks)):
        for j, note in enumerate(in_):
            print('\rmake sounds {0}/3... {1}/{2}: {3:.2%}'.format(i+1, j+1, len(in_), (j+1)/len(in_)), end='')

            sound = gensound.overlay(
                gensound.Sound.from_sinwave(note['freq'],
                                            duration=note['duration'],
                                            volume=2/4/3),
                gensound.Sound.from_sinwave(note['freq']/2,
                                            duration=note['duration'],
                                            volume=1/4/3),
                gensound.Sound.from_sinwave(note['freq']*2,
                                            duration=note['duration'],
                                            volume=1/4/3),
            )
            sound = gensound.LinearFadeIn(duration=1/16).apply(sound)
            sound = gensound.LinearFadeOut(duration=min(3/4, note['duration'])).apply(sound)
            out.append(sound)

        print('\rmake sounds {0}/3... {1}/{1}: 100.00%'.format(i+1, len(in_), end=''))

    print('concatenate sounds...')
    return gensound.overlay(*(gensound.concat(*track) for track in sound_tracks))


if __name__ == '__main__':
    input_name = sys.argv[1]

    notes = image2notes(cv2.cvtColor(cv2.imread(input_name), cv2.COLOR_BGR2HSV))

    sound = notes2sound(notes)

    print('write...')
    sound.write(sys.argv[2])

    print('done')
