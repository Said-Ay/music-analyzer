import yt_dlp
import subprocess # 新しい道具！Pythonの中からコマンドを実行する子

# ----------------------------------------------------

# ダウンロードしたいYouTube動画のURL
youtube_url = 'https://www.youtube.com/watch?v=Fqz_s4sr-5M' # ← 好きなURLに変えてみてね

# ダウンロード設定
# ファイル名は 'audio.mp3' にしておく
output_filename = 'audio'
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': output_filename,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# --- YouTubeから音声ダウンロード ---
print(f"'{youtube_url}' から音声をダウンロード中…")
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print("ダウンロード完了！")
except Exception as e:
    print(f"ダウンロード中にエラー発生: {e}")
    exit() # エラーが起きたらここで終了

# --- ここからdemucsを使った楽器分析 ---
print("---------------------------------")
print("次に、楽器の分析（音源分離）を始めるよ…（ちょっと時間がかかるかも）")

# demucsを実行するコマンドを組み立てる
# 「demucsを起動して、『separated』フォルダに結果を出力してね。対象ファイルは『audio.mp3』だよ」
command = ["py", "-m", "demucs", "-o", "separated", "audio.mp3"]

# コマンドを実行
subprocess.run(command)

print("---------------------------------")
print("分析完了！ 左のファイル一覧に'separated'フォルダができたか確認してみて！")