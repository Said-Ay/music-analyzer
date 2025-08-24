# --- 必要な道具を全部、道具箱から取り出す ---
import yt_dlp
import subprocess
import os
import re # 文字をキレイにする専門家
import shutil # フォルダごと削除する専門家
import librosa # 音の分析なら彼に任せろ
import librosa.display
import numpy as np # 数学が得意な専門家
from scipy.ndimage import median_filter # グラフを滑らかにする専門家
from scipy.signal import find_peaks # グラフの山を見つける専門家
from music21 import stream, chord # music21からは、コード分析の専門家だけ呼ぶ
import matplotlib.pyplot as plt # グラフを描く専門家

# ----------------------------------------------------
# ★ 機能ごとに、整理箱（関数）を用意する ★
# ----------------------------------------------------

def download_from_youtube(url, output_filename="audio.mp3"):
    """YouTubeから音声をダウンロードする専門家 (固定ファイル名)"""
    print(f"'{output_filename}' としてダウンロード中…")
    
    ydl_opts_info = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'untitled')
        print(f"曲名: '{title}'")

    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.splitext(output_filename)[0],
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        ydl.download([url])
        
    print("ダウンロード完了！")
    return output_filename

def analyze_music_karute(audio_path, drum_path=None):
    """曲のBPM、キー、構造を分析して「カルテ」を作成する専門家"""
    try:
        print("\n---------------------------------")
        print(f"音楽博士が'{audio_path}'を分析中…")
        
        y, sr = librosa.load(audio_path)

        print("\n📋========= 音楽カルテ =========📋")

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        print(f" BPM (テンポ): {np.mean(tempo):.2f}")

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
        estimated_key_mode = "Major" if major_similarity > minor_similarity else "Minor"
        print(f" キー (調) 　: {estimated_key_root} {estimated_key_mode}")

        # --- ここから構造分析 ---
        print("\n 曲の構造 (セクションごとの開始時間):")
        
        segment_times = []
        # ★★★ ここが新しい機能！ ★★★
        # もしドラムの音源があるなら、それを使って高精度分析する
        if drum_path and os.path.exists(drum_path):
            print("  - ドラムのビートと全体のハーモニーを元に、高精度で分析中…")
            y_drums, sr_drums = librosa.load(drum_path)
            # ドラムから正確なビート位置を検出
            _, beats = librosa.beat.beat_track(y=y_drums, sr=sr_drums)
            beat_times = librosa.frames_to_time(beats, sr=sr_drums)
            
            # 元の曲全体のハーモニー情報（クロマグラム）を、ドラムのビートに同期させる
            beat_chroma = librosa.util.sync(chromagram, beats, aggregate=np.median)

            # 類似度行列（設計図）を作成
            R = librosa.segment.recurrence_matrix(beat_chroma, metric='cosine', sparse=False)
            # 設計図を滑らかにして、大きな構造を見つけやすくする
            R_smooth = median_filter(R, size=(1, 9))
            # 場面転換の度合いをグラフにする（ノベルティカーブ）
            novelty_curve = np.sum(np.diff(R_smooth, axis=1)**2, axis=0)
            novelty_curve = np.pad(novelty_curve, (1, 0), 'constant')
            # グラフの山（＝場面転換の瞬間）を見つける
            peaks, _ = find_peaks(novelty_curve, prominence=np.median(novelty_curve) * 1.5)
            
            # 見つけた山の位置（ビート番号）を、実際の時間（秒）に変換
            segment_times = beat_times[peaks]
            # 曲の開始点(0秒)を必ず含める
            segment_times = np.concatenate(([0], segment_times))

        # ドラム音源がない場合は、今まで通りのシンプルな方法で分析
        else:
            print("  - 音量の変化を元に、シンプルに分析中…")
            segment_boundaries_samples = librosa.effects.split(y, top_db=25)
            segment_times = librosa.samples_to_time([boundary[0] for boundary in segment_boundaries_samples], sr=sr)
        
        segment_labels = ['イントロ', 'Aメロ', 'Bメロ', 'サビ', 'Cメロ', '間奏', 'アウトロ']
        for i, t in enumerate(segment_times):
            label = segment_labels[i] if i < len(segment_labels) else f"セクション{i+1}"
            print(f"  - {label}: {t:.2f}秒 から")

        print("📋==============================📋\n")

        # --- 構造を可視化して画像ファイルとして保存 ---
        fig, ax = plt.subplots(figsize=(12, 4))
        librosa.display.waveshow(y, sr=sr, ax=ax, alpha=0.5)
        ax.vlines(segment_times, -1, 1, color='r', linestyle='--', label='セクション区切り')
        ax.set_title('Song Waveform and Structure')
        ax.legend()
        plt.tight_layout()
        
        base_filename = os.path.splitext(audio_path)[0]
        plot_filename = f"{base_filename}_structure.png"
        plt.savefig(plot_filename)
        plt.close(fig) # メモリを解放
        print(f"'{plot_filename}' に構造のグラフを保存しました。")


    except Exception as e:
        print(f"音楽分析中にエラーが発生しました: {e}")


def separate_instruments(audio_path, stems=4):
    """demucsで楽器を分離する専門家 (固定フォルダ名)"""
    print("---------------------------------")
    print(f"楽器の分析（{stems}パート分離）を開始…")
    
    output_folder = "separated"
    
    absolute_audio_path = os.path.abspath(audio_path)
    
    command = ["py", "-m", "demucs", "--mp3", "-o", output_folder, absolute_audio_path]
    if stems == 2:
        command.append("--two-stems=vocals")
    
    subprocess.run(command)
    print("音源分離完了！")
    
    input_filename_stem = os.path.splitext(os.path.basename(audio_path))[0]
    result_folder = os.path.join(output_folder, "htdemucs", input_filename_stem)

    if os.path.exists(result_folder):
        print(f"\n🎉🎉🎉 おめでとう！ 🎉🎉🎉")
        print(f"'{result_folder}' の中に、パート別の音楽ファイルが保存されたよ。")
        # ドラムファイルのパスを返す
        drum_path = os.path.join(result_folder, "drums.mp3")
        return drum_path if os.path.exists(drum_path) else None
    else:
        print("\nあれ？分離されたファイルが見つからないみたい…。")
        return None

# ----------------------------------------------------
# ★ メインの指揮者 ★
# ----------------------------------------------------

def main():
    """
    プログラム全体の流れを指揮する、メインの関数。
    """
    # 最初に、前回の結果が残っていたらお掃除する
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    if os.path.exists("separated"):
        shutil.rmtree("separated")
    for item in os.listdir('.'):
        if item.endswith("_structure.png"):
            os.remove(item)


    # 1. ユーザーに質問する
    youtube_url = input("分析したいYouTube動画URLを貼り付けてください: ")
    structure_mode = input("曲の構造を、ドラムパターンから高精度で分析しますか？ (y/n): ")
    
    print("---------------------------------")

    # 2. YouTubeからダウンロードする
    downloaded_file = download_from_youtube(youtube_url, "audio.mp3")

    if os.path.exists(downloaded_file):
        drum_path = None
        # 高精度モードが選ばれたら、まず楽器分離を行う
        if structure_mode.lower() == 'y':
            # ドラム分離には4パート分離が必要
            drum_path = separate_instruments(downloaded_file, 4)
        
        # 3. 曲のBPMとキーと構造を分析する
        analyze_music_karute(downloaded_file, drum_path)
        
        # 4. 自動お掃除機能
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
