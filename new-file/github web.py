#!/usr/bin/env python3
"""简单的作业上传服务器"""
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
HOMEWORK_FOLDERS = {
    'homework1': '第一次作业_基础造型练习',
    'homework2': '第二次作业_色彩构成设计',
    'homework3': '第三次作业_创意概念设计',
    'homework4': '第四次作业_数字媒体作品',
    'homework5': '第五次作业_综合材料探索',
    'homework6': '第六次作业_空间设计实践'
}

# 创建上传目录
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class HomeworkHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/list':
            self.handle_list(parsed)
        elif parsed.path.startswith('/uploads/'):
            self.handle_download(parsed)
        else:
            super().do_GET()

    def handle_upload(self):
        content_type = self.headers['Content-Type']
        if not content_type or 'multipart/form-data' not in content_type:
            self.send_json_response({'success': False, 'error': 'Invalid content type'})
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # 解析 multipart 数据
        boundary = content_type.split('boundary=')[1].encode()
        parts = body.split(b'--' + boundary)

        homework_id = None
        member = None
        files_data = []
        current_filename = None
        current_file_data = b''
        in_file = False

        for part in parts:
            if not part.strip() or part == b'--':
                continue

            # 解析头部
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue

            headers = part[:header_end].decode('utf-8', errors='ignore')
            body_data = part[header_end + 4:]
            # 移除末尾的边界
            if body_data.endswith(b'\r\n'):
                body_data = body_data[:-2]

            if 'Content-Disposition: form-data' in headers:
                if 'name="homework"' in headers:
                    homework_id = body_data.decode('utf-8').strip()
                elif 'name="member"' in headers:
                    member = body_data.decode('utf-8').strip()
                elif 'name="files"' in headers:
                    # 提取文件名
                    filename_start = headers.find('filename="') + 10
                    filename_end = headers.find('"', filename_start)
                    filename = headers[filename_start:filename_end] if filename_start > 10 else 'upload.bin'
                    files_data.append({'filename': filename, 'data': body_data})

        if not homework_id or not member:
            self.send_json_response({'success': False, 'error': 'Missing homework or member'})
            return

        # 创建作业文件夹
        homework_name = HOMEWORK_FOLDERS.get(homework_id, homework_id)
        member_folder = os.path.join(UPLOAD_DIR, homework_name)
        if not os.path.exists(member_folder):
            os.makedirs(member_folder)

        # 保存文件
        uploaded_files = []
        for file_info in files_data:
            filename = file_info['filename']
            # 确保文件名唯一
            base, ext = os.path.splitext(filename)
            counter = 1
            save_path = os.path.join(member_folder, filename)
            while os.path.exists(save_path):
                save_path = os.path.join(member_folder, f'{base}_{counter}{ext}')
                counter += 1

            with open(save_path, 'wb') as f:
                f.write(file_info['data'])
            uploaded_files.append(os.path.basename(save_path))

        self.send_json_response({'success': True, 'files': uploaded_files})

    def handle_list(self, parsed):
        params = parse_qs(parsed.query)
        homework_id = params.get('homework', [''])[0]

        if not homework_id:
            self.send_json_response({'files': []})
            return

        homework_name = HOMEWORK_FOLDERS.get(homework_id, homework_id)
        homework_dir = os.path.join(UPLOAD_DIR, homework_name)

        files = []
        if os.path.exists(homework_dir):
            for f in os.listdir(homework_dir):
                files.append(f)

        self.send_json_response({'files': sorted(files)})

    def handle_download(self, parsed):
        from urllib.parse import unquote
        filename = unquote(parsed.path.replace('/uploads/', '', 1))
        # 安全检查：防止目录遍历
        if '..' in filename or '/' in filename or '\\' in filename:
            self.send_error(403, 'Forbidden')
            return

        print(f'Download request for: {filename}')

        # 直接在所有子文件夹中查找文件
        if os.path.exists(UPLOAD_DIR):
            for folder in os.listdir(UPLOAD_DIR):
                folder_path = os.path.join(UPLOAD_DIR, folder)
                if os.path.isdir(folder_path):
                    filepath = os.path.join(folder_path, filename)
                    if os.path.exists(filepath):
                        print(f'Found file: {filepath}')
                        self.send_file(filepath)
                        return
                    # 尝试未编码的文件名
                    filepath_raw = os.path.join(folder_path, filename)
                    if os.path.exists(filepath_raw):
                        print(f'Found file (raw): {filepath_raw}')
                        self.send_file(filepath_raw)
                        return

        print(f'File not found: {filename}')
        self.send_error(404, 'File not found')

    def send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    def send_json_response(self, data):
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{self.log_date_time_string()}] {args[0]}")

def main():
    port = 8080
    server = HTTPServer(('127.0.0.1', port), HomeworkHandler)
    print(f'服务器启动成功！')
    print(f'访问地址: http://localhost:{port}/index.html')
    print(f'上传的文件将保存在: {UPLOAD_DIR}')
    print(f'按 Ctrl+C 停止服务器')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()

if __name__ == '__main__':
    main()
