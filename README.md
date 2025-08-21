# Markdown Slider

A Streamlit application to create, edit, and view Markdown files as a slideshow presentation.

## Features

- **File Operations**: Create a new file, upload an existing Markdown file (`.md`), and save your work.
- **Command-Line Loading**: Open a file directly when starting the app (`streamlit run slider.py <file_path>`).
- **Live Editor**: View and edit the raw Markdown source.
- **Full Page View**: See the fully rendered Markdown on a single, scrollable page.
- **Slideshow Mode**: Present the Markdown as a slideshow with easy-to-use navigation controls.
- **Dynamic Slide Splitting**: Dynamically split slides based on various separators, which can be combined:
  - Horizontal Rules (`---`)
  - Headings (H1, H2, H3, H4)
  - Bold text (`**...**`)
  - After an image
  - By a specified number of lines
- **Quick Navigation**: Use the "Jump to" feature to quickly navigate to any slide via a generated table of contents.
- **Integrated Image Server**: Automatically serves local images for correct display in the presentation. No need to run a separate server.
- **Obsidian-style Images**: Supports `![[image.png]]` syntax for embedding images.

## How to Run and Use

1.  **Install Dependencies:**
    Open your terminal and install the necessary Python packages from `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    In your terminal, navigate to the project directory and run the Streamlit app.

    *To start with an empty editor:*
    ```bash
    streamlit run slider.py
    ```

    *To open a specific file:*
    ```bash
    streamlit run slider.py "path/to/your/file.md"
    ```

3.  **Using the App:**
    - The application will open in your web browser.
    - Use the sidebar to **New File**, **Open Markdown file**, or **Save File**.
    - The filename and save path can be edited in the sidebar.

4.  **Displaying Local Images:**
    - When you open a file, the app automatically starts a server in the file's directory to display images.
    - You can manually set the **Image Directory** in the sidebar and click **Start/Restart Image Server**.
    - The app supports standard Markdown image syntax (`![](path/to/image.png)`) and Obsidian-style links (`![[image.png]]`).

5.  **Navigating Slides:**
    - Go to the **Slides** tab.
    - Use the **◀** and **▶** buttons or the slider to move between slides.
    - Click the **Jump** button to open a table of contents for quick navigation.
    - Use the **Split** popover to customize how the content is divided into slides. Changes are applied instantly.