from flask import Flask, request, Response, render_template, send_file, abort
from argparse import ArgumentParser, ArgumentTypeError
from io import BytesIO
from pathlib import Path
import sys
import os

app = Flask(__name__)

video_info = {}

@app.route("/subtitle")
def subtitle():
    if not 'vtt_subtitles' in video_info:
        return "No subtitles were added.", 404
    
    return send_file(
        BytesIO(video_info['vtt_subtitles'].encode('utf-8')),
        mimetype="text/plain"
    )

@app.route("/video")
def video():
    return send_file(video_info['video_file'], mimetype="video/mp4")

@app.route("/")
def index():
    return render_template('index.html', **video_info)

def get_vtt_string(srt_filepath):
    vtt = ['WEBVTT\n\n']

    with open(srt_filepath, encoding='utf-8') as srt:
        is_empty = True
        for line in srt:
            stripped = line.strip()

            if stripped.isdigit() and is_empty:
                continue
 
            if '-->' in line:
                line = line.replace(',', '.')

            vtt.append(line)
            is_empty = not stripped
    return ''.join(vtt)

def main():
    def file_ext(ext):
        def file(path):
            path = Path(path)

            if not path.is_file():
                raise ArgumentTypeError(f"Invalid {ext} path.")
            
            if path.suffix != f'.{ext}':
                raise ArgumentTypeError(f"File extension is not {ext}")
            
            return path
        return file
    
    def port(number):
        number = int(number)
        if number < 0 or number > 65535:
            raise ArgumentTypeError(f"Invalid port number.")
        return number
    
    parser = ArgumentParser()
    parser.add_argument('video', help="mp4 file to play", type=file_ext('mp4'))
    parser.add_argument('-s', '--srt', help="subtitle file", type=file_ext('srt'))
    parser.add_argument('-p', '--port', help="server port", default=5000, type=port)
    args = parser.parse_args()

    video_info['video_file'] = args.video

    if args.srt:
        video_info['srt_filename'] = Path(args.srt).name
        video_info['vtt_subtitles'] = get_vtt_string(args.srt)
    
    app.run(host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()