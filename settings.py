import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from utils import set_window_icon, ThemeManager, create_tooltip


class SettingsWindow:
    def __init__(self, parent, config_manager, on_theme_change=None):
        self.config = config_manager
        self.on_theme_change = on_theme_change
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - File Structure Extractor")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()

        # Set icon
        set_window_icon(self.window)

        # Get theme
        self.dark_mode = self.config.get('general', 'dark_mode') or False
        self.theme = ThemeManager.get_theme(self.dark_mode)

        # Apply theme to window
        self.window.configure(bg=self.theme['bg'])

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        w, h = self.window.winfo_width(), self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        """Create all widgets"""
        # Top frame with buttons
        top_frame = tk.Frame(self.window, bg=self.theme['bg'])
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # Save/Cancel buttons
        save_btn = tk.Button(top_frame, text="💾 Save Settings",
                             command=self.save_settings,
                             bg=self.theme['button'], fg='white',
                             activebackground=self.theme['accent'],
                             font=('Helvetica', 10, 'bold'), padx=20, pady=8,
                             relief=tk.RAISED, bd=2, cursor='hand2')
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.add_button_effects(save_btn, self.theme['button'], self.theme['accent'])

        cancel_btn = tk.Button(top_frame, text="❌ Cancel",
                               command=self.window.destroy,
                               bg='#666666', fg='white',
                               activebackground='#888888',
                               font=('Helvetica', 10), padx=20, pady=8,
                               relief=tk.RAISED, bd=2, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 5))
        self.add_button_effects(cancel_btn, '#666666', '#888888')

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook', background=self.theme['bg'])
        style.configure('TNotebook.Tab', background=self.theme['frame_bg'],
                        foreground=self.theme['fg'], padding=[12, 8])

        # Create tabs
        self.create_general_tab()
        self.create_folders_tab()
        self.create_extensions_tab()
        self.create_files_tab()

    def create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="⚙️ General")

        # Main container
        main_container = tk.Frame(general_frame, bg=self.theme['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Output settings
        output_frame = tk.LabelFrame(main_container, text="Output Settings",
                                     font=('Helvetica', 10, 'bold'),
                                     bg=self.theme['bg'], fg=self.theme['fg'])
        output_frame.pack(fill=tk.X, pady=(0, 15))

        # Output file prefix
        tk.Label(output_frame, text="File prefix:", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 10)).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.prefix_var = tk.StringVar(value=self.config.get('general', 'output_file_prefix'))
        prefix_entry = tk.Entry(output_frame, textvariable=self.prefix_var,
                                font=('Helvetica', 10))
        ThemeManager.apply_theme(prefix_entry, self.theme, 'entry')
        prefix_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        # File format
        tk.Label(output_frame, text="Output format:", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 10)).pack(anchor=tk.W, padx=10, pady=(0, 5))

        format_frame = tk.Frame(output_frame, bg=self.theme['bg'])
        format_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.format_var = tk.StringVar(value=self.config.get('general', 'file_format'))

        formats = [('Markdown (.md)', 'md'), ('Text (.txt)', 'txt'),
                   ('JSON (.json)', 'json'), ('YAML (.yaml)', 'yaml')]

        for i, (text, value) in enumerate(formats):
            rb = tk.Radiobutton(format_frame, text=text, variable=self.format_var,
                                value=value, bg=self.theme['bg'], fg=self.theme['fg'],
                                activebackground=self.theme['bg'], selectcolor=self.theme['accent'],
                                font=('Helvetica', 10), relief=tk.FLAT, bd=2, padx=5, pady=2)
            rb.grid(row=i // 2, column=i % 2, sticky='w', padx=(0, 20), pady=2)
            self.add_radiobutton_effects(rb)

        # Max file size
        tk.Label(output_frame, text="Max file size (MB):", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 10)).pack(anchor=tk.W, padx=10, pady=(0, 5))

        self.size_var = tk.StringVar(value=str(self.config.get('general', 'max_file_size_mb')))
        size_entry = tk.Entry(output_frame, textvariable=self.size_var,
                              font=('Helvetica', 10), width=10)
        ThemeManager.apply_theme(size_entry, self.theme, 'entry')
        size_entry.pack(anchor=tk.W, padx=10, pady=(0, 10))

        # Other settings
        other_frame = tk.LabelFrame(main_container, text="Other Settings",
                                    font=('Helvetica', 10, 'bold'),
                                    bg=self.theme['bg'], fg=self.theme['fg'])
        other_frame.pack(fill=tk.X, pady=(0, 15))

        # Delete previous files
        self.delete_var = tk.BooleanVar(value=self.config.get('general', 'delete_previous_files'))
        delete_cb = tk.Checkbutton(other_frame, text="Delete previous output files",
                                   variable=self.delete_var, bg=self.theme['bg'],
                                   fg=self.theme['fg'], activebackground=self.theme['bg'],
                                   selectcolor=self.theme['accent'], font=('Helvetica', 10),
                                   relief=tk.FLAT, bd=2, padx=5, pady=3)
        delete_cb.pack(anchor=tk.W, padx=10, pady=10)
        self.add_checkbox_effects(delete_cb)

        # Dark mode
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        dark_cb = tk.Checkbutton(other_frame, text="Dark mode (requires restart)",
                                 variable=self.dark_mode_var, bg=self.theme['bg'],
                                 fg=self.theme['fg'], activebackground=self.theme['bg'],
                                 selectcolor=self.theme['accent'], font=('Helvetica', 10),
                                 relief=tk.FLAT, bd=2, padx=5, pady=3)
        dark_cb.pack(anchor=tk.W, padx=10, pady=(0, 10))
        self.add_checkbox_effects(dark_cb)

        # Sort mode
        tk.Label(other_frame, text="Directory list sort:", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 10)).pack(anchor=tk.W, padx=10, pady=(0, 5))

        sort_frame = tk.Frame(other_frame, bg=self.theme['bg'])
        sort_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.sort_var = tk.StringVar(value=self.config.get('general', 'sort_mode'))

        sort_options = [('Recent', 'recent'), ('Alphabetical', 'alphabetical'),
                        ('Size', 'size'), ('Date Modified', 'date_modified')]

        for i, (text, value) in enumerate(sort_options):
            rb = tk.Radiobutton(sort_frame, text=text, variable=self.sort_var,
                                value=value, bg=self.theme['bg'], fg=self.theme['fg'],
                                activebackground=self.theme['bg'], selectcolor=self.theme['accent'],
                                font=('Helvetica', 10), relief=tk.FLAT, bd=2, padx=5, pady=2)
            rb.grid(row=i // 2, column=i % 2, sticky='w', padx=(0, 20), pady=2)
            self.add_radiobutton_effects(rb)

    def add_checkbox_effects(self, checkbox):
        """Add visual effects to checkboxes"""

        def on_enter(e):
            checkbox.configure(relief=tk.RAISED)

        def on_leave(e):
            checkbox.configure(relief=tk.FLAT)

        checkbox.bind('<Enter>', on_enter)
        checkbox.bind('<Leave>', on_leave)

    def add_radiobutton_effects(self, radiobutton):
        """Add visual effects to radio buttons"""

        def on_enter(e):
            radiobutton.configure(relief=tk.RAISED)

        def on_leave(e):
            radiobutton.configure(relief=tk.FLAT)

        radiobutton.bind('<Enter>', on_enter)
        radiobutton.bind('<Leave>', on_leave)

    def create_folders_tab(self):
        """Create folders tab with both ignored and excluded"""
        folders_frame = ttk.Frame(self.notebook)
        self.notebook.add(folders_frame, text="📁 Folders")

        main_container = tk.Frame(folders_frame, bg=self.theme['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Instructions
        instruction_text = ("Ignored folders: appear in structure but contents aren't read\n"
                            "Excluded folders: completely hidden from structure")
        tk.Label(main_container, text=instruction_text, font=('Helvetica', 10),
                 bg=self.theme['bg'], fg=self.theme['fg'], justify=tk.LEFT).pack(pady=(0, 15))

        # Two columns for ignored and excluded
        columns_frame = tk.Frame(main_container, bg=self.theme['bg'])
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Ignored folders (left)
        ignored_frame = tk.LabelFrame(columns_frame, text="Ignored Folders",
                                      font=('Helvetica', 10, 'bold'),
                                      bg=self.theme['bg'], fg=self.theme['fg'])
        ignored_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.ignored_folders_listbox = self.create_listbox_with_controls(
            ignored_frame, self.config.get('folders', 'ignored') or [],
            self.add_ignored_folder, self.remove_ignored_folder)

        # Excluded folders (right)
        excluded_frame = tk.LabelFrame(columns_frame, text="Excluded Folders",
                                       font=('Helvetica', 10, 'bold'),
                                       bg=self.theme['bg'], fg=self.theme['fg'])
        excluded_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.excluded_folders_listbox = self.create_listbox_with_controls(
            excluded_frame, self.config.get('folders', 'excluded') or [],
            self.add_excluded_folder, self.remove_excluded_folder)

        # Quick add buttons
        self.create_folder_quick_add(main_container)

    def create_extensions_tab(self):
        """Create extensions tab with both ignored and excluded"""
        ext_frame = ttk.Frame(self.notebook)
        self.notebook.add(ext_frame, text="📄 Extensions")

        main_container = tk.Frame(ext_frame, bg=self.theme['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Instructions
        instruction_text = ("Ignored extensions: files appear in structure but contents aren't read\n"
                            "Excluded extensions: files completely hidden from structure")
        tk.Label(main_container, text=instruction_text, font=('Helvetica', 10),
                 bg=self.theme['bg'], fg=self.theme['fg'], justify=tk.LEFT).pack(pady=(0, 15))

        # Two columns
        columns_frame = tk.Frame(main_container, bg=self.theme['bg'])
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Ignored extensions (left)
        ignored_frame = tk.LabelFrame(columns_frame, text="Ignored Extensions",
                                      font=('Helvetica', 10, 'bold'),
                                      bg=self.theme['bg'], fg=self.theme['fg'])
        ignored_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.ignored_ext_listbox = self.create_listbox_with_controls(
            ignored_frame, self.config.get('extensions', 'ignored') or [],
            self.add_ignored_extension, self.remove_ignored_extension)

        # Excluded extensions (right)
        excluded_frame = tk.LabelFrame(columns_frame, text="Excluded Extensions",
                                       font=('Helvetica', 10, 'bold'),
                                       bg=self.theme['bg'], fg=self.theme['fg'])
        excluded_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.excluded_ext_listbox = self.create_listbox_with_controls(
            excluded_frame, self.config.get('extensions', 'excluded') or [],
            self.add_excluded_extension, self.remove_excluded_extension)

        # Quick add buttons
        self.create_extension_quick_add(main_container)

    def create_files_tab(self):
        """Create files tab with both ignored and excluded"""
        files_frame = ttk.Frame(self.notebook)
        self.notebook.add(files_frame, text="📝 Files")

        main_container = tk.Frame(files_frame, bg=self.theme['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Instructions
        instruction_text = ("Specify individual files by name. Use * for wildcards (e.g., '*.log')\n"
                            "Ignored files: appear in structure but contents aren't read\n"
                            "Excluded files: completely hidden from structure")
        tk.Label(main_container, text=instruction_text, font=('Helvetica', 10),
                 bg=self.theme['bg'], fg=self.theme['fg'], justify=tk.LEFT).pack(pady=(0, 15))

        # Two columns
        columns_frame = tk.Frame(main_container, bg=self.theme['bg'])
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Ignored files (left)
        ignored_frame = tk.LabelFrame(columns_frame, text="Ignored Files",
                                      font=('Helvetica', 10, 'bold'),
                                      bg=self.theme['bg'], fg=self.theme['fg'])
        ignored_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.ignored_files_listbox = self.create_listbox_with_controls(
            ignored_frame, self.config.get('files', 'ignored') or [],
            self.add_ignored_file, self.remove_ignored_file)

        # Excluded files (right)
        excluded_frame = tk.LabelFrame(columns_frame, text="Excluded Files",
                                       font=('Helvetica', 10, 'bold'),
                                       bg=self.theme['bg'], fg=self.theme['fg'])
        excluded_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.excluded_files_listbox = self.create_listbox_with_controls(
            excluded_frame, self.config.get('files', 'excluded') or [],
            self.add_excluded_file, self.remove_excluded_file)

    def create_listbox_with_controls(self, parent, items, add_func, remove_func):
        """Create a listbox with add/remove controls"""
        # Listbox frame
        list_frame = tk.Frame(parent, bg=self.theme['frame_bg'], relief=tk.RIDGE, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar and listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                             font=('Helvetica', 10), selectmode=tk.SINGLE)
        ThemeManager.apply_theme(listbox, self.theme, 'listbox')
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for item in sorted(items):
            listbox.insert(tk.END, item)

        # Entry and buttons
        entry_frame = tk.Frame(parent, bg=self.theme['bg'])
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        entry = tk.Entry(entry_frame, font=('Helvetica', 10))
        ThemeManager.apply_theme(entry, self.theme, 'entry')
        entry.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        btn_frame = tk.Frame(entry_frame, bg=self.theme['bg'])
        btn_frame.pack(fill=tk.X)

        add_btn = tk.Button(btn_frame, text="Add", command=lambda: add_func(entry, listbox),
                            bg=self.theme['button'], fg='white', width=8,
                            activebackground=self.theme['accent'], font=('Helvetica', 9),
                            relief=tk.RAISED, bd=2, cursor='hand2')
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.add_button_effects(add_btn, self.theme['button'], self.theme['accent'])

        remove_btn = tk.Button(btn_frame, text="Remove", command=lambda: remove_func(listbox),
                               bg='#d32f2f', fg='white', width=8,
                               activebackground='#f44336', font=('Helvetica', 9),
                               relief=tk.RAISED, bd=2, cursor='hand2')
        remove_btn.pack(side=tk.LEFT)
        self.add_button_effects(remove_btn, '#d32f2f', '#f44336')

        return listbox

    def add_button_effects(self, button, normal_color, hover_color):
        """Add hover and click effects to buttons"""

        def on_enter(e):
            if button['state'] != tk.DISABLED:
                button.configure(bg=hover_color)

        def on_leave(e):
            if button['state'] != tk.DISABLED:
                button.configure(bg=normal_color)

        def on_click(e):
            if button['state'] != tk.DISABLED:
                button.configure(relief=tk.SUNKEN)
                button.after(100, lambda: button.configure(relief=tk.RAISED))

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        button.bind('<Button-1>', on_click)

    def create_folder_quick_add(self, parent):
        """Create quick add buttons for folders"""
        quick_frame = tk.LabelFrame(parent, text="Quick Add Common Folders",
                                    font=('Helvetica', 10, 'bold'),
                                    bg=self.theme['bg'], fg=self.theme['fg'])
        quick_frame.pack(fill=tk.X, pady=15)

        btn_frame = tk.Frame(quick_frame, bg=self.theme['bg'])
        btn_frame.pack(padx=10, pady=10)

        # Common folders from original code
        ignored_folders = [
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            '.idea', '.vscode', 'target', '.pytest_cache', '.mypy_cache',
            'build', 'dist', '.next', '.nuxt', 'coverage'
        ]

        excluded_folders = [
            'static', 'assets', 'media', 'uploads'
        ]

        all_folders = [(f, 'ignored') for f in ignored_folders] + [(f, 'excluded') for f in excluded_folders]

        for i, (folder, folder_type) in enumerate(all_folders):
            color = self.theme['button'] if folder_type == 'ignored' else '#d32f2f'
            active_color = self.theme['accent'] if folder_type == 'ignored' else '#f44336'

            def make_command(f, ftype):
                if ftype == 'ignored':
                    return lambda: self.quick_add_ignored_folder(f)
                else:
                    return lambda: self.quick_add_excluded_folder(f)

            btn = tk.Button(btn_frame, text=f"📁 {folder}",
                            command=make_command(folder, folder_type),
                            bg=color, fg='white',
                            activebackground=active_color,
                            relief=tk.RAISED, bd=2,
                            width=12, font=('Helvetica', 8))
            btn.grid(row=i // 4, column=i % 4, padx=3, pady=3, sticky='ew')

            # Improve button feedback
            def on_enter(e, b=btn, c=active_color):
                b.configure(bg=c)

            def on_leave(e, b=btn, c=color):
                b.configure(bg=c)

            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)

    def create_extension_quick_add(self, parent):
        """Create quick add buttons for extensions"""
        quick_frame = tk.LabelFrame(parent, text="Quick Add Common Extensions",
                                    font=('Helvetica', 10, 'bold'),
                                    bg=self.theme['bg'], fg=self.theme['fg'])
        quick_frame.pack(fill=tk.X, pady=15)

        btn_frame = tk.Frame(quick_frame, bg=self.theme['bg'])
        btn_frame.pack(padx=10, pady=10)

        # Common extensions from original code
        ignored_extensions = [
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe', '.obj', '.o', '.a', '.lib'
        ]

        excluded_extensions = [
            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
            '.mp4', '.avi', '.mov', '.mp3', '.wav', '.pdf',
            '.zip', '.rar', '.tar', '.msi', '.dmg'
        ]

        all_extensions = [(e, 'ignored') for e in ignored_extensions] + [(e, 'excluded') for e in excluded_extensions]

        for i, (ext, ext_type) in enumerate(all_extensions):
            color = self.theme['button'] if ext_type == 'ignored' else '#d32f2f'
            active_color = self.theme['accent'] if ext_type == 'ignored' else '#f44336'

            def make_command(e, etype):
                if etype == 'ignored':
                    return lambda: self.quick_add_ignored_extension(e)
                else:
                    return lambda: self.quick_add_excluded_extension(e)

            btn = tk.Button(btn_frame, text=f"📄 {ext}",
                            command=make_command(ext, ext_type),
                            bg=color, fg='white',
                            activebackground=active_color,
                            relief=tk.RAISED, bd=2,
                            width=8, font=('Helvetica', 8))
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky='ew')

            # Improve button feedback
            def on_enter(e, b=btn, c=active_color):
                b.configure(bg=c)

            def on_leave(e, b=btn, c=color):
                b.configure(bg=c)

            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)

    # Add/remove methods for folders
    def add_ignored_folder(self, entry, listbox):
        folder = entry.get().strip()
        if folder and folder not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, folder)
            entry.delete(0, tk.END)

    def remove_ignored_folder(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def add_excluded_folder(self, entry, listbox):
        folder = entry.get().strip()
        if folder and folder not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, folder)
            entry.delete(0, tk.END)

    def remove_excluded_folder(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    # Similar methods for extensions and files...
    def add_ignored_extension(self, entry, listbox):
        ext = entry.get().strip()
        if not ext.startswith('.'):
            ext = '.' + ext
        if ext and ext not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, ext)
            entry.delete(0, tk.END)

    def remove_ignored_extension(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def add_excluded_extension(self, entry, listbox):
        ext = entry.get().strip()
        if not ext.startswith('.'):
            ext = '.' + ext
        if ext and ext not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, ext)
            entry.delete(0, tk.END)

    def remove_excluded_extension(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def add_ignored_file(self, entry, listbox):
        file = entry.get().strip()
        if file and file not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, file)
            entry.delete(0, tk.END)

    def remove_ignored_file(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def add_excluded_file(self, entry, listbox):
        file = entry.get().strip()
        if file and file not in self.get_listbox_items(listbox):
            listbox.insert(tk.END, file)
            entry.delete(0, tk.END)

    def remove_excluded_file(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    # Quick add methods
    def quick_add_ignored_folder(self, folder):
        if folder not in self.get_listbox_items(self.ignored_folders_listbox):
            self.ignored_folders_listbox.insert(tk.END, folder)

    def quick_add_excluded_folder(self, folder):
        if folder not in self.get_listbox_items(self.excluded_folders_listbox):
            self.excluded_folders_listbox.insert(tk.END, folder)

    def quick_add_ignored_extension(self, ext):
        if ext not in self.get_listbox_items(self.ignored_ext_listbox):
            self.ignored_ext_listbox.insert(tk.END, ext)

    def quick_add_excluded_extension(self, ext):
        if ext not in self.get_listbox_items(self.excluded_ext_listbox):
            self.excluded_ext_listbox.insert(tk.END, ext)

    def get_listbox_items(self, listbox):
        """Get all items from a listbox"""
        return [listbox.get(i) for i in range(listbox.size())]

    def save_settings(self):
        """Save all settings"""
        try:
            # Validate numeric inputs
            max_size = float(self.size_var.get())
            if max_size <= 0:
                raise ValueError("Max file size must be positive")

            # Update general settings
            self.config.set('general', 'output_file_prefix', self.prefix_var.get() or 'project_structure')
            self.config.set('general', 'file_format', self.format_var.get())
            self.config.set('general', 'max_file_size_mb', max_size)
            self.config.set('general', 'delete_previous_files', self.delete_var.get())
            self.config.set('general', 'dark_mode', self.dark_mode_var.get())
            self.config.set('general', 'sort_mode', self.sort_var.get())

            # Update folder settings
            self.config.config['folders']['ignored'] = self.get_listbox_items(self.ignored_folders_listbox)
            self.config.config['folders']['excluded'] = self.get_listbox_items(self.excluded_folders_listbox)

            # Update extension settings
            self.config.config['extensions']['ignored'] = self.get_listbox_items(self.ignored_ext_listbox)
            self.config.config['extensions']['excluded'] = self.get_listbox_items(self.excluded_ext_listbox)

            # Update file settings
            self.config.config['files']['ignored'] = self.get_listbox_items(self.ignored_files_listbox)
            self.config.config['files']['excluded'] = self.get_listbox_items(self.excluded_files_listbox)

            # Save configuration
            self.config.save_config()

            # Check if theme changed
            if self.dark_mode_var.get() != self.dark_mode and self.on_theme_change:
                messagebox.showinfo("Theme Changed",
                                    "Dark mode setting changed. Please restart the application for the change to take effect.")

            messagebox.showinfo("Success", "Settings saved successfully!")
            self.window.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")