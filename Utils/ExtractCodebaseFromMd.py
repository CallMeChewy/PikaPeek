# Path: utils/ExtractCodebaseFromMd.py

"""
------------------------------------------------------------------------------
Module      : ExtractCodebaseFromMd
Location    : utils/ExtractCodebaseFromMd.py
Author      : Herb Bowers (Project Himalaya)
Created     : 2025-05-19
Last Update : 2025-05-19  17:38:00
Standard    : AIDEV-PascalCase-1.7

Description :
    Extracts code and documentation blocks from a Project Himalaya markdown
    bundle using "# Path: ..." headers, saves code files to their intended
    filesystem paths (no date folder), saves docs/markdown/misc to dated
    docs subfolder, and writes a manifest in docs/Updates/.

    Usage:
        python utils/ExtractCodebaseFromMd.py [input_md_file]

History    :
    2025-05-19 - Initial version, fully standards-compliant
------------------------------------------------------------------------------
"""

import os
import re
import sys
from datetime import datetime

class ExtractCodebaseFromMd:
    """
    Extracts files from a markdown bundle into project filesystem, docs,
    and logs manifest and warnings, per AIDEV-PascalCase-1.7 standard.
    """

    CodeExtensions = ('.py', '.sh', '.c', '.cpp', '.h', '.hpp', '.js', '.css', '.html', '.json')
    DocExtensions  = ('.md', '.txt')

    def __init__(self, MdFile):
        self.MdFile = MdFile
        self.Today = datetime.now().strftime('%Y-%m-%d')
        self.NowStamp = datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
        self.Summary = []
        self.Manifest = []

    def IsCodeFile(self, Path):
        return Path.endswith(self.CodeExtensions)

    def SaveBlock(self, Path, Content, BlockNum):
        OriginalPath = Path
        if Path.endswith(self.DocExtensions) or Path.startswith('docs/'):
            SavePath = os.path.join('docs', self.Today, os.path.basename(Path))
        elif self.IsCodeFile(Path):
            SavePath = Path
        else:
            Base = os.path.basename(Path) or f'Block{BlockNum}'
            SavePath = os.path.join('docs', self.Today, Base)
            self.Summary.append(f"Questionable path for block {BlockNum}: header '{OriginalPath}', saved as '{SavePath}'")
        os.makedirs(os.path.dirname(SavePath), exist_ok=True)
        with open(SavePath, 'w', encoding='utf-8') as FileObj:
            Filtered = [Line for Line in Content if not Line.strip().startswith('```')]
            FileObj.writelines(Filtered)
        self.Manifest.append(SavePath)

    def ParseAndSave(self):
        with open(self.MdFile, 'r', encoding='utf-8') as FileObj:
            Lines = FileObj.readlines()

        CurrentPath = None
        Buffer = []
        BlockNum = 0

        for Line in Lines:
            Match = re.match(r'# Path: (.+)', Line)
            if Match:
                if CurrentPath and Buffer:
                    BlockNum += 1
                    self.SaveBlock(CurrentPath, Buffer, BlockNum)
                CurrentPath = Match.group(1).strip()
                Buffer = []
            elif CurrentPath:
                Buffer.append(Line)

        if CurrentPath and Buffer:
            BlockNum += 1
            self.SaveBlock(CurrentPath, Buffer, BlockNum)

        self.WriteSummary()

    def WriteSummary(self):
        os.makedirs('docs/Updates', exist_ok=True)
        SummaryPath = f'docs/Updates/{self.NowStamp.replace(":", "").replace(" ", "_")}.md'
        with open(SummaryPath, 'w', encoding='utf-8') as FileObj:
            FileObj.write(f'# Extraction Summary ({self.NowStamp})\n\n')
            FileObj.write('## Files Created:\n')
            for Path in self.Manifest:
                FileObj.write(f'- {Path}\n')
            if self.Summary:
                FileObj.write('\n## Warnings/Questionable Blocks:\n')
                for Msg in self.Summary:
                    FileObj.write(f'- {Msg}\n')

        print('\nManifest of files created:')
        for Path in self.Manifest:
            print(' -', Path)
        print(f"\nSummary written to: {SummaryPath}")

if __name__ == '__main__':
    InputFile = sys.argv[1] if len(sys.argv) > 1 else 'GPU.md'
    ExtractCodebaseFromMd(InputFile).ParseAndSave()
