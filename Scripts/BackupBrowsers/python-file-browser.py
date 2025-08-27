#!/usr/bin/env python3
"""
Simple Python file browser for backup exploration
"""
import os
import sys
import shutil
from pathlib import Path

class BackupBrowser:
    def __init__(self, start_path):
        self.current_path = Path(start_path)
        
    def list_contents(self):
        try:
            items = sorted(self.current_path.iterdir())
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            print(f"\n📁 Current location: {self.current_path}")
            print("=" * 60)
            
            # Show directories first
            if dirs:
                print("📂 Directories:")
                for i, dir_item in enumerate(dirs, 1):
                    print(f"  {i:2d}) {dir_item.name}/")
            
            # Show files
            if files:
                print("\n📄 Files:")
                for i, file_item in enumerate(files, len(dirs) + 1):
                    size = file_item.stat().st_size
                    size_str = self.format_size(size)
                    print(f"  {i:2d}) {file_item.name} ({size_str})")
            
            if not dirs and not files:
                print("Empty directory")
                
            return dirs + files
            
        except PermissionError:
            print("❌ Permission denied")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def navigate(self):
        while True:
            items = self.list_contents()
            
            print("\n" + "=" * 60)
            print("Commands:")
            print("  Number: Enter directory/view file")
            print("  ..: Go up one level")
            print("  /: Go to root")
            print("  ~: Go to home")
            print("  copy <num>: Copy file to Desktop")
            print("  search <pattern>: Search for files")
            print("  quit: Exit browser")
            
            choice = input("\n🔍 Enter command: ").strip()
            
            if choice.lower() == 'quit':
                break
            elif choice == '..':
                if self.current_path.parent != self.current_path:
                    self.current_path = self.current_path.parent
            elif choice == '/':
                self.current_path = Path('/home/herb/pika-browse')
            elif choice == '~':
                self.current_path = Path.home()
            elif choice.startswith('copy '):
                try:
                    num = int(choice.split()[1]) - 1
                    if 0 <= num < len(items) and items[num].is_file():
                        dest = Path.home() / 'Desktop' / items[num].name
                        shutil.copy2(items[num], dest)
                        print(f"✅ Copied {items[num].name} to Desktop")
                    else:
                        print("❌ Invalid file number or not a file")
                except (ValueError, IndexError):
                    print("❌ Usage: copy <number>")
            elif choice.startswith('search '):
                pattern = choice.split(' ', 1)[1]
                self.search_files(pattern)
            elif choice.isdigit():
                num = int(choice) - 1
                if 0 <= num < len(items):
                    item = items[num]
                    if item.is_dir():
                        self.current_path = item
                    else:
                        self.view_file(item)
                else:
                    print("❌ Invalid selection")
            else:
                print("❌ Unknown command")
            
            input("\n📎 Press Enter to continue...")
    
    def view_file(self, file_path):
        try:
            size = file_path.stat().st_size
            if size > 1024 * 1024:  # 1MB
                print(f"📄 File too large to display ({self.format_size(size)})")
                return
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # First 2000 chars
                print(f"\n📄 {file_path.name}:")
                print("-" * 40)
                print(content)
                if len(content) == 2000:
                    print("\n... (truncated)")
        except Exception as e:
            print(f"❌ Cannot read file: {e}")
    
    def search_files(self, pattern):
        print(f"\n🔍 Searching for '*{pattern}*'...")
        matches = []
        try:
            for item in self.current_path.rglob(f'*{pattern}*'):
                if item.is_file():
                    matches.append(item)
                if len(matches) >= 20:  # Limit results
                    break
            
            if matches:
                for i, match in enumerate(matches, 1):
                    rel_path = match.relative_to(self.current_path)
                    print(f"  {i:2d}) {rel_path}")
            else:
                print("  No matches found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")

if __name__ == "__main__":
    start_path = "/home/herb/pika-browse"
    if len(sys.argv) > 1:
        start_path = sys.argv[1]
    
    if not os.path.exists(start_path):
        print(f"❌ Path does not exist: {start_path}")
        sys.exit(1)
    
    browser = BackupBrowser(start_path)
    print("🐭 Pika Backup File Browser")
    print("Navigate your backup files with ease!")
    browser.navigate()
    print("👋 Goodbye!")