from flask import Flask, Response, request, jsonify, send_from_directory
import cv2
import threading
import os
import datetime

# --- 忽略系统代理 ---
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

app = Flask(__name__)
# 获取脚本所在的绝对目录，确保在任何地方运行都能找到文件
project_root = os.path.abspath(os.path.dirname(__file__))

camera_index = 0
lock = threading.Lock()

# --- 录制相关的全局变量 ---
is_recording = False
video_writer = None
output_filename = ""

# --- 配置摄像头 ---
# 使用try-except兼容不同操作系统
try:
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
except Exception as e:
    print(f"DSHOW backend failed, falling back to default: {e}")
    cap = cv2.VideoCapture(camera_index)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FPS = 10  # 录制帧率


def switch_camera(index):
    """切换摄像头"""
    global cap
    with lock:
        if cap.isOpened():
            cap.release()
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        except Exception:
            cap = cv2.VideoCapture(index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)


@app.route('/frame')
def get_frame():
    """获取视频帧，并在录制时写入文件"""
    with lock:
        if not cap.isOpened():
            return "Camera not available", 503

        success, frame = cap.read()
        if not success:
            return "Failed to read frame", 500

        # 如果正在录制，将当前帧写入视频文件
        if is_recording:
            if video_writer is not None:
                video_writer.write(frame)

        # 编码并返回帧给前端
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not ret:
            return "Failed to encode frame", 500
        return Response(buffer.tobytes(), mimetype='image/jpeg')


def format_size(size_bytes):
    """将字节大小格式化为可读的KB, MB, GB"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"


# --- 文件管理接口 ---

@app.route('/files')
def list_files():
    """【新】获取文件列表，包含图片和视频"""
    try:
        files_data = []
        # 遍历项目根目录下的所有文件
        for filename in os.listdir(project_root):
            if filename.lower().endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                file_path = os.path.join(project_root, filename)
                stat = os.stat(file_path)

                file_type = 'video' if filename.lower().endswith('.mp4') else 'image'

                files_data.append({
                    "name": filename,
                    "type": file_type,
                    "size": format_size(stat.st_size),
                    "created_at": datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
        # 按创建时间降序排序，最新的文件在最前面
        files_data.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify(files_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """【新】下载指定文件（作为附件）"""
    return send_from_directory(project_root, filename, as_attachment=True)


@app.route('/view/<path:filename>')
def view_file(filename):
    """【新】在线预览文件（用于Image和Video组件）"""
    return send_from_directory(project_root, filename)


@app.route('/delete/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    """【新】删除指定文件"""
    try:
        file_path = os.path.join(project_root, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted file: {filename}")
            return jsonify({"message": f"'{filename}' deleted successfully."})
        else:
            return jsonify({"error": "File not found."}), 404
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
        return jsonify({"error": str(e)}), 500


# --- 原有功能接口 ---

@app.route('/record/start', methods=['POST'])
def start_recording():
    global is_recording, video_writer, output_filename
    with lock:
        if is_recording:
            return jsonify({"message": "Already recording."}), 400

        now = datetime.datetime.now()
        output_filename = f"recording_{now.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

        # *** 核心修改点: 更换视频编码器为 'avc1' (H.264)，以获得更好的兼容性 ***
        # noinspection PyUnresolvedReferences
        fourcc = cv2.VideoWriter_fourcc(*'avc1')

        video_writer = cv2.VideoWriter(output_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
        if not video_writer.isOpened():
            print("Error: VideoWriter failed to open. Trying 'mp4v' fallback...")
            # 如果avc1失败，尝试回退到mp4v
            # noinspection PyUnresolvedReferences
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
            if not video_writer.isOpened():
                print("Error: Fallback to 'mp4v' also failed. Check installed codecs.")
                return jsonify({"error": "Failed to initialize video recorder."}), 500

        is_recording = True
        print(f"Started recording to {output_filename}")
        return jsonify({"message": "Recording started", "filename": output_filename})


@app.route('/record/stop', methods=['POST'])
def stop_recording():
    global is_recording, video_writer
    with lock:
        if not is_recording:
            return jsonify({"message": "Not currently recording."}), 400

        is_recording = False
        if video_writer is not None:
            video_writer.release()
            video_writer = None

        print(f"Stopped recording. File saved as {output_filename}")
        return jsonify({"message": "Recording stopped", "filename": output_filename})


@app.route('/snapshot')
def get_snapshot():
    with lock:
        if not cap.isOpened(): return "Camera not available", 503
        success, frame = cap.read()
        if not success: return "Camera error", 500
        # 保存为带时间戳的文件，避免覆盖
        now = datetime.datetime.now()
        snapshot_filename = f"snapshot_{now.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        cv2.imwrite(snapshot_filename, frame)
        print(f"Snapshot saved to {snapshot_filename}")
        return jsonify({"message": f"Snapshot saved as {snapshot_filename}"})


@app.route('/switch', methods=['POST'])
def switch():
    global camera_index
    new_index = int(request.json.get("index", 0))
    if new_index != camera_index:
        camera_index = new_index
        switch_camera(camera_index)
    return jsonify({"message": f"Switched to camera {camera_index}."})


if __name__ == '__main__':
    print("===================================================")
    print(f"Flask server running on http://0.0.0.0:5000")
    print(f"Serving files from directory: {project_root}")
    print("API Endpoints:")
    print("  /frame              - Get camera frame")
    print("  /snapshot           - Take a picture")
    print("  /switch             - Switch camera")
    print("  /record/start       - Start recording")
    print("  /record/stop        - Stop recording")
    print("  /files              - [NEW] List media files")
    print("  /view/<filename>    - [NEW] View a file")
    print("  /download/<filename>- [NEW] Download a file")
    print("  /delete/<filename>  - [NEW] Delete a file")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)