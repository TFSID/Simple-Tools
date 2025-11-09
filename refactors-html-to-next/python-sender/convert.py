import sys
import re
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# --- Configuration ---
GEMINI_API_URL = "http://localhost:8017/v1/generate"
GEMINI_API_KEY = "sk-e0dde619-2dd3-4018-aad1-e7f602d58534" 

# --- Create the Flask App ---
app = Flask(__name__)

# --- 1. AI Helper Function (Unchanged) ---
def call_gemini(prompt_text):
    """
    Calls your local Gemini API endpoint with the provided prompt.
    """
    headers = {
        "accept": "application/json",
        "x-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    body = {
        "prompt": prompt_text,
        "model_name": "gemini-2.5-flash-preview-05-20",
        "temperature": 0.5,
        "top_p": 0.95,
        "max_output_tokens": 65536,
        "system_instruction": "You are an expert HTML to Next.js 14 converter. You will be given raw HTML, possibly with inline CSS and JS. Your job is to convert this into a single, functional Next.js `app/page.js` component. Use 'use client' if client-side interactivity is needed. Convert <img> to <Image>, <a> to <Link> for relative paths. Convert inline `style` attributes to React's object syntax. Convert `class` to `className`.",
        "user_metadata": ""
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("output_text", "Error: 'output_text' not found in response.")
    except requests.exceptions.RequestException as e:
        return f"API Call Failed: {e}"

# --- 2. Regex Filters (Unchanged) ---
def apply_basic_regex(html_content):
    """
    Applies simple, safe regex substitutions before sending to the AI.
    """
    content = re.sub(r'class="', 'className="', html_content)
    content = re.sub(r'for="', 'htmlFor="', html_content)
    content = re.sub(r'', r'{/* \1 */}', content, flags=re.DOTALL)
    return content

# --- 3. Main Conversion Logic (Unchanged) ---
def convert_html_to_nextjs(raw_html):
    """
    The main processing pipeline.
    """
    soup = BeautifulSoup(raw_html, 'html.parser')
    scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]
    styles = [link.get('href') for link in soup.find_all('link', rel='stylesheet') if link.get('href')]
    processed_html = apply_basic_regex(str(soup))
    
    prompt = f"""
    Please convert the following HTML into a single Next.js 14 'app/page.js' component.
    Context:
    - External scripts: {scripts}
    - External stylesheets: {styles}
    Conversion Rules:
    1. Create a functional React component.
    2. Add 'use client' if interactivity is implied.
    3. Convert <img> to <Image> from 'next/image'.
    4. Convert relative <a> to <Link> from 'next/link'.
    5. Convert `style` attributes to JSX style objects.
    6. Ensure all attributes are JSX-compliant (className, htmlFor).
    7. Handle inline <script> and <style> tags (e.g., in useEffect).

    HTML to Convert:
    ```html
    {processed_html}
    ```
    Converted Next.js Component:
    """
    
    converted_code = call_gemini(prompt)
    return converted_code

# --- 4. Flask API Endpoint ---
@app.route('/convert', methods=['POST'])
def handle_conversion():
    """
    This is the new API endpoint that Bun will call.
    """
    try:
        # Get the raw HTML from the POST request body
        input_html = request.data.decode('utf-8')
        
        if not input_html:
            return "No HTML content provided.", 400

        # Run the same conversion logic
        result = convert_html_to_nextjs(input_html)
        
        # Return the result as plain text
        return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return f"Error during conversion: {e}", 500

# --- Main execution ---
if __name__ == "__main__":
    # Run the Flask server
    print("Starting Python conversion server on http://localhost:5003")
    app.run(port=5003, debug=True)