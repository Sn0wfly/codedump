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
        
        # Refresh button
        refresh_button = ttk.Button(
            top_frame,
            text="Refresh",
            command=self.refresh_directory
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        
        # Button to edit selected file
        edit_file_button = ttk.Button(
            buttons_frame,
            text="Edit Original File",
            command=self.edit_selected_file
        )
        
        # Button to edit section in dump
        edit_section_button = ttk.Button(
            buttons_frame,
            text="Edit Section in Dump",
            command=self.open_edit_section_dialog
        )
        
        # Layout
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        edit_file_button.pack(side=tk.LEFT, padx=5)
        edit_section_button.pack(side=tk.LEFT, padx=5)
        
        # Double-click also opens edit dialog
        self.file_listbox.bind("<Double-Button-1>", lambda e: self.open_edit_section_dialog())
    
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
        # Use tkinter.filedialog to get the directory path
        directory = filedialog.askdirectory()
        
        if directory:
            # Store the selected path
            self.selected_directory.set(directory)
            
            # Update status
            self.status_var.set("Loading directory...")
            self.update_idletasks()
            
            # Clear the treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear the selected files listbox
            self.file_listbox.delete(0, tk.END)
            
            # Clear the preview text area
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.config(state='disabled')
            
            # Clear selected files list and dump content
            self.selected_files = []
            self.dump_content = ""
            
            # Populate the treeview with the selected directory
            # Create root node for the directory
            root_dir = os.path.basename(directory)
            if not root_dir:  # If it's the root directory
                root_dir = directory
                
            root_node = self.tree.insert('', 'end', iid=directory, 
                                        text=f"☐ {root_dir}",
                                        tags=('unchecked', 'folder'), 
                                        open=True,
                                        image=self.folder_icon if self.use_icons else '')
            
            # Populate starting from the root node
            self.populate_treeview(directory, parent_node=root_node)
            
            # Update status
            self.status_var.set(f"Directory loaded: {os.path.basename(directory)}")
        else:
            self.status_var.set("Ready")
    
    def populate_treeview(self, directory_path, parent_node=''):
        """Fill the treeview with directory structure using os.scandir for efficiency
        
        Args:
            directory_path: Path to the directory to populate
            parent_node: Parent node ID in the treeview (default: root)
        """
        try:
            # Iterate over items in the directory using os.scandir (more efficient)
            for item in os.scandir(directory_path):
                # Get full path
                item_path = item.path
                
                # Skip items that should be filtered out
                if should_skip(item_path):
                    continue
                
                # Determine icon to use based on whether it's a directory
                if item.is_dir():
                    icon = self.folder_icon if self.use_icons else ''
                    tags = ('unchecked', 'folder')
                else:
                    icon = self.file_icon if self.use_icons else ''
                    tags = ('unchecked', 'file')
                
                # Insert item into treeview with checkbox symbol
                node_id = item_path
                node = self.tree.insert(
                    parent_node, 'end', iid=node_id, 
                    text=f"☐ {item.name}",
                    tags=tags, open=False,
                    image=icon
                )
                
                # Recursively process subdirectories
                if item.is_dir():
                    self.populate_treeview(item_path, parent_node=node_id)
                    
        except PermissionError:
            # Handle permission errors
            error_id = f"{directory_path}_error_perm"
            self.tree.insert(parent_node, 'end', iid=error_id, 
                            text="Access Denied (Permission Error)")
        except Exception as e:
            # Handle other errors
            error_id = f"{directory_path}_error_general"
            self.tree.insert(parent_node, 'end', iid=error_id, 
                            text=f"Error: {str(e)}")
    
    def toggle_check(self, event):
        """Handle clicking on tree items to toggle checkboxes
        
        This detects clicks on tree items and toggles their checked/unchecked state,
        updating both the visual representation and the underlying tags.
        If the item is a folder, the state is applied recursively to all children.
        """
        # Identify clicked region and item
        region = self.tree.identify_region(event.x, event.y)
        item_id = self.tree.identify_row(event.y)
        
        # Only process valid clicks on text, icon, or tree item (not on empty space)
        if not item_id or region not in ('tree', 'cell', 'text', 'image'):
            return
            
        # Get item properties
        tags = list(self.tree.item(item_id, 'tags'))
        current_text = self.tree.item(item_id, 'text')
        item_name = current_text[2:] if current_text.startswith(('☐', '☑')) else current_text
        
        # Determine if this is a folder
        is_folder = 'folder' in tags
            
        # Toggle check state
        if 'checked' in tags:
            # Change to unchecked
            new_state = 'unchecked'
            new_tags = [tag for tag in tags if tag != 'checked'] + ['unchecked']
            new_text = f"☐ {item_name}"
        else:
            # Change to checked
            new_state = 'checked'
            new_tags = [tag for tag in tags if tag != 'unchecked'] + ['checked']
            new_text = f"☑ {item_name}"
        
        # Update item
        self.tree.item(item_id, text=new_text, tags=new_tags)
        
        # Apply to children if it's a folder
        if is_folder:
            self.update_descendants_check_state(item_id, new_state)
                
        # Update selected files list
        self.update_selected_files()
    
    def update_descendants_check_state(self, parent_id, state):
        """Recursively update check state of all descendants
        
        Args:
            parent_id: ID of the parent node in the treeview
            state: New state to apply ('checked' or 'unchecked')
        """
        # Symbol to use based on state
        symbol = '☑' if state == 'checked' else '☐'
        
        # Process all children
        for child_id in self.tree.get_children(parent_id):
            # Get child properties
            child_tags = list(self.tree.item(child_id, 'tags'))
            current_text = self.tree.item(child_id, 'text')
            item_name = current_text[2:] if current_text.startswith(('☐', '☑')) else current_text
            
            # Determine type (preserve folder/file tag)
            is_folder = 'folder' in child_tags
            type_tag = 'folder' if is_folder else 'file'
            
            # Create new tags: keep type tag and add new state
            new_tags = [type_tag, state]
            
            # Update text with appropriate symbol
            new_text = f"{symbol} {item_name}"
            
            # Update the item
            self.tree.item(child_id, text=new_text, tags=new_tags)
            
            # Recursively process children if this is a folder
            if is_folder:
                self.update_descendants_check_state(child_id, state)
    
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
        """Recursively get all checked files
        
        Args:
            parent: Parent node ID in the treeview (default: root)
        
        Returns:
            list: List of checked file paths
        """
        checked_files = []
        
        def collect_checked(parent_node):
            for item_id in self.tree.get_children(parent_node):
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
        edit_window.title(f"Edit File: {os.path.basename(file_path)}")
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
    
    def open_edit_section_dialog(self):
        """Open a dialog to edit the selected section in the dump"""
        # Get selected index in listbox
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            self.status_var.set("No section selected for editing")
            return
            
        # Get section index
        section_idx = selected_indices[0]
        
        # Check if the index is valid
        if section_idx < 0 or section_idx >= len(self.dump_sections):
            self.status_var.set("Invalid section selected")
            return
        
        # Get section data
        section_data = self.dump_sections[section_idx]
        section_path = section_data['path']
        section_name = section_data['name']
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Section: {section_name}")
        dialog.geometry("800x600")
        dialog.transient(self)  # Make dialog transient to parent
        dialog.resizable(True, True)
        dialog.grab_set()  # Make dialog modal
        
        # Create text editor with scrollbars
        editor_frame = ttk.Frame(dialog)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        editor = tk.Text(editor_frame, wrap=tk.NONE)
        y_scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=editor.yview)
        x_scrollbar = ttk.Scrollbar(editor_frame, orient="horizontal", command=editor.xview)
        
        editor.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Layout
        editor.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        
        # Get section content from the dump
        section_tag = f"section_{section_idx}"
        section_ranges = self.preview_text.tag_ranges(section_tag)
        
        if section_ranges:
            # Get the text from the preview
            section_text = self.preview_text.get(section_ranges[0], section_ranges[1])
            editor.insert(tk.END, section_text)
        else:
            # Fallback to original content
            editor.insert(tk.END, section_data['header'] + section_data['content'])
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save button
        save_button = ttk.Button(
            button_frame, 
            text="Save Changes", 
            command=lambda: self.save_section_edit(dialog, editor, section_idx)
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to be closed
        self.wait_window(dialog)
    
    def save_section_edit(self, dialog, editor, section_idx):
        """Save the edited section back to the dump
        
        Args:
            dialog: The dialog window
            editor: The text editor widget containing the edited text
            section_idx: The index of the section being edited
        """
        # Get edited text
        edited_text = editor.get('1.0', tk.END)
        
        # Get section tag
        section_tag = f"section_{section_idx}"
        
        # Find the original tag range
        ranges = self.preview_text.tag_ranges(section_tag)
        
        if ranges:
            # Enable editing of the preview text
            self.preview_text.config(state='normal')
            
            # Delete the old content
            self.preview_text.delete(ranges[0], ranges[1])
            
            # Insert the new content
            self.preview_text.insert(ranges[0], edited_text)
            
            # Calculate new end position
            new_end = f"{ranges[0]} + {len(edited_text)}c"
            
            # Reapply the tag
            self.preview_text.tag_add(section_tag, ranges[0], new_end)
            
            # Make the preview text read-only again
            self.preview_text.config(state='disabled')
            
            # Update the section data
            if section_idx < len(self.dump_sections):
                self.dump_sections[section_idx]['content'] = edited_text
                
                # Update the clipboard content
                self.update_dump_content()
            
            self.status_var.set(f"Section updated: {self.dump_sections[section_idx]['name']}")
        else:
            self.status_var.set("Error: Could not find section in the preview")
        
        # Close the dialog
        dialog.destroy()
    
    def update_dump_content(self):
        """Update the dump content string after editing sections"""
        # Regenerate the dump content
        output = []
        
        for section in self.dump_sections:
            output.append(section['header'])
            output.append(section['content'])
        
        # Update the dump content for clipboard
        self.dump_content = '\n'.join(output)
    
    def generate_dump(self):
        """Generate dump from selected files
        
        This function:
        1. Collects all checked files from the tree
        2. Generates formatted content for each file
        3. Adds sections to the Text widget with tags
        4. Updates the file listbox with section information
        """
        # Collect checked files
        selected_files = self.get_checked_files()
        
        # Check if any files are selected
        if not selected_files:
            self.status_var.set("No files selected. Please check some files.")
            self.show_preview_text("No files selected. Please check files in the tree view.")
            return
        
        # Update status
        self.status_var.set(f"Generating dump from {len(selected_files)} files...")
        self.update_idletasks()
        
        # Prepare for content generation
        output = []
        total_size = 0
        error_count = 0
        
        # Store sections for later reference
        self.dump_sections = []
        
        # Make the preview text widget editable and clear it
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        # Clear the file listbox
        self.file_listbox.delete(0, tk.END)
        
        # Process each file
        for index, file_path in enumerate(selected_files):
            # Update status periodically
            if index % 5 == 0:
                self.status_var.set(f"Processing file {index+1} of {len(selected_files)}...")
                self.update_idletasks()
            
            try:
                # Get file info
                file_info = get_file_info(file_path)
                total_size += file_info['size']
                
                # Create header
                header = f"\n\n{'=' * 80}\n"
                header += f"File: {file_path}\n"
                header += f"Size: {file_info['size']} bytes\n"
                header += f"Last Modified: {file_info['last_modified']}\n"
                header += '=' * 80 + '\n'
                
                # Get content with error handling
                content = ""
                error = None
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try with alternative encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        content = f"Error reading file (encoding issue): {str(e)}"
                        error = e
                        error_count += 1
                except PermissionError as e:
                    content = "Error reading file: Permission denied"
                    error = e
                    error_count += 1
                except Exception as e:
                    content = f"Error reading file: {str(e)}"
                    error = e
                    error_count += 1
                
                # Store section data
                section_data = {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'header': header,
                    'content': content,
                    'error': error
                }
                self.dump_sections.append(section_data)
                
                # Add to output for clipboard
                output.append(header)
                output.append(content)
                
                # Insert into text widget with tags
                start_index = self.preview_text.index(tk.END)
                self.preview_text.insert(tk.END, header, "header")
                self.preview_text.insert(tk.END, content, "content")
                end_index = self.preview_text.index(tk.END)
                
                # Add a section tag for navigation
                section_tag = f"section_{index}"
                self.preview_text.tag_add(section_tag, start_index, end_index)
                
                # Add file to listbox
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
                
            except Exception as e:
                # Handle any other errors
                error_msg = f"\n\n{'=' * 80}\n"
                error_msg += f"Error processing file {file_path}: {str(e)}\n"
                error_msg += '=' * 80 + '\n'
                
                output.append(error_msg)
                self.preview_text.insert(tk.END, error_msg, "error")
                error_count += 1
        
        # Configure tags for styling
        self.preview_text.tag_configure("header", foreground="blue", font=("Courier", 10, "bold"))
        self.preview_text.tag_configure("content", foreground="black")
        self.preview_text.tag_configure("error", foreground="red")
        
        # Make the text widget read-only again
        self.preview_text.config(state='disabled')
        
        # Save content for clipboard
        self.dump_content = '\n'.join(output)
        
        # Update status
        size_str = self.format_size(total_size)
        if error_count > 0:
            self.status_var.set(f"Dump generated with {error_count} errors: {len(selected_files)} files, {size_str}")
        else:
            self.status_var.set(f"Dump generated successfully: {len(selected_files)} files, {size_str}")
        
        # Connect listbox selection to section navigation
        self.file_listbox.bind('<<ListboxSelect>>', self.navigate_to_section)
    
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
        """Copy current preview text content to clipboard"""
        try:
            # Get content directly from the Text widget
            full_dump_text = self.preview_text.get('1.0', f"{tk.END}-1c")
            
            # Check if there is any content to copy
            if not full_dump_text.strip():
                self.status_var.set("No content to copy. Generate a dump first.")
                return
            
            # Update status and copy to clipboard
            self.status_var.set("Copying to clipboard...")
            self.update_idletasks()
            
            # Copy to clipboard
            pyperclip.copy(full_dump_text)
            
            # Provide visual feedback
            self.preview_text.tag_add("copy_highlight", "1.0", tk.END)
            self.preview_text.tag_config("copy_highlight", background="#e6ffe6")  # Light green
            
            # Update status
            self.status_var.set("Content copied to clipboard!")
            
            # Clear highlighting and reset status after delay
            self.after(1000, lambda: self.preview_text.tag_remove("copy_highlight", "1.0", tk.END))
            self.after(2000, lambda: self.status_var.set("Ready"))
            
        except Exception as e:
            self.status_var.set(f"Error copying to clipboard: {str(e)}")
            self.after(2000, lambda: self.status_var.set("Ready"))
    
    def navigate_to_section(self, event):
        """Navigate to a section in the preview text when selected in the listbox
        
        Args:
            event: The event generated by the listbox selection
        """
        # Get selected index in the listbox
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return
            
        index = selected_indices[0]
        
        # Check if the index is valid
        if index < 0 or index >= len(self.dump_sections):
            self.status_var.set("Invalid section selected")
            return
            
        # Get section tag
        section_tag = f"section_{index}"
        
        # Find the tag range
        try:
            tag_ranges = self.preview_text.tag_ranges(section_tag)
            if tag_ranges:
                # Scroll to the beginning of the section
                self.preview_text.see(tag_ranges[0])
                
                # Highlight the section temporarily
                self.preview_text.tag_config(section_tag, background="lightyellow")
                
                # Reset the highlight after a short delay
                self.after(1000, lambda: self.preview_text.tag_config(section_tag, background=""))
                
                # Update status
                section_name = self.dump_sections[index]['name']
                self.status_var.set(f"Navigated to: {section_name}")
        except Exception as e:
            self.status_var.set(f"Error navigating to section: {str(e)}")
    
    def refresh_directory(self):
        """Refresh the current directory without reselecting it"""
        directory = self.selected_directory.get()
        if directory and os.path.exists(directory):
            # Save currently checked items
            checked_items = []
            
            def collect_checked_items(parent=''):
                for item_id in self.tree.get_children(parent):
                    tags = self.tree.item(item_id, 'tags')
                    if 'checked' in tags:
                        checked_items.append(item_id)
                    
                    if self.tree.get_children(item_id):
                        collect_checked_items(item_id)
            
            # Start collecting from the root node
            collect_checked_items()
            
            # Update status
            self.status_var.set("Refreshing directory...")
            self.update_idletasks()
            
            # Clear the treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Repopulate the tree
            root_dir = os.path.basename(directory)
            if not root_dir:  # If it's the root directory
                root_dir = directory
                
            root_node = self.tree.insert('', 'end', iid=directory, 
                                         text=f"☐ {root_dir}",
                                         tags=('unchecked', 'folder'), 
                                         open=True,
                                         image=self.folder_icon if self.use_icons else '')
            
            # Populate starting from the root node
            self.populate_treeview(directory, parent_node=root_node)
            
            # Restore checked items that still exist
            for item_id in checked_items:
                if os.path.exists(item_id) and self.tree.exists(item_id):
                    # Get current tags and text
                    tags = list(self.tree.item(item_id, 'tags'))
                    current_text = self.tree.item(item_id, 'text')
                    item_name = current_text[2:]  # Remove checkbox symbol
                    
                    # Update to checked
                    if 'unchecked' in tags:
                        tags.remove('unchecked')
                    if 'checked' not in tags:
                        tags.append('checked')
                    
                    # Update item
                    self.tree.item(item_id, text=f"☑ {item_name}", tags=tags)
            
            # Update status
            self.status_var.set(f"Directory refreshed: {os.path.basename(directory)}")
        else:
            self.status_var.set("No directory selected to refresh")

def main():
    app = CodeDumpApp()
    app.mainloop()

if __name__ == "__main__":
    main() 