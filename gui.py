import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from datetime import datetime

from utils import set_window_icon, ThemeManager, open_directory_in_explorer, create_tooltip, format_file_size, \
    get_directory_size
from settings import SettingsWindow
from extractor import FileStructureExtractor


class FileStructureGUI:
    def __init__(self, config_manager):
        self.config = config_manager
        self.extractor = FileStructureExtractor(config_manager)

        # Get theme
        self.dark_mode = self.config.get('general', 'dark_mode') or False
        self.theme = ThemeManager.get_theme(self.dark_mode)

        # Create main window
        self.root = tk.Tk()
        self.root.title("File Structure Extractor")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        # Set icon
        set_window_icon(self.root)

        # Apply theme
        self.root.configure(bg=self.theme['bg'])

        # Initialize variables
        self.valid_dirs = []
        self.filtered_dirs = []

        self.create_widgets()
        self.setup_bindings()
        self.refresh_directory_list()
        self.center_window()

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        """Create all GUI widgets"""
        # Configure ttk styles
        self.setup_styles()

        # Main container
        main_frame = tk.Frame(self.root, bg=self.theme['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_frame)

        # Options panel
        self.create_options_panel(main_frame)

        # Search frame
        self.create_search_frame(main_frame)

        # Directory list
        self.create_directory_list(main_frame)

        # Progress bar
        self.create_progress_bar(main_frame)

        # Buttons
        self.create_buttons(main_frame)

        # Status bar
        self.create_status_bar()

    def setup_styles(self):
        """Setup ttk styles for theme"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

        # Configure styles based on theme
        style.configure('TButton',
                        background=self.theme['button'],
                        foreground='white',
                        font=('Helvetica', 10),
                        padding=6)
        style.map('TButton',
                  background=[('active', self.theme['accent']), ('pressed', self.theme['button'])])

        style.configure('TCheckbutton',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'],
                        font=('Helvetica', 10))
        style.map('TCheckbutton',
                  background=[('active', self.theme['bg'])],
                  indicatorcolor=[('selected', self.theme['accent'])])

        style.configure('TRadiobutton',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'],
                        font=('Helvetica', 10))
        style.map('TRadiobutton',
                  background=[('active', self.theme['bg'])],
                  indicatorcolor=[('selected', self.theme['accent'])])

        style.configure('TFrame', background=self.theme['bg'])
        style.configure('TLabel', background=self.theme['bg'], foreground=self.theme['fg'])

    def create_header(self, parent):
        """Create header with title and settings button"""
        header_frame = tk.Frame(parent, bg=self.theme['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title_label = tk.Label(header_frame, text="File Structure Extractor",
                               font=('Helvetica', 16, 'bold'),
                               bg=self.theme['bg'], fg=self.theme['fg'])
        title_label.pack(side=tk.LEFT)

        # Settings button
        settings_btn = tk.Button(header_frame, text="⚙️ Settings",
                                 command=self.open_settings,
                                 bg='#666666', fg='white',
                                 activebackground='#888888',
                                 font=('Helvetica', 10), padx=15, pady=5)
        settings_btn.pack(side=tk.RIGHT)
        create_tooltip(settings_btn, "Configure extraction settings")

    def create_options_panel(self, parent):
        """Create options panel"""
        options_frame = tk.Frame(parent, bg=self.theme['frame_bg'], relief=tk.RIDGE, bd=1)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        # Title bar
        title_bar = tk.Frame(options_frame, bg=self.theme['button'])
        title_bar.pack(fill=tk.X)
        tk.Label(title_bar, text="Quick Options", font=("Helvetica", 11, "bold"),
                 bg=self.theme['button'], fg="white", padx=10, pady=5).pack(anchor=tk.W)

        # Content
        content_frame = tk.Frame(options_frame, bg=self.theme['frame_bg'], padx=15, pady=10)
        content_frame.pack(fill=tk.X)

        # Delete previous files option
        self.delete_var = tk.BooleanVar(value=self.config.get('general', 'delete_previous_files'))
        delete_cb = tk.Checkbutton(content_frame, text="Delete previous project structure files",
                                   variable=self.delete_var, bg=self.theme['frame_bg'],
                                   fg=self.theme['fg'], activebackground=self.theme['frame_bg'],
                                   selectcolor=self.theme['accent'], font=("Helvetica", 10),
                                   relief=tk.FLAT, bd=2, padx=5, pady=3)
        delete_cb.pack(anchor=tk.W, pady=(0, 10))
        self.add_checkbox_effects(delete_cb)

        # Format selection
        format_frame = tk.Frame(content_frame, bg=self.theme['frame_bg'])
        format_frame.pack(fill=tk.X)

        tk.Label(format_frame, text="Output format:", bg=self.theme['frame_bg'],
                 fg=self.theme['fg'], font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.format_var = tk.StringVar(value=self.config.get('general', 'file_format'))

        formats = [("Markdown (.md)", "md"), ("Text (.txt)", "txt"),
                   ("JSON (.json)", "json"), ("YAML (.yaml)", "yaml")]

        for text, value in formats:
            rb = tk.Radiobutton(format_frame, text=text, variable=self.format_var, value=value,
                                bg=self.theme['frame_bg'], fg=self.theme['fg'],
                                activebackground=self.theme['frame_bg'],
                                selectcolor=self.theme['accent'],
                                font=("Helvetica", 10), relief=tk.FLAT, bd=2, padx=5, pady=2)
            rb.pack(side=tk.LEFT, padx=(0, 20))
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

    def create_search_frame(self, parent):
        """Create search frame"""
        search_frame = tk.Frame(parent, bg=self.theme['bg'])
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # Search label and entry
        tk.Label(search_frame, text="Search:", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)

        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Helvetica', 10))
        ThemeManager.apply_theme(search_entry, self.theme, 'entry')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Clear button
        clear_btn = tk.Button(search_frame, text="Clear", command=lambda: self.search_var.set(""),
                              bg='#999999', fg='white', font=('Helvetica', 9), width=6)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Sort options
        sort_frame = tk.Frame(search_frame, bg=self.theme['bg'])
        sort_frame.pack(side=tk.RIGHT)

        tk.Label(sort_frame, text="Sort:", bg=self.theme['bg'],
                 fg=self.theme['fg'], font=('Helvetica', 9)).pack(side=tk.LEFT, padx=(0, 5))

        self.sort_var = tk.StringVar(value=self.config.get('general', 'sort_mode'))
        self.sort_var.trace('w', self.on_sort_change)

        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, width=12,
                                  values=['recent', 'alphabetical', 'size', 'date_modified'],
                                  state='readonly', font=('Helvetica', 9))
        sort_combo.pack(side=tk.LEFT)

    def create_directory_list(self, parent):
        """Create directory list with header"""
        list_container = tk.Frame(parent, bg=self.theme['bg'])
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # List header
        header_frame = tk.Frame(list_container, bg=self.theme['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 5))

        list_label = tk.Label(header_frame, text="Previously used directories:",
                              font=('Helvetica', 10, 'bold'),
                              bg=self.theme['bg'], fg=self.theme['fg'])
        list_label.pack(side=tk.LEFT)

        self.count_var = tk.StringVar()
        count_label = tk.Label(header_frame, textvariable=self.count_var,
                               font=('Helvetica', 9),
                               bg=self.theme['bg'], fg='#666666')
        count_label.pack(side=tk.RIGHT)

        # Listbox container
        listbox_container = tk.Frame(list_container, bd=1, relief=tk.SOLID,
                                     bg=self.theme['accent'])
        listbox_container.pack(fill=tk.BOTH, expand=True)

        listbox_inner = tk.Frame(listbox_container, bg=self.theme['listbox_bg'])
        listbox_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Scrollbar and listbox
        scrollbar = ttk.Scrollbar(listbox_inner)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.directory_listbox = tk.Listbox(listbox_inner, yscrollcommand=scrollbar.set,
                                            font=('Helvetica', 10), height=12,
                                            bd=0, highlightthickness=0, activestyle='none')
        ThemeManager.apply_theme(self.directory_listbox, self.theme, 'listbox')
        self.directory_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.directory_listbox.yview)

        # Bind events
        self.directory_listbox.bind('<Double-1>', lambda e: self.process_selected_directory())
        self.directory_listbox.bind('<Button-3>', self.show_context_menu)  # Right click
        self.directory_listbox.bind('<<ListboxSelect>>', lambda e: self.update_button_states())  # Selection change

    def create_progress_bar(self, parent):
        """Create progress bar (initially hidden)"""
        self.progress_frame = tk.Frame(parent, bg=self.theme['bg'])

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var,
                                            maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.progress_label = tk.Label(self.progress_frame, text="",
                                       bg=self.theme['bg'], fg=self.theme['fg'],
                                       font=('Helvetica', 9))
        self.progress_label.pack()

    def create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg=self.theme['bg'])
        button_frame.pack(fill=tk.X)

        button_style = {
            'font': ('Helvetica', 10, 'bold'),
            'relief': tk.RAISED,
            'bd': 2,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }

        # Select new directory
        self.new_btn = tk.Button(button_frame, text="📁 Select New Directory",
                                 command=self.select_new_directory,
                                 bg=self.theme['button'], fg='white',
                                 activebackground=self.theme['accent'], **button_style)
        self.new_btn.pack(side=tk.LEFT, padx=(0, 10))
        create_tooltip(self.new_btn, "Browse for a new directory to process")
        self.add_button_effects(self.new_btn, self.theme['button'], self.theme['accent'])

        # Use selected directory
        self.use_btn = tk.Button(button_frame, text="✅ Process Selected",
                                 command=self.process_selected_directory,
                                 bg=self.theme['button'], fg='white',
                                 activebackground=self.theme['accent'], **button_style)
        self.use_btn.pack(side=tk.LEFT, padx=(0, 10))
        create_tooltip(self.use_btn, "Process the selected directory")
        self.add_button_effects(self.use_btn, self.theme['button'], self.theme['accent'])

        # Open in explorer
        self.open_btn = tk.Button(button_frame, text="📂 Open in Explorer",
                                  command=self.open_selected_directory,
                                  bg=self.theme['button'], fg='white',
                                  activebackground=self.theme['accent'], **button_style)
        self.open_btn.pack(side=tk.LEFT, padx=(0, 10))
        create_tooltip(self.open_btn, "Open selected directory in file explorer")
        self.add_button_effects(self.open_btn, self.theme['button'], self.theme['accent'])

        # Remove from list
        self.remove_btn = tk.Button(button_frame, text="🗑️ Remove Selected",
                                    command=self.remove_selected_directory,
                                    bg='#d32f2f', fg='white',
                                    activebackground='#f44336', **button_style)
        self.remove_btn.pack(side=tk.LEFT, padx=(0, 10))
        create_tooltip(self.remove_btn, "Remove selected directory from list (Delete key)")
        self.add_button_effects(self.remove_btn, '#d32f2f', '#f44336')

        # Refresh button
        refresh_btn = tk.Button(button_frame, text="🔄", command=self.refresh_directory_list,
                                bg='#555555', fg='white', activebackground='#777777',
                                font=('Helvetica', 10), width=3, padx=5, pady=8,
                                relief=tk.RAISED, bd=2, cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT)
        create_tooltip(refresh_btn, "Refresh directory list (F5)")
        self.add_button_effects(refresh_btn, '#555555', '#777777')

        self.update_button_states()

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

    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = tk.Frame(self.root, bg=self.theme['button'], height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                                     anchor=tk.W, bg=self.theme['button'], fg='white',
                                     font=('Helvetica', 9), padx=10, pady=4)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Copy path button
        self.copy_btn = tk.Button(self.status_frame, text="📋 Copy Path",
                                  command=self.copy_last_output_path,
                                  bg=self.theme['accent'], fg='white',
                                  font=('Helvetica', 8), bd=0, padx=10,
                                  state=tk.DISABLED)
        self.copy_btn.pack(side=tk.RIGHT, padx=5)
        create_tooltip(self.copy_btn, "Copy last output file path to clipboard")

    def setup_bindings(self):
        """Setup keyboard shortcuts and bindings"""
        self.root.bind('<F5>', lambda e: self.refresh_directory_list())
        self.root.bind('<Delete>', lambda e: self.remove_selected_directory())
        self.root.bind('<Return>', lambda e: self.process_selected_directory())
        self.root.bind('<Control-o>', lambda e: self.select_new_directory())
        self.root.bind('<Control-s>', lambda e: self.open_settings())

    def on_search(self, *args):
        """Handle search input changes"""
        self.update_directory_list()
        self.update_button_states()

    def on_sort_change(self, *args):
        """Handle sort option changes"""
        self.config.set('general', 'sort_mode', self.sort_var.get())
        self.update_directory_list()

    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            # Select the item under cursor
            index = self.directory_listbox.nearest(event.y)
            self.directory_listbox.selection_clear(0, tk.END)
            self.directory_listbox.selection_set(index)

            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.configure(bg=self.theme['frame_bg'], fg=self.theme['fg'])

            context_menu.add_command(label="Process Directory", command=self.process_selected_directory)
            context_menu.add_command(label="Open in Explorer", command=self.open_selected_directory)
            context_menu.add_separator()
            context_menu.add_command(label="Remove from List", command=self.remove_selected_directory)

            # Show menu
            context_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def refresh_directory_list(self):
        """Refresh the directory list from config"""
        self.config.cleanup_directories()
        self.valid_dirs = [d for d in self.config.config['previous_directories'] if os.path.exists(d)]
        self.update_directory_list()
        self.update_button_states()
        self.status_var.set("Directory list refreshed")

    def update_directory_list(self):
        """Update the directory listbox based on search and sort"""
        search_text = self.search_var.get().lower()
        sort_mode = self.sort_var.get()

        # Filter directories
        self.filtered_dirs = []
        for directory in self.valid_dirs:
            if search_text in directory.lower():
                self.filtered_dirs.append(directory)

        # Sort directories
        if sort_mode == 'alphabetical':
            self.filtered_dirs.sort()
        elif sort_mode == 'size':
            self.filtered_dirs.sort(key=lambda d: get_directory_size(d), reverse=True)
        elif sort_mode == 'date_modified':
            self.filtered_dirs.sort(key=lambda d: os.path.getmtime(d), reverse=True)
        # 'recent' is already in the correct order

        # Update listbox
        self.directory_listbox.delete(0, tk.END)
        for i, directory in enumerate(self.filtered_dirs):
            self.directory_listbox.insert(tk.END, directory)
            # Alternate row colors
            if i % 2 == 0:
                self.directory_listbox.itemconfigure(i, background='#f9f9f9' if not self.dark_mode else '#404040')

        # Update count
        total_dirs = len(self.valid_dirs)
        shown_dirs = len(self.filtered_dirs)
        self.count_var.set(f"Showing {shown_dirs} of {total_dirs} directories")

    def update_button_states(self):
        """Update button states based on selection and available directories"""
        has_dirs = len(self.filtered_dirs) > 0
        has_selection = bool(self.directory_listbox.curselection()) if has_dirs else False

        # Always enable new directory button
        self.new_btn.configure(state=tk.NORMAL)

        # Enable other buttons only if there are directories available
        for btn, requires_selection in [(self.use_btn, False), (self.open_btn, True), (self.remove_btn, True)]:
            if has_dirs and (not requires_selection or has_selection):
                btn.configure(state=tk.NORMAL)
                if btn == self.remove_btn:
                    btn.configure(bg='#d32f2f', activebackground='#f44336')
                else:
                    btn.configure(bg=self.theme['button'], activebackground=self.theme['accent'])
            else:
                btn.configure(state=tk.DISABLED, bg=self.theme['disabled_bg'],
                              activebackground=self.theme['disabled_bg'])

    def select_new_directory(self):
        """Select a new directory to process"""
        directory = filedialog.askdirectory(parent=self.root, title="Select Directory to Process")
        if directory:
            self.config.add_directory(directory)
            self.refresh_directory_list()
            self.process_directory(directory)

    def process_selected_directory(self):
        """Process the selected directory"""
        try:
            selection = self.directory_listbox.curselection()

            # If no selection but directories available, select the first one
            if not selection and self.filtered_dirs:
                self.directory_listbox.selection_set(0)
                selection = (0,)

            if not selection:
                self.status_var.set("No directories available to process")
                return

            directory = self.filtered_dirs[selection[0]]
            self.process_directory(directory)
        except (IndexError, KeyError):
            self.status_var.set("Please select a directory from the list")

    def open_selected_directory(self):
        """Open selected directory in file explorer"""
        try:
            selection = self.directory_listbox.curselection()
            if not selection:
                self.status_var.set("Please select a directory from the list")
                return

            directory = self.filtered_dirs[selection[0]]
            self.status_var.set(f"Opening: {os.path.basename(directory)}...")
            self.root.update()
            open_directory_in_explorer(directory)
            self.status_var.set(f"Opened: {os.path.basename(directory)}")
        except IndexError:
            self.status_var.set("Please select a directory from the list")

    def remove_selected_directory(self):
        """Remove selected directory from list"""
        try:
            selection = self.directory_listbox.curselection()
            if not selection:
                self.status_var.set("Please select a directory from the list")
                return

            directory = self.filtered_dirs[selection[0]]

            result = messagebox.askyesno("Confirm Removal",
                                         f"Remove this directory from the list?\n\n{directory}\n\n"
                                         "Note: This only removes it from the recent list, "
                                         "the actual directory remains unchanged.",
                                         parent=self.root)
            if result:
                if self.config.remove_directory(directory):
                    self.status_var.set(f"Removed: {os.path.basename(directory)}")
                    self.refresh_directory_list()
                else:
                    self.status_var.set("Failed to remove directory")
        except IndexError:
            self.status_var.set("Please select a directory from the list")

    def process_directory(self, directory):
        """Process a directory with progress tracking"""
        # Update config with current UI settings
        self.config.set('general', 'delete_previous_files', self.delete_var.get())
        self.config.set('general', 'file_format', self.format_var.get())

        # Show progress
        self.show_progress(True)

        # Disable buttons
        self.set_buttons_enabled(False)

        def update_progress(value):
            self.progress_var.set(value)
            self.progress_label.config(text=f"Processing... {int(value)}%")
            self.root.update()

        def run_extraction():
            try:
                self.status_var.set(f"Processing: {os.path.basename(directory)}...")
                self.root.update()

                success, message = self.extractor.extract_structure(directory, update_progress)

                # Update UI from main thread
                self.root.after(0, lambda: self.extraction_complete(success, message, directory))

            except Exception as e:
                self.root.after(0, lambda: self.extraction_complete(False, f"Error: {str(e)}", directory))

        # Run extraction in background thread
        thread = threading.Thread(target=run_extraction)
        thread.daemon = True
        thread.start()

    def extraction_complete(self, success, message, directory):
        """Handle extraction completion"""
        # Re-enable buttons
        self.set_buttons_enabled(True)

        # Hide progress
        self.show_progress(False)

        if success:
            self.status_var.set(message)

            # Store output path for copying
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_format = self.config.get('general', 'file_format')
            prefix = self.config.get('general', 'output_file_prefix')
            output_path = os.path.join(directory, f"{prefix}_{timestamp}.{file_format}")
            self.last_output_path = output_path
            self.copy_btn.config(state=tk.NORMAL)

            # Refresh list to update the directory order
            self.refresh_directory_list()
        else:
            self.status_var.set(f"Failed: {message}")
            messagebox.showerror("Error", message, parent=self.root)

    def show_progress(self, show):
        """Show or hide progress bar"""
        if show:
            self.progress_frame.pack(fill=tk.X, pady=(0, 15))
            self.progress_var.set(0)
        else:
            self.progress_frame.pack_forget()

    def set_buttons_enabled(self, enabled):
        """Enable or disable all buttons"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in [self.new_btn, self.use_btn, self.open_btn, self.remove_btn]:
            btn.configure(state=state)

    def copy_last_output_path(self):
        """Copy last output file path to clipboard"""
        if hasattr(self, 'last_output_path') and self.last_output_path:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_output_path)
            self.status_var.set("Output path copied to clipboard!")
            self.root.after(2000, lambda: self.status_var.set("Ready"))

    def open_settings(self):
        """Open settings window"""

        def on_theme_change():
            # This would be called if theme changes, but we'll just show a message
            # since the main window theme change requires restart
            pass

        SettingsWindow(self.root, self.config, on_theme_change)

    def run(self):
        """Start the GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()