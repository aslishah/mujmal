from dash_renderer import export_html
from your_dash_app import app  # Import your dash app

# Export to static HTML
html = export_html(app)
with open("index.html", "w") as f:
    f.write(html)
