import json
import os
from datetime import datetime


class ConfigManager:
    def __init__(self):
        self.user_home = os.path.expanduser("~")
        self.config_dir = os.path.join(self.user_home, ".file_extractor")
        self.config_file = os.path.join(self.config_dir, "config.json")

        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.config = self.load_config()

    def get_default_config(self):
        """Return default configuration"""
        return {
            "general": {
                "output_file_prefix": "project_structure",
                "delete_previous_files": True,
                "file_format": "md",
                "max_file_size_mb": 1,
                "dark_mode": False,
                "sort_mode": "recent"  # recent, alphabetical, size, date_modified
            },
            "folders": {
                "ignored": [".venv", ".idea", "build", "dist", "__pycache__", "node_modules", ".git"],
                "excluded": []
            },
            "extensions": {
                "ignored": ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe', '.obj', '.o', '.a', '.lib'],
                "excluded": []
            },
            "files": {
                "ignored": [],
                "excluded": []
            },
            "previous_directories": []
        }

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge with defaults to ensure all keys exist
                default_config = self.get_default_config()
                self.merge_configs(default_config, loaded_config)
                return default_config
            else:
                return self.get_default_config()
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def merge_configs(self, default, loaded):
        """Recursively merge loaded config with default config"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self.merge_configs(default[key], value)
                else:
                    default[key] = value

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except (PermissionError, OSError) as e:
            print(f"Error saving config: {e}")

    def get(self, section, key=None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)

    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def add_directory(self, directory):
        """Add directory to recent list"""
        dirs = self.config["previous_directories"]
        if directory in dirs:
            dirs.remove(directory)
        dirs.insert(0, directory)
        # Keep only last 50 directories
        self.config["previous_directories"] = dirs[:50]
        self.save_config()

    def remove_directory(self, directory):
        """Remove directory from recent list"""
        dirs = self.config["previous_directories"]
        if directory in dirs:
            dirs.remove(directory)
            self.save_config()
            return True
        return False

    def cleanup_directories(self):
        """Remove non-existent directories"""
        valid_dirs = [d for d in self.config["previous_directories"] if os.path.exists(d)]
        if len(valid_dirs) != len(self.config["previous_directories"]):
            self.config["previous_directories"] = valid_dirs
            self.save_config()

    def get_text_extensions(self):
        """Get list of supported text file extensions"""
        return ['.py', '.html', '.js', '.css', '.txt', '.md', '.json', '.xml', '.yml', '.yaml',
                '.ini', '.cfg', '.conf', '.sh', '.bat', '.ps1', '.sql', '.java', '.c', '.cpp',
                '.h', '.hpp', '.cs', '.rb', '.php', '.go', '.ts', '.jsx', '.tsx', '.vue',
                '.dart', '.rs', '.swift', '.r', '.m', '.mm', '.kt', '.gradle', '.cmake',
                '.makefile', '.dockerfile', '.env', '.gitignore', '.editorconfig', '.toml']