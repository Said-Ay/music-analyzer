# --- 必要な道具だけを、道具箱から取り出す ---
import yt_dlp
import subprocess
import os

# ----------------------------------------------------
# ★ 機能ごとに、整理箱（関数）を用意する ★
# ----------------------------------------------------

def download_from_youtube(url, output_filename="audio.mp3"):
    """YouTubeから音声をダウンロードする専門家"""
    print(f"'{url}' から音声をダウンロード中…")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.splitext(output_filename)[0], # 'audio.mp3' -> 'audio'
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'noplaylist': True # プレイリストの場合は最初の1曲だけにする
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("ダウンロード完了！")
    return output_filename

def separate_instruments(audio_path):
    """demucsで楽器を分離する専門家"""
    print("---------------------------------")
    print("楽器の分析（音源分離）を開始…（曲の長さによっては、結構時間がかかるよ）")
    output_folder = "separated"
    absolute_audio_path = os.path.abspath(audio_path)
    
    command = ["py", "-m", "demucs", "--mp3", "-o", output_folder, absolute_audio_path]
    subprocess.run(command)
    print("音源分離完了！")
    
    # 分離されたファイルが入っているフォルダのパスを確認
    input_filename_stem = os.path.splitext(os.path.basename(audio_path))[0]
    result_folder = os.path.join(output_folder, "htdemucs", input_filename_stem)
    
    if os.path.exists(result_folder):
        print(f"\n🎉🎉🎉 おめでとう！ 🎉🎉🎉")
        print(f"'{result_folder}' の中に、パート別の音楽ファイルが保存されたよ。")
    else:
        print("\nあれ？分離されたファイルが見つからないみたい…。")
        print("demucsのバージョンによっては、出力フォルダの構造が違うことがあるかも。")

# ----------------------------------------------------
# ★ メインの指揮者 ★
# ----------------------------------------------------

def main():
    """
    プログラム全体の流れを指揮する、メインの関数。
    """
    # 1. ユーザーに質問する
    youtube_url = input("楽器を分離したいYouTube動画URLを貼り付けてください: ")
    print("---------------------------------")

    # 2. YouTubeからダウンロードする
    downloaded_file = download_from_youtube(youtube_url)

    # 3. 楽器を分離する
    separate_instruments(downloaded_file)

    print("---------------------------------")
    print("すべての処理が完了しました！")


# --- このプログラムが実行されたら、まずここが呼ばれる ---
if __name__ == "__main__":
    main()

