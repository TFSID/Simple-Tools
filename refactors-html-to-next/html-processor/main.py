import os
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json


class HTMLMergerWithGemini:
    def __init__(self, api_url, api_key):
        """
        Initialize dengan Gemini API credentials
        
        Args:
            api_url: URL endpoint Gemini API (e.g., 'http://localhost:8017/v1/generate')
            api_key: API key untuk autentikasi
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'accept': 'application/json',
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
    
    def call_gemini_api(self, prompt, system_instruction="", temperature=1, top_p=0.95, max_tokens=65536):
        """
        Memanggil Gemini API untuk pemrosesan text
        
        Args:
            prompt: Prompt yang akan dikirim ke Gemini
            system_instruction: Instruksi sistem untuk Gemini
            temperature: Kreativitas respons (0-2)
            top_p: Nucleus sampling parameter
            max_tokens: Maksimum token output
            
        Returns:
            Response text dari Gemini
        """
        payload = {
            "prompt": prompt,
            "model_name": "gemini-2.5-flash-preview-05-20",
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_tokens,
            "system_instruction": system_instruction,
            "user_metadata": ""
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get('output_text', '')
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def read_html_file(self, filepath):
        """Membaca file HTML dari local"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return None
    
    def read_local_resource(self, filepath, base_path):
        """Membaca resource lokal (CSS/JS)"""
        try:
            full_path = os.path.join(base_path, filepath)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading resource {filepath}: {e}")
            return None
    
    def merge_html_with_resources(self, html_content, base_path):
        """
        Menggabungkan HTML dengan semua CSS dan JS lokal
        
        Args:
            html_content: Konten HTML sebagai string
            base_path: Path dasar untuk mencari file lokal
            
        Returns:
            HTML yang sudah digabung dengan semua resource lokal
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Merge CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href and not href.startswith(('http://', 'https://', '//', 'data:')):
                css_content = self.read_local_resource(href, base_path)
                if css_content:
                    # Buat style tag baru
                    style_tag = soup.new_tag('style')
                    style_tag.string = f"\n/* Merged from: {href} */\n{css_content}\n"
                    link.replace_with(style_tag)
                    print(f"✓ Merged CSS: {href}")
        
        # Merge JS files
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if src and not src.startswith(('http://', 'https://', '//', 'data:')):
                js_content = self.read_local_resource(src, base_path)
                if js_content:
                    # Buat script tag baru tanpa src
                    new_script = soup.new_tag('script')
                    new_script.string = f"\n/* Merged from: {src} */\n{js_content}\n"
                    # Preserve attributes kecuali src
                    for attr, value in script.attrs.items():
                        if attr != 'src':
                            new_script[attr] = value
                    script.replace_with(new_script)
                    print(f"✓ Merged JS: {src}")
        
        return str(soup)
    
    def apply_regex_filters(self, content, filters):
        """
        Menerapkan regex filters ke konten
        
        Args:
            content: String konten yang akan difilter
            filters: List of tuples (pattern, replacement)
            
        Returns:
            Konten yang sudah difilter
        """
        for pattern, replacement in filters:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        return content
    
    def optimize_with_gemini(self, content, task_description):
        """
        Menggunakan Gemini untuk mengoptimasi atau mengisi bagian yang kurang
        
        Args:
            content: Konten yang akan dioptimasi
            task_description: Deskripsi task yang ingin dilakukan Gemini
            
        Returns:
            Konten yang sudah dioptimasi
        """
        prompt = f"""Task: {task_description}

Content to process:
{content}

Please provide the optimized/completed version."""
        
        print(f"🤖 Calling Gemini API for: {task_description}")
        result = self.call_gemini_api(prompt, system_instruction="You are a helpful assistant that optimizes and completes web content.")
        
        if result:
            print(f"✓ Gemini processing completed")
            return result
        else:
            print(f"⚠ Gemini processing failed, returning original content")
            return content
    
    def process_html_file(self, input_file, output_file, regex_filters=None, gemini_tasks=None):
        """
        Proses lengkap: baca HTML, merge resources, apply filters, optimize dengan Gemini
        
        Args:
            input_file: Path ke file HTML input
            output_file: Path ke file HTML output
            regex_filters: List of (pattern, replacement) tuples
            gemini_tasks: List of task descriptions untuk Gemini processing
        """
        print(f"📂 Reading HTML file: {input_file}")
        html_content = self.read_html_file(input_file)
        
        if not html_content:
            print("❌ Failed to read HTML file")
            return False
        
        # Get base path untuk resource lokal
        base_path = os.path.dirname(os.path.abspath(input_file))
        
        # Step 1: Merge local resources
        print("\n🔗 Merging local CSS and JS files...")
        merged_content = self.merge_html_with_resources(html_content, base_path)
        
        # Step 2: Apply regex filters
        if regex_filters:
            print(f"\n🔍 Applying {len(regex_filters)} regex filters...")
            merged_content = self.apply_regex_filters(merged_content, regex_filters)
            print("✓ Regex filters applied")
        
        # Step 3: Optimize dengan Gemini (untuk bagian-bagian kecil)
        if gemini_tasks:
            print(f"\n🤖 Processing with Gemini ({len(gemini_tasks)} tasks)...")
            for task in gemini_tasks:
                # Extract bagian yang perlu diproses berdasarkan task
                # Ini contoh sederhana, bisa disesuaikan dengan kebutuhan
                merged_content = self.optimize_with_gemini(merged_content, task)
        
        # Save hasil akhir
        print(f"\n💾 Saving merged file: {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            print("✅ Process completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False


# Contoh penggunaan
if __name__ == "__main__":
    # Konfigurasi
    API_URL = "http://localhost:8017/v1/generate"
    API_KEY = "sk-e0dde619-2dd3-4018-aad1-e7f602d58534"
    
    # Initialize processor
    processor = HTMLMergerWithGemini(API_URL, API_KEY)
    
    # Contoh regex filters
    regex_filters = [
        # Hapus comments HTML
        (r'<!--.*?-->', ''),
        # Hapus whitespace berlebih
        (r'\n\s*\n', '\n'),
        # Minify inline styles (hapus whitespace di CSS)
        (r':\s+', ':'),
    ]
    
    # Contoh Gemini tasks
    gemini_tasks = [
        "Optimize and minify the CSS code while preserving functionality",
        "Add meta description and improve SEO tags",
        "Ensure all links and scripts are properly formatted"
    ]
    
    # Process file
    input_html = "index.html"  # Ganti dengan file HTML Anda
    output_html = "merged_output.html"
    
    processor.process_html_file(
        input_file=input_html,
        output_file=output_html,
        regex_filters=regex_filters,
        gemini_tasks=gemini_tasks
    )
    
    # Atau gunakan Gemini untuk task spesifik saja
    print("\n" + "="*50)
    print("Testing standalone Gemini API call:")
    result = processor.call_gemini_api("Explain what HTML merging means in one sentence")
    print(f"Response: {result}")