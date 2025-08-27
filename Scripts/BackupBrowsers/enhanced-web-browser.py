#!/usr/bin/env python3
"""
Enhanced web-based file browser with preview and temp copy features
"""

import os
import sys
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import json
from pathlib import Path
import mimetypes
import webbrowser
import threading
import time

class EnhancedBackupBrowserHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, backup_path=None, recovery_path=None, temp_path=None, **kwargs):
        self.backup_path = backup_path
        self.recovery_path = recovery_path
        self.temp_path = temp_path
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path.startswith('/browse'):
            self.serve_directory_listing()
        elif self.path.startswith('/copy'):
            self.copy_file()
        elif self.path.startswith('/temp'):
            self.copy_to_temp()
        elif self.path.startswith('/preview'):
            self.preview_file()
        elif self.path.startswith('/download'):
            self.download_file()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pika Backup Browser</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #2196F3; color: white; padding: 15px; border-radius: 5px; }
                .directory { background: #f5f5f5; margin: 10px 0; padding: 10px; border-radius: 5px; }
                .file-list { margin: 10px 0; }
                .file-item { padding: 5px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
                .file-item:hover { background: #f0f0f0; }
                .directory-item { color: #2196F3; font-weight: bold; }
                .file-size { color: #666; font-size: 0.9em; }
                .copy-btn { background: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin: 2px; }
                .temp-btn { background: #FF9800; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin: 2px; }
                .preview-btn { background: #9C27B0; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin: 2px; }
                .copy-btn:hover { background: #45a049; }
                .temp-btn:hover { background: #e68900; }
                .preview-btn:hover { background: #7B1FA2; }
                .breadcrumb { margin: 10px 0; }
                .breadcrumb a { color: #2196F3; text-decoration: none; margin-right: 5px; }
                #status { margin: 10px 0; padding: 10px; background: #dff0d8; border-radius: 5px; display: none; }
                #preview { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; display: none; max-height: 400px; overflow: auto; }
                .button-group { display: flex; gap: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🐭 Pika Backup File Browser (Enhanced)</h1>
                <p>Navigate, preview, and selectively copy your backup files</p>
            </div>
            
            <div id="status"></div>
            <div id="preview"></div>
            
            <div class="directory">
                <h3>Quick Access:</h3>
                <a href="/browse?path=Desktop">📁 Desktop</a> | 
                <a href="/browse?path=Documents">📁 Documents</a> | 
                <a href="/browse?path=Projects">📁 Projects</a> | 
                <a href="/browse?path=Pictures">📁 Pictures</a> | 
                <a href="/browse?path=Downloads">📁 Downloads</a> | 
                <a href="/browse?path=Scripts">📁 Scripts</a> | 
                <a href="/browse?path=">📁 Home Directory</a>
            </div>
            
            <div id="content">
                <p>Select a folder above to start browsing your backup files.</p>
                <p><strong>New Features:</strong></p>
                <ul>
                    <li><strong>Preview:</strong> View file contents without copying</li>
                    <li><strong>Temp Copy:</strong> Copy to ~/Desktop/TempPreview for quick access</li>
                    <li><strong>Permanent Copy:</strong> Copy to ~/Desktop/RecoveredFiles</li>
                </ul>
            </div>
            
            <script>
                function copyFile(filePath, fileName) {
                    fetch('/copy?file=' + encodeURIComponent(filePath))
                    .then(response => response.text())
                    .then(data => showStatus('Permanently copied: ' + fileName + ' to RecoveredFiles/'));
                }
                
                function tempCopy(filePath, fileName) {
                    fetch('/temp?file=' + encodeURIComponent(filePath))
                    .then(response => response.text())
                    .then(data => showStatus('Temp copied: ' + fileName + ' to TempPreview/'));
                }
                
                function previewFile(filePath, fileName) {
                    fetch('/preview?file=' + encodeURIComponent(filePath))
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('preview').style.display = 'block';
                        document.getElementById('preview').innerHTML = '<h3>Preview: ' + fileName + '</h3><pre>' + data + '</pre>';
                    });
                }
                
                function showStatus(message) {
                    document.getElementById('status').style.display = 'block';
                    document.getElementById('status').innerHTML = message;
                    setTimeout(() => {
                        document.getElementById('status').style.display = 'none';
                    }, 3000);
                }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_directory_listing(self):
        # Parse the path parameter
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        rel_path = params.get('path', [''])[0]
        
        full_path = os.path.join(self.backup_path, rel_path)
        
        if not os.path.exists(full_path):
            self.send_error(404, "Path not found")
            return
        
        try:
            items = []
            
            # Add parent directory link if not at root
            if rel_path:
                parent_path = '/'.join(rel_path.split('/')[:-1])
                items.append({
                    'name': '..',
                    'is_dir': True,
                    'path': parent_path,
                    'size': ''
                })
            
            # List directory contents
            for item in sorted(os.listdir(full_path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(full_path, item)
                rel_item_path = os.path.join(rel_path, item) if rel_path else item
                
                is_dir = os.path.isdir(item_path)
                size = ''
                
                if not is_dir:
                    try:
                        size_bytes = os.path.getsize(item_path)
                        if size_bytes < 1024:
                            size = f"{size_bytes} B"
                        elif size_bytes < 1024*1024:
                            size = f"{size_bytes/1024:.1f} KB"
                        elif size_bytes < 1024*1024*1024:
                            size = f"{size_bytes/(1024*1024):.1f} MB"
                        else:
                            size = f"{size_bytes/(1024*1024*1024):.1f} GB"
                    except:
                        size = "Unknown"
                
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'path': rel_item_path,
                    'full_path': item_path,
                    'size': size
                })
            
            # Generate HTML
            breadcrumb = self.generate_breadcrumb(rel_path)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pika Backup Browser - {rel_path or 'Home'}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; }}
                    .breadcrumb {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
                    .breadcrumb a {{ color: #2196F3; text-decoration: none; margin-right: 5px; }}
                    .file-list {{ margin: 10px 0; }}
                    .file-item {{ padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
                    .file-item:hover {{ background: #f0f0f0; }}
                    .directory-item {{ color: #2196F3; font-weight: bold; }}
                    .file-info {{ display: flex; align-items: center; }}
                    .file-name {{ margin-right: 10px; }}
                    .file-size {{ color: #666; font-size: 0.9em; margin-right: 20px; }}
                    .copy-btn {{ background: #4CAF50; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; margin: 2px; font-size: 0.9em; }}
                    .temp-btn {{ background: #FF9800; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; margin: 2px; font-size: 0.9em; }}
                    .preview-btn {{ background: #9C27B0; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; margin: 2px; font-size: 0.9em; }}
                    .copy-btn:hover {{ background: #45a049; }}
                    .temp-btn:hover {{ background: #e68900; }}
                    .preview-btn:hover {{ background: #7B1FA2; }}
                    .button-group {{ display: flex; gap: 2px; }}
                    #status {{ margin: 10px 0; padding: 10px; background: #dff0d8; border-radius: 5px; display: none; }}
                    #preview {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; display: none; max-height: 400px; overflow: auto; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🐭 Pika Backup File Browser</h1>
                    <p>Current location: /{rel_path}</p>
                </div>
                
                <div id="status"></div>
                <div id="preview"></div>
                
                <div class="breadcrumb">
                    {breadcrumb} | <a href="/">🏠 Home</a>
                </div>
                
                <div class="file-list">
            """
            
            for item in items:
                if item['is_dir']:
                    html += f"""
                    <div class="file-item">
                        <div class="file-info">
                            <a href="/browse?path={item['path']}" class="directory-item">📁 {item['name']}</a>
                        </div>
                    </div>
                    """
                else:
                    # Determine if file can be previewed
                    can_preview = self.can_preview_file(item['name'])
                    preview_button = f'<button class="preview-btn" onclick="previewFile(\'{item["full_path"]}\', \'{item["name"]}\')">Preview</button>' if can_preview else ''
                    
                    html += f"""
                    <div class="file-item">
                        <div class="file-info">
                            <span class="file-name">📄 {item['name']}</span>
                            <span class="file-size">{item['size']}</span>
                        </div>
                        <div class="button-group">
                            {preview_button}
                            <button class="temp-btn" onclick="tempCopy('{item['full_path']}', '{item['name']}')">Temp</button>
                            <button class="copy-btn" onclick="copyFile('{item['full_path']}', '{item['name']}')">Copy</button>
                        </div>
                    </div>
                    """
            
            html += """
                </div>
                
                <script>
                    function copyFile(filePath, fileName) {
                        fetch('/copy?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => showStatus('Permanently copied: ' + fileName + ' to RecoveredFiles/'));
                    }
                    
                    function tempCopy(filePath, fileName) {
                        fetch('/temp?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => showStatus('Temp copied: ' + fileName + ' to TempPreview/ (auto-deleted on restart)'));
                    }
                    
                    function previewFile(filePath, fileName) {
                        fetch('/preview?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => {
                            document.getElementById('preview').style.display = 'block';
                            document.getElementById('preview').innerHTML = '<h3>Preview: ' + fileName + '</h3><pre style="white-space: pre-wrap; word-wrap: break-word;">' + data + '</pre>';
                            document.getElementById('preview').scrollIntoView();
                        })
                        .catch(error => {
                            showStatus('Error previewing file: ' + fileName);
                        });
                    }
                    
                    function showStatus(message) {
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').innerHTML = message;
                        setTimeout(() => {
                            document.getElementById('status').style.display = 'none';
                        }, 4000);
                    }
                </script>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def can_preview_file(self, filename):
        """Check if file can be previewed (text files, code, etc.)"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
                          '.sh', '.bat', '.ps1', '.ini', '.cfg', '.conf', '.log', '.sql', '.csv'}
        _, ext = os.path.splitext(filename.lower())
        return ext in text_extensions or filename.lower() in {'readme', 'license', 'changelog'}
    
    def generate_breadcrumb(self, path):
        if not path:
            return '<a href="/">🏠 Home</a>'
        
        parts = path.split('/')
        breadcrumb = '<a href="/">🏠 Home</a> > '
        
        for i, part in enumerate(parts):
            if part:
                partial_path = '/'.join(parts[:i+1])
                if i == len(parts) - 1:
                    breadcrumb += f'<strong>{part}</strong>'
                else:
                    breadcrumb += f'<a href="/browse?path={partial_path}">{part}</a> > '
        
        return breadcrumb
    
    def copy_file(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        if not file_path or not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
        
        try:
            os.makedirs(self.recovery_path, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.recovery_path, filename)
            shutil.copy2(file_path, dest_path)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Copied {filename} to {dest_path}".encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def copy_to_temp(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        if not file_path or not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
        
        try:
            os.makedirs(self.temp_path, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.temp_path, filename)
            shutil.copy2(file_path, dest_path)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Temp copied {filename} to {dest_path}".encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def preview_file(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        if not file_path or not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
        
        try:
            # Check file size (limit preview to reasonable size)
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB limit
                content = f"File too large to preview ({file_size/1024/1024:.1f} MB). Use Temp or Copy instead."
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)  # First 10k characters
                    if len(content) == 10000:
                        content += "\n\n... (truncated - showing first 10,000 characters)"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8', errors='replace'))
            
        except Exception as e:
            self.send_error(500, str(e))

def create_handler(backup_path, recovery_path, temp_path):
    def handler(*args, **kwargs):
        return EnhancedBackupBrowserHandler(*args, backup_path=backup_path, recovery_path=recovery_path, temp_path=temp_path, **kwargs)
    return handler

def main():
    backup_path = "/home/herb/pika-browse/home/herb"
    recovery_path = "/home/herb/Desktop/RecoveredFiles"
    temp_path = "/home/herb/Desktop/TempPreview"
    
    if not os.path.exists(backup_path):
        print(f"Backup path not found: {backup_path}")
        sys.exit(1)
    
    # Create directories
    os.makedirs(recovery_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    
    port = 8081
    handler = create_handler(backup_path, recovery_path, temp_path)
    
    try:
        server = HTTPServer(('localhost', port), handler)
        print(f"🌐 Enhanced Web File Browser started!")
        print(f"📂 Backup path: {backup_path}")
        print(f"💾 Recovery path: {recovery_path}")
        print(f"🗂️  Temp path: {temp_path}")
        print(f"🔗 Open in browser: http://localhost:{port}")
        
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()