#!/usr/bin/env python3
"""
File Structure Extractor - Enhanced Version
A tool to extract and document file structures from directories.

Features:
- Multiple output formats (Markdown, Text, JSON, YAML)
- Configurable ignore/exclude rules for folders, extensions, and files
- Dark mode support
- Directory sorting options
- Progress tracking
- Modern GUI with settings management
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import ConfigManager
    from gui import FileStructureGUI
    from utils import set_window_icon
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are in the same directory:")
    print("- main.py")
    print("- config.py")
    print("- gui.py")
    print("- settings.py")
    print("- extractor.py")
    print("- utils.py")
    sys.exit(1)


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    # Check for yaml support
    try:
        import yaml
    except ImportError:
        missing_deps.append("pyyaml")

    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))

        # Show GUI message if possible
        try:
            root = tk.Tk()
            root.withdraw()
            set_window_icon(root)

            message = ("Missing required dependencies:\n\n" +
                       "\n".join(f"• {dep}" for dep in missing_deps) +
                       f"\n\nInstall with:\npip install {' '.join(missing_deps)}")

            messagebox.showerror("Missing Dependencies", message)
            root.destroy()
        except:
            pass

        return False

    return True


def main():
    """Main entry point"""
    print("File Structure Extractor - Enhanced Version")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    try:
        # Initialize configuration manager
        config_manager = ConfigManager()

        # Create and run GUI
        app = FileStructureGUI(config_manager)
        app.run()

    except Exception as e:
        print(f"Error starting application: {e}")

        # Try to show error in GUI
        try:
            root = tk.Tk()
            root.withdraw()
            set_window_icon(root)

            error_msg = f"Error starting File Structure Extractor:\n\n{str(e)}"
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()