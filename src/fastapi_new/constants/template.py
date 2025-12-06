TEMPLATE_MAIN = """
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files (if views folder exists)
# app.mount("/static", StaticFiles(directory="views/css"), name="static")

@app.get("/")
def main():
    return {"message": "Welcome to your FastAPI project!"}
"""

TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI View</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1>Hello from FastAPI Views! 🚀</h1>
        <script src="/static/js/main.js"></script>
    </body>
</html>
"""

TEMPLATE_CSS = """
body {
    font-family: sans-serif;
    background-color: #f0fdf4; /* Green-50 */
    color: #166534; /* Green-800 */
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}
"""

TEMPLATE_JS = """
console.log("FastAPI Views are active!");
"""