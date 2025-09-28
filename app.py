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
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

        # Only use cookies if file exists
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = "cookies.txt"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            initial_path = ydl.prepare_filename(info)
            final_path = os.path.splitext(initial_path)[0] + ".mp4"

            # Fallback check
            if not os.path.exists(final_path):
                potential_files = [
                    f for f in os.listdir(DOWNLOAD_FOLDER)
                    if f.startswith(os.path.basename(os.path.splitext(initial_path)[0]))
                ]
                if potential_files:
                    final_path = os.path.join(DOWNLOAD_FOLDER, potential_files[0])
                else:
                    raise Exception("Downloaded file not found. Possibly login required or video restricted.")

            return jsonify({
                'status': 'success',
                'filename': os.path.basename(final_path),
                'title': info.get('title', os.path.basename(final_path))
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Download failed: {str(e)}"}), 500

@app.route('/downloads/<path:filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)
