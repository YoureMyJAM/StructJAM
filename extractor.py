import os
import json
import yaml
from datetime import datetime
from config import ConfigManager


class FileStructureExtractor:
    def __init__(self, config_manager):
        self.config = config_manager

    def should_ignore_path(self, path):
        """Check if path should be ignored based on folder rules"""
        parts = path.split(os.sep)
        ignored_folders = self.config.get('folders', 'ignored') or []
        excluded_folders = self.config.get('folders', 'excluded') or []

        return any(folder in parts for folder in ignored_folders + excluded_folders)

    def should_exclude_file(self, filename):
        """Check if file should be completely excluded"""
        _, ext = os.path.splitext(filename)

        excluded_extensions = self.config.get('extensions', 'excluded') or []
        excluded_files = self.config.get('files', 'excluded') or []

        # Check extension exclusion
        if ext.lower() in excluded_extensions:
            return True

        # Check specific file exclusion
        if filename in excluded_files:
            return True

        # Check wildcard patterns
        for pattern in excluded_files:
            if '*' in pattern:
                if pattern.startswith('*') and filename.endswith(pattern[1:]):
                    return True
                elif pattern.endswith('*') and filename.startswith(pattern[:-1]):
                    return True
                elif '*' in pattern.replace(pattern.split('*')[0], '').replace(pattern.split('*')[-1], ''):
                    # Complex wildcard matching - simplified
                    parts = pattern.split('*')
                    if all(part in filename for part in parts if part):
                        return True

        return False

    def should_ignore_file_content(self, filename):
        """Check if file content should be ignored but file shown in structure"""
        _, ext = os.path.splitext(filename)

        ignored_extensions = self.config.get('extensions', 'ignored') or []
        ignored_files = self.config.get('files', 'ignored') or []

        # Check extension
        if ext.lower() in ignored_extensions:
            return True

        # Check specific files and patterns
        if filename in ignored_files:
            return True

        for pattern in ignored_files:
            if '*' in pattern:
                if pattern.startswith('*') and filename.endswith(pattern[1:]):
                    return True
                elif pattern.endswith('*') and filename.startswith(pattern[:-1]):
                    return True

        return False

    def is_output_file(self, filename):
        """Check if file is a generated output file"""
        prefix = self.config.get('general', 'output_file_prefix') or 'project_structure'
        return (filename.startswith(prefix) and
                (filename.endswith('.txt') or filename.endswith('.md') or
                 filename.endswith('.json') or filename.endswith('.yaml')))

    def delete_previous_output_files(self, directory):
        """Delete previous output files if option is enabled"""
        deleted_files = []
        if not self.config.get('general', 'delete_previous_files'):
            return deleted_files

        try:
            for fname in os.listdir(directory):
                if self.is_output_file(fname):
                    fpath = os.path.join(directory, fname)
                    try:
                        os.remove(fpath)
                        deleted_files.append(fname)
                    except Exception as e:
                        print(f"Error deleting {fpath}: {e}")
        except Exception as e:
            print(f"Error scanning directory: {e}")

        return deleted_files

    def count_files_and_folders(self, directory):
        """Count total files and folders for progress tracking"""
        total_files = 0
        total_folders = 0

        ignored_folders = self.config.get('folders', 'ignored') or []

        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_folders]

            if self.should_ignore_path(root):
                continue

            total_folders += 1
            for file in files:
                if not self.is_output_file(file) and not self.should_exclude_file(file):
                    total_files += 1

        return total_files, total_folders

    def write_structure_header(self, f, directory, total_files, total_folders, file_format):
        """Write the header for the structure file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if file_format == 'md':
            f.write(f"# File Structure for: {directory}\n\n")
            f.write(f"**Generated on:** {timestamp}\n\n")
            f.write(f"**Total Files:** {total_files} | **Total Folders:** {total_folders}\n\n")
            f.write("---\n\n## DIRECTORY STRUCTURE\n\n```\n")
        elif file_format == 'json':
            # JSON header will be written as metadata in the JSON structure
            pass
        elif file_format == 'yaml':
            f.write(f"# File Structure for: {directory}\n")
            f.write(f"# Generated on: {timestamp}\n")
            f.write(f"# Total Files: {total_files} | Total Folders: {total_folders}\n\n")
        else:  # txt
            f.write(f"File Structure for: {directory}\n")
            f.write(f"Generated on: {timestamp}\n")
            f.write(f"Total Files: {total_files} | Total Folders: {total_folders}\n")
            f.write('=' * 80 + "\n\nDIRECTORY STRUCTURE:\n" + '=' * 80 + "\n")

    def write_directory_structure(self, f, directory, file_format):
        """Write the directory structure to file"""
        ignored_folders = self.config.get('folders', 'ignored') or []

        if file_format in ['json', 'yaml']:
            structure_data = self.build_structure_data(directory)
            if file_format == 'json':
                json.dump(structure_data, f, indent=2, ensure_ascii=False)
            else:  # yaml
                yaml.dump(structure_data, f, default_flow_style=False, allow_unicode=True)
            return

        # Text-based formats
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignored_folders]

            if self.should_ignore_path(root):
                continue

            rel = os.path.relpath(root, directory)
            level = 0 if rel == "." else rel.count(os.sep)
            indent = "│   " * level
            name = os.path.basename(directory) if rel == "." else os.path.basename(root)
            f.write(f"{indent}├── {name}/\n")

            sub_indent = "│   " * (level + 1)
            for file in sorted(files):
                if self.is_output_file(file) or self.should_exclude_file(file):
                    continue
                f.write(f"{sub_indent}├── {file}\n")

    def build_structure_data(self, directory):
        """Build structure data for JSON/YAML export"""
        ignored_folders = self.config.get('folders', 'ignored') or []

        def build_tree(path, name):
            tree = {"name": name, "type": "directory", "children": []}

            try:
                items = os.listdir(path)
                # Sort items: directories first, then files
                dirs = [item for item in items if os.path.isdir(os.path.join(path, item))
                        and item not in ignored_folders]
                files = [item for item in items if os.path.isfile(os.path.join(path, item))
                         and not self.is_output_file(item) and not self.should_exclude_file(item)]

                for dirname in sorted(dirs):
                    dir_path = os.path.join(path, dirname)
                    if not self.should_ignore_path(dir_path):
                        tree["children"].append(build_tree(dir_path, dirname))

                for filename in sorted(files):
                    file_info = {"name": filename, "type": "file"}
                    file_path = os.path.join(path, filename)
                    try:
                        file_info["size"] = os.path.getsize(file_path)
                    except OSError:
                        file_info["size"] = 0
                    tree["children"].append(file_info)

            except (OSError, PermissionError):
                pass

            return tree

        return {
            "metadata": {
                "directory": directory,
                "generated_on": datetime.now().isoformat(),
                "total_files": self.count_files_and_folders(directory)[0],
                "total_folders": self.count_files_and_folders(directory)[1]
            },
            "structure": build_tree(directory, os.path.basename(directory))
        }

    def write_file_contents(self, f, directory, file_format, progress_callback=None):
        """Write file contents to the output file"""
        if file_format in ['json', 'yaml']:
            return  # File contents not included in structured formats

        ignored_folders = self.config.get('folders', 'ignored') or []
        max_file_size = self.config.get('general', 'max_file_size_mb') or 1
        text_extensions = self.config.get_text_extensions()

        # Write section header
        if file_format == 'md':
            f.write("```\n\n## FILE CONTENTS\n\n")
        else:  # txt
            f.write(f"\nFILE CONTENTS:\n{'=' * 80}\n\n")

        processed_items = 0
        total_files = self.count_files_and_folders(directory)[0]

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignored_folders]

            if self.should_ignore_path(root):
                continue

            for file in sorted(files):
                if self.is_output_file(file) or self.should_exclude_file(file):
                    continue

                processed_items += 1
                if progress_callback and total_files > 0:
                    progress_callback(50 + (processed_items / total_files * 50))

                path = os.path.join(root, file)
                rel = os.path.relpath(path, directory)

                try:
                    _, file_ext = os.path.splitext(file)

                    # Check if file content should be ignored
                    if self.should_ignore_file_content(file):
                        msg = "Content ignored (configured in settings)"
                        if file_format == 'md':
                            f.write(f"### FILE: {rel}\n\n{msg}\n\n")
                        else:
                            f.write(f"FILE: {rel}\n{msg}\n\n")
                        continue

                    # Check file size
                    size = os.path.getsize(path)
                    if size > max_file_size * 1024 * 1024:
                        msg = f"Content too large (>{max_file_size}MB)"
                        if file_format == 'md':
                            f.write(f"### FILE: {rel}\n\n{msg}\n\n")
                        else:
                            f.write(f"FILE: {rel}\n{msg}\n\n")
                        continue

                    # Check if it's a supported text file
                    if file_ext.lower() not in text_extensions:
                        continue

                    # Read file content
                    try:
                        with open(path, "r", encoding="utf-8") as src:
                            content = src.read()
                    except UnicodeDecodeError:
                        try:
                            with open(path, "r", encoding="latin-1") as src:
                                content = src.read()
                        except:
                            content = "Error: Unable to decode file content"

                    # Write content
                    if file_format == 'md':
                        lang = file_ext.lstrip('.') or 'text'
                        f.write(f"### FILE: {rel}\n\n```{lang}\n{content}\n```\n\n---\n\n")
                    else:
                        f.write(f"FILE: {rel}\n{'-' * 80}\n{content}\n\n{'=' * 80}\n\n")

                except Exception as e:
                    msg = f"Error reading file: {str(e)}"
                    if file_format == 'md':
                        f.write(f"### FILE: {rel}\n\n{msg}\n\n")
                    else:
                        f.write(f"FILE: {rel}\n{msg}\n\n")

    def extract_structure(self, directory, progress_callback=None):
        """Main method to extract file structure"""
        if not directory or not os.path.exists(directory):
            return False, f"Directory does not exist: {directory}"

        try:
            # Clean up previous files
            deleted_files = self.delete_previous_output_files(directory)

            # Get file format
            file_format = self.config.get('general', 'file_format') or 'md'

            # Count items for progress
            total_files, total_folders = self.count_files_and_folders(directory)

            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.config.get('general', 'output_file_prefix') or 'project_structure'
            output_file = os.path.join(directory, f"{prefix}_{timestamp}.{file_format}")

            # Write the structure file
            with open(output_file, "w", encoding="utf-8") as f:
                # Write header
                self.write_structure_header(f, directory, total_files, total_folders, file_format)

                # Update progress
                if progress_callback:
                    progress_callback(25)

                # Write directory structure
                self.write_directory_structure(f, directory, file_format)

                # Update progress
                if progress_callback:
                    progress_callback(50)

                # Write file contents (for text formats only)
                if file_format in ['txt', 'md']:
                    self.write_file_contents(f, directory, file_format, progress_callback)

            return True, f"Successfully created: {os.path.basename(output_file)}"

        except Exception as e:
            return False, f"Error: {str(e)}"