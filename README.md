# Markdown Slider

A Streamlit application to view Markdown files as a slideshow presentation.

## Features

- Upload Markdown files (`.md`).
- View the original Markdown source in an editable text area.
- View the fully rendered Markdown on a single page.
- Present the Markdown as a slideshow with navigation controls.
- Dynamically split slides based on various separators:
  - Horizontal Rules (`---`)
  - Headings (H1, H2, H3, H4)
  - Bold text (`**...**`)
  - After an image
  - By a specified number of lines
- "Jump to" feature to quickly navigate to any slide using a generated table of contents.
- Automatically rewrites local image paths to point to a local image server for correct display.

## How to Run

1.  **Install Dependencies:**
    Open your terminal and install the necessary Python package from `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Image Server (If using local images):**
    For images with local paths in your Markdown file (e.g., `![alt](./images/pic.png)`), you need to run a local HTTP server in the directory where your images are stored.

    Navigate to your image directory in the terminal and run:

    ```bash
    python -m http.server 8080
    ```
    The application defaults to using `http://127.0.0.1:8080/` as the image server base URL. You can change this in the application's sidebar.

3.  **Run the Application:**
    In your terminal, navigate to the project directory and run the Streamlit app.

    ```bash
    streamlit run slider.py
    ```

## How to Use

1.  Open the web browser to the local URL provided by Streamlit (usually `http://localhost:8501`).
2.  Use the sidebar to upload your Markdown file.
3.  If you are using local images, ensure your image server is running and the URL in the sidebar is correct.
4.  Navigate between the **Source**, **One Page**, and **Slides** tabs.
5.  In the **Slides** tab:
    - Use the **◀** and **▶** buttons to move between slides.
    - Use the slider to navigate to a specific slide number.
    - Click the **Jump** button to open a table of contents and go directly to a slide.
    - Click the **Split** button (in the popover) to customize how the slides are divided. Changes are applied instantly.
