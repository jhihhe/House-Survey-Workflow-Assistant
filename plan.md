# Project Rewrite & Beautification Plan

## Goal
Rewrite the application using **PyQt6** for a modern, professional interface while maintaining all existing functionality. Optimize the codebase structure for better separation of concerns and maintainability. Package the application for both macOS and Windows as standalone executables.

## 1. Architecture & Structure Optimization
- **Refactor `Config`**: Move from hardcoded paths to a dynamic configuration system that persists user settings (Photographer Name, Source/Target Directories).
- **Service Layer**: Ensure `FolderService` and `ImportService` are completely decoupled from the UI, using signals or callbacks for progress updates.
- **Project Structure**:
    ```
    src/
      ├── main.py              # Entry point
      ├── ui/                  # PyQt6 UI components
      │   ├── main_window.py
      │   ├── styles.py        # QSS Stylesheets (Dracula theme)
      │   └── widgets/         # Custom widgets (if any)
      ├── services/            # Business logic
      │   ├── folder_service.py
      │   ├── import_service.py
      │   └── excel_service.py # Extract Excel logic from fs_utils
      └── utils/
          ├── config.py
          ├── fs_utils.py
          └── platform_utils.py # OS-specific path handling
    ```

## 2. UI Rewrite (PyQt6)
- **Main Window**: A clean, modern two-column or tabbed layout.
    - **Input Area**: Enhanced text editor for folder names with syntax highlighting (if possible) or clean typography.
    - **Control Panel**:
        - **Photographer Settings**: Name input.
        - **Path Settings**: Collapsible or separate tab to configure "Photo Source", "VR Source", and "Work Root" directories.
        - **Action Buttons**: Large, clear buttons for "Import" and "Create Folders".
        - **Progress Section**: Modern progress bars with detailed status labels.
- **Theme**: Apply a "Dracula" inspired dark theme using QSS (Qt Style Sheets).

## 3. Functionality Preservation
- **Folder Generation**: Re-implement the logic to parse input and create folders.
- **Excel Logging**: Ensure the Excel update logic (copying yesterday's file, adding new rows) works seamlessly.
- **Import Workflow**: maintain the multi-threaded import process with progress tracking.
- **Cross-Platform**: Use `pathlib` and `platform` checks to ensure paths work on both macOS and Windows.

## 4. Packaging
- **PyInstaller**: Create a robust `.spec` file that:
    - Bundles necessary assets (icons, templates).
    - Handles platform-specific settings (icon for .app/.exe).
    - Excludes unnecessary modules to keep size down.
- **Scripts**: Provide `build_macos.sh` and `build_windows.bat` (or instructions) for generating the binaries.

## 5. Execution Steps
1.  **Environment Setup**: Verify PyQt6 and other dependencies.
2.  **Backend Refactoring**: Update `Config` and `fs_utils`.
3.  **UI Implementation**: Build the PyQt6 interface.
4.  **Integration**: Connect UI to backend services.
5.  **Testing**: Verify functionality on macOS (current env).
6.  **Packaging Config**: Create PyInstaller spec.
