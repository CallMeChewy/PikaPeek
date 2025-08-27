#!/usr/bin/env python3
"""
Simple, reliable backup date browser
"""

import os
import sys
import shutil
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import webbrowser
import threading
import time
from datetime import datetime

class SimpleBackupBrowserHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
        self.recovery_path = "/home/herb/Desktop/RecoveredFiles"
        self.temp_path = "/home/herb/Desktop/TempPreview"
        self.mount_point = "/home/herb/simple-backup-mount"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path.startswith('/browse/'):
            self.browse_archive()
        elif self.path.startswith('/copy'):
            self.copy_file()
        elif self.path.startswith('/temp'):
            self.copy_to_temp()
        else:
            self.send_error(404)
    
    def get_archives(self):
        """Get simplified archive list"""
        try:
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg list "{self.repo_path}"'],
                capture_output=True, text=True, check=False
            )
            
            archives = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        archive_name = parts[0]
                        date_str = f"{parts[2]} {parts[3]}"
                        archives.append((archive_name, date_str))
            
            return list(reversed(archives))[:10]  # Last 10 backups
            
        except:
            return []
    
    def serve_main_page(self):
        archives = self.get_archives()
        
        archive_links = ""
        for archive_name, date_str in archives:
            archive_links += f"""
            <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                <strong>{date_str}</strong><br>
                <a href="/browse/{archive_name}" style="color: #2196F3; text-decoration: none;">
                    📁 Browse this backup →
                </a>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Backup Browser</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐭 Simple Backup Browser</h1>
                    <p>Click any date to browse that backup</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>📅 Available Backups:</h3>
                    {archive_links}
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>📂 Files will be copied to:</strong></p>
                    <ul>
                        <li><strong>Temp:</strong> ~/Desktop/TempPreview/</li>
                        <li><strong>Permanent:</strong> ~/Desktop/RecoveredFiles/</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def browse_archive(self):
        # Extract archive name from URL
        archive_name = self.path.split('/browse/')[-1]
        
        if not archive_name:
            self.send_error(400, "Invalid archive")
            return
        
        # Mount the archive
        try:
            # Clean up any existing mount
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount archive
            full_archive = f"{self.repo_path}::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                self.send_error(500, f"Mount failed: {result.stderr}")
                return
            
            # List files in Desktop
            desktop_path = os.path.join(self.mount_point, "home/herb/Desktop")
            
            files_html = ""
            if os.path.exists(desktop_path):
                files = []
                for item in sorted(os.listdir(desktop_path)):
                    if item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(desktop_path, item)
                    
                    if os.path.isfile(item_path):
                        try:
                            size = os.path.getsize(item_path)
                            stat = os.stat(item_path)
                            mod_date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                            
                            if size < 1024:
                                size_str = f"{size} B"
                            elif size < 1024*1024:
                                size_str = f"{size/1024:.1f} KB"
                            else:
                                size_str = f"{size/(1024*1024):.1f} MB"
                            
                            files_html += f"""
                            <tr>
                                <td>📄 {item}</td>
                                <td>{mod_date}</td>
                                <td>{size_str}</td>
                                <td>
                                    <a href="/temp?file={item_path}" style="background: #FF9800; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; margin: 2px;">Temp</a>
                                    <a href="/copy?file={item_path}" style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; margin: 2px;">Copy</a>
                                </td>
                            </tr>
                            """
                        except:
                            continue
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Backup Files - {archive_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
                    th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
                    th {{ background: #f5f5f5; }}
                    .status {{ margin: 10px 0; padding: 10px; background: #dff0d8; border-radius: 5px; display: none; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🐭 Backup Files</h1>
                    <p>Archive: {archive_name} | <a href="/" style="color: white;">📅 Back to Date Selection</a></p>
                </div>
                
                <div id="status" class="status"></div>
                
                <h3>📁 Desktop Files:</h3>
                <table>
                    <tr>
                        <th>File Name</th>
                        <th>Date Modified</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                    {files_html}
                </table>
                
                <p><strong>Other folders:</strong></p>
                <ul>
                    <li><a href="/browse/{archive_name}/Documents">📁 Documents</a></li>
                    <li><a href="/browse/{archive_name}/Projects">📁 Projects</a></li>
                    <li><a href="/browse/{archive_name}/Downloads">📁 Downloads</a></li>
                </ul>
                
                <script>
                    // Show status when file operations complete
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('copied')) {{
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').textContent = 'File copied successfully!';
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
    
    def copy_file(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        try:
            os.makedirs(self.recovery_path, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.recovery_path, filename)
            shutil.copy2(file_path, dest_path)
            
            # Redirect back with success message
            self.send_response(302)
            self.send_header('Location', f'{self.path.split("?")[0].replace("/copy", "/browse")}?copied=1')
            self.end_headers()
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def copy_to_temp(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        try:
            os.makedirs(self.temp_path, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.temp_path, filename)
            shutil.copy2(file_path, dest_path)
            
            # Simple response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <head><title>File Copied</title></head>
            <body>
                <h2>✅ File copied to temp folder!</h2>
                <p><strong>File:</strong> {filename}</p>
                <p><strong>Location:</strong> ~/Desktop/TempPreview/</p>
                <p><a href="javascript:history.back()">← Go Back</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error(500, str(e))

def main():
    port = 8083
    
    try:
        server = HTTPServer(('localhost', port), SimpleBackupBrowserHandler)
        print(f"🌐 Simple Backup Browser started!")
        print(f"🔗 URL: http://localhost:{port}")
        
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()