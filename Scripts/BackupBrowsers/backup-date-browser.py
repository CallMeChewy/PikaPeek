#!/usr/bin/env python3
"""
Backup Date Browser - Select backup archive and view files with original dates
"""

import os
import sys
import shutil
import subprocess
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
from pathlib import Path
import mimetypes
import webbrowser
import threading
import time
from datetime import datetime

class BackupDateBrowserHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, repo_path=None, recovery_path=None, temp_path=None, **kwargs):
        self.repo_path = repo_path
        self.recovery_path = recovery_path
        self.temp_path = temp_path
        self.current_mount = None
        self.mount_point = "/home/herb/backup-browser-mount"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_archive_selector()
        elif self.path.startswith('/mount'):
            self.mount_archive()
        elif self.path.startswith('/browse'):
            self.serve_directory_listing()
        elif self.path.startswith('/copy'):
            self.copy_file()
        elif self.path.startswith('/temp'):
            self.copy_to_temp()
        elif self.path.startswith('/preview'):
            self.preview_file()
        elif self.path.startswith('/unmount'):
            self.unmount_current()
        else:
            self.send_error(404)
    
    def get_archive_list(self):
        """Get list of all backup archives with dates"""
        try:
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg list "{self.repo_path}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                return []
            
            archives = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        archive_name = parts[0]
                        # Parse date and time
                        date_str = parts[2] + " " + parts[3]
                        try:
                            # Convert to readable format
                            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                            readable_date = dt.strftime("%B %d, %Y at %I:%M %p")
                        except:
                            readable_date = date_str
                        
                        archives.append({
                            'name': archive_name,
                            'date': readable_date,
                            'raw_date': date_str
                        })
            
            return list(reversed(archives))  # Most recent first
            
        except Exception as e:
            print(f"Error getting archive list: {e}")
            return []
    
    def serve_archive_selector(self):
        archives = self.get_archive_list()
        
        archive_options = ""
        for i, archive in enumerate(archives):
            archive_options += f"""
            <div class="archive-item">
                <div class="archive-info">
                    <strong>{archive['date']}</strong><br>
                    <small>Archive: {archive['name']}</small>
                </div>
                <button class="mount-btn" onclick="mountArchive('{archive['name']}', '{archive['date']}')">
                    Browse This Backup
                </button>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pika Backup Date Selector</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .archive-list {{ margin: 20px 0; }}
                .archive-item {{ 
                    background: white; 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 8px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .archive-item:hover {{ box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
                .archive-info {{ flex-grow: 1; }}
                .mount-btn {{ 
                    background: #4CAF50; 
                    color: white; 
                    border: none; 
                    padding: 12px 20px; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-size: 14px;
                }}
                .mount-btn:hover {{ background: #45a049; }}
                #status {{ 
                    margin: 20px 0; 
                    padding: 15px; 
                    background: #dff0d8; 
                    border-radius: 5px; 
                    display: none; 
                }}
                .info-box {{ 
                    background: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 20px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .current-mount {{ 
                    background: #e3f2fd; 
                    border-left: 4px solid #2196F3; 
                    padding: 15px; 
                    margin: 20px 0; 
                    border-radius: 0 8px 8px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐭 Pika Backup Date Selector</h1>
                    <p>Choose which backup date to explore</p>
                </div>
                
                <div id="status"></div>
                
                <div class="info-box">
                    <h3>📊 Available Backups: {len(archives)}</h3>
                    <p>Select a backup date below to browse files with their original timestamps.</p>
                    <p><strong>Repository:</strong> {self.repo_path}</p>
                </div>
                
                <div class="archive-list">
                    {archive_options}
                </div>
                
                <div class="info-box">
                    <h3>💡 How to Use:</h3>
                    <ul>
                        <li>Click "Browse This Backup" for any date</li>
                        <li>Files will show their original creation/modification dates</li>
                        <li>Use Preview, Temp Copy, or Permanent Copy for each file</li>
                        <li>Temp copies go to ~/Desktop/TempPreview/</li>
                        <li>Permanent copies go to ~/Desktop/RecoveredFiles/</li>
                    </ul>
                </div>
            </div>
            
            <script>
                function mountArchive(archiveName, archiveDate) {{
                    showStatus('Mounting backup from ' + archiveDate + '...');
                    
                    fetch('/mount?archive=' + encodeURIComponent(archiveName) + '&date=' + encodeURIComponent(archiveDate))
                    .then(response => response.text())
                    .then(data => {{
                        if (data.includes('success')) {{
                            window.location.href = '/browse?path=&date=' + encodeURIComponent(archiveDate);
                        }} else {{
                            showStatus('Error mounting backup: ' + data);
                        }}
                    }})
                    .catch(error => {{
                        showStatus('Error: ' + error);
                    }});
                }}
                
                function showStatus(message) {{
                    document.getElementById('status').style.display = 'block';
                    document.getElementById('status').innerHTML = message;
                }}
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def mount_archive(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        archive_name = params.get('archive', [''])[0]
        archive_date = params.get('date', [''])[0]
        
        if not archive_name:
            self.send_error(400, "Archive name required")
            return
        
        try:
            # Unmount any existing archive
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], 
                             capture_output=True, check=False)
            
            # Create mount point
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount the archive
            full_archive_path = f"{self.repo_path}::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive_path}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode == 0:
                self.current_mount = {'archive': archive_name, 'date': archive_date}
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"success: Mounted {archive_name}".encode())
            else:
                self.send_error(500, f"Failed to mount: {result.stderr}")
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_directory_listing(self):
        if not self.current_mount:
            self.send_error(400, "No archive mounted")
            return
        
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        rel_path = params.get('path', [''])[0]
        archive_date = params.get('date', ['Current Archive'])[0]
        
        full_path = os.path.join(self.mount_point, "home/herb", rel_path)
        
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
                    'size': '',
                    'date': ''
                })
            
            # List directory contents with original dates
            for item in sorted(os.listdir(full_path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(full_path, item)
                rel_item_path = os.path.join(rel_path, item) if rel_path else item
                
                is_dir = os.path.isdir(item_path)
                size = ''
                mod_date = ''
                
                try:
                    stat = os.stat(item_path)
                    # Get modification time from backup
                    mod_timestamp = stat.st_mtime
                    mod_date = datetime.fromtimestamp(mod_timestamp).strftime("%Y-%m-%d %H:%M")
                    
                    if not is_dir:
                        size_bytes = stat.st_size
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
                    mod_date = "Unknown"
                
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'path': rel_item_path,
                    'full_path': item_path,
                    'size': size,
                    'date': mod_date
                })
            
            # Generate HTML
            breadcrumb = self.generate_breadcrumb(rel_path, archive_date)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Backup Browser - {archive_date}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; }}
                    .archive-info {{ background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                    .breadcrumb {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
                    .breadcrumb a {{ color: #2196F3; text-decoration: none; margin-right: 5px; }}
                    .file-list {{ margin: 10px 0; }}
                    .file-item {{ 
                        padding: 8px; 
                        border-bottom: 1px solid #eee; 
                        display: grid; 
                        grid-template-columns: 2fr 1fr 1fr 1fr; 
                        gap: 10px;
                        align-items: center; 
                    }}
                    .file-item:hover {{ background: #f0f0f0; }}
                    .directory-item {{ color: #2196F3; font-weight: bold; }}
                    .file-date {{ color: #666; font-size: 0.9em; }}
                    .file-size {{ color: #666; font-size: 0.9em; }}
                    .button-group {{ display: flex; gap: 2px; }}
                    .copy-btn {{ background: #4CAF50; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.8em; }}
                    .temp-btn {{ background: #FF9800; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.8em; }}
                    .preview-btn {{ background: #9C27B0; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.8em; }}
                    .copy-btn:hover {{ background: #45a049; }}
                    .temp-btn:hover {{ background: #e68900; }}
                    .preview-btn:hover {{ background: #7B1FA2; }}
                    #status {{ margin: 10px 0; padding: 10px; background: #dff0d8; border-radius: 5px; display: none; }}
                    #preview {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; display: none; max-height: 400px; overflow: auto; }}
                    .header-row {{ 
                        font-weight: bold; 
                        background: #f0f0f0; 
                        padding: 10px 8px; 
                        display: grid; 
                        grid-template-columns: 2fr 1fr 1fr 1fr; 
                        gap: 10px;
                        border-bottom: 2px solid #ddd;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🐭 Pika Backup Browser</h1>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>Backup Date: {archive_date}</span>
                        <div>
                            <a href="/" style="color: white; text-decoration: none; margin-right: 15px;">📅 Change Date</a>
                            <a href="/unmount" style="color: white; text-decoration: none;">🔒 Unmount</a>
                        </div>
                    </div>
                </div>
                
                <div id="status"></div>
                <div id="preview"></div>
                
                <div class="breadcrumb">
                    {breadcrumb}
                </div>
                
                <div class="header-row">
                    <div>📁 Name</div>
                    <div>📅 Date Modified</div>
                    <div>📊 Size</div>
                    <div>⚡ Actions</div>
                </div>
                
                <div class="file-list">
            """
            
            for item in items:
                if item['is_dir']:
                    html += f"""
                    <div class="file-item">
                        <a href="/browse?path={item['path']}&date={archive_date}" class="directory-item">📁 {item['name']}</a>
                        <span class="file-date">{item['date']}</span>
                        <span class="file-size">--</span>
                        <span>--</span>
                    </div>
                    """
                else:
                    can_preview = self.can_preview_file(item['name'])
                    preview_button = f'<button class="preview-btn" onclick="previewFile(\'{item["full_path"]}\', \'{item["name"]}\')">Preview</button>' if can_preview else ''
                    
                    html += f"""
                    <div class="file-item">
                        <span>📄 {item['name']}</span>
                        <span class="file-date">{item['date']}</span>
                        <span class="file-size">{item['size']}</span>
                        <div class="button-group">
                            {preview_button}
                            <button class="temp-btn" onclick="tempCopy('{item['full_path']}', '{item['name']}')">Temp</button>
                            <button class="copy-btn" onclick="copyFile('{item['full_path']}', '{item['name']}')">Copy</button>
                        </div>
                    </div>
                    """
            
            html += f"""
                </div>
                
                <script>
                    function copyFile(filePath, fileName) {{
                        fetch('/copy?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => showStatus('Permanently copied: ' + fileName + ' to RecoveredFiles/'));
                    }}
                    
                    function tempCopy(filePath, fileName) {{
                        fetch('/temp?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => showStatus('Temp copied: ' + fileName + ' to TempPreview/'));
                    }}
                    
                    function previewFile(filePath, fileName) {{
                        fetch('/preview?file=' + encodeURIComponent(filePath))
                        .then(response => response.text())
                        .then(data => {{
                            document.getElementById('preview').style.display = 'block';
                            document.getElementById('preview').innerHTML = '<h3>Preview: ' + fileName + '</h3><pre style="white-space: pre-wrap; word-wrap: break-word;">' + data + '</pre>';
                            document.getElementById('preview').scrollIntoView();
                        }});
                    }}
                    
                    function showStatus(message) {{
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').innerHTML = message;
                        setTimeout(() => {{
                            document.getElementById('status').style.display = 'none';
                        }}, 4000);
                    }}
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
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
                          '.sh', '.bat', '.ps1', '.ini', '.cfg', '.conf', '.log', '.sql', '.csv'}
        _, ext = os.path.splitext(filename.lower())
        return ext in text_extensions
    
    def generate_breadcrumb(self, path, archive_date):
        breadcrumb = f'<a href="/browse?path=&date={archive_date}">🏠 Home</a>'
        
        if path:
            parts = path.split('/')
            for i, part in enumerate(parts):
                if part:
                    partial_path = '/'.join(parts[:i+1])
                    if i == len(parts) - 1:
                        breadcrumb += f' > <strong>{part}</strong>'
                    else:
                        breadcrumb += f' > <a href="/browse?path={partial_path}&date={archive_date}">{part}</a>'
        
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
            self.wfile.write(f"Copied {filename}".encode())
            
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
            self.wfile.write(f"Temp copied {filename}".encode())
            
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
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:
                content = f"File too large to preview ({file_size/1024/1024:.1f} MB)"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)
                    if len(content) == 10000:
                        content += "\\n\\n... (truncated)"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8', errors='replace'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def unmount_current(self):
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            self.current_mount = None
            
            # Redirect to main page
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        except Exception as e:
            self.send_error(500, str(e))

def create_handler(repo_path, recovery_path, temp_path):
    def handler(*args, **kwargs):
        return BackupDateBrowserHandler(*args, repo_path=repo_path, recovery_path=recovery_path, temp_path=temp_path, **kwargs)
    return handler

def main():
    repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
    recovery_path = "/home/herb/Desktop/RecoveredFiles"
    temp_path = "/home/herb/Desktop/TempPreview"
    
    if not os.path.exists(repo_path):
        print(f"Repository not found: {repo_path}")
        sys.exit(1)
    
    os.makedirs(recovery_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    
    port = 8082
    handler = create_handler(repo_path, recovery_path, temp_path)
    
    try:
        server = HTTPServer(('localhost', port), handler)
        print(f"🗓️  Backup Date Browser started!")
        print(f"📂 Repository: {repo_path}")
        print(f"💾 Recovery: {recovery_path}")
        print(f"🗂️  Temp: {temp_path}")
        print(f"🔗 URL: http://localhost:{port}")
        
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\\n👋 Server stopped")

if __name__ == "__main__":
    main()