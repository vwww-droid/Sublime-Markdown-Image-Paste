import sublime
import sublime_plugin
import os
import time
import uuid
import shutil
import tempfile
import threading
import platform

# Plugin loading debug information
def plugin_loaded():
    print("MarkdownImagePaste plugin loaded!")
    sublime.status_message("MarkdownImagePaste plugin loaded")

def plugin_unloaded():
    print("MarkdownImagePaste plugin unloaded")

class PasteImageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Process image pasting in background thread to avoid blocking UI
        threading.Thread(target=self.paste_image_async).start()
    
    def paste_image_async(self):
        try:
            # Check if current file is saved
            file_path = self.view.file_name()
            if not file_path:
                sublime.error_message("Please save the current file first!")
                return
            
            # Try to get image from clipboard
            temp_image_path = self.get_clipboard_image()
            if not temp_image_path:
                return
            
            # Get plugin settings
            settings = sublime.load_settings("MarkdownImagePaste.sublime-settings")
            image_folder = settings.get("image_folder", "images")
            image_prefix = settings.get("image_prefix", "image")
            include_timestamp = settings.get("include_timestamp", True)
            include_unique_id = settings.get("include_unique_id", True)
            default_alt_text = settings.get("default_alt_text", "Image")
            link_path_type = settings.get("link_path_type", "relative")
            
            # Parse image storage path
            images_dir = self.resolve_image_path(image_folder, file_path)
            
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            # Generate filename
            filename_parts = [image_prefix]
            if include_timestamp:
                filename_parts.append(str(int(time.time())))
            if include_unique_id:
                filename_parts.append(str(uuid.uuid4())[:8])
            
            image_filename = "_".join(filename_parts) + ".png"
            final_image_path = os.path.join(images_dir, image_filename)
            
            # Move image to target location
            shutil.move(temp_image_path, final_image_path)
            
            # Generate Markdown link
            link_path = self.generate_link_path(final_image_path, file_path, image_folder, link_path_type)
            markdown_link = "![{}]({})".format(default_alt_text, link_path)
            
            # Insert text in main thread
            sublime.set_timeout(lambda: self.insert_markdown_link(markdown_link), 0)
            
        except Exception as e:
            sublime.error_message("Failed to paste image: {}".format(str(e)))
            print("PasteImageCommand error: {}".format(e))
    
    def get_clipboard_image(self):
        """Get clipboard image (macOS only)"""
        try:
            system = platform.system()
            if system != "Darwin":
                sublime.error_message("This plugin only supports macOS")
                return None
                
            temp_dir = tempfile.mkdtemp()
            temp_image_path = os.path.join(temp_dir, "clipboard_image.png")
            
            return self.get_clipboard_image_macos(temp_image_path)
                
        except Exception as e:
            sublime.error_message("Failed to get clipboard image: {}".format(str(e)))
            return None
    
    def get_clipboard_image_macos(self, temp_path):
        """Get clipboard image on macOS"""
        try:
            import subprocess
            
            # Use pngpaste tool (compatible with Python 3.3)
            try:
                # Use subprocess.call instead of subprocess.run, and suppress output
                with open(os.devnull, 'w') as devnull:
                    result = subprocess.call(['pngpaste', temp_path], 
                                           stderr=devnull, stdout=devnull)
                
                if result == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path
                else:
                    # Clean up empty file if created
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    sublime.error_message("No image in clipboard!\nPlease copy an image first.")
                    return None
            except OSError:  # FileNotFoundError is subclass of OSError in Python 3.3
                sublime.error_message("macOS requires pngpaste tool:\nbrew install pngpaste")
                return None
                
        except Exception as e:
            sublime.error_message("macOS clipboard processing failed: {}".format(str(e)))
            return None
    
    def resolve_image_path(self, image_folder, markdown_file_path):
        """Parse image storage path, supporting relative paths, absolute paths, and environment variables"""
        # Expand environment variables
        expanded_path = os.path.expandvars(image_folder)
        expanded_path = os.path.expanduser(expanded_path)
        
        # Check if it's an absolute path
        if os.path.isabs(expanded_path):
            return expanded_path
        else:
            # Relative path: relative to current markdown file
            file_dir = os.path.dirname(markdown_file_path)
            return os.path.join(file_dir, expanded_path)
    
    def generate_link_path(self, image_file_path, markdown_file_path, original_image_folder, link_path_type):
        """Generate path used in Markdown links"""
        image_filename = os.path.basename(image_file_path)
        
        if link_path_type == "absolute":
            # Use absolute path
            return image_file_path
        elif link_path_type == "same_as_storage":
            # Keep consistent with storage path
            expanded_folder = os.path.expandvars(original_image_folder)
            expanded_folder = os.path.expanduser(expanded_folder)
            if os.path.isabs(expanded_folder):
                return os.path.join(expanded_folder, image_filename)
            else:
                return "{}/{}".format(original_image_folder, image_filename)
        else:
            # Default to relative path
            markdown_dir = os.path.dirname(markdown_file_path)
            image_dir = os.path.dirname(image_file_path)
            
            try:
                # Calculate relative path
                rel_path = os.path.relpath(image_file_path, markdown_dir)
                return rel_path.replace(os.sep, '/')  # Use forward slashes consistently
            except ValueError:
                # If unable to calculate relative path (e.g., different drives), use absolute path
                return image_file_path
    
    def insert_markdown_link(self, markdown_link):
        # Insert text in main thread
        def insert_text():
            # Create a temporary text command to insert text
            self.view.run_command('insert_markdown_image_text', {'text': markdown_link})
            sublime.status_message("Image pasted successfully!")
        
        insert_text()

class InsertMarkdownImageTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        # Get current cursor position and insert text
        cursor_pos = self.view.sel()[0].begin()
        self.view.insert(edit, cursor_pos, text)

class PasteImageFromFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get supported file formats
        settings = sublime.load_settings("MarkdownImagePaste.sublime-settings")
        supported_formats = settings.get("supported_formats", ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp"])
        
        # Use input panel for user to enter file path
        window = self.view.window()
        if window:
            window.show_input_panel(
                "Enter image file path:",
                "",
                self.on_file_selected,
                None,
                None
            )
    
    def on_file_selected(self, selected_file):
        if not selected_file:
            return
        
        try:
            # Check if current file is saved
            current_file = self.view.file_name()
            if not current_file:
                sublime.error_message("Please save the current file first!")
                return
            
            # Check if selected file exists
            if not os.path.exists(selected_file):
                sublime.error_message("Selected file does not exist!")
                return
            
            # Get plugin settings
            settings = sublime.load_settings("MarkdownImagePaste.sublime-settings")
            image_folder = settings.get("image_folder", "images")
            include_timestamp = settings.get("include_timestamp", True)
            default_alt_text = settings.get("default_alt_text", "Image")
            link_path_type = settings.get("link_path_type", "relative")
            supported_formats = settings.get("supported_formats", ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp"])
            
            # Parse image storage path
            images_dir = self._resolve_image_path(image_folder, current_file)
            
            # Create image directory
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            # Generate new filename
            filename = os.path.basename(selected_file)
            name, ext = os.path.splitext(filename)
            
            if include_timestamp:
                timestamp = int(time.time())
                new_filename = "{}_{}{}" .format(name, timestamp, ext)
            else:
                new_filename = filename
                
            new_path = os.path.join(images_dir, new_filename)
            
            # If file already exists, add number suffix
            counter = 1
            original_new_path = new_path
            while os.path.exists(new_path):
                name_part, ext_part = os.path.splitext(original_new_path)
                new_path = "{}_{}{}" .format(name_part, counter, ext_part)
                counter += 1
                new_filename = os.path.basename(new_path)
            
            # Copy file
            shutil.copy2(selected_file, new_path)
            
            # Generate Markdown link
            link_path = self._generate_link_path(new_path, current_file, image_folder, link_path_type)
            markdown_link = "![{}]({})".format(default_alt_text, link_path)
            
            # Insert link
            self.view.run_command('insert_markdown_image_text', {'text': markdown_link})
            sublime.status_message("Image file inserted successfully!")
            
        except Exception as e:
            sublime.error_message("Failed to insert image file: {}".format(str(e)))
            print("PasteImageFromFileCommand error: {}".format(e))
    
    def _resolve_image_path(self, image_folder, markdown_file_path):
        """Parse image storage path, supporting relative paths, absolute paths, and environment variables"""
        # Expand environment variables
        expanded_path = os.path.expandvars(image_folder)
        expanded_path = os.path.expanduser(expanded_path)
        
        # Check if it's an absolute path
        if os.path.isabs(expanded_path):
            return expanded_path
        else:
            # Relative path: relative to current markdown file
            file_dir = os.path.dirname(markdown_file_path)
            return os.path.join(file_dir, expanded_path)
    
    def _generate_link_path(self, image_file_path, markdown_file_path, original_image_folder, link_path_type):
        """Generate path used in Markdown links"""
        image_filename = os.path.basename(image_file_path)
        
        if link_path_type == "absolute":
            # Use absolute path
            return image_file_path
        elif link_path_type == "same_as_storage":
            # Keep consistent with storage path
            expanded_folder = os.path.expandvars(original_image_folder)
            expanded_folder = os.path.expanduser(expanded_folder)
            if os.path.isabs(expanded_folder):
                return os.path.join(expanded_folder, image_filename)
            else:
                return "{}/{}".format(original_image_folder, image_filename)
        else:
            # Default to relative path
            markdown_dir = os.path.dirname(markdown_file_path)
            image_dir = os.path.dirname(image_file_path)
            
            try:
                # Calculate relative path
                rel_path = os.path.relpath(image_file_path, markdown_dir)
                return rel_path.replace(os.sep, '/')  # Use forward slashes consistently
            except ValueError:
                # If unable to calculate relative path (e.g., different drives), use absolute path
                return image_file_path

class MarkdownImagePasteListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        # Only enable shortcuts in Markdown files
        if key == "markdown_image_paste_enabled":
            syntax = view.settings().get('syntax', '')
            is_markdown = 'markdown' in syntax.lower() or view.file_name() and view.file_name().endswith('.md')
            return is_markdown
        return None