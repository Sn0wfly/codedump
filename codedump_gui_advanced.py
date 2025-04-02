import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import datetime
from codedump.codedump import concatenate_files, should_skip, get_file_info
import pyperclip
from PIL import ImageTk, Image

class CodeDumpApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CodeDump GUI")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Variables
        self.selected_directory = tk.StringVar(value="")
        self.dump_content = ""
        self.status_var = tk.StringVar(value="Ready")
        self.selected_files = []
        
        # Load icons
        self.load_icons()
        
        # Create UI components
        self.create_main_layout()
        
        # Configure row and column weights for proper resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Main frame expands
    
    def load_icons(self):
        """Load and resize icons for folders and files"""
        icon_size = (16, 16)
        self.use_icons = False
        
        # Create icons directory if it doesn't exist
        if not os.path.exists("icons"):
            os.makedirs("icons")
            self.generate_default_icons("icons")
        
        try:
            # Try to load icons from icons directory
            folder_img_orig = Image.open("icons/folder.png")
            file_img_orig = Image.open("icons/file.png")
            
            # Resize icons
            folder_img_resized = folder_img_orig.resize(icon_size, Image.Resampling.LANCZOS)
            file_img_resized = file_img_orig.resize(icon_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            self.folder_icon = ImageTk.PhotoImage(folder_img_resized)
            self.file_icon = ImageTk.PhotoImage(file_img_resized)
            
            self.use_icons = True
        except FileNotFoundError:
            print("Warning: Icon files not found. Using default icons.")
            self.folder_icon = None
            self.file_icon = None
            
            # Try to create simple default icons
            try:
                # Create simple icons
                folder_img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
                for i in range(icon_size[0]):
                    for j in range(icon_size[1]):
                        if (i == 0 or i == icon_size[0]-1 or j == 0 or j == icon_size[1]-1 or 
                            (i == 5 and j <= 10) or (j == 10 and i <= 5)):
                            folder_img.putpixel((i, j), (0, 0, 128, 255))  # Blue
                
                file_img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
                for i in range(icon_size[0]):
                    for j in range(icon_size[1]):
                        if (i == 0 or i == icon_size[0]-1 or j == 0 or j == icon_size[1]-1 or 
                            (i == 4 and 2 <= j <= 13) or (i == 8 and 2 <= j <= 13) or (i == 12 and 2 <= j <= 13)):
                            file_img.putpixel((i, j), (0, 100, 0, 255))  # Dark green
                
                self.folder_icon = ImageTk.PhotoImage(folder_img)
                self.file_icon = ImageTk.PhotoImage(file_img)
                self.use_icons = True
            except Exception as e:
                print(f"Warning: Failed to create default icons. {e}")
                self.folder_icon = None
                self.file_icon = None
    
    def generate_default_icons(self, directory):
        """Generate default icons and save them to the specified directory"""
        try:
            # Create folder icon (blue folder)
            folder_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            for i in range(32):
                for j in range(32):
                    # Draw folder outline
                    if (i == 0 or i == 31 or j == 0 or j == 31 or 
                        (2 <= i <= 30 and (j == 5 or j == 25)) or
                        (2 <= j <= 25 and (i == 2 or i == 30))):
                        folder_img.putpixel((i, j), (30, 50, 180, 255))  # Blue outline
                    # Fill folder
                    elif 3 <= i <= 29 and 6 <= j <= 24:
                        folder_img.putpixel((i, j), (100, 150, 255, 255))  # Light blue fill
            
            # Create file icon (green document)
            file_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            for i in range(32):
                for j in range(32):
                    # Draw file outline
                    if (i == 0 or i == 31 or j == 0 or j == 31 or
                        (3 <= j <= 29 and (i == 3 or i == 29))):
                        file_img.putpixel((i, j), (0, 100, 0, 255))  # Green outline
                    # File content lines
                    elif 6 <= i <= 26 and (j == 8 or j == 12 or j == 16 or j == 20 or j == 24):
                        file_img.putpixel((i, j), (100, 180, 100, 255))  # Light green lines
                    # Fill file
                    elif 4 <= i <= 28 and 4 <= j <= 28:
                        file_img.putpixel((i, j), (240, 255, 240, 255))  # Very light green fill
            
            # Save icons
            folder_img.save(os.path.join(directory, "folder.png"))
            file_img.save(os.path.join(directory, "file.png"))
            print(f"Default icons created in {directory}")
        except Exception as e:
            print(f"Error creating default icons: {e}")
    
    def create_main_layout(self):
        """Create the main UI layout"""
        # Top frame with directory selection
        self.create_top_frame()
        
        # Main frame with panels
        self.create_main_frame()
        
        # Bottom frame with buttons
        self.create_bottom_frame()
        
        # Status bar
        self.create_status_bar()
    
    def create_top_frame(self):
        """Create the top frame with directory selection"""
        top_frame = ttk.Frame(self, padding="10")
        top_frame.grid(row=0, column=0, sticky='ew')
        
        # Directory selection button
        select_dir_button = ttk.Button(
            top_frame, 
            text="Select Directory",
            command=self.select_directory
        )
        select_dir_button.pack(side=tk.LEFT, padx=5)
        
        # Directory path label
        dir_label = ttk.Label(
            top_frame,
            textvariable=self.selected_directory,
            background="white",
            relief="sunken",
            padding=5
        )
        dir_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_main_frame(self):
        """Create the main frame with file tree and content panels"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=1, column=0, sticky='nsew')
        
        # Create a horizontal PanedWindow to divide the main frame
        h_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        h_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for file tree
        tree_frame = ttk.Frame(h_paned)
        h_paned.add(tree_frame, weight=1)
        
        # Create Treeview for file structure
        self.create_file_tree(tree_frame)
        
        # Right panel
        right_panel = ttk.Frame(h_paned)
        h_paned.add(right_panel, weight=2)
        
        # Create a vertical PanedWindow for the right panel
        v_paned = ttk.PanedWindow(right_panel, orient=tk.VERTICAL)
        v_paned.pack(fill=tk.BOTH, expand=True)
        
        # Upper right panel for file list
        file_list_frame = ttk.LabelFrame(v_paned, text="Selected Files")
        v_paned.add(file_list_frame, weight=1)
        
        # Create selected files list
        self.create_file_list(file_list_frame)
        
        # Lower right panel for preview
        preview_frame = ttk.LabelFrame(v_paned, text="Preview")
        v_paned.add(preview_frame, weight=3)
        
        # Create preview text area
        self.create_preview_area(preview_frame)
    
    def create_file_tree(self, parent):
        """Create the file tree view"""
        # Create Treeview
        self.tree = ttk.Treeview(parent)
        self.tree.heading('#0', text='Files and Directories', anchor='w')
        
        # Configure tags for different file types
        self.tree.tag_configure('folder', foreground='navy')
        self.tree.tag_configure('file', foreground='darkgreen')
        self.tree.tag_configure('checked', foreground='black')
        self.tree.tag_configure('unchecked', foreground='gray')
        
        # Bind events
        self.tree.bind("<Button-1>", self.toggle_check)
        
        # Scrollbars
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configure weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def create_file_list(self, parent):
        """Create the selected files list"""
        # Frame for listbox and buttons
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox for selected files
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        
        # Scrollbar
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Button to edit selected section
        edit_button = ttk.Button(
            list_frame,
            text="Edit Selected File",
            command=self.edit_selected_file
        )
        
        # Layout
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        edit_button.pack(side=tk.BOTTOM, pady=5)
    
    def create_preview_area(self, parent):
        """Create the preview text area"""
        # Text widget for preview
        self.preview_text = tk.Text(parent, wrap=tk.NONE, state='disabled')
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.preview_text.yview)
        x_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.preview_text.xview)
        self.preview_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Layout
        self.preview_text.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def create_bottom_frame(self):
        """Create the bottom frame with action buttons"""
        bottom_frame = ttk.Frame(self, padding="10")
        bottom_frame.grid(row=2, column=0, sticky='ew')
        
        # Generate button
        generate_button = ttk.Button(
            bottom_frame,
            text="Generate Dump",
            command=self.generate_dump
        )
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        copy_button = ttk.Button(
            bottom_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard
        )
        copy_button.pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Create the status bar"""
        status_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=3, column=0, sticky='ew')
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=2
        )
        status_label.pack(fill=tk.X)
    
    def select_directory(self):
        """Select a directory and update the file tree"""
        self.status_var.set("Selecting directory...")
        self.update_idletasks()
        
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
            self.status_var.set("Loading directory...")
            self.update_idletasks()
            
            self.populate_treeview(directory)
            self.status_var.set(f"Directory loaded: {os.path.basename(directory)}")
        else:
            self.status_var.set("Ready")
    
    def populate_treeview(self, path):
        """Fill the treeview with directory structure"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Reset selected files
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        
        # Function to add nodes recursively
        def add_node(parent, path, dirname):
            # Skip directories that should be skipped
            if os.path.isdir(path) and should_skip(path):
                return
            
            # Create node ID and insert into tree
            node_id = path
            
            # Determine icon to use
            icon = self.folder_icon if self.use_icons else ''
            
            # Insert folder node
            node = self.tree.insert(
                parent, 'end', iid=node_id, text=f"☐ {dirname}",
                tags=('unchecked', 'folder'), open=False,
                image=icon
            )
            
            try:
                # Process directory contents
                for item in sorted(os.listdir(path)):
                    item_path = os.path.join(path, item)
                    
                    # Skip files that should be skipped
                    if should_skip(item_path):
                        continue
                    
                    # Recursively add directories
                    if os.path.isdir(item_path):
                        add_node(node, item_path, item)
                    else:
                        # Add file as leaf node
                        file_icon = self.file_icon if self.use_icons else ''
                        self.tree.insert(
                            node, 'end', iid=item_path, text=f"☐ {item}",
                            tags=('unchecked', 'file'),
                            image=file_icon
                        )
            except PermissionError:
                # Handle permission errors
                error_id = f"{node_id}_error_perm"
                self.tree.insert(node, 'end', iid=error_id, text="Access Denied (Permission Error)")
            except Exception as e:
                # Handle other errors
                error_id = f"{node_id}_error_general"
                self.tree.insert(node, 'end', iid=error_id, text=f"Error: {str(e)}")
        
        # Add root directory
        root_dir = os.path.basename(path)
        if not root_dir:  # If it's the root directory
            root_dir = path
        add_node('', path, root_dir)
    
    def toggle_check(self, event):
        """Handle clicking on tree items to toggle checkboxes"""
        # Identify clicked region and item
        region = self.tree.identify_region(event.x, event.y)
        item_id = self.tree.identify_row(event.y)
        
        # Only process valid clicks
        if region in ('tree', 'cell', 'text', 'image') and item_id:
            tags = list(self.tree.item(item_id, 'tags'))
            current_text = self.tree.item(item_id, 'text')
            item_name = current_text[2:]  # Remove checkbox character
            
            # Toggle check state
            if 'unchecked' in tags:
                # Change to checked
                tags.remove('unchecked')
                tags.append('checked')
                new_text = f"☑ {item_name}"
            else:
                # Change to unchecked
                if 'checked' in tags:
                    tags.remove('checked')
                tags.append('unchecked')
                new_text = f"☐ {item_name}"
            
            # Update item
            self.tree.item(item_id, text=new_text, tags=tags)
            
            # Apply to children if it's a folder
            if 'folder' in tags:
                self.toggle_children(item_id, 'checked' in tags)
                
            # Update selected files list
            self.update_selected_files()
    
    def toggle_children(self, parent_id, checked):
        """Recursively toggle check state of all children"""
        for child_id in self.tree.get_children(parent_id):
            child_tags = list(self.tree.item(child_id, 'tags'))
            current_text = self.tree.item(child_id, 'text')
            item_name = current_text[2:]  # Remove checkbox character
            
            # Update tags
            if 'checked' in child_tags and not checked:
                child_tags.remove('checked')
                child_tags.append('unchecked')
            elif 'unchecked' in child_tags and checked:
                child_tags.remove('unchecked')
                child_tags.append('checked')
            
            # Update text with appropriate symbol
            new_text = f"☑ {item_name}" if checked else f"☐ {item_name}"
            self.tree.item(child_id, text=new_text, tags=child_tags)
            
            # Recursively process children
            if self.tree.get_children(child_id):
                self.toggle_children(child_id, checked)
    
    def update_selected_files(self):
        """Update the selected files list based on checked items"""
        # Get selected files
        selected_files = self.get_checked_files()
        
        # Update the listbox
        self.file_listbox.delete(0, tk.END)
        self.selected_files = selected_files
        
        for file_path in selected_files:
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, filename)
    
    def get_checked_files(self, parent=''):
        """Recursively get all checked files"""
        checked_files = []
        
        def collect_checked(parent):
            for item_id in self.tree.get_children(parent):
                tags = self.tree.item(item_id, 'tags')
                
                if 'checked' in tags:
                    # If it's a file and is checked, add to list
                    if 'file' in tags and os.path.isfile(item_id):
                        checked_files.append(item_id)
                
                # Process children recursively
                if self.tree.get_children(item_id):
                    collect_checked(item_id)
        
        collect_checked(parent)
        return checked_files
    
    def edit_selected_file(self):
        """Open selected file for editing"""
        # Get selected index in listbox
        selected_idx = self.file_listbox.curselection()
        if not selected_idx:
            self.status_var.set("No file selected for editing")
            return
        
        # Get file path
        file_idx = selected_idx[0]
        if file_idx >= len(self.selected_files):
            self.status_var.set("Invalid file selection")
            return
        
        file_path = self.selected_files[file_idx]
        
        # Create a new window for editing
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Edit: {os.path.basename(file_path)}")
        edit_window.geometry("800x600")
        
        # Add a text editor
        editor = tk.Text(edit_window, wrap=tk.NONE)
        editor.pack(fill=tk.BOTH, expand=True)
        
        # Load file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                editor.insert(tk.END, content)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    editor.insert(tk.END, content)
            except Exception as e:
                editor.insert(tk.END, f"Error reading file: {str(e)}")
        except Exception as e:
            editor.insert(tk.END, f"Error reading file: {str(e)}")
        
        # Button frame
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X)
        
        # Save button
        def save_file():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.get(1.0, tk.END))
                self.status_var.set(f"File saved: {os.path.basename(file_path)}")
                edit_window.destroy()
            except Exception as e:
                self.status_var.set(f"Error saving file: {str(e)}")
        
        save_button = ttk.Button(button_frame, text="Save", command=save_file)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def generate_dump(self):
        """Generate dump from selected files"""
        # Check if any files are selected
        if not self.selected_files:
            self.status_var.set("No files selected. Please check some files.")
            self.show_preview_text("No files selected. Please check files in the tree view.")
            return
        
        # Update status
        self.status_var.set(f"Generating dump from {len(self.selected_files)} files...")
        self.update_idletasks()
        
        # Generate dump
        output = []
        total_size = 0
        error_count = 0
        
        for index, file_path in enumerate(self.selected_files):
            # Update status periodically
            if index % 5 == 0:
                self.status_var.set(f"Processing file {index+1} of {len(self.selected_files)}...")
                self.update_idletasks()
            
            try:
                # Get file info
                file_info = get_file_info(file_path)
                total_size += file_info['size']
                
                # Add file header
                output.append(f"\n\n{'=' * 80}")
                output.append(f"File: {file_path}")
                output.append(f"Size: {file_info['size']} bytes")
                output.append(f"Last Modified: {file_info['last_modified']}")
                output.append('=' * 80 + '\n')
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        output.append(content)
                except UnicodeDecodeError:
                    # Try with alternative encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                            output.append(content)
                    except Exception as e:
                        output.append(f"Error reading file (encoding issue): {str(e)}")
                        error_count += 1
                except PermissionError:
                    output.append("Error reading file: Permission denied")
                    error_count += 1
                except Exception as e:
                    output.append(f"Error reading file: {str(e)}")
                    error_count += 1
            except Exception as e:
                output.append(f"\n\n{'=' * 80}")
                output.append(f"Error processing file {file_path}: {str(e)}")
                output.append('=' * 80 + '\n')
                error_count += 1
        
        # Save content for clipboard
        self.dump_content = '\n'.join(output)
        
        # Show in preview
        self.show_preview_text(self.dump_content)
        
        # Update status
        size_str = self.format_size(total_size)
        if error_count > 0:
            self.status_var.set(f"Dump generated with {error_count} errors: {len(self.selected_files)} files, {size_str}")
        else:
            self.status_var.set(f"Dump generated successfully: {len(self.selected_files)} files, {size_str}")
    
    def show_preview_text(self, text):
        """Display text in the preview area"""
        # Enable editing
        self.preview_text.config(state='normal')
        
        # Clear existing content
        self.preview_text.delete(1.0, tk.END)
        
        # Insert new text
        self.preview_text.insert(tk.END, text)
        
        # Disable editing
        self.preview_text.config(state='disabled')
    
    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
    
    def copy_to_clipboard(self):
        """Copy dump content to clipboard"""
        if not self.dump_content:
            self.status_var.set("No content to copy. Generate a dump first.")
            return
        
        try:
            self.status_var.set("Copying to clipboard...")
            self.update_idletasks()
            
            pyperclip.copy(self.dump_content)
            self.status_var.set("Content copied to clipboard")
            
            # Reset status after delay
            self.after(2000, lambda: self.status_var.set("Ready"))
        except Exception as e:
            self.status_var.set(f"Error copying to clipboard: {str(e)}")

def main():
    app = CodeDumpApp()
    app.mainloop()

if __name__ == "__main__":
    main() 