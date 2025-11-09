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
  meta?: {
    retries: number;
    key_rotations: number;
    backoff_applied: boolean;
  };
}

interface GeminiError {
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
  message?: string;
}

// Retry configuration
const RETRY_CONFIG = {
  MAX_RETRIES: 3,
  INITIAL_DELAY: 1000,
  MAX_DELAY: 10000,
  BACKOFF_MULTIPLIER: 2
};

// Sleep helper
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Gemini API Call Helper with robust error handling
async function callGemini(
  prompt: string, 
  systemInstruction: string = '',
  retryCount: number = 0
): Promise<string> {
  try {
    console.log(`  🤖 Calling Gemini API (attempt ${retryCount + 1}/${RETRY_CONFIG.MAX_RETRIES + 1})...`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

    const response = await fetch(CONFIG.GEMINI_API_URL, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'x-api-key': CONFIG.GEMINI_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: prompt.substring(0, 50000), // Limit prompt size
        model_name: CONFIG.MODEL_NAME,
        temperature: 1,
        top_p: 0.95,
        max_output_tokens: 65536,
        system_instruction: systemInstruction,
        user_metadata: ''
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    // Handle non-OK responses
    if (!response.ok) {
      const errorText = await response.text();
      let errorData: GeminiError;
      
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { message: errorText };
      }

      const errorMessage = errorData.error?.message || errorData.message || response.statusText;
      const errorCode = errorData.error?.code || response.status;

      console.error(`  ❌ API Error [${errorCode}]: ${errorMessage}`);

      // Retry on specific errors
      if (retryCount < RETRY_CONFIG.MAX_RETRIES) {
        const shouldRetry = 
          response.status === 500 || // Internal Server Error
          response.status === 502 || // Bad Gateway
          response.status === 503 || // Service Unavailable
          response.status === 504 || // Gateway Timeout
          response.status === 429;   // Rate Limit

        if (shouldRetry) {
          const delay = Math.min(
            RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_MULTIPLIER, retryCount),
            RETRY_CONFIG.MAX_DELAY
          );
          
          console.log(`  ⏳ Retrying in ${delay}ms...`);
          await sleep(delay);
          return callGemini(prompt, systemInstruction, retryCount + 1);
        }
      }

      throw new Error(`Gemini API error [${errorCode}]: ${errorMessage}`);
    }

    // Parse response
    const data: GeminiResponse = await response.json();
    
    if (!data.output_text) {
      throw new Error('Empty response from Gemini API');
    }

    console.log(`  ✓ Success (${data.usage?.total_tokens || 0} tokens)`);
    return data.output_text;

  } catch (error: any) {
    // Handle fetch errors (network, timeout, etc.)
    if (error.name === 'AbortError') {
      console.error('  ❌ Request timeout (60s)');
      
      if (retryCount < RETRY_CONFIG.MAX_RETRIES) {
        const delay = RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_MULTIPLIER, retryCount);
        console.log(`  ⏳ Retrying in ${delay}ms...`);
        await sleep(delay);
        return callGemini(prompt, systemInstruction, retryCount + 1);
      }
      
      throw new Error('Gemini API request timeout after retries');
    }

    // Network errors
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      console.error(`  ❌ Network error: Cannot connect to ${CONFIG.GEMINI_API_URL}`);
      
      if (retryCount < RETRY_CONFIG.MAX_RETRIES) {
        const delay = RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_MULTIPLIER, retryCount);
        console.log(`  ⏳ Retrying in ${delay}ms...`);
        await sleep(delay);
        return callGemini(prompt, systemInstruction, retryCount + 1);
      }
      
      throw new Error(`Cannot connect to Gemini API at ${CONFIG.GEMINI_API_URL}. Check if the service is running.`);
    }

    // Re-throw if it's already our custom error
    if (error.message.startsWith('Gemini API error')) {
      throw error;
    }

    // Unknown error
    console.error('  ❌ Unexpected error:', error.message);
    throw new Error(`Gemini API call failed: ${error.message}`);
  }
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
  try {
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
  } catch (error: any) {
    console.warn('⚠️  Component analysis failed, using fallback structure');
    console.warn(`   Reason: ${error.message}`);
    
    // Return fallback structure
    return JSON.stringify({
      components: [
        { name: 'MainPage', selector: 'body', type: 'full' }
      ]
    });
  }
}

// Convert HTML section to Next.js component using Gemini
async function convertToNextComponent(
  componentName: string,
  html: string,
  hasClientInteractivity: boolean
): Promise<string> {
  try {
    const prompt = `Convert this HTML into a Next.js ${hasClientInteractivity ? 'client' : 'server'} component named "${componentName}":

${html.substring(0, 15000)}

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
  } catch (error: any) {
    console.warn(`⚠️  AI conversion failed for ${componentName}, using basic conversion`);
    console.warn(`   Reason: ${error.message}`);
    
    // Fallback: basic conversion
    const directive = hasClientInteractivity ? "'use client';\n\n" : '';
    return `${directive}export default function ${componentName}() {
  return (
    <div>
      {/* TODO: Manual conversion needed */}
      <div dangerouslySetInnerHTML={{ __html: \`${html.replace(/`/g, '\\`').substring(0, 5000)}\` }} />
    </div>
  );
}`;
  }
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

  try {
    // Step 1: Read HTML and local resources
    console.log('📖 Reading HTML and local resources...');
    const { html, scripts, styles } = await readHTMLWithResources(htmlFilePath);
    console.log(`   Found ${scripts.size} scripts and ${styles.size} stylesheets`);

    // Step 2: Merge into single file
    console.log('🔗 Merging resources...');
    const mergedHTML = mergeResources(html, scripts, styles);
    console.log(`   Merged into ${mergedHTML.length} characters`);

    // Step 3: Apply basic regex transformations
    console.log('🔄 Applying basic transformations...');
    const transformed = applyBasicTransformations(mergedHTML);

    // Step 4: Analyze component structure with Gemini
    console.log('🤖 Analyzing component structure with Gemini...');
    const structureAnalysis = await analyzeComponentStructure(transformed);
    
    let components: Array<{name: string, selector: string, type: string}> = [];
    try {
      const cleaned = structureAnalysis.replace(/```json\n?|\n?```/g, '').trim();
      const parsed = JSON.parse(cleaned);
      components = parsed.components || [];
      console.log(`   ✓ Identified ${components.length} components`);
    } catch (e) {
      console.log('⚠️  JSON parse failed, using default structure');
      components = [{ name: 'MainPage', selector: 'body', type: 'full' }];
    }

    // Step 5: Convert each component with Gemini
    console.log('✨ Converting components with Gemini...');
    const outputDir = join(CONFIG.OUTPUT_DIR, basename(htmlFilePath, '.html'));
    await mkdir(outputDir, { recursive: true });

    const convertedComponents: string[] = [];
    for (const comp of components) {
      console.log(`  → Converting ${comp.name}...`);
      
      try {
        const needsClient = needsClientComponent(transformed);
        const componentCode = await convertToNextComponent(comp.name, transformed, needsClient);
        
        const fileName = `${comp.name}.tsx`;
        await writeFile(join(outputDir, fileName), componentCode);
        console.log(`  ✓ Created ${fileName}`);
        convertedComponents.push(comp.name);
      } catch (error: any) {
        console.error(`  ❌ Failed to convert ${comp.name}: ${error.message}`);
        console.log(`  ⏭️  Skipping ${comp.name}...`);
      }
    }

    if (convertedComponents.length === 0) {
      throw new Error('No components were successfully converted');
    }

    // Step 6: Create main page.tsx
    console.log('📄 Creating page.tsx...');
    try {
      const pageContent = await callGemini(
        `Create a Next.js page.tsx that imports and uses these components: ${convertedComponents.join(', ')}. Return only the code.`,
        'You are a Next.js expert. Create clean page components.'
      );
      
      await writeFile(join(outputDir, 'page.tsx'), pageContent);
      console.log('  ✓ Created page.tsx');
    } catch (error: any) {
      console.warn('⚠️  Failed to create page.tsx with AI, using fallback');
      
      const fallbackPage = `export default function Page() {
  return (
    <div>
      {/* Import and use your components here */}
      <h1>Converted Page</h1>
    </div>
  );
}`;
      await writeFile(join(outputDir, 'page.tsx'), fallbackPage);
    }

    console.log(`\n✅ Conversion complete! Output: ${outputDir}`);
    console.log(`   Successfully converted ${convertedComponents.length}/${components.length} components\n`);

  } catch (error: any) {
    console.error('\n❌ Conversion failed:', error.message);
    
    if (error.stack) {
      console.error('\nStack trace:');
      console.error(error.stack);
    }
    
    console.error('\n💡 Troubleshooting tips:');
    console.error('   1. Check if Gemini API service is running');
    console.error('   2. Verify API key and endpoint URL');
    console.error('   3. Check network connectivity');
    console.error('   4. Review input HTML file format\n');
    
    throw error;
  }
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
- API Key: ${CONFIG.GEMINI_API_KEY.substring(0, 10)}...

Error Handling:
- Automatic retries (max ${RETRY_CONFIG.MAX_RETRIES})
- Exponential backoff
- Fallback conversions
- Detailed error logging
    `);
    return;
  }

  const inputPath = args[0];

  if (!existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    console.error('   Please provide a valid HTML file path');
    process.exit(1);
  }

  try {
    // Verify API connectivity before starting
    console.log('🔍 Verifying Gemini API connectivity...');
    await callGemini('test', 'Respond with "ok"');
    console.log('✓ API connection verified\n');
    
    await convertHTMLToNextJS(inputPath);
    process.exit(0);
  } catch (error: any) {
    console.error('\n💥 Fatal error during conversion');
    
    // Check if it's an API connectivity issue
    if (error.message.includes('Cannot connect')) {
      console.error('\n🔧 API Connection Issue:');
      console.error(`   The Gemini API at ${CONFIG.GEMINI_API_URL} is not reachable.`);
      console.error('   Please ensure:');
      console.error('   1. The API service is running');
      console.error('   2. The URL is correct');
      console.error('   3. No firewall is blocking the connection\n');
    }
    
    process.exit(1);
  }
}

main();