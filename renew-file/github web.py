#!/usr/bin/env python3
"""简单的作业上传服务器"""
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
HOMEWORK_FOLDERS = {
    'homework1': '项目管理',
    'homework2': 'Arduino输出',
    'homework3': 'Arduino输入',
    'homework4': '接口应用程序',
    'homework5': 'CAD',
    'homework6': '材料与工具',
    'homework7': '3D打印机',
    'homework8': '激光切割与数控',
    'homework9': '物联网与交互'
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

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path == '/delete':
            self.handle_delete()
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

        for part in parts:
            if not part.strip() or part == b'--':
                continue

            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue

            headers = part[:header_end].decode('utf-8', errors='ignore')
            body_data = part[header_end + 4:]
            if body_data.endswith(b'\r\n'):
                body_data = body_data[:-2]

            if 'Content-Disposition: form-data' in headers:
                if 'name="homework"' in headers:
                    homework_id = body_data.decode('utf-8').strip()
                elif 'name="member"' in headers:
                    member = body_data.decode('utf-8').strip()
                elif 'name="files"' in headers:
                    filename_start = headers.find('filename="') + 10
                    filename_end = headers.find('"', filename_start)
                    filename = headers[filename_start:filename_end] if filename_start > 10 else 'upload.bin'
                    files_data.append({'filename': filename, 'data': body_data})

        if not homework_id or not member:
            self.send_json_response({'success': False, 'error': 'Missing homework or member'})
            return

        homework_name = HOMEWORK_FOLDERS.get(homework_id, homework_id)
        member_folder = os.path.join(UPLOAD_DIR, homework_name)
        if not os.path.exists(member_folder):
            os.makedirs(member_folder)

        uploaded_files = []
        for file_info in files_data:
            filename = file_info['filename']
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

    def handle_delete(self):
        """删除已上传的文件"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            homework_id = data.get('homework', '')
            filename = data.get('filename', '')
            
            if not homework_id or not filename:
                self.send_json_response({'success': False, 'error': 'Missing homework or filename'})
                return
            
            # 安全检查：防止目录遍历
            if '..' in filename or '/' in filename or '\\' in filename:
                self.send_json_response({'success': False, 'error': 'Invalid filename'})
                return
            
            homework_name = HOMEWORK_FOLDERS.get(homework_id, homework_id)
            homework_dir = os.path.join(UPLOAD_DIR, homework_name)
            filepath = os.path.join(homework_dir, filename)
            
            # 确保文件在上传目录内
            if not os.path.abspath(filepath).startswith(os.path.abspath(UPLOAD_DIR)):
                self.send_json_response({'success': False, 'error': 'Invalid file path'})
                return
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f'Deleted file: {filepath}')
                self.send_json_response({'success': True, 'message': f'文件 {filename} 已删除'})
            else:
                self.send_json_response({'success': False, 'error': 'File not found'})
        except Exception as e:
            print(f'Error deleting file: {e}')
            self.send_json_response({'success': False, 'error': str(e)})

    def handle_download(self, parsed):
        from urllib.parse import unquote
        filename = unquote(parsed.path.replace('/uploads/', '', 1))
        
        # 安全检查：防止目录遍历
        if '..' in filename or '/' in filename or '\\' in filename:
            self.send_error(403)
            return

        print(f'Download request for: {filename}')

        # 在所有子文件夹中查找文件
        if os.path.exists(UPLOAD_DIR):
            for folder in os.listdir(UPLOAD_DIR):
                folder_path = os.path.join(UPLOAD_DIR, folder)
                if os.path.isdir(folder_path):
                    filepath = os.path.join(folder_path, filename)
                    if os.path.isfile(filepath):
                        print(f'Found file: {filepath}')
                        self._send_file_response(filepath)
                        return

        print(f'File not found: {filename}')
        self.send_error(404)

    def _send_file_response(self, filepath):
        """发送文件响应，确保不会重复发送响应头"""
        try:
            file_size = os.path.getsize(filepath)
        except Exception as e:
            print(f'Error getting file size: {e}')
            self.send_error(500)
            return

        # 手动构建完整的响应，避免使用 send_response 和 send_header
        # 防止任何重复的 Content-Length 头
        import mimetypes
        content_type, _ = mimetypes.guess_type(filepath)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        try:
            # 使用 send_response_only 只发送状态行，不发送 Date/Server 头
            # 然后手动发送所有需要的头
            self.send_response_only(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Content-Disposition', f'inline; filename="{os.path.basename(filepath)}"')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # 分块发送文件内容，避免一次性读取大文件
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                self.wfile.flush()
        except Exception as e:
            print(f'Error sending file: {e}')

    def send_json_response(self, data):
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
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
