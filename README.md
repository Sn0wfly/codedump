# CodeDump

CodeDump is a simple Python tool that concatenates and dumps code from a directory, including file information such as size and last modified time.

## Installation

To install CodeDump, run:

    pip install codedump

Or clone this repository and run:

    pip install -e .

## Usage

### Command Line Interface

CodeDump can be used from the command line:

    # Dump all code files from current directory
    codedump

    # Dump all code files from a specific directory
    codedump /path/to/directory

    # Only list file paths without content
    codedump -l
    codedump --list-only

The tool will:
1. Recursively scan the specified directory
2. Find all code and configuration files
3. Output their contents with file information
4. Automatically copy the output to your clipboard

CodeDump automatically filters out:
- Binary files
- Build directories
- Cache directories
- Version control directories
- Log files
- Temporary files

### Graphical User Interface

CodeDump includes a graphical interface for easier interaction with the tool.

#### Requirements

- Python 3.6+
- Required packages: `tkinter`, `pillow`, `pyperclip` (automatically installed with the package)

#### GUI Features

To run the GUI:

```bash
# Run the GUI
codedump-gui
```

The graphical interface includes these features:

- **Split-Panel Interface**: Separate panels for file tree, selected files, and preview
- **Custom Icons**: Visual distinction between files and folders
- **File Editor**: Ability to edit selected files directly in the application
- **Selected Files List**: Quick overview of files included in the dump
- **Adjustable Panels**: Resize panels using draggable dividers
- **Refresh Button**: Reload the current directory to pick up newly added or modified files without having to reselect the directory
- **Folder Structure Generator**: Create a visual representation of your folder structure with proper indentation, showing only the selected files and folders

##### How to use:

1. Click "Select Directory" to choose your project folder
2. Navigate the file tree and check the files you want to include
3. View selected files in the upper right panel
4. Edit files if needed by selecting them and clicking "Edit Selected File"
5. If files change, use the "Refresh" button to update the directory view
6. Click "Generate Dump" to create the code dump with full file contents, or "Generate Folder Structure" to create a lightweight directory tree view
7. Review the output in the preview panel
8. Click "Copy to Clipboard" to copy the content

![CodeDump Advanced GUI](https://github.com/Sn0wfly/codedump/raw/main/docs/codedump_gui_advanced_screenshot.png)
