# 道具箱から、yt_dlpっていう新しい道具を取り出す
import yt_dlp

# ----------------------------------------------------

# ダウンロードしたいYouTube動画のURL
# まずは練習で、短い動画のURLをここに貼ってみよう
youtube_url = 'https://www.youtube.com/watch?v=bTtZ600zer0' # ← あとで好きなURLに変えてみてね

# ダウンロードするときの設定をいろいろ決める
# ここでは「音声だけ」「mp3形式で」「'downloaded_audio'っていう名前で」保存してね、とお願いしてる
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloaded_audio.%(ext)s', # 保存するファイル名
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3', # mp3形式に変換
        'preferredquality': '192', # 音質
    }],
}

# ----------------------------------------------------

# いよいよダウンロードを実行！
print(f"'{youtube_url}' から音声をダウンロードするよ…")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print("---------------------------------")
    print("ダウンロード完了！ フォルダの中にmp3ファイルができたか確認してみてね。")

except Exception as e:
    print("---------------------------------")
    print("ありゃ、ダウンロード中にエラーが起きちゃったみたい…。")
    print(f"エラー内容: {e}")