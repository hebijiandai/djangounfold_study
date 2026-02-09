# Django Unfold Study Project Deployment Guide

This guide provides instructions to set up and run the Django project.

## Prerequisites

*   **Python:** Ensure you have Python 3.11 (or a compatible version) installed on your system.
*   **uv:** Download the `uv` executable for your operating system (e.g., `uv-x86_64-pc-windows-msvc` for Windows) and place the extracted folder containing `uv.exe` directly inside the `djangounfold_study` directory.

## Deployment Steps

Follow these steps to get the project running:

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and navigate to the `djangounfold_study` directory:
    ```bash
    cd djangounfold_study
    ```

2.  **Create/Recreate Virtual Environment:**
    First, ensure you have the `uv-x86_64-pc-windows-msvc` folder (or equivalent for your OS) with `uv.exe` inside your `djangounfold_study` directory.
    Then, create a new virtual environment. If a `.venv` directory already exists, this command will recreate it, ensuring a clean environment.
    ```bash
    .\uv-x86_64-pc-windows-msvc\uv.exe venv
    ```
    *(Note: On Linux/macOS, you would typically use `./uv-x86_64-unknown-linux-gnu/uv venv` or similar path.)*

3.  **Install Dependencies:**
    Install Django and `django-unfold` (and any other project dependencies) into the newly created virtual environment:
    ```bash
    .\uv-x86_64-pc-windows-msvc\uv.exe pip install Django django-unfold
    ```
    *(Adjust the `uv.exe` path as needed for your OS.)*

4.  **Run the Django Development Server:**
    Once the dependencies are installed, you can start the development server:
    ```bash
    .\uv-x86_64-pc-windows-msvc\uv.exe run python manage.py runserver
    ```
    The server should now be running, typically accessible at `http://127.0.0.1:8000/`.

---
**Note on `uv` and Python Interpreter:**

During virtual environment creation, `uv` might report using a system-wide Python interpreter (e.g., from Anaconda). While ideally, `uv` should pick a minimal Python, the subsequent `uv pip install` and `uv run` commands will ensure that project dependencies are managed and isolated within the `.venv` directory, overriding global packages where conflicts exist.

If you encounter persistent issues with `uv` defaulting to an undesirable global Python, you may need to explicitly point `uv` to a specific Python interpreter during `venv` creation using a command like `uv venv --python <path_to_desired_python_exe>`.
