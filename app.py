from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_main_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Attempt to identify main content using common tags and classes
    main_content = soup.find(['article', 'main', 'section'], recursive=True)
    if not main_content:
        main_content = soup.body

    # Extract paragraphs and code blocks within the main content
    content = []
    for element in main_content.find_all(['p', 'pre', 'code'], recursive=True):
        if element.name == 'p':
            content.append(element.get_text(strip=True))
        elif element.name in ['pre', 'code']:
            content.append(f"\nCode:\n{element.get_text(strip=True)}\n")

    final_content = "\n\n".join(content)
    return final_content

@app.route('/')
def home():
    # Enhanced homepage with a URL input form
    return render_template_string("""
    <html>
        <head>
            <title>ReadEasy/title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.6;
                    color: #333;
                    margin: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                h1 {
                    font-size: 2em;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    width: 100%;
                    max-width: 500px;
                }
                input[type="text"] {
                    font-size: 1em;
                    padding: 8px;
                    margin-bottom: 10px;
                }
                button {
                    font-size: 1em;
                    padding: 10px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Readeasy</h1>
            <p>Enter a URL to get a simplified text version of the content:</p>
            <form action="/readeasy" method="get">
                <input type="text" name="url" placeholder="Enter URL here" required>
                <button type="submit">Get Text Version</button>
            </form>
            <p>Or, add "readeasy/" before the URL in the browser's address bar.</p>
        </body>
    </html>
    """)

@app.route('/readeasy')
def readeasy_form():
    url = request.args.get('url')
    if not url:
        return "<h1>Error:</h1><p>URL parameter missing.</p>"
    return readeasy_url(url)

@app.route('/readeasy/<path:url>')
def readeasy_url(url):
    # Ensure URL starts with http/https
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        content = extract_main_content(url)
        return render_template_string(f"""
        <html>
            <head>
                <title>Readeasy Output</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 16px;
                        line-height: 1.6;
                        color: #333;
                        margin: 20px;
                    }}
                    .content {{
                        white-space: pre-wrap;
                    }}
                </style>
            </head>
            <body>
                <div class="content">{{{{ content }}}}</div>
            </body>
        </html>
        """, content=content)
    except Exception as e:
        return f"<h1>Error:</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True)

