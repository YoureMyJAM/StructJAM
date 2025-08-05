# StructJAM - File Structure Extractor

Extracts complete project structures into markdown documentation files, capturing all code and text files with their full contents across directories and subdirectories.

## Overview

StructJAM recursively scans directories to generate comprehensive markdown files containing:
- Complete directory tree structure
- Full contents of all text/code files
- Organized format suitable for documentation or AI model context

Perfect for documenting large codebases, sharing project structures, or creating comprehensive snapshots of development work.

## Key Features

**Complete Structure Capture**
- Recursively processes all subdirectories
- Handles projects of any size and complexity
- Preserves exact folder hierarchy

**Full Content Extraction**
- Includes complete file contents for all supported text files
- Supports all common programming languages and text formats
- Maintains original formatting and syntax

**Smart Filtering System**
- **Ignore**: Files/folders appear in structure but contents are skipped
- **Exclude**: Files/folders are completely hidden from output
- Applies to folders, file extensions, and individual files

## Directory Management

**Recent Directories**
- Automatically saves previously processed directories
- Quick access to frequently used project folders
- Browse for new directories as needed

## Output

Generates timestamped markdown files in the target directory containing the complete project documentation with both structure and contents.

### Example Output

````markdown
# File Structure for: C:/Projects/MyApp

**Generated on:** 2025-08-05 14:30:45
**Total Files:** 12 | **Total Folders:** 4

---

## DIRECTORY STRUCTURE

```
├── MyApp/
│   ├── src/
│   │   ├── main.py
│   │   ├── utils.py
│   │   └── config.json
│   ├── tests/
│   │   └── test_main.py
│   └── README.md
```

## FILE CONTENTS

### FILE: src/main.py

```py
def main():
    print("Hello World")
    
if __name__ == "__main__":
    main()
```

### FILE: src/utils.py

```py
def helper_function():
    return "Helper"
```

### FILE: src/config.json

```json
{
  "app_name": "MyApp",
  "version": "1.0.0"
}
```

### FILE: tests/test_main.py

```py
import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertTrue(True)
```
````
