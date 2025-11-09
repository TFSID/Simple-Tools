import { readdir, readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname, basename, extname } from 'path';
import { existsSync } from 'fs';

// Configuration
const CONFIG = {
  GEMINI_API_URL: 'http://localhost:8017/v1/generate',
  GEMINI_API_KEY: 'sk-e0dde619-2dd3-4018-aad1-e7f602d58534',
  MODEL_NAME: 'gemini-2.5-flash-preview-05-20',
  INPUT_DIR: './html-input',
  OUTPUT_DIR: './nextjs-output'
};

interface GeminiResponse {
  model: string;
  output_text: string;
  finish_reason: string | null;
  usage: {
    input_tokens: number | null;
    output_tokens: number | null;
    total_tokens: number;
  };
}

// Gemini API Call Helper
async function callGemini(prompt: string, systemInstruction: string = ''): Promise<string> {
  const response = await fetch(CONFIG.GEMINI_API_URL, {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'x-api-key': CONFIG.GEMINI_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt,
      model_name: CONFIG.MODEL_NAME,
      temperature: 1,
      top_p: 0.95,
      max_output_tokens: 65536,
      system_instruction: systemInstruction,
      user_metadata: ''
    })
  });

  if (!response.ok) {
    throw new Error(`Gemini API error: ${response.statusText}`);
  }

  const data: GeminiResponse = await response.json();
  return data.output_text;
}

// Read HTML file and extract local resources
async function readHTMLWithResources(htmlPath: string): Promise<{
  html: string;
  scripts: Map<string, string>;
  styles: Map<string, string>;
}> {
  const html = await readFile(htmlPath, 'utf-8');
  const baseDir = dirname(htmlPath);
  
  const scripts = new Map<string, string>();
  const styles = new Map<string, string>();

  // Extract and read local scripts
  const scriptRegex = /<script\s+(?:.*?\s+)?src=["']([^"']+)["'][^>]*><\/script>/gi;
  let match;
  
  while ((match = scriptRegex.exec(html)) !== null) {
    const src = match[1];
    if (!src.startsWith('http') && !src.startsWith('//')) {
      const scriptPath = join(baseDir, src);
      if (existsSync(scriptPath)) {
        const content = await readFile(scriptPath, 'utf-8');
        scripts.set(src, content);
        console.log(`✓ Loaded script: ${src}`);
      }
    }
  }

  // Extract and read local stylesheets
  const linkRegex = /<link\s+(?:.*?\s+)?href=["']([^"']+)["'][^>]*>/gi;
  
  while ((match = linkRegex.exec(html)) !== null) {
    const href = match[1];
    if (match[0].includes('stylesheet') && !href.startsWith('http') && !href.startsWith('//')) {
      const stylePath = join(baseDir, href);
      if (existsSync(stylePath)) {
        const content = await readFile(stylePath, 'utf-8');
        styles.set(href, content);
        console.log(`✓ Loaded stylesheet: ${href}`);
      }
    }
  }

  return { html, scripts, styles };
}

// Merge HTML with local resources
function mergeResources(html: string, scripts: Map<string, string>, styles: Map<string, string>): string {
  let merged = html;

  // Inline scripts
  for (const [src, content] of scripts) {
    const scriptTag = new RegExp(`<script\\s+(?:.*?\\s+)?src=["']${src.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'][^>]*><\\/script>`, 'gi');
    merged = merged.replace(scriptTag, `<script>\n${content}\n</script>`);
  }

  // Inline styles
  for (const [href, content] of styles) {
    const linkTag = new RegExp(`<link\\s+(?:.*?\\s+)?href=["']${href.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'][^>]*>`, 'gi');
    merged = merged.replace(linkTag, `<style>\n${content}\n</style>`);
  }

  return merged;
}

// Basic regex transformations
function applyBasicTransformations(html: string): string {
  let transformed = html;

  // Convert class to className
  transformed = transformed.replace(/\sclass=/g, ' className=');
  
  // Convert inline styles to objects (simple cases)
  transformed = transformed.replace(/style="([^"]*)"/g, (match, styles) => {
    const styleObj = styles.split(';')
      .filter((s: string) => s.trim())
      .map((s: string) => {
        const [key, value] = s.split(':').map((x: string) => x.trim());
        const camelKey = key.replace(/-([a-z])/g, (g: string) => g[1].toUpperCase());
        return `${camelKey}: '${value}'`;
      })
      .join(', ');
    return `style={{${styleObj}}}`;
  });

  // Self-closing tags
  transformed = transformed.replace(/<(img|br|hr|input|meta|link)([^>]*)>/gi, '<$1$2 />');

  return transformed;
}

// Extract component structure using Gemini
async function analyzeComponentStructure(html: string): Promise<string> {
  const prompt = `Analyze this HTML and identify reusable components. Return a JSON structure with component names and their HTML sections:

${html.substring(0, 10000)}

Return only valid JSON in this format:
{
  "components": [
    {"name": "Header", "selector": "header", "type": "semantic"},
    {"name": "Navigation", "selector": "nav", "type": "semantic"}
  ]
}`;

  const systemInstruction = 'You are an expert in React and Next.js component architecture. Analyze HTML and suggest component breakdown.';
  
  return await callGemini(prompt, systemInstruction);
}

// Convert HTML section to Next.js component using Gemini
async function convertToNextComponent(
  componentName: string,
  html: string,
  hasClientInteractivity: boolean
): Promise<string> {
  const prompt = `Convert this HTML into a Next.js ${hasClientInteractivity ? 'client' : 'server'} component named "${componentName}":

${html}

Requirements:
- Use TypeScript
- ${hasClientInteractivity ? "Add 'use client' directive" : 'Make it a server component'}
- Use modern Next.js 14+ conventions
- Convert all attributes to React/JSX format
- Extract inline scripts to proper event handlers
- Use Tailwind CSS classes if styling is present
- Add proper TypeScript types for props

Return ONLY the complete component code, no explanations.`;

  const systemInstruction = 'You are an expert Next.js developer. Convert HTML to clean, modern Next.js components following best practices.';
  
  return await callGemini(prompt, systemInstruction);
}

// Detect if HTML section needs client-side interactivity
function needsClientComponent(html: string): boolean {
  const clientIndicators = [
    /<script/i,
    /onclick/i,
    /onchange/i,
    /onsubmit/i,
    /addEventListener/i,
    /useState/i,
    /useEffect/i
  ];

  return clientIndicators.some(pattern => pattern.test(html));
}

// Main conversion pipeline
async function convertHTMLToNextJS(htmlFilePath: string) {
  console.log(`\n🚀 Starting conversion: ${htmlFilePath}\n`);

  // Step 1: Read HTML and local resources
  console.log('📖 Reading HTML and local resources...');
  const { html, scripts, styles } = await readHTMLWithResources(htmlFilePath);

  // Step 2: Merge into single file
  console.log('🔗 Merging resources...');
  const mergedHTML = mergeResources(html, scripts, styles);

  // Step 3: Apply basic regex transformations
  console.log('🔄 Applying basic transformations...');
  const transformed = applyBasicTransformations(mergedHTML);

  // Step 4: Analyze component structure with Gemini
  console.log('🤖 Analyzing component structure with Gemini...');
  const structureAnalysis = await analyzeComponentStructure(transformed);
  
  let components: Array<{name: string, selector: string, type: string}> = [];
  try {
    const parsed = JSON.parse(structureAnalysis.replace(/```json\n?|\n?```/g, ''));
    components = parsed.components || [];
  } catch (e) {
    console.log('⚠️  Using default component structure');
    components = [{ name: 'MainPage', selector: 'body', type: 'full' }];
  }

  // Step 5: Convert each component with Gemini
  console.log('✨ Converting components with Gemini...');
  const outputDir = join(CONFIG.OUTPUT_DIR, basename(htmlFilePath, '.html'));
  await mkdir(outputDir, { recursive: true });

  for (const comp of components) {
    console.log(`  → Converting ${comp.name}...`);
    
    const needsClient = needsClientComponent(transformed);
    const componentCode = await convertToNextComponent(comp.name, transformed, needsClient);
    
    const fileName = `${comp.name}.tsx`;
    await writeFile(join(outputDir, fileName), componentCode);
    console.log(`  ✓ Created ${fileName}`);
  }

  // Step 6: Create main page.tsx
  console.log('📄 Creating page.tsx...');
  const pageContent = await callGemini(
    `Create a Next.js page.tsx that imports and uses these components: ${components.map(c => c.name).join(', ')}. Return only the code.`,
    'You are a Next.js expert. Create clean page components.'
  );
  
  await writeFile(join(outputDir, 'page.tsx'), pageContent);

  console.log(`\n✅ Conversion complete! Output: ${outputDir}\n`);
}

// CLI Interface
async function main() {
  const args = Bun.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
HTML to Next.js Converter
========================

Usage: bun run converter.ts <html-file-path>

Example: bun run converter.ts ./input/index.html

Configuration:
- Input: Single HTML file or directory
- Output: ${CONFIG.OUTPUT_DIR}
- Gemini API: ${CONFIG.GEMINI_API_URL}
    `);
    return;
  }

  const inputPath = args[0];

  if (!existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    return;
  }

  try {
    await convertHTMLToNextJS(inputPath);
  } catch (error) {
    console.error('❌ Conversion failed:', error);
  }
}

main();