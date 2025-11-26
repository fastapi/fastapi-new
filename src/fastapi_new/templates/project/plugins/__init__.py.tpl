"""
Plugins Module
Contains remote and local plugins that extend application functionality.

Plugins are self-contained modules that can be:
- Downloaded from a remote registry
- Installed locally
- Dynamically loaded at runtime

Plugin Structure:
    plugins/your_plugin/
    ├── __init__.py
    ├── manifest.json   # Plugin metadata and configuration
    ├── routes.py       # Optional API endpoints
    ├── services.py     # Plugin business logic
    └── dependencies.py # Plugin dependencies

Manifest Example (manifest.json):
    {
        "name": "auth",
        "version": "1.0.0",
        "description": "Authentication plugin",
        "author": "Your Name",
        "dependencies": ["pyjwt", "passlib"],
        "auto_register": true
    }

Install a remote plugin using:
    fastapi-new addremote <plugin_name>
"""
