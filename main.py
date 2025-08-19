# まずは道具箱から、music21っていう便利な道具を取り出す
from music21 import *

# ----------------------------------------------------

# 分析したいコード進行をリストとして用意する
# ここを好きなコード進行に変えて遊んでみてね
chord_progression = ['a', 'd', 'E7', 'a']

# ----------------------------------------------------

# music21がわかるように、コードを楽譜データに変換していく
chord_stream = stream.Stream()
for c_name in chord_progression:
    # 1個ずつコードを楽譜に追加していく
    chord_stream.append(chord.Chord(c_name))

# ----------------------------------------------------

# いよいよ分析！「この楽譜のキーを教えて！」ってお願いする
key = chord_stream.analyze('key')

# ----------------------------------------------------

# 結果を表示する
print(f"分析したコード進行: {chord_progression}")
print("---------------------------------")
print(f"このコード進行、たぶん… {key.tonic.name} {key.mode} だね！")
print("---------------------------------")
print("各コードの役割（ディグリー）はこんな感じ：")

for c_name in chord_progression:
    # ★まず、ちゃんとコードの形に変換してあげる
    current_chord = chord.Chord(c_name)
    
    # ★その上で、「このコードの役割は？」って聞く
    roman_numeral = roman.romanNumeralFromChord(current_chord, key)
    
    # ちょっと見た目を整えて表示する
    print(f"  {c_name.ljust(5)} -> {roman_numeral.figure}")