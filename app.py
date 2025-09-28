from flask import Flask, render_template, request, send_from_directory, jsonify
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    platform = request.form.get('platform')

    if not url or not platform:
        return jsonify({'status': 'error', 'message': 'Missing URL or platform'}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',           # ensures merged MP4
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'            # correct spelling
            }],
        }

        # Use cookies if available for age-restricted/private videos
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            initial_path = ydl.prepare_filename(info)
            final_path = initial_path if initial_path.endswith(".mp4") else os.path.splitext(initial_path)[0] + ".mp4"

            # fallback: search in downloads folder
            if not os.path.exists(final_path):
                potential_files = [
                    f for f in os.listdir(DOWNLOAD_FOLDER)
                    if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f)) and
                       f.startswith(os.path.basename(os.path.splitext(initial_path)[0]))
                ]
                if potential_files:
                    final_path = os.path.join(DOWNLOAD_FOLDER, potential_files[0])
                else:
                    raise Exception("Could not locate the downloaded file.")

            video_title = info.get('title', os.path.basename(final_path))

            return jsonify({
                'status': 'success',
                'filename': os.path.basename(final_path),
                'title': video_title
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Download failed: {str(e)}"}), 500

@app.route('/downloads/<path:filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)
