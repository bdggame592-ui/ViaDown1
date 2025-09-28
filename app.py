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
            'ignoreerrors': False,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferredformat': 'mp4'
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            initial_path = ydl.prepare_filename(info)

            # Determine final downloaded path
            if initial_path.endswith(".mp4") and os.path.exists(initial_path):
                final_path = initial_path
            else:
                base_name = os.path.splitext(initial_path)[0]
                final_path = base_name + ".mp4"
                if not os.path.exists(final_path):
                    # Fallback search in DOWNLOAD_FOLDER
                    potential_files = [f for f in os.listdir(DOWNLOAD_FOLDER)
                                       if f.startswith(os.path.basename(base_name))]
                    if potential_files:
                        final_path = os.path.join(DOWNLOAD_FOLDER, potential_files[0])
                    else:
                        raise Exception("Could not locate downloaded file.")

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
