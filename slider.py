import streamlit as st
import re
import os
import sys
import threading
import http.server
import socketserver
from urllib.parse import quote

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Markdown Slider", page_icon="📄", layout="wide")

def find_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        return s.server_address[1]

def start_server(path, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=path, **kwargs)

        def translate_path(self, path):
            # Decode URL-encoded paths
            return super().translate_path(quote(path))

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

def main():
    """
    Main function to run the Streamlit application.
    Initializes session state and lays out the UI components.
    """
    # --- Session State Initialization ---
    # Initialize session state variables to preserve state across reruns.
    st.session_state.text = st.session_state.get("text", "")
    st.session_state.current_page = st.session_state.get("current_page", 0)
    st.session_state.separator = st.session_state.get("separator", "Page length")
    st.session_state.page_lines = st.session_state.get("page_lines", 20)
    # Flags for different slide separators
    st.session_state.separator_hr = st.session_state.get("separator_hr", True)
    st.session_state.separator_h1 = st.session_state.get("separator_h1", False)
    st.session_state.separator_h2 = st.session_state.get("separator_h2", False)
    st.session_state.separator_h3 = st.session_state.get("separator_h3", False)
    st.session_state.separator_h4 = st.session_state.get("separator_h4", False)
    st.session_state.separator_bold = st.session_state.get("separator_bold", False)
    st.session_state.separator_after_image = st.session_state.get("separator_after_image", False)
    st.session_state.separator_page_length = st.session_state.get("separator_page_length", False)
    # Core content and file info
    st.session_state.markdown_content = st.session_state.get("markdown_content", "")
    st.session_state.last_uploaded_file_id = st.session_state.get("last_uploaded_file_id", None)
    st.session_state.file_name = st.session_state.get("file_name", None)
    st.session_state.file_save_path = st.session_state.get("file_save_path", os.getcwd())
    st.session_state.image_directory = st.session_state.get("image_directory", os.getcwd())

    # --- Server Management ---
    if 'server_thread' not in st.session_state:
        st.session_state.server_thread = None
    if 'server_port' not in st.session_state:
        st.session_state.server_port = None

    # --- Load file from command line argument ---
    if 'cli_file_loaded' not in st.session_state:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        st.session_state.markdown_content = f.read()
                    st.session_state.file_name = os.path.basename(file_path)
                    st.session_state.last_uploaded_file_id = file_path
                    file_dir = os.path.dirname(file_path)
                    if file_dir:
                        st.session_state.file_save_path = file_dir
                        st.session_state.image_directory = file_dir

                    # Start image server automatically
                    if os.path.isdir(st.session_state.image_directory):
                        if st.session_state.server_thread is None:
                            port = find_free_port()
                            st.session_state.server_port = port
                            thread = threading.Thread(target=start_server, args=(st.session_state.image_directory, port), daemon=True)
                            thread.start()
                            st.session_state.server_thread = thread
                            st.toast(f"Image server started on port {port}.")
                    
                    resplit()
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            else:
                st.warning(f"File not found: {file_path}")
        st.session_state.cli_file_loaded = True

    # --- Sidebar UI ---
    with st.sidebar:
        st.title("Markdown Slider")
        
        # Button to create a new, empty file
        if st.button("New File", use_container_width=True):
            st.session_state.markdown_content = ""
            st.session_state.last_uploaded_file_id = "new_file"
            st.session_state.file_name = "untitled.md"
            resplit()

        # File uploader for markdown files
        uploaded_md_file = st.file_uploader(
            "Open Markdown file",
            type=["md"]
        )
    
        # Process uploaded file
        if uploaded_md_file:
            # Check if a new file has been uploaded
            if st.session_state.get('last_uploaded_file_id') != uploaded_md_file.file_id:
                st.session_state.markdown_content = uploaded_md_file.getvalue().decode("utf-8")
                st.session_state.last_uploaded_file_id = uploaded_md_file.file_id
                st.session_state.file_name = uploaded_md_file.name
                resplit()
    
        # File operations (Save) appear only if a file is loaded or new
        if st.session_state.last_uploaded_file_id:
            st.text_input("Filename", key="file_name")
            if st.button("Save File", use_container_width=True):
                try:
                    save_path = os.path.join(st.session_state.file_save_path, st.session_state.file_name)
                    os.makedirs(st.session_state.file_save_path, exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state.markdown_content)
                    st.success(f"Saved to {save_path}")
                except Exception as e:
                    st.error(f"Failed to save file: {e}")
    
        # Input for setting the file save path
        st.text_input(
            "File Save Path",
            key="file_save_path"
        )

        # Input for the image directory
        st.text_input(
            "Image Directory",
            key="image_directory"
        )

        if st.button("Start/Restart Image Server"):
            if os.path.isdir(st.session_state.image_directory):
                if st.session_state.server_thread is None:
                    port = find_free_port()
                    st.session_state.server_port = port
                    thread = threading.Thread(target=start_server, args=(st.session_state.image_directory, port), daemon=True)
                    thread.start()
                    st.session_state.server_thread = thread
                    st.toast(f"Image server started on port {port}.")
                else:
                    st.warning("Server is already running. Restart the app to change the directory.")
            else:
                st.error("The specified directory does not exist.")

    image_server_url = f"http://localhost:{st.session_state.server_port}" if st.session_state.server_port else None

    # --- Main Content Area ---
    if st.session_state.last_uploaded_file_id:
        # First convert ![[file_name]] format to ![](file_name)
        processed_markdown = re.sub(r'!\[\[(.*?)\]\]', r'![](\1)', st.session_state.markdown_content)
        
        # Then process local image paths to be served from the specified URL
        # Regex looks for ![alt](path) where path is not a web URL
        if image_server_url:
            processed_markdown = re.sub(r"!\[(.*?)\]\(((?!https?://).*?)\)", lambda m: replace_image_path(m, image_server_url), processed_markdown)
    
        # Main display tabs
        tab1, tab2, tab3 = st.tabs(["Source", "One Page", "Slides"])


        # Tab 1: Raw Markdown Editor
        with tab1:
            st.text_area("Edit", key="markdown_content", height=600, label_visibility="collapsed")
    
        # Tab 2: Rendered view of the entire markdown file
        with tab2:
            st.markdown(processed_markdown, unsafe_allow_html=True)
    
        # Tab 3: Slideshow view
        with tab3:
            all_pages = split_content(processed_markdown)
            index, pages = make_index(all_pages)  # Now returns both index and valid pages
            
            if not pages:  # Check if there are any valid pages
                st.warning("No valid content pages found.")
                return
                
            placeholder = st.empty()
            st.divider()
            
            # Ensure current_page is within valid range
            if st.session_state.current_page >= len(pages):
                st.session_state.current_page = 0
                
            # --- Slide Navigation Controls ---
            col1, col2, col3, col4, col5 = st.columns([1, 1, 8, 1, 1])
    
            with col1: # Previous button
                if st.button("◀", use_container_width=True):
                    if st.session_state.current_page == 0:
                        st.session_state.current_page = len(pages)-1
                    else:
                        st.session_state.current_page -= 1
    
            with col2: # Next button
                if st.button("▶", use_container_width=True):
                    if st.session_state.current_page == len(pages)-1:
                        st.session_state.current_page = 0
                    else:
                        st.session_state.current_page += 1
    
            with col3: # Page slider
                slider = st.empty()
    
            with col4: # Jump to page (index) button
                if st.button("Jump", use_container_width=True):
                    show_index(index)
    
            with col5: # Splitting options popover
                with st.popover("Split"):
                    st.checkbox(r"\---", key="separator_hr", on_change=resplit)
                    st.checkbox(r"\#", key="separator_h1", on_change=resplit)
                    st.checkbox(r"\##", key="separator_h2", on_change=resplit)
                    st.checkbox(r"\###", key="separator_h3", on_change=resplit)
                    st.checkbox(r"\####", key="separator_h4", on_change=resplit)
                    st.checkbox(r"\*\* ~ \*\*", key="separator_bold", on_change=resplit)
                    st.checkbox("After image", key="separator_after_image", on_change=resplit)
                    st.checkbox("Page length", key="separator_page_length", on_change=resplit)
                    st.slider("Select page length", min_value=1, max_value=30, key="page_lines", on_change=resplit)
    
            # Display the slider if there is more than one page
            if len(pages) > 1:
                slider.slider("Go to", min_value=1, max_value=len(pages),
                                value=st.session_state.current_page + 1,
                                key="page_slider",
                                on_change=update_slider,
                                label_visibility="collapsed")
    
            # Display the content of the current slide
            slide_content = pages[st.session_state.current_page]
            placeholder.markdown(slide_content, unsafe_allow_html=True)


def split_by_regex(regex: str, text: str) -> list[str]:
    """
    Splits a text by a given regex pattern, avoiding splits inside code blocks or tables.
    If splitting by horizontal rule ('---'), excludes the separator from the output.
    """
    parts = []
    current_part = ""
    in_code_block = False
    in_table = False
    table_content = ""
    
    for line in text.splitlines():
        # Toggle code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        # Detect table content to treat it as a single block
        if line.strip().startswith('|') or line.strip().startswith('+-'):
            if not in_table:
                in_table = True
            table_content += line + "\n"
            continue  # Skip adding table line to current_part
        elif in_table and not line.strip():
            in_table = False
            current_part += table_content  # Add complete table at once
            table_content = ""
            continue  # Skip adding empty line after table
        
        # Skip if still collecting table content
        if in_table:
            table_content += line + "\n"
            continue
        
        # Split if the line matches the regex and is not inside a code block
        if re.match(regex, line) and not in_code_block:
            if current_part:
                parts.append(current_part)
                current_part = ""
            # Only add the separator line if it's not a horizontal rule
            if not re.match(r'---\s*$', line):
                current_part += line + "\n"
        else:
            current_part += line + "\n"
    
    # Add any remaining table content
    if table_content:
        current_part += table_content
    
    # Add the last remaining part
    if current_part:
        parts.append(current_part)
    
    return parts

def split_by_lines(num: int, text: str) -> list[str]:
    """
    Splits a text into chunks of a specified number of lines.
    Avoids splitting within code blocks, tables, or right before a heading.
    """
    parts = []
    lines = text.splitlines()
    
    current_chunk = []
    in_table = False
    in_code_block = False
    chunk_line_count = 0
    
    for line in lines:
        # Toggle code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        # Detect table content
        if line.strip().startswith('|') or line.strip().startswith('+-'):
            in_table = True
        elif in_table and not line.strip():
            in_table = False
        
        current_chunk.append(line)
        chunk_line_count += 1
        
        # Split if line limit is reached and not inside a special block
        if chunk_line_count >= num and not in_table and not in_code_block:
            chunk_text = '\n'.join(current_chunk) + '\n'
            
            # If the last line is a heading, split before it to keep it with its content
            if is_markdown_heading(current_chunk[-1]):
                split_chunks = split_at_last_heading(chunk_text)
                parts.extend(split_chunks[:-1])
                current_chunk = [split_chunks[-1].strip()]
            else:
                parts.append(chunk_text)
                current_chunk = []
            
            chunk_line_count = len(current_chunk)
    
    # Add any remaining lines as the last part
    if current_chunk:
        parts.append('\n'.join(current_chunk) + '\n')
    
    return parts

def split_after_image(text: str) -> list[str]:
    """
    Splits the text into pages immediately after each image.
    """
    parts = []
    current_part = ""
    for line in text.splitlines():
        current_part += line + "\n"
        # Split after a line containing markdown image syntax
        if re.match(r"!\[.*\]\(.*\)", line.strip()):
            parts.append(current_part)
            current_part = ""
    # Add any remaining content
    if current_part:
        parts.append(current_part)
    return parts

@st.cache_data
def split_content(text):
    """
    Splits the markdown text into a list of pages based on selected criteria.
    Uses caching to improve performance.
    """
    parts = [text]
    
    # Dictionary mapping session state keys to splitting functions
    split_conditions = {
        "separator_page_length": (lambda x: split_by_lines(st.session_state.page_lines, x)),
        "separator_hr": (lambda x: split_by_regex(r'---\s*$', x)),
        "separator_h1": (lambda x: split_by_regex(r'^# .*$', x)),
        "separator_h2": (lambda x: split_by_regex(r'^## .*$', x)),
        "separator_h3": (lambda x: split_by_regex(r'^### .*$', x)),
        "separator_bold": (lambda x: split_by_regex(r'^\*\*(.*?)\*\*$', x)),
        "separator_after_image": (split_after_image)
    }
    
    # Apply each selected splitting function sequentially
    for separator, split_func in split_conditions.items():
        if st.session_state.get(separator, False):
            # Flatten the list of parts after each split
            parts = [part for page in parts for part in split_func(page)]
    
    return parts if len(parts) > 1 else [text]

def resplit():
    """
    Callback function to reset the page and clear caches when splitting options change.
    """
    st.session_state.current_page = 0
    split_content.clear()

def update_slider():
    """
    Callback function to update the current page when the navigation slider is moved.
    """
    page = st.session_state.page_slider -1
    if page != st.session_state.current_page:
        st.session_state.current_page = page

@st.cache_data
def is_markdown_heading(line):
    """
    Checks if a line is a markdown heading (levels 1-4).
    """
    stripped_line = line.strip()
    return (
            stripped_line.startswith('#') or 
            stripped_line.startswith('##') or 
            stripped_line.startswith('###') or 
            stripped_line.startswith('####'))

def split_at_last_heading(text):
    """
    Finds the last heading in a chunk of text and splits the text before it.
    This prevents a heading from being the last line of a page.
    """
    lines = text.splitlines()
    last_heading_index = -1
    
    # Find the index of the last heading
    for i, line in enumerate(lines):
        if is_markdown_heading(line):
            last_heading_index = i
    
    # If a heading is found and it's not the first line, split the text
    if last_heading_index > 0:
        part1 = '\n'.join(lines[:last_heading_index]) + '\n'
        part2 = '\n'.join(lines[last_heading_index:]) + '\n'
        return [part1, part2]
    
    return ['\n'.join(lines) + '\n']

@st.cache_data
def remove_decorators(text):
    """
    Removes markdown decorators (like #, **) from a line for a cleaner index display.
    """
    text = text.lstrip('#')
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    if text.endswith(':'):
        text = text[:-1]
    return text

def find_index(lst, target):
    """
    Finds the index of a target item in a list.
    """
    for i, str_item in enumerate(lst):
        if str_item == target:
            return i
    return -1

def replace_image_path(match, base_url):
    """
    Rewrites local image paths to point to the specified image server URL.
    Used as a callback for re.sub().
    """
    alt_text = match.group(1)
    original_path = match.group(2)
    try:
        image_filename = os.path.basename(original_path)
        base_url = base_url if base_url.endswith('/') else base_url + '/'
        new_url = f"{base_url}{image_filename}"
        return f"![{alt_text}]({new_url})"
    except Exception as e:
        st.error(f"Error processing image path {original_path}: {e}")
        return match.group(0)  # Return original string on error

@st.dialog("Page Index", width="large")
def show_index(toc):
    """
    Displays a dialog with a table of contents (TOC) for jumping to specific pages.
    """
    idx = st.session_state.current_page
    
    # Function to format TOC items for better display
    def format_func(item):
        return item[:60] + ("..." if len(item) > 60 else "")

    # Radio button list for page selection
    selected = st.radio(
        "Contents:",
        toc,
        index=idx,
        format_func=format_func,
        label_visibility="collapsed"
    )
    # If a new page is selected, update the state and rerun
    if selected is not None:
        idx = find_index(toc, selected)
        if idx != -1 and st.session_state.current_page != idx:
            st.session_state.current_page = idx
            st.rerun()

@st.cache_data
def make_index(pages):
    """
    Creates a table of contents from the list of pages.
    The first line of each page is used as the index entry.
    Skips pages that are empty or contain only separators.
    """
    index = []
    valid_pages = []
    
    for page in pages:
        # Skip if page is empty or contains only whitespace/separators
        page_content = page.strip()
        if not page_content or page_content in ['---', '----', '-----']:
            continue
            
        # Get the first non-empty line and clean it up for the index
        lines = [line for line in page.split('\n') if line.strip()]
        if lines:
            first_line = remove_decorators(lines[0].strip())
            first_line = f"{len(valid_pages)+1}. {first_line}"
            index.append(first_line)
            valid_pages.append(page)
            
    return index, valid_pages


# --- Main Execution ---
if __name__ == "__main__":
    main()
