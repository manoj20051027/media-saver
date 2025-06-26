
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from yt_dlp import YoutubeDL
import instaloader
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def stream_file(path):
    with open(path, "rb") as file:
        yield from file

@app.get("/download/youtube")
def download_youtube(url: str = Query(...), quality: str = Query("best")):
    ydl_opts = {
        "format": quality,
        "outtmpl": f"{DOWNLOAD_DIR}/video.%(ext)s",  # Safe static filename
        "merge_output_format": "mp4",
        "noplaylist": True,
        "external_downloader": "aria2c",
        "external_downloader_args": ["-x", "16", "-k", "1M"]
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + ".mp4"
            safe_filename = os.path.join(DOWNLOAD_DIR, "video.mp4")
            return StreamingResponse(stream_file(safe_filename), media_type="video/mp4", headers={
                "Content-Disposition": "attachment; filename=video.mp4"
            })
    except Exception as e:
        return {"error": str(e)}

@app.get("/download/instagram")
def download_instagram(url: str = Query(...)):
    try:
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_DIR)
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)
        return {"status": "Downloaded", "post": shortcode}
    except Exception as e:
        return {"error": str(e)}
