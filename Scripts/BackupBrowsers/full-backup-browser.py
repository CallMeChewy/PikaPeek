#!/usr/bin/env python3
"""
Full Backup Browser - All backups with complete file system navigation
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

class FullBackupBrowserHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
        self.recovery_path = "/home/herb/Desktop/RecoveredFiles"
        self.temp_path = "/home/herb/Desktop/TempPreview"
        self.mount_point = "/home/herb/full-backup-mount"
        self.current_archive = None
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path.startswith('/browse/'):
            self.handle_browse()
        elif self.path.startswith('/copy'):
            self.copy_file()
        elif self.path.startswith('/temp'):
            self.copy_to_temp()
        elif self.path.startswith('/preview'):
            self.preview_file()
        elif self.path.startswith('/unmount'):
            self.unmount_archive()
        else:
            self.send_error(404)
    
    def get_all_archives(self):
        """Get complete archive list"""
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
            
            return list(reversed(archives))  # Most recent first
            
        except:
            return []
    
    def serve_main_page(self):
        archives = self.get_all_archives()
        
        # Group archives by date for better display
        archive_rows = ""
        for i, (archive_name, date_str) in enumerate(archives):
            # Color alternate rows
            bg_color = "#f9f9f9" if i % 2 == 0 else "white"
            
            archive_rows += f"""
            <tr style="background: {bg_color};">
                <td style="padding: 8px;">{i+1}</td>
                <td style="padding: 8px;"><strong>{date_str}</strong></td>
                <td style="padding: 8px;">{archive_name}</td>
                <td style="padding: 8px;">
                    <a href="/browse/{archive_name}" 
                       style="background: #2196F3; color: white; padding: 6px 12px; 
                              border-radius: 4px; text-decoration: none; font-size: 0.9em;">
                        📁 Browse Files
                    </a>
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Full Backup Browser</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .stats {{ background: white; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }}
                th {{ background: #f0f0f0; padding: 12px; text-align: left; font-weight: bold; }}
                td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #e3f2fd !important; }}
                .search-box {{ margin: 20px 0; }}
                .search-box input {{ padding: 10px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐭 Full Pika Backup Browser</h1>
                    <p>Complete backup history with file system navigation</p>
                </div>
                
                <div class="stats">
                    <h3>📊 Backup Statistics</h3>
                    <ul>
                        <li><strong>Total Backups:</strong> {len(archives)}</li>
                        <li><strong>Repository:</strong> {self.repo_path}</li>
                        <li><strong>Recovery Folder:</strong> ~/Desktop/RecoveredFiles/</li>
                        <li><strong>Temp Folder:</strong> ~/Desktop/TempPreview/</li>
                    </ul>
                </div>
                
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Search backups by date..." 
                           onkeyup="searchBackups()" style="margin-right: 10px;">
                    <span style="color: #666; font-size: 0.9em;">Enter date (YYYY-MM-DD) or time</span>
                </div>
                
                <table id="backupTable">
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th style="width: 200px;">📅 Backup Date</th>
                        <th>🏷️ Archive Name</th>
                        <th style="width: 120px;">⚡ Action</th>
                    </tr>
                    {archive_rows}
                </table>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>💡 How to Use:</h3>
                    <ol>
                        <li><strong>Browse Files:</strong> Click on any backup date to explore files</li>
                        <li><strong>Navigate Folders:</strong> Click folder names to navigate deeper</li>
                        <li><strong>File Actions:</strong> Preview, Temp Copy, or Permanent Copy</li>
                        <li><strong>Search:</strong> Use the search box to find specific backup dates</li>
                    </ol>
                </div>
            </div>
            
            <script>
                function searchBackups() {{
                    const input = document.getElementById('searchInput');
                    const filter = input.value.toLowerCase();
                    const table = document.getElementById('backupTable');
                    const rows = table.getElementsByTagName('tr');
                    
                    for (let i = 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const dateCell = row.getElementsByTagName('td')[1];
                        if (dateCell) {{
                            const dateText = dateCell.textContent.toLowerCase();
                            if (dateText.includes(filter)) {{
                                row.style.display = '';
                            }} else {{
                                row.style.display = 'none';
                            }}
                        }}
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_browse(self):
        # Parse URL: /browse/archive_name/optional/path
        path_parts = self.path.split('/')[2:]  # Remove empty and 'browse'
        
        if not path_parts:
            self.send_error(400, "Invalid browse path")
            return
        
        archive_name = path_parts[0]
        sub_path = '/'.join(path_parts[1:]) if len(path_parts) > 1 else ''
        
        # Mount archive if different from current
        if self.current_archive != archive_name:
            if not self.mount_archive(archive_name):
                self.send_error(500, "Failed to mount archive")
                return
        
        # Build full path to browse
        base_path = os.path.join(self.mount_point, "home/herb")
        if sub_path:
            full_path = os.path.join(base_path, sub_path)
        else:
            full_path = base_path
        
        if not os.path.exists(full_path):
            self.send_error(404, f"Path not found: {sub_path}")
            return
        
        self.serve_directory_listing(archive_name, sub_path, full_path)
    
    def mount_archive(self, archive_name):
        """Mount a specific archive"""
        try:
            # Clean up existing mount
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount new archive
            full_archive = f"{self.repo_path}::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode == 0:
                self.current_archive = archive_name
                return True
            else:
                print(f"Mount failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Mount error: {e}")
            return False
    
    def serve_directory_listing(self, archive_name, sub_path, full_path):
        """Serve directory listing with navigation"""
        
        try:
            # Build breadcrumb navigation
            breadcrumb = f'<a href="/">🏠 All Backups</a> > <a href="/browse/{archive_name}">📁 {archive_name}</a>'
            
            if sub_path:
                path_parts = sub_path.split('/')
                current_path = ""
                for part in path_parts:
                    current_path = f"{current_path}/{part}" if current_path else part
                    if part == path_parts[-1]:
                        breadcrumb += f' > <strong>{part}</strong>'
                    else:
                        breadcrumb += f' > <a href="/browse/{archive_name}/{current_path}">{part}</a>'
            
            # List directory contents
            items = []
            
            # Add parent directory link if not at root
            if sub_path:
                parent_path = '/'.join(sub_path.split('/')[:-1]) if '/' in sub_path else ''
                parent_url = f"/browse/{archive_name}/{parent_path}" if parent_path else f"/browse/{archive_name}"
                items.append({
                    'name': '..',
                    'is_dir': True,
                    'url': parent_url,
                    'size': '',
                    'date': '',
                    'is_parent': True
                })
            
            # List all items
            for item in sorted(os.listdir(full_path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(full_path, item)
                is_dir = os.path.isdir(item_path)
                
                # Build URL for navigation
                if sub_path:
                    item_url = f"/browse/{archive_name}/{sub_path}/{item}"
                else:
                    item_url = f"/browse/{archive_name}/{item}"
                
                # Get file info
                size = ''
                date = ''
                try:
                    stat = os.stat(item_path)
                    date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
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
                    pass
                
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'url': item_url,
                    'full_path': item_path,
                    'size': size,
                    'date': date,
                    'is_parent': False
                })
            
            # Generate file list HTML
            file_rows = ""
            for item in items:
                if item['is_parent']:
                    file_rows += f"""
                    <tr>
                        <td><a href="{item['url']}" style="color: #2196F3; text-decoration: none;">📁 {item['name']}</a></td>
                        <td>--</td>
                        <td>--</td>
                        <td>--</td>
                    </tr>
                    """
                elif item['is_dir']:
                    file_rows += f"""
                    <tr>
                        <td><a href="{item['url']}" style="color: #2196F3; text-decoration: none;">📁 {item['name']}</a></td>
                        <td>{item['date']}</td>
                        <td>Folder</td>
                        <td>--</td>
                    </tr>
                    """
                else:
                    # File actions
                    actions = f"""
                    <a href="/temp?file={item['full_path']}" 
                       style="background: #FF9800; color: white; padding: 3px 6px; border-radius: 3px; 
                              text-decoration: none; font-size: 0.8em; margin: 1px;">Temp</a>
                    <a href="/copy?file={item['full_path']}" 
                       style="background: #4CAF50; color: white; padding: 3px 6px; border-radius: 3px; 
                              text-decoration: none; font-size: 0.8em; margin: 1px;">Copy</a>
                    """
                    
                    # Add preview for text files
                    if self.can_preview_file(item['name']):
                        actions += f"""
                        <a href="/preview?file={item['full_path']}" target="_blank"
                           style="background: #9C27B0; color: white; padding: 3px 6px; border-radius: 3px; 
                                  text-decoration: none; font-size: 0.8em; margin: 1px;">Preview</a>
                        """
                    
                    file_rows += f"""
                    <tr>
                        <td>📄 {item['name']}</td>
                        <td>{item['date']}</td>
                        <td>{item['size']}</td>
                        <td>{actions}</td>
                    </tr>
                    """
            
            # Get archive date for display
            archive_date = "Unknown"
            try:
                result = subprocess.run(
                    ['bash', '-c', f'echo "y" | borg list "{self.repo_path}" | grep "{archive_name}"'],
                    capture_output=True, text=True, check=False
                )
                if result.stdout.strip():
                    parts = result.stdout.strip().split()
                    if len(parts) >= 4:
                        archive_date = f"{parts[2]} {parts[3]}"
            except:
                pass
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Files: {archive_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; }}
                    .breadcrumb {{ margin: 15px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
                    .breadcrumb a {{ color: #2196F3; text-decoration: none; margin: 0 5px; }}
                    .archive-info {{ background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                    table {{ width: 100%; border-collapse: collapse; background: white; }}
                    th {{ background: #f0f0f0; padding: 10px; text-align: left; }}
                    td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                    tr:hover {{ background: #f9f9f9; }}
                    .status {{ margin: 10px 0; padding: 10px; background: #dff0d8; border-radius: 5px; display: none; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🐭 Backup File Browser</h1>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>Browsing: {archive_name}</span>
                        <a href="/unmount" style="color: white; text-decoration: none;">🔒 Unmount & Change Date</a>
                    </div>
                </div>
                
                <div class="archive-info">
                    <strong>📅 Backup Date:</strong> {archive_date} | 
                    <strong>📁 Current Path:</strong> /{sub_path if sub_path else 'home/herb'} |
                    <strong>📊 Items:</strong> {len([i for i in items if not i['is_parent']])}
                </div>
                
                <div id="status" class="status"></div>
                
                <div class="breadcrumb">
                    {breadcrumb}
                </div>
                
                <table>
                    <tr>
                        <th style="width: 40%;">📁 Name</th>
                        <th style="width: 20%;">📅 Date Modified</th>
                        <th style="width: 15%;">📊 Size</th>
                        <th style="width: 25%;">⚡ Actions</th>
                    </tr>
                    {file_rows}
                </table>
                
                <div style="margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px;">
                    <h4>💡 Navigation Tips:</h4>
                    <ul>
                        <li><strong>Click folders</strong> to navigate deeper</li>
                        <li><strong>Use ".."</strong> to go back up one level</li>
                        <li><strong>Temp:</strong> Quick copy to ~/Desktop/TempPreview/</li>
                        <li><strong>Copy:</strong> Permanent copy to ~/Desktop/RecoveredFiles/</li>
                        <li><strong>Preview:</strong> View text files in new tab</li>
                    </ul>
                </div>
                
                <script>
                    // Show status messages from redirects
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('copied')) {{
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').textContent = 'File copied successfully!';
                        setTimeout(() => {{
                            document.getElementById('status').style.display = 'none';
                        }}, 3000);
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
        """Check if file can be previewed"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
                          '.sh', '.bat', '.ps1', '.ini', '.cfg', '.conf', '.log', '.sql', '.csv'}
        _, ext = os.path.splitext(filename.lower())
        return ext in text_extensions
    
    def copy_file(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        try:
            os.makedirs(self.recovery_path, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.recovery_path, filename)
            shutil.copy2(file_path, dest_path)
            
            # Redirect back with success
            referer = self.headers.get('Referer', '/')
            self.send_response(302)
            self.send_header('Location', f'{referer}?copied=1')
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
            
            # Simple success page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <head><title>File Copied</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h2>✅ File copied to temp folder!</h2>
                <p><strong>File:</strong> {filename}</p>
                <p><strong>Location:</strong> ~/Desktop/TempPreview/</p>
                <p><a href="javascript:history.back()" style="color: #2196F3;">← Go Back</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def preview_file(self):
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        file_path = params.get('file', [''])[0]
        
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            if file_size > 1024 * 1024:  # 1MB limit
                content = f"File too large to preview ({file_size/1024/1024:.1f} MB)"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)
                    if len(content) == 10000:
                        content += "\\n\\n... (showing first 10,000 characters)"
            
            html = f"""
            <html>
            <head><title>Preview: {filename}</title></head>
            <body style="font-family: monospace; margin: 20px;">
                <h3>📄 Preview: {filename}</h3>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow: auto;">{content}</pre>
                <p><a href="javascript:history.back()" style="color: #2196F3;">← Go Back</a></p>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def unmount_archive(self):
        """Unmount current archive and return to main page"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            self.current_archive = None
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        except Exception as e:
            self.send_error(500, str(e))

def main():
    port = 8084
    
    try:
        server = HTTPServer(('localhost', port), FullBackupBrowserHandler)
        print(f"🌐 Full Backup Browser started!")
        print(f"🔗 URL: http://localhost:{port}")
        print(f"Features: All backups + Full file system navigation")
        
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()