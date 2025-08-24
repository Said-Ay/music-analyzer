# --- 必要な道具だけを、道具箱から取り出す ---
import yt_dlp
import subprocess
import os
import re # 文字をキレイにする専門家
import shutil # 新メンバー！フォルダごと削除する専門家
import librosa # 音の分析なら彼に任せろ
import numpy as np # 数学が得意な専門家
from music21 import stream, chord # music21からは、コード分析の専門家だけ呼ぶ

# ----------------------------------------------------
# ★ 機能ごとに、整理箱（関数）を用意する ★
# ----------------------------------------------------

def download_from_youtube(url, output_filename="audio.mp3"):
    """YouTubeから音声をダウンロードする専門家 (固定ファイル名)"""
    print(f"'{output_filename}' としてダウンロード中…")
    
    # --- まずは動画のタイトルだけを取得（表示用） ---
    ydl_opts_info = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'untitled')
        print(f"曲名: '{title}'")

    # --- ダウンロード処理 ---
    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.splitext(output_filename)[0], # 'audio.mp3' -> 'audio'
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        ydl.download([url])
        
    print("ダウンロード完了！")
    return output_filename

def analyze_musical_properties(audio_path):
    """曲のBPMとキーを分析する専門家"""
    print("---------------------------------")
    print(f"'{audio_path}' の音楽的な特徴を分析中…")
    try:
        # librosaで音声ファイルを読み込む
        y, sr = librosa.load(audio_path)

        # --- BPMの推定 ---
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        print(f"  - 推定BPM: {tempo:.2f}")

        # --- キーの推定 ---
        chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chromagram, axis=1)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_index = np.argmax(chroma_mean)
        estimated_key_root = notes[key_index]

        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        
        chroma_rotated = np.roll(chroma_mean, -key_index)
        
        major_similarity = np.dot(chroma_rotated, major_profile)
        minor_similarity = np.dot(chroma_rotated, minor_profile)

        if major_similarity > minor_similarity:
            estimated_key_mode = "Major"
        else:
            estimated_key_mode = "Minor"

        print(f"  - 推定キー: {estimated_key_root} {estimated_key_mode}")

    except Exception as e:
        print(f"音楽分析中にエラーが発生しました: {e}")


def separate_instruments(audio_path, stems):
    """demucsで楽器を分離する専門家 (固定フォルダ名)"""
    print("---------------------------------")
    print(f"楽器の分析（{stems}パート分離）を開始…")
    
    output_folder = "separated" # 固定のフォルダ名
    
    absolute_audio_path = os.path.abspath(audio_path)
    
    command = ["py", "-m", "demucs", "--mp3", "-o", output_folder, absolute_audio_path]
    if stems == 2:
        command.append("--two-stems=vocals")
    
    subprocess.run(command)
    print("音源分離完了！")
    
    # demucsは入力ファイル名のサブフォルダを作るので、その名前を取得
    input_filename_stem = os.path.splitext(os.path.basename(audio_path))[0]
    result_folder = os.path.join(output_folder, "htdemucs", input_filename_stem)

    if os.path.exists(result_folder):
        print(f"\n🎉🎉🎉 おめでとう！ 🎉🎉🎉")
        print(f"'{result_folder}' の中に、パート別の音楽ファイルが保存されたよ。")
    else:
        print("\nあれ？分離されたファイルが見つからないみたい…。")

# ----------------------------------------------------
# ★ メインの指揮者 ★
# ----------------------------------------------------

def main():
    """
    プログラム全体の流れを指揮する、メインの関数。
    """
    # ★★★ ここから追加 ★★★
    # 最初に、前回の結果が残っていたらお掃除する
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    if os.path.exists("separated"):
        shutil.rmtree("separated")
    # ★★★ ここまで追加 ★★★

    # 1. ユーザーに質問する
    youtube_url = input("分析したいYouTube動画URLを貼り付けてください: ")
    stems_choice = input("何パートに分離しますか？ (4 = 全パート, 2 = ボーカル/伴奏, 0 = 分離しない): ")
    
    print("---------------------------------")

    # 2. YouTubeからダウンロードする
    downloaded_file = download_from_youtube(youtube_url, "audio.mp3")

    if os.path.exists(downloaded_file):
        # 3. 曲のBPMとキーを分析する
        analyze_musical_properties(downloaded_file)
        
        # 4. 楽器を分離する（'0'が選ばれなかった場合）
        if stems_choice != '0':
            stems = 2 if stems_choice == '2' else 4
            separate_instruments(downloaded_file, stems)
        
        # 5. 自動お掃除機能 (元のmp3だけを消す)
        cleanup_choice = input("\n処理が終わったので、元のファイル ('{}') を削除しますか？ (y/n): ".format(downloaded_file))
        if cleanup_choice.lower() == 'y':
            os.remove(downloaded_file)
            print(f"'{downloaded_file}' を削除しました。")
    else:
        print(f"エラー: '{downloaded_file}' が見つかりませんでした。")

    print("---------------------------------")
    print("すべての処理が完了しました！")


# --- このプログラムが実行されたら、まずここが呼ばれる ---
if __name__ == "__main__":
    main()

