import sys
import re
import requests
import json
from bs4 import BeautifulSoup

# --- Configuration ---
GEMINI_API_URL = "http://localhost:8017/v1/generate"
# This is the key from your example.
# In a real app, read this from an environment variable.
GEMINI_API_KEY = "sk-e0dde619-2dd3-4018-aad1-e7f602d58534" 

# --- 1. AI Helper Function ---
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
        "temperature": 0.5, # Lowered for more predictable code generation
        "top_p": 0.95,
        "max_output_tokens": 65536,
        "system_instruction": "You are an expert HTML to Next.js 14 converter. You will be given raw HTML, possibly with inline CSS and JS. Your job is to convert this into a single, functional Next.js `app/page.js` component. Use 'use client' if client-side interactivity is needed. Convert <img> to <Image>, <a> to <Link> for relative paths. Convert inline `style` attributes to React's object syntax. Convert `class` to `className`.",
        "user_metadata": ""
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(body))
        response.raise_for_status() # Raise an exception for bad status codes
        
        response_data = response.json()
        return response_data.get("output_text", "Error: 'output_text' not found in response.")
        
    except requests.exceptions.RequestException as e:
        # Send error message to stdout so Bun can see it
        return f"API Call Failed: {e}"

# --- 2. Regex Filters ---
def apply_basic_regex(html_content):
    """
    Applies simple, safe regex substitutions before sending to the AI.
    This helps the AI focus on the harder tasks.
    """
    # Convert class to className
    content = re.sub(r'class="', 'className="', html_content)
    # Convert for to htmlFor
    content = re.sub(r'for="', 'htmlFor="', content)
    # Convert HTML comments to JSX comments
    content = re.sub(r'', r'{/* \1 */}', content, flags=re.DOTALL)
    
    return content

# --- 3. Main Conversion Logic ---
def convert_html_to_nextjs(raw_html):
    """
    The main processing pipeline.
    """
    
    # --- Step 1: Read and parse HTML (Your "Read local links") ---
    # We use BeautifulSoup to find scripts/styles, not to merge, 
    # but to give the AI context about them.
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]
    styles = [link.get('href') for link in soup.find_all('link', rel='stylesheet') if link.get('href')]

    # --- Step 2: Apply basic regex (Your "Regex filters") ---
    processed_html = apply_basic_regex(str(soup))
    
    # --- Step 3: Build the AI Prompt (Your "Gemini API integration") ---
    prompt = f"""
    Please convert the following HTML into a single Next.js 14 'app/page.js' component.

    **Context:**
    - The page references these external scripts: {scripts}
    - The page references these external stylesheets: {styles}
    - Please assume these are handled or import them if necessary.

    **Conversion Rules:**
    1.  Create a functional React component.
    2.  Add 'use client' at the top if any interactivity (like from <script> tags or event handlers) is implied.
    3.  Convert all `<img>` tags to `<Image>` from `next/image`. Remember to add `import Image from 'next/image'`.
    4.  Convert all relative `<a>` tags to `<Link>` from `next/link`. Remember to add `import Link from 'next/link'`.
    5.  All `style` attributes must be converted to JSX style objects (e.g., style="font-size: 10px;" becomes style={{fontSize: '10px'}}).
    6.  Ensure all `className` and `htmlFor` attributes are correct.
    7.  Handle inline `<script>` and `<style>` tags by converting their logic into React (e.g., `useEffect`) or CSS Modules/global.css, respectively. For this task, just do your best to convert any inline JS to a useEffect hook.

    **HTML to Convert:**
    ```html
    {processed_html}
    ```

    **Converted Next.js Component:**
    """
    
    # --- Step 4: Call AI and get response ---
    converted_code = call_gemini(prompt)
    return converted_code

# --- Main execution ---
if __name__ == "__main__":
    # Read all content from standard input (piped from Bun)
    input_html = sys.stdin.read()
    
    # Run the conversion
    result = convert_html_to_nextjs(input_html)
    
    # Print the final result to standard output
    # Bun will read this!
    print(result)