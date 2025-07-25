"""
Simple Flask server for the AI Model Tracker.

This app serves the static dashboard (HTML/JS/CSS) and exposes the
models.json data for local development.  When deployed on GitHub Pages,
the server is not required; the front‑end fetches the JSON directly.
"""

from flask import Flask, send_from_directory, abort
import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(ROOT_DIR, 'public')
DATA_DIR = os.path.join(ROOT_DIR, 'data')

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path: str):
    """Serve static files from the public directory."""
    file_path = os.path.join(PUBLIC_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(PUBLIC_DIR, path)
    # Fallback: return 404
    abort(404)


@app.route('/data/models.json')
def serve_models():
    """Expose the models JSON file."""
    return send_from_directory(DATA_DIR, 'models.json')


if __name__ == '__main__':
    # Run the development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)