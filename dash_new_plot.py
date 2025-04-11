# Mujmal al-hikma App - published version
# English text is converted from Markdown to html
# Persian's OpenITI mArkdown is also converted to html

import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import re
import json
from dash.exceptions import PreventUpdate

# Get the directory and make sure it is absolute
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Define sections directory relative to the script location
sections_dir = os.path.join(script_dir, "sections")
print(f"Sections directory: {sections_dir}")

# Initialize the Dash app
app = dash.Dash(__name__,
                # requests_pathname_prefix='/<mujmal>/', #these were used for github action
                # routes_pathname_prefix='/<mujmal>/', #this was also for github actions
                suppress_callback_exceptions=True,
                title='Mujmal al-Hikma - Epistles of the Ikhwan al-Safa', 
                external_stylesheets=[
                    # Google Fonts for Sans Serif
                    "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap"
                ])
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
server = app.server
# Modify the get_section_files function to also return headings
def get_section_files(sections_dir=sections_dir): #use the absolute path by default
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
        if filename == "Preface.txt":
            return 0  # Place Preface first
        elif "Risala" in filename:
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
    Convert OpenITI markdown to Dash HTML components, handling both Arabic/Persian and English text.
    """
    # Create a list to store HTML components
    components = []

    # Common style with Terafik font for Arabic/Persian
    terafik_style = {'fontFamily': 'Terafik, sans-serif', 'direction': 'rtl', 'textAlign': 'right'}
    
    # Style for English text
    english_style = {'fontFamily': 'Open Sans, sans-serif', 'direction': 'ltr', 'textAlign': 'left'}
    
    # Flag to track if we're in the English translation section
    in_english_section = False
    
    # Split the text into sections
    sections = text.split("--- ENGLISH TRANSLATION ---")
    
    # Process Arabic section (OpenITI Markdown)
    if len(sections) > 0:
        arabic_text = sections[0]
        arabic_lines = arabic_text.split('\n')
        
        for line in arabic_lines:
            # Skip empty lines
            if not line.strip():
                components.append(html.Br())
                continue
            
            # Process headers (### | syntax)
            if line.startswith('### | '):
                content = line.replace('### | ', '')
                components.append(html.H1(content, className='openiti-h1', style=terafik_style))
                continue
            
            if line.startswith('### || '):
                content = line.replace('### || ', '')
                components.append(html.H2(content, className='openiti-h2', style=terafik_style))
                continue
                
            if line.startswith('### ||| '):
                content = line.replace('### ||| ', '')
                components.append(html.H3(content, className='openiti-h3', style=terafik_style))
                continue
            
            # Process comments (% syntax)
            if line.startswith('%'):
                content = line[1:].strip()
                components.append(html.Div(content, className='openiti-comment', style=terafik_style))
                continue

            # Process regular paragraphs
            components.append(html.P(line, style=terafik_style))
    
    # Add separator if English section exists
    if len(sections) > 1:
        components.append(html.Hr(style={'margin': '30px 0'}))
        components.append(html.H2("English Translation", style={'textAlign': 'center', 'margin': '20px 0'}))
        components.append(html.Hr(style={'margin': '30px 0'}))
        
        # Process English section (Standard Markdown)
        english_text = sections[1]
        
        # Create a div with the English style that contains the Markdown content
        components.append(
            html.Div([
                dcc.Markdown(
                    english_text,
                    dangerously_allow_html=True,
                )
            ], style=english_style)
        )
    
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
                src: url('/assets/terafik.ttf') format('truetype');
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
                padding: 5px;
                margin: 2px 0;
                border-radius: 5px;
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
                font-family: 'Terafik', serif;
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
                font-weight: regular;
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
                background-size: 75%;
                background-repeat: no-repeat; /* Prevents the image from repeating */
                background-position: left;
                position: relative;
                border-bottom: 3px solid #3a3529; /* Darker border at bottom */
                box-shadow: 0 4px 12px rgba(0,0,0,0.5); /* Stronger shadow effect */
                height: 50px; /* Fixed height to ensure proper fitting */
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.15)), url('/assets/mujmal.png');
                background-size: contain;
                background-position: left;
                background-repeat: no-repeat;
                background-color: #e8dcb5;   
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
            .main-header::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(ellipse at center, transparent 70%, #e8dcb5 100%);
                pointer-events: none;
}
            /* Text header styling */
            .text-header {
                font-family: 'Open Sans', sans-serif;
                color: #5d4037;
                border-bottom: 1px solid #8d6e63; /* Thinner border */
                padding-bottom: 10px; /* Reduced padding */
                text-align: right;
                font-size: 24px; /* Smaller font size (was 36px) */
                font-weight: regular;
                margin-bottom: 10px; /* Reduced margin */
                min-height: auto; /* Allow it to shrink to content */
            }
            /* Arabic text in header */
            .main-header h1 span {
                font-size: 36px; /* Even larger for Arabic text */
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
    # Header with Persian manuscript background and tabs
    html.Div([
        # Flex container for header content
        html.Div([
            # Title with original styling
            html.H1([
                " ",
                html.Span("مجمل الحكمة", style={'fontFamily': 'Neirizi, serif'})
            ], style={
                'textAlign': 'right',
                'margin': '30px',
                'position': 'relative',
                'zIndex': '1',
                'fontFamily': 'Open Sans, sans-serif',
                'fontWeight': '600',
                'flex': '1',  
                'color': '#FFD700',
            }),
            
            # Tabs to the right of the title
            html.Div([
                dcc.Tabs(id='header-tabs', value=None, children=[
                    dcc.Tab(label='Rasaʾil Ikhwan al-Safaʾ', value='tab-manuscript-1', 
                           style={
                               'padding': '5px', 
                               'fontSize': '18px',
                               'backgroundColor': '#739480',
                               'color': '#e8dcb5',
                               'border': 'none',
                               'marginRight': '10px',
                               'boxShadow': '0 2px 4px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',  # Ensure it fits the text
                               'whiteSpace': 'nowrap', 
                           },
                           selected_style={
                               'padding': '5px', 
                               'fontSize': '18px', 
                               'fontWeight': 'bold',
                               'backgroundColor': 'transparent',
                               'color': '#e8dcb5', 
                               'borderBottom': '2px solid #FFD700',
                               'boxShadow': '0 1px 2px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',
                               'whiteSpace': 'nowrap',
                           }),
                           dcc.Tab(label='Mujmal al-Hikma', value='tab-manuscript-2', 
                           style={
                               'padding': '5px', 
                               'fontSize': '18px',
                               'backgroundColor': '#8d6e63',
                               'color': '#e8dcb5',
                               'border': 'none',
                               'marginRight': '10px',
                               'boxShadow': '0 2px 4px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',
                               'whiteSpace': 'nowrap', 
                           },
                           selected_style={
                               'padding': '5px', 
                               'fontSize': '18px', 
                               'fontWeight': 'bold',
                               'backgroundColor': 'transparent',
                               'color': '#e8dcb5', 
                               'borderBottom': '2px solid #FFD700',
                               'boxShadow': '0 1px 2px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',
                               'whiteSpace': 'nowrap',
                           }),
                    dcc.Tab(label='Visualization', value='tab-visualization', 
                           style={
                               'padding': '5px', 
                               'fontSize': '18px',
                               'backgroundColor': '#7d0005',
                               'color': '#e8dcb5',
                               'border': 'none',
                               'marginRight': '10px',
                               'boxShadow': '0 2px 4px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',
                               'whiteSpace': 'nowrap', 
                           },
                           selected_style={
                               'padding': '5px', 
                               'fontSize': '18px', 
                               'fontWeight': 'bold',
                               'backgroundColor': 'red',
                               'color': '#e8dcb5',  
                               'borderBottom': '2px solid #FFD700',
                               'boxShadow': '0 1px 2px rgba(0,0,0,0.5)',
                               'width': 'auto',
                               'minWidth': 'fit-content',
                               'whiteSpace': 'nowrap', 
                           }),

                               # New About tab
                    dcc.Tab(label='About', value='tab-about',
                        style={
                            'padding': '5px',
                            'fontSize': '18px',
                            'backgroundColor': 'rgba(0,0,0,0.3)',
                            'color': '#e8dcb5',
                            'border': 'none',
                            'borderRadius': '5px',
                            'marginRight': '10px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.5)',
                            'width': 'auto',
                            'direction': 'ltr',
                            'minWidth': 'fit-content',
                            'whiteSpace': 'nowrap',
                        },
                        selected_style={
                            'padding': '5px',
                            'fontSize': '18px', 
                            'fontWeight': 'bold',
                            'backgroundColor': 'rgba(0,0,0,0.5)',
                            'color': '#FFD700',
                            'border': 'none',
                            'borderRadius': '5px',
                            'marginRight': '10px',
                            'boxShadow': '0 1px 2px rgba(0,0,0,0.5)',
                            'width': 'auto',
                            'minWidth': 'fit-content',
                            'whiteSpace': 'nowrap',
                        }),
                    
                ], style={
                    'fontFamily': 'Open Sans, sans-serif',
                    'height': '30px',
                    'backgroundColor': 'transparent',
                    'borderBottom': 'none',
                    'display': 'flex',
                })
            ], style={
                'marginRight': '20px',
                'alignSelf': 'center',
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',  # Keep as row to place tabs to the right
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'width': '100%',
        })
    ], className='main-header'),
    
    # Main container with flex display
    html.Div([
        # Section selection area - Rock style (Left panel)
        html.Div([
            # Add search functionality at the top
            html.Div([
                html.H3("Search within the epistles:", 
                        className='sidebar-header',
                        style={'marginBottom': '20px', 'color': '#f5f5f5'}),
                
                # Search input
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='...Enter search term',
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': 'none',
                        'backgroundColor': '#e8dcb5',
                        'marginBottom': '10px',
                        'direction': 'rtl',
                        'textAlign': 'right'
                    }
                ),
                
                # Search button
                html.Button('Search', 
                            id='search-button', 
                            style={
                                'width': '100%',
                                'padding': '10px',
                                'borderRadius': '5px',
                                'border': 'none',
                                'backgroundColor': '#8d6e63',
                                'color': 'white',
                                'cursor': 'pointer',
                                'marginBottom': '20px'
                            }),
                            
                # Search results container moved here - directly under the search button
                html.Div(id='search-results', 
                         style={
                             'marginTop': '10px',
                             'maxHeight': '300px',
                             'overflowY': 'auto',
                             'color': '#3e2723'
                         })
            ], style={'marginBottom': '30px'}),
            
            # Then the section selector
            html.H3("Select a Risala:", 
                    className='sidebar-header',
                    style={
                        'marginBottom': '20px',
                        'marginTop': '0px',
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
                    'margin': '2px 0', 
                    'cursor': 'pointer',
                    'padding': '2px',
                    'borderRadius': '2px',
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
            html.H3(id='text-header', 
                    className='text-header',
                    style={
                        'marginBottom': '10px',
                        'marginTop': '0px',
                        'fontFamily': 'Open Sans, sans-serif',
                        'fontSize': '18px',
                        'padding': '0px 0',
                        'lineHeight': '1.5'
                    }),
            # Container for OpenITI content
            html.Div(id='text-content', 
                    className='papyrus-bg papyrus-scroll openiti-content',
                    style={
                        'padding': '30px',
                        'borderRadius': '0px',
                        'flex': '1',
                        'overflowY': 'auto',
                        'backgroundColor': '#e8dcb5',
                        'backgroundImage': 'url("https://www.transparenttextures.com/patterns/papyrus.png")',
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                    })
        ], className='content')
    ], className='content-container', id='main-content-container'),
    
    # Add a hidden container for the modal content
    html.Div(id='modal-container', style={'display': 'none'}),
    
    # Footer
    html.Footer([
        html.Div([
            html.P(" By Aslisho Qurboniev (2025), CC-BY-SA 4.0", 
                  style={
                      'margin': '0',
                      'textAlign': 'left'
                  })
        ], className='footer-content')
    ], className='main-footer')
], className='main-container')

# Add a callback to handle tab clicks and show modal content
@app.callback(
    [Output('modal-container', 'children'),
     Output('modal-container', 'style')],
    [Input('header-tabs', 'value')]
)
def show_modal_content(tab_value):
    # If no tab is selected or if About tab is selected, hide the modal
    if tab_value is None or tab_value == 'tab-about':
        return None, {'display': 'none'}
    
    # If manuscript tab is selected
    if tab_value == 'tab-manuscript-1':
        # IIIF manifest URL
        manifest_url = "https://iiif.bodleian.ox.ac.uk/iiif/manifest/12fcf5c5-2bb0-4e0e-b8a9-7620bd6bec90.json"
        modal_content = html.Div([
            # Close button
            html.Button("×", id='close-modal', style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'border': 'none',
                'background': 'none',
                'cursor': 'pointer',
                'zIndex': '1000',
                'color': '#5d4037'
            }),
            
            # Modal title
            html.H2("Rasāʾil Ikhwān al-Ṣafāʾ, Bodleian Library MS. Laud Or. 260 (CC BY-NC 4.0)", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'color': '#5d4037'
            }),
            
            # Mirador viewer (replaced Universal Viewer)
            html.Iframe(
            src=f"https://projectmirador.org/embed/?iiif-content={manifest_url}",
            style={
                'width': '100%',
                'height': 'calc(100vh - 150px)',
                'border': 'none',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
            }
        )
        ], style={
            'position': 'relative',
            'padding': '20px',
            'backgroundColor': '#f5f5f5',
            'borderRadius': '5px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'width': '90%',
            'maxWidth': '1200px',
            'margin': '0 auto',
            'height': '90vh',
            'overflowY': 'auto'
        })
        
        return modal_content, {
            'display': 'flex',
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.7)',
            'zIndex': '1000',
            'justifyContent': 'center',
            'alignItems': 'center'
        }
    # If second manuscript tab is selected (new tab)
    elif tab_value == 'tab-manuscript-2':
        # IIIF manifest URL for second manuscript - use a different manuscript
        manifest_url = "https://content.staatsbibliothek-berlin.de/dc/1690824786/manifest"  # Mujmal Berlin
        
        modal_content = html.Div([
            # Close button
            html.Button("×", id='close-modal', style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'border': 'none',
                'background': 'none',
                'cursor': 'pointer',
                'zIndex': '1000',
                'color': '#5d4037'
            }),
            
            # Modal title
            html.H2("Mujmal al-Hikma, mss. Berlin Diez A oct. 132 (Public Domain Mark 1.0)", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'color': '#5d4037'
            }),
            
            # Mirador Viewer iframe
            html.Iframe(
                src=f"https://projectmirador.org/embed/?iiif-content={manifest_url}",
                style={
                    'width': '100%',
                    'height': 'calc(100vh - 150px)',
                    'border': 'none',
                    'borderRadius': '5px',
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                }
            )
        ], style={
            'position': 'relative',
            'padding': '20px',
            'backgroundColor': '#f5f5f5',
            'borderRadius': '5px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'width': '90%',
            'maxWidth': '1200px',
            'margin': '0 auto',
            'height': '90vh',
            'overflowY': 'auto'
        })
        
        return modal_content, {
            'display': 'flex',
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.7)',
            'zIndex': '1000',
            'justifyContent': 'center',
            'alignItems': 'center'
        }
    # If visualization tab is selected
    elif tab_value == 'tab-visualization':
        # Path to the HTML visualization file
        viz_path = "assets/visualization.html"
        
        modal_content = html.Div([
            # Close button
            html.Button("×", id='close-modal', style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'border': 'none',
                'background': 'none',
                'cursor': 'pointer',
                'zIndex': '1000',
                'color': '#5d4037'
            }),
            
            # Modal title
            html.H2("The Length of the Epistles in Mujmal al-Hikma", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'color': '#5d4037'
            }),
            
            # HTML visualization iframe
            html.Iframe(
                src=viz_path,
                style={
                    'width': '100%',
                    'height': 'calc(100vh - 150px)',
                    'border': 'none',
                    'borderRadius': '5px',
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                }
            )
        ], style={
            'position': 'relative',
            'padding': '20px',
            'backgroundColor': '#f5f5f5',
            'borderRadius': '5px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'width': '90%',
            'maxWidth': '1200px',
            'margin': '0 auto',
            'height': '90vh',
            'overflowY': 'auto'
        })
        
        return modal_content, {
            'display': 'flex',
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.7)',
            'zIndex': '1000',
            'justifyContent': 'center',
            'alignItems': 'center'
        }
    
    # Default case
    return None, {'display': 'none'}

# Add a callback to close the modal when the close button is clicked
@app.callback(
    [Output('header-tabs', 'value'),
     Output('modal-container', 'style', allow_duplicate=True)],
    [Input('close-modal', 'n_clicks')],
    prevent_initial_call=True
)
def close_modal(n_clicks):
    if n_clicks:
        return None, {'display': 'none'}
    return dash.no_update, dash.no_update

# The callback remains the same
@app.callback(
    [Output('text-header', 'children'),
     Output('text-content', 'children')],
    [Input('section-selector', 'value'),
     Input('header-tabs', 'value')]
)
def update_text_content(selected_file, selected_tab):
    # Get the context of the callback to determine which input triggered it
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    # If the About tab was clicked
    if selected_tab == 'tab-about':
        # Path to the about.md file in the assets folder
        about_file_path = os.path.join(script_dir, 'assets', 'about.md')
        try:
            # Check if the file exists
            if os.path.exists(about_file_path):
                # Read the markdown file
                with open(about_file_path, 'r', encoding='utf-8') as file:
                    about_markdown = file.read()
            else:
                # If file doesn't exist, provide default content
                print(f"About file not found at: {about_file_path}")
                about_markdown = """
# About Mujmal al-Hikma

This application presents the *Mujmal al-Hikma* (Summary of Wisdom), a collection of epistles attributed to the Ikhwan al-Safa (Brethren of Purity).

The Ikhwan al-Safa were a secret brotherhood of philosophers in Basra, Iraq during the 10th century CE. They produced an encyclopedia of 52 epistles covering subjects from mathematics and logic to spirituality and mysticism.

## About This Project

This digital edition was created by Aslisho Qurboniev (2025) as part of research on the Ikhwan al-Safa corpus. The text is presented in its original Persian with English translations.

The application features:

- Original Persian text with English translations
- Manuscript viewers for examining historical documents
- Data visualizations of textual analysis
- Full-text search capabilities

## License

This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0).

## Contact

For questions or feedback about this project, please contact Aslisho Qurboniev at [example@email.com](mailto:example@email.com).
                """
            
            # Create a container with the markdown content
            about_content = html.Div([
                dcc.Markdown(
                    about_markdown,
                    dangerously_allow_html=True,
                    style={
                        'fontSize': '16px',
                        'lineHeight': '1.6',
                        'color': '#3e2723',  # Same brown color used elsewhere
                        'fontFamily': 'Open Sans, sans-serif',  # Same font as other English text
                        'padding': '20px',
                        'direction': 'ltr',
                        'textAlign': 'left'
                    }
                )
            ], style={
                'backgroundColor': '#e8dcb5',  # Same papyrus background color
                'backgroundImage': 'url("https://www.transparenttextures.com/patterns/papyrus.png")',  # Same texture
                'borderRadius': '5px',

                'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',  # Same shadow effect
                'padding': '20px',
                'overflowY': 'auto',


                'direction': 'ltr',
                'textAlign': 'left',
                'flex': '1',  # Take up available space like other content
                'height': '100%',  # Full height like other content
                'fontFamily': 'Open Sans, sans-serif'  # Consistent font family
            })
            
            return "About this app", about_content
            
        except Exception as e:


            print(f"Error handling about tab: {str(e)}")
            # Provide a fallback content in case of error
            error_content = html.Div([
                html.H1("About this app"),
                html.P(f"Error loading about page: {str(e)}"),
                html.P("Please check if the about.md file exists in the assets folder.")
            ])
            return "About this app", error_content
    
    # If a section was selected
    elif selected_file:
        section_name = selected_file.replace('.txt', '')


        file_path = os.path.join(sections_dir, selected_file)
        
        print(f"Attempting to read file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")

        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"Successfully read {len(content)} characters from {file_path}")
            
            # Convert OpenITI markdown to HTML components
            components = openiti_to_html_components(content)
            

            return f"{section_name}", components
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")


            return f"Error: {section_name}", f"Could not read the file: {str(e)}"
    
    # Default case - use Preface.txt
    else:
        default_file = 'Preface.txt'
        section_name = default_file.replace('.txt', '')
        file_path = os.path.join(sections_dir, default_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convert OpenITI markdown to HTML components
            components = openiti_to_html_components(content)
            
            return f"{section_name}", components
        except Exception as e:
            print(f"Error reading default file {file_path}: {str(e)}")
            return "Welcome to the Text Viewer", "Please select a section to view its content"
@app.callback(
    Output('section-selector', 'value'),
    [Input({'type': 'search-result', 'index': ALL}, 'n_clicks'),
     Input({'type': 'match-context', 'index': ALL}, 'n_clicks_timestamp')],
    prevent_initial_call=True
)
def open_search_result(result_clicks, context_clicks):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        raise PreventUpdate
    
    # Get the triggered component's ID
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        # Parse the ID to get the file path
        id_dict = json.loads(triggered_id)
        if 'index' in id_dict:
            file_path = id_dict['index']
            print(f"Opening file: {file_path}")
            return file_path
    except:
        # If there's an error parsing the ID, try using regex
        match = re.search(r'"index":"([^"]+)"', triggered_id)
        if match:
            file_path = match.group(1)
            print(f"Opening file using regex: {file_path}")
            return file_path
    
    # If we couldn't determine which file to open
    raise PreventUpdate
@app.callback(
    Output('search-results', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('search-input', 'value')]
)
def simple_search(n_clicks, search_term):
    # Don't run on initial load
    if n_clicks is None or not search_term:
        return []
    
    # Debug output
    print(f"Searching for: '{search_term}'")
    
    # Initialize results
    results = []
    total_matches = 0
    
    # Get all text files
    try:
        section_files = [file for file, _ in section_files_with_headings]
        
        # Search through each file
        for file in section_files:
            file_path = os.path.join(sections_dir, file)
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple text search
                if search_term in content:
                    # Get display name for the file
                    display_name = next((display for f, display in section_files_with_headings if f == file), file)
                    
                    # Find matches with context
                    matches = []
                    all_matches = list(re.finditer(re.escape(search_term), content))
                    total_matches += len(all_matches)
                    
                    for match in all_matches[:3]:  # Limit to first 3 matches per file
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end]
                        
                        # Highlight the match by adding HTML tags
                        match_text = content[match.start():match.end()]
                        highlighted = context.replace(
                            match_text, 
                            f'<span style="background-color: yellow; color: black">{match_text}</span>'
                        )
                        matches.append(highlighted)
                    
                    # Add to results
                    if matches:
                        results.append({
                            'file': file,
                            'display_name': display_name,
                            'matches': matches,
                            'match_count': len(all_matches)
                        })
            except Exception as e:
                print(f"Error searching file {file_path}: {str(e)}")
        
        # Format results for display
        formatted_results = []
        
        if results:
            # Add a summary header showing total results
            formatted_results.append(
                html.H3(
                    f"Found {total_matches} matches in {len(results)} risalas",
                    style={
                        'color': '#e8dcb5',
                        'marginBottom': '15px',
                        'borderBottom': '1px solid #e8dcb5',
                        'paddingBottom': '5px'
                    }
                )
            )
            
            # Sort results by match count (most matches first)
            results.sort(key=lambda x: x['match_count'], reverse=True)
            

            for i, result in enumerate(results):
                # Create clickable result
                formatted_results.append(
                    html.Div([
                        html.Button(  # Use a button instead of a div for better click handling
                            f"{result['display_name']} ({result['match_count']} matches)",
                            id={
                                'type': 'search-result-button',
                                'index': i,  # Use a simple numeric index
                                'file': result['file']  # Store the file path as a separate property
                            },
                            style={
                                'color': '#3e2723',
                                'cursor': 'pointer',
                                'textAlign': 'left',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'textDecoration': 'underline',
                                'fontWeight': 'bold',
                                'fontSize': '16px',
                                'width': '100%',
                                'padding': '8px',
                                'marginBottom': '5px'
                            }
                        ),
                        html.Div([
                            html.P(
                                dcc.Markdown(f"...{match}...", dangerously_allow_html=True),
                                style={
                                    'direction': 'rtl', 
                                    'textAlign': 'right', 
                                    'backgroundColor': 'rgba(232, 220, 181, 0.2)',
                                    'padding': '8px',
                                    'borderRadius': '5px',
                                    'margin': '5px 0'
                                }
                            ) for match in result['matches']
                        ]),
                        html.Hr(style={'borderColor': 'rgba(62, 39, 35, 0.3)'})
                    ],
                    style={
                        'marginBottom': '15px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'backgroundColor': 'rgba(232, 220, 181, 0.1)'
                    })
                )
        else:
            formatted_results = [html.P("No matches found", style={'color': '#e8dcb5'})]
        
        return formatted_results
        
    except Exception as e:
        print(f"Error in search function: {str(e)}")
        return [html.P(f"Error: {str(e)}", style={'color': '#e8dcb5'})]
@app.callback(
    Output('section-selector', 'value', allow_duplicate=True),


    [Input({'type': 'search-result-button', 'index': ALL, 'file': ALL}, 'n_clicks')],
    prevent_initial_call=True
)

def open_search_result(n_clicks_list):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        raise PreventUpdate
    
    # Get the triggered component's ID directly from callback_context
    triggered_id = ctx.triggered_id
    
    if triggered_id and isinstance(triggered_id, dict) and 'file' in triggered_id:
        file_path = triggered_id['file']
        print(f"Opening file: {file_path}")
        return file_path
    print("Could not determine which file to show")
    raise PreventUpdate
@app.callback(
    Output('header-tabs', 'value', allow_duplicate=True),
    [Input('section-selector', 'value')],
    prevent_initial_call=True
)
def clear_tab_selection(selected_section):
    # If a section is selected, clear the tab selection
    if selected_section:
        return None
    raise PreventUpdate
current_dir =os.getcwd()
print(current_dir)
# Run the app
if __name__ == '__main__':
    print("Starting Dash app...")
    app.run(debug=True, host='127.0.0.1', port=8080)

# This text shows that the code hasn't been modifed (18:56)
#This text shows that the code hasn't been modifed (21:54) search terms implemented
# trying to improve highlighting funtion and clickability of search results 29 march 11:56

#new changes
##new change s 22
## this line should go
