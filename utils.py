import os
import sys
import tkinter as tk
from tkinter import messagebox


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def open_directory_in_explorer(path):
    """Open the specified directory in the system file explorer"""
    if not os.path.exists(path):
        messagebox.showerror("Error", f"Directory no longer exists: {path}")
        return

    try:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{path}"')
        else:  # Linux and other Unix-like
            os.system(f'xdg-open "{path}"')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open directory: {e}")


def set_window_icon(window):
    """Set the application icon for a window"""
    icon_path = resource_path("SG_icon.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting window icon: {e}")


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def get_directory_size(path):
    """Get total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
    except (OSError, PermissionError):
        pass
    return total_size


def create_tooltip(widget, text):
    """Create a tooltip for a widget"""

    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = tk.Label(tooltip, text=text,
                         background="#ffffcc", foreground="#000000",
                         relief="solid", borderwidth=1,
                         font=("Helvetica", 9), padx=5, pady=3)
        label.pack()
        widget.tooltip = tooltip

    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


def validate_filename(filename):
    """Validate if filename contains valid characters"""
    invalid_chars = '<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)


class ThemeManager:
    """Manage light and dark themes"""

    LIGHT_THEME = {
        'bg': '#f5f5f5',
        'fg': '#2c3e50',
        'accent': '#a822f5',
        'button': '#77349e',
        'entry_bg': '#ffffff',
        'entry_fg': '#2c3e50',
        'listbox_bg': '#ffffff',
        'listbox_fg': '#2c3e50',
        'select_bg': '#a822f5',
        'select_fg': '#ffffff',
        'frame_bg': '#ffffff',
        'disabled_bg': '#e0e0e0',
        'disabled_fg': '#808080'
    }

    DARK_THEME = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'accent': '#bb86fc',
        'button': '#6200ee',
        'entry_bg': '#3c3c3c',
        'entry_fg': '#ffffff',
        'listbox_bg': '#3c3c3c',
        'listbox_fg': '#ffffff',
        'select_bg': '#bb86fc',
        'select_fg': '#000000',
        'frame_bg': '#3c3c3c',
        'disabled_bg': '#404040',
        'disabled_fg': '#808080'
    }

    @classmethod
    def get_theme(cls, dark_mode=False):
        """Get theme colors"""
        return cls.DARK_THEME if dark_mode else cls.LIGHT_THEME

    @classmethod
    def apply_theme(cls, widget, theme, widget_type='default'):
        """Apply theme to a widget"""
        try:
            if widget_type == 'entry':
                widget.configure(bg=theme['entry_bg'], fg=theme['entry_fg'],
                                 insertbackground=theme['fg'])
            elif widget_type == 'listbox':
                widget.configure(bg=theme['listbox_bg'], fg=theme['listbox_fg'],
                                 selectbackground=theme['select_bg'],
                                 selectforeground=theme['select_fg'])
            elif widget_type == 'button':
                widget.configure(bg=theme['button'], fg='#ffffff',
                                 activebackground=theme['accent'])
            elif widget_type == 'frame':
                widget.configure(bg=theme['frame_bg'])
            else:
                widget.configure(bg=theme['bg'], fg=theme['fg'])
        except tk.TclError:
            # Widget doesn't support the configuration
            pass