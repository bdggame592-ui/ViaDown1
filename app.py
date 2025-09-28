from flask import Flask, render_template, request, send_from_directory, jsonify
import yt_dlp
import os
import subprocess, sys

# Auto-update yt-dlp safely
try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
except Exception as e:
    print("⚠️ Warning: yt-dlp auto-update failed:", e)

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
        # Options to always get playable, merged MP4
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            # Use 'temp_path' for the template initially
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'), 
            'noplaylist': True,
            'ignoreerrors': False,
            'quiet': True,   # quiet to avoid breaking JSON
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # ensure final format is mp4
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Setting download=True to fetch and download
            info = ydl.extract_info(url, download=True) 
            
            # This is the path yt-dlp *thinks* the file is at before any final processing
            initial_path = ydl.prepare_filename(info) 

            # Determine the final path with .mp4 extension
            if initial_path.endswith(".mp4"):
                final_path = initial_path
            else:
                # Assuming yt-dlp merged the files and removed the temp extension
                base_name = os.path.splitext(initial_path)[0]
                final_path = base_name + ".mp4"
            
            # Ensure the path exists after downloading/merging (important for some platforms)
            if not os.path.exists(final_path):
                # Fallback check for common yt-dlp issue where .mp4 is added post-merge
                if os.path.exists(initial_path) and initial_path.endswith(".mp4"):
                     final_path = initial_path
                else:
                    # Final attempt to find the file if path was wrong
                    potential_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f)) and f.startswith(os.path.basename(os.path.splitext(initial_path)[0]))]
                    if potential_files:
                        final_path = os.path.join(DOWNLOAD_FOLDER, potential_files[0])
                    else:
                        raise Exception("Could not locate the downloaded file after processing.")
                        
            # Extract video title for the front-end
            video_title = info.get('title', os.path.basename(final_path))

            # Return both filename and title
            return jsonify({
                'status': 'success', 
                'filename': os.path.basename(final_path), # We only send the filename to the frontend
                'title': video_title                     # The title for display
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Download failed: {str(e)}"}), 500

@app.route('/downloads/<path:filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=False) # as_attachment=False to allow previewing in the browser

if __name__ == '__main__':
    app.run(debug=True)