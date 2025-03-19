# Mujmal al-hikma App

import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import re

# Initialize the Dash app
app = dash.Dash(__name__, 
                # Add external stylesheets for custom fonts
                external_stylesheets=[
                    # Google Fonts for Sans Serif
                    "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap"
                ])
<<<<<<< HEAD

# Add this function to extract the first line (heading) from a file
def get_first_line_after_header(file_path):
    """
    Extract the first line after the '### | ' header from a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith('### | '):
                    # Return the header line itself, without the '### | ' prefix
                    return line.replace('### | ', '').strip()
            # If no header found, return empty string
            return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""

# Modify the get_section_files function to also return headings
=======
server = app.server
# Function to get all section files
>>>>>>> ea5f31a5a871c1f60e4ffb69f18eb600c98edb3a
def get_section_files(sections_dir="sections"):
    """
    Get all text files from the sections directory and sort them properly.
    Returns a list of tuples (filename, display_name) where display_name includes the heading.
    """
    # Check if directory exists
    if not os.path.exists(sections_dir):
        print(f"Warning: Directory '{sections_dir}' does not exist!")
        return []
        
    section_files = [f for f in os.listdir(sections_dir) if f.endswith('.txt')]
    print(f"Found {len(section_files)} text files in '{sections_dir}'")
    
    # Custom sorting function that handles special filenames
    def sort_key(filename):
        if filename == "Introduction.txt":
            return 0  # Place Introduction first
        elif "Risala_" in filename:
            # Extract the number after "Risala_"
            try:
                return int(filename.split('_')[1].split('.')[0])
            except (IndexError, ValueError):
                return float('inf')  # Place invalid formats at the end
        else:
            # For any other special filenames
            return float('inf')  # Place at the end
    
    # Sort the files using the custom sorting function
    section_files.sort(key=sort_key)
    
    # Create a list of tuples (filename, display_name)
    result = []
    for file in section_files:
        file_path = os.path.join(sections_dir, file)
        heading = get_first_line_after_header(file_path)
        display_name = file.replace('.txt', '')
        
        # Add heading if available
        if heading:
            # Truncate heading if too long (for better UI)
            if len(heading) > 50:
                heading = heading[:47] + "..."
            display_name = f"{display_name}: {heading}"
        
        result.append((file, display_name))
    
    return result

# Get the section files with headings
section_files_with_headings = get_section_files()

def openiti_to_html_components(text):
    """
    Convert OpenITI markdown to Dash HTML components.
    """
    # Create a list to store HTML components
    components = []
    
    # Process the text line by line
    lines = text.split('\n')
    for line in lines:
        # Skip empty lines
        if not line.strip():
            components.append(html.Br())
            continue
        
        # Process headers (### | syntax)
        if line.startswith('### | '):
            content = line.replace('### | ', '')
            components.append(html.H1(content, className='openiti-h1'))
            continue
        
        if line.startswith('### || '):
            content = line.replace('### || ', '')
            components.append(html.H2(content, className='openiti-h2'))
            continue
            
        if line.startswith('### ||| '):
            content = line.replace('### ||| ', '')
            components.append(html.H3(content, className='openiti-h3'))
            continue
        
        # Process comments (% syntax)
        if line.startswith('%'):
            content = line[1:].strip()
            components.append(html.Div(content, className='openiti-comment'))
            continue
        
        # Process regular paragraphs
        # For page numbers, uncertain readings, and editorial notes, we'll use simple text
        # as these would require more complex HTML manipulation
        components.append(html.P(line))
    
    return components

# Define custom CSS for the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Import custom fonts */
            @font-face {
                font-family: 'Uthman Taha Naskh';
                src: url('/assets/KFGQPC Uthman Taha Naskh Bold.ttf') format('opentype');
                font-weight: normal;
                font-style: normal;
            }
            
            @font-face {
                font-family: 'Sharif FarsiWeb';
                src: url('/assets/Fahood.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
                        @font-face {
                font-family: 'Neirizi';
                src: url('/assets/Neirizi.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            /* Custom CSS for styling */
            body {
                font-family: 'Open Sans', sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                height: 100vh;
                overflow: hidden;
            }
            
            /* Main container */
            .main-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                width: 100%;
            }
            
            /* Content container */
            .content-container {
                display: flex;
                flex-direction: row;
                flex: 1;
                overflow: hidden;
            }
            
            /* Papyrus-like background for text content */
            .papyrus-bg {
                background-color: #e8dcb5;
                background-image: url('/assets/natural-paper.png');
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                border-radius: 5px;
                direction: rtl; /* Right-to-left text direction */
                text-align: right;
            }
        
            
            /* Ancient rock background for sidebar */
            .rock-bg {
                background-color: #aa7641; /* Base color */
                background-image: url('/assets/natural-paper.png');
                background-repeat: repeat; /* Make the image repeat as a pattern */
                background-size: auto; /* Don't try to fit/cover the container */
                box-shadow: inset 0 0 10px rgba(0,0,0,0.7);
                color: #f5f5f5;
            }
            
            /* Custom scrollbar for the papyrus */
            .papyrus-scroll::-webkit-scrollbar {
                width: 12px;
            }
            
            .papyrus-scroll::-webkit-scrollbar-track {
                background: #d4c9a3;
            }
            
            .papyrus-scroll::-webkit-scrollbar-thumb {
                background-color: #8a7e55;
                border-radius: 6px;
                border: 3px solid #d4c9a3;
            }
            
            /* Custom scrollbar for the rock panel */
            .rock-scroll::-webkit-scrollbar {
                width: 12px;
            }
            
            .rock-scroll::-webkit-scrollbar-track {
                background: #5a5343;
            }
            
            .rock-scroll::-webkit-scrollbar-thumb {
                background-color: #AD9C8D;
                border-radius: 6px;
                border: 3px solid #5a5343;
            }
            
            /* Custom radio button styling */
            .custom-radio {
                cursor: pointer;
                padding: 10px;
                margin: 5px 0;
                border-radius: 10px;
                transition: background-color 0.3s;
                font-family: 'Open Sans', sans-serif;
            }
            
            .custom-radio:hover {
                background-color: rgba(0,0,0,0.2);
            }
            
            /* Ensure the panels stay side by side */
            .sidebar {
                width: 30%;
                height: 100%;
                overflow-y: auto;
                padding: 20px;
                box-sizing: border-box;
            }
            
            .content {
                width: 70%;
                height: 100%;
                padding: 20px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
            }
            
            /* OpenITI Markdown styling */
            .openiti-content {
                font-family: 'Sharif FarsiWeb', 'Times New Roman', serif;
                line-height: 1.8;
                color: #3e2723;
                direction: rtl;
                text-align: right;
                font-size: 18px;
            }
            
            .openiti-content p {
                margin: 0.7em 0;
            }
            
            .openiti-h1 {
                font-size: 2em;
                color: #5d4037;
                margin: 1em 0 0.5em 0;
                border-bottom: 1px solid #8d6e63;
                padding-bottom: 0.3em;
                font-family: 'Uthman Taha Naskh', serif;
                font-weight: bold;
            }
            
            .openiti-h2 {
                font-size: 1.7em;
                color: #5d4037;
                margin: 0.8em 0 0.4em 0;
                font-family: 'Uthman Taha Naskh', serif;
                font-weight: bold;
            }
            
            .openiti-h3 {
                font-size: 1.4em;
                color: #5d4037;
                margin: 0.6em 0 0.3em 0;
                font-family: 'Uthman Taha Naskh', serif;
                font-weight: bold;
            }
            
            .openiti-comment {
                color: #388e3c;
                font-style: italic;
                margin: 0.5em 0;
                padding: 0.5em;
                background-color: rgba(56, 142, 60, 0.1);
                border-radius: 3px;
            }
            
            /* Sidebar header styling */
            .sidebar-header {
                font-family: 'Open Sans', sans-serif;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            
            /* Main header styling */
            .main-header {
                font-family: 'Open Sans', sans-serif;
                color: #FFD700; /* Golden text color */
                padding: 25px;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
                background-image: url('/assets/mujmal.png');
                background-size: 120%;
                background-position: center center;
                position: relative;
                border-bottom: 3px solid #3a3529; /* Darker border at bottom */
                box-shadow: 0 4px 12px rgba(0,0,0,0.5); /* Stronger shadow effect */
                height: 120px; /* Fixed height to ensure proper fitting */
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Overlay for better text readability on the manuscript background */
            .main-header::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                background: rgba(0, 0, 0, 0.6);
                z-index: -1;
            }
            
            /* Text header styling */
            .text-header {
                font-family: 'Open Sans', sans-serif;
                color: #5d4037;
                border-bottom: 2px solid #8d6e63;
                padding-bottom: 15px;
                text-align: right;
                background-image: url('/assets/mujmal.png')
                font-size: 36px;
                font-weight: bold;
            }
            /* Arabic text in header */
            .main-header h1 span {
                font-size: 40px; /* Even larger for Arabic text */
                font-weight: bold;
                display: inline-block;
                margin-left: 5px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Then modify the app layout to use the new section_files_with_headings
app.layout = html.Div([
    # Header with Persian manuscript background
    html.Div([
        html.H1([
            "Mujmal al-Hikma – ",
            html.Span("مجمل الحكمة", style={'fontFamily': 'Uthman Taha Naskh, serif'})
        ], style={
            'textAlign': 'center',
            'margin': '0',
            'position': 'relative',
            'zIndex': '1',
            'fontFamily': 'Open Sans, sans-serif',
            'fontWeight': '700'
        })
    ], className='main-header'),
    
    # Main container with flex display
    html.Div([
        # Section selection area - Rock style (Left panel)
        html.Div([
            html.H3("Select a Risala:", 
                    className='sidebar-header',
                    style={
                        'marginBottom': '20px',
                        'color': '#f5f5f5',
                        'textAlign': 'left',
                        'fontFamily': 'Open Sans, sans-serif'
                    }),
            
            # Modified radio items for section selection with headings
            dcc.RadioItems(
                id='section-selector',
                options=[{'label': display_name, 'value': file} 
                         for file, display_name in section_files_with_headings],
                value=section_files_with_headings[0][0] if section_files_with_headings else None,
                labelStyle={
                    'display': 'block', 
                    'margin': '10px 0', 
                    'cursor': 'pointer',
                    'padding': '10px',
                    'borderRadius': '5px',
                    'transition': 'background-color 0.3s'
                },
                className='custom-radio'
            )
        ], className='sidebar rock-bg rock-scroll', style={
            'borderRight': '1px solid #3a3529',
            'overflowY': 'auto'
        }),
        
        # Text display area - Papyrus style (Right panel)
        html.Div([
            html.H2(id='text-header', 
                    className='text-header',
                    style={
                        'marginBottom': '20px',
                        'fontFamily': 'Open Sans, sans-serif'
                    }),
            # Container for OpenITI content
            html.Div(id='text-content', 
                    className='papyrus-bg papyrus-scroll openiti-content',
                    style={
                        'padding': '20px',
                        'borderRadius': '5px',
                        'flex': '1',
                        'overflowY': 'auto',
                        'backgroundColor': '#e8dcb5',
                        'backgroundImage': 'url("https://www.transparenttextures.com/patterns/papyrus.png")',
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                    })
        ], className='content')
    ], className='content-container'),
    
    # Footer
    html.Footer([
        html.Div([
            html.P("© Aslisho Qurboniev 2025", 
                  style={
                      'margin': '0',
                      'textAlign': 'left'
                  })
        ], className='footer-content')
    ], className='main-footer')
], className='main-container')

# The callback remains the same
@app.callback(
    [Output('text-header', 'children'),
     Output('text-content', 'children')],
    [Input('section-selector', 'value')]
)
def update_text_content(selected_file):
    if not selected_file:
        return "Welcome to the Text Viewer", "Please select a section to view its content."
    
    section_name = selected_file.replace('.txt', '')
    file_path = os.path.join("sections", selected_file)
    
    print(f"Attempting to read file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"Successfully read {len(content)} characters from {file_path}")
        
        # Convert OpenITI markdown to HTML components
        components = openiti_to_html_components(content)
        
        return f"Summary of {section_name}", components
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return f"Error: {section_name}", f"Could not read the file: {str(e)}"    
# Run the app
if __name__ == '__main__':
    print("Starting Dash app...")
    app.run(debug=True)

