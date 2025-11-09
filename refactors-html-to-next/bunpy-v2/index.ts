import { readdir, readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname, basename, extname } from 'path';
import { existsSync } from 'fs';

// Configuration
const CONFIG = {
  GEMINI_API_URL: 'http://localhost:8017/v1/generate',
  GEMINI_API_KEY: 'sk-e0dde619-2dd3-4018-aad1-e7f602d58534',
  MODEL_NAME: 'gemini-2.5-flash-preview-05-20',
  INPUT_DIR: './html-input',
  OUTPUT_DIR: './nextjs-output',
  TASKS_DIR: './task-lists'
};

interface TaskItem {
  id: string;
  title: string;
  description: string;
  type: 'code_generation' | 'analysis' | 'conversion' | 'review' | 'testing';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'high' | 'medium' | 'low';
  dependencies: string[];
  input_data?: any;
  output_data?: any;
  code?: string;
  errors?: string[];
  estimated_time?: number;
  actual_time?: number;
}

interface TaskList {
  id: string;
  title: string;
  description: string;
  created_at: string;
  tasks: TaskItem[];
  current_task_index: number;
  goals: string[];
  status: 'active' | 'completed' | 'paused';
}

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

// Retry configuration
const RETRY_CONFIG = {
  MAX_RETRIES: 3,
  INITIAL_DELAY: 1000,
  MAX_DELAY: 10000,
  BACKOFF_MULTIPLIER: 2
};

// Sleep helper
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Generate unique ID
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Extract JSON from text that may contain markdown, explanations, or other content
function extractJSON(text: string): string {
  // Remove common markdown code block indicators
  text = text.trim();
  text = text.replace(/```json/g, '');
  text = text.replace(/```typescript/g, '');
  text = text.replace(/```tsx/g, '');
  text = text.replace(/```ts/g, '');
  text = text.replace(/```javascript/g, '');
  text = text.replace(/```jsx/g, '');
  text = text.replace(/```js/g, '');
  text = text.replace(/```/g, '');
  
  // Remove any text before the first '{'
  const firstBrace = text.indexOf('{');
  if (firstBrace > 0) {
    text = text.substring(firstBrace);
  }
  
  // Remove any text after the last '}'
  const lastBrace = text.lastIndexOf('}');
  if (lastBrace >= 0 && lastBrace < text.length - 1) {
    text = text.substring(0, lastBrace + 1);
  }
  
  // Remove any leading/trailing whitespace and newlines
  text = text.trim();
  
  // If the text doesn't look like JSON, try to extract just the JSON part
  if (!text.startsWith('{') || !text.endsWith('}')) {
    // Try to find JSON using regex
    const jsonMatch = text.match(/\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/);
    if (jsonMatch) {
      return jsonMatch[0];
    }
  }
  
  return text;
}

// Gemini API Call Helper with robust error handling
async function callGemini(
  prompt: string, 
  systemInstruction: string = '',
  retryCount: number = 0
): Promise<string> {
  try {
    console.log(`  🤖 Calling Gemini API (attempt ${retryCount + 1}/${RETRY_CONFIG.MAX_RETRIES + 1})...`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    const response = await fetch(CONFIG.GEMINI_API_URL, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'x-api-key': CONFIG.GEMINI_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: prompt.substring(0, 50000),
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

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`  ❌ API Error [${response.status}]: ${errorText}`);
      throw new Error(`Gemini API error: ${errorText}`);
    }

    const data: GeminiResponse = await response.json();
    
    if (!data.output_text) {
      throw new Error('Empty response from Gemini API');
    }

    let cleanedOutput = data.output_text.trim();
    cleanedOutput = cleanedOutput
      .replace(/^```(?:typescript|tsx|ts|javascript|jsx|js)\n/gm, '')
      .replace(/^```\n/gm, '')
      .replace(/\n```$/gm, '')
      .replace(/^```|```$/g, '')
      .trim();

    console.log(`  ✓ Success (${data.usage?.total_tokens || 0} tokens)`);
    return cleanedOutput;

  } catch (error: any) {
    if (retryCount < RETRY_CONFIG.MAX_RETRIES) {
      const delay = Math.min(
        RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_MULTIPLIER, retryCount),
        RETRY_CONFIG.MAX_DELAY
      );
      console.log(`  ⏳ Retrying in ${delay}ms...`);
      await sleep(delay);
      return callGemini(prompt, systemInstruction, retryCount + 1);
    }
    throw error;
  }
}

// Task List Management
class TaskSynthesisManager {
  private taskLists: Map<string, TaskList> = new Map();
  private currentTaskList: TaskList | null = null;

  async createTaskList(
    goal: string, 
    inputContext?: any
  ): Promise<TaskList> {
    console.log(`\n🎯 Creating task list for goal: ${goal}`);

    const prompt = `Create a comprehensive task list for the following goal: "${goal}"

Input context: ${JSON.stringify(inputContext, null, 2)}

Create tasks that follow this workflow:
1. Create todo list
2. Input to task 
3. Execute code
4. Review results
5. Repeat for next task

Each task should be:
- Specific and actionable
- Have clear input and output expectations
- Include error handling considerations
- Be executable and testable

Return ONLY valid JSON in this format:
{
  "id": "generated_unique_id",
  "title": "Task List Title",
  "description": "Overall description of what will be accomplished",
  "created_at": "2025-11-09T02:42:32.000Z",
  "tasks": [
    {
      "id": "task_1",
      "title": "Task Title",
      "description": "What this task accomplishes",
      "type": "conversion",
      "priority": "high",
      "dependencies": [],
      "estimated_time": 30
    }
  ],
  "current_task_index": 0,
  "goals": ["goal1", "goal2"],
  "status": "active"
}

Task types: code_generation, analysis, conversion, review, testing
Priority levels: high, medium, low`;

    const systemInstruction = 'You are an expert project manager and developer. Return ONLY valid JSON without markdown formatting.';

    try {
      const result = await callGemini(prompt, systemInstruction);
      
      // Robust JSON extraction
      const jsonData = extractJSON(result);
      console.log(`Raw API response: ${result.substring(0, 200)}...`);
      console.log(`Extracted JSON: ${jsonData.substring(0, 200)}...`);
      
      let taskList: TaskList;
      try {
        taskList = JSON.parse(jsonData);
      } catch (parseError: any) {
        console.error('JSON parsing failed after extraction:');
        console.error(`Raw response: ${result.substring(0, 500)}`);
        console.error(`Extracted JSON: ${jsonData.substring(0, 200)}`);
        console.error(`Parse error: ${parseError.message}`);
        throw new Error(`Failed to parse AI response as JSON. Raw response: ${result.substring(0, 200)}...`);
      }
      
      taskList.id = taskList.id || generateId();
      taskList.created_at = new Date().toISOString();
      taskList.current_task_index = 0;
      taskList.status = 'active';

      this.taskLists.set(taskList.id, taskList);
      this.currentTaskList = taskList;

      console.log(`✓ Created task list with ${taskList.tasks.length} tasks`);
      return taskList;
    } catch (error: any) {
      console.error('Failed to create task list:', error.message);
      console.error(`Response was: ${typeof result !== 'undefined' ? result.substring(0, 200) : 'No response available'}`);
      throw error;
    }
  }

  async processNextTask(): Promise<TaskItem | null> {
    if (!this.currentTaskList) {
      throw new Error('No active task list');
    }

    const taskList = this.currentTaskList;
    
    // Find next pending task
    const nextTask = taskList.tasks.find(task => 
      task.status === 'pending' && 
      task.dependencies.every(depId => 
        taskList.tasks.find(t => t.id === depId)?.status === 'completed'
      )
    );

    if (!nextTask) {
      console.log('🎉 All tasks completed or no available tasks');
      taskList.status = 'completed';
      return null;
    }

    console.log(`\n🔄 Processing task: ${nextTask.title}`);
    console.log(`   Description: ${nextTask.description}`);
    console.log(`   Type: ${nextTask.type}, Priority: ${nextTask.priority}`);

    // Update task status
    nextTask.status = 'in_progress';
    nextTask.actual_time = Date.now();

    try {
      // Execute the task based on its type
      await this.executeTask(nextTask);
      
      nextTask.status = 'completed';
      nextTask.actual_time = Date.now() - nextTask.actual_time!;
      
      console.log(`✅ Task completed in ${nextTask.actual_time}ms`);
      
      // Auto-review the result
      await this.reviewTask(nextTask);
      
      return nextTask;
    } catch (error: any) {
      nextTask.status = 'failed';
      nextTask.errors = [error.message];
      console.error(`❌ Task failed: ${error.message}`);
      throw error;
    }
  }

  private async executeTask(task: TaskItem): Promise<void> {
    switch (task.type) {
      case 'conversion':
        await this.executeConversionTask(task);
        break;
      case 'code_generation':
        await this.executeCodeGenerationTask(task);
        break;
      case 'analysis':
        await this.executeAnalysisTask(task);
        break;
      case 'review':
        await this.executeReviewTask(task);
        break;
      case 'testing':
        await this.executeTestingTask(task);
        break;
      default:
        throw new Error(`Unknown task type: ${task.type}`);
    }
  }

  private async executeConversionTask(task: TaskItem): Promise<void> {
    console.log('  🔄 Executing conversion task...');
    
    const prompt = `Convert the following input to the target format:

Input: ${JSON.stringify(task.input_data, null, 2)}

Requirements:
- Follow modern best practices
- Include proper error handling
- Add TypeScript types if applicable
- Use clean, readable code

Return the converted code/content as raw text, no markdown formatting.`;

    const systemInstruction = 'You are an expert developer specializing in code conversion and transformation.';
    
    const result = await callGemini(prompt, systemInstruction);
    task.output_data = { converted_content: result };
    task.code = result;
  }

  private async executeCodeGenerationTask(task: TaskItem): Promise<void> {
    console.log('  💻 Executing code generation task...');
    
    const prompt = `Generate code for the following requirement:

${task.description}

Input context: ${JSON.stringify(task.input_data, null, 2)}

Requirements:
- Use modern language features
- Include error handling
- Add comments for clarity
- Follow best practices
- Return only the code, no explanations`;

    const systemInstruction = 'You are an expert software developer. Generate clean, production-ready code.';
    
    const result = await callGemini(prompt, systemInstruction);
    task.output_data = { generated_code: result };
    task.code = result;
  }

  private async executeAnalysisTask(task: TaskItem): Promise<void> {
    console.log('  🔍 Executing analysis task...');
    
    const prompt = `Analyze the following input and provide insights:

Input: ${JSON.stringify(task.input_data, null, 2)}

Analysis requirements:
- Identify key patterns and insights
- Highlight potential issues or opportunities
- Provide actionable recommendations
- Return structured analysis as JSON or text`;

    const systemInstruction = 'You are an expert analyst. Provide thorough, actionable analysis.';
    
    const result = await callGemini(prompt, systemInstruction);
    task.output_data = { analysis: result };
  }

  private async executeReviewTask(task: TaskItem): Promise<void> {
    console.log('  👀 Executing review task...');
    
    const prompt = `Review the following work and provide feedback:

Input to review: ${JSON.stringify(task.input_data, null, 2)}

Review criteria:
- Code quality and best practices
- Potential issues or bugs
- Performance considerations
- Security concerns
- Maintainability

Provide constructive feedback and recommendations.`;

    const systemInstruction = 'You are an expert code reviewer. Provide thorough, constructive feedback.';
    
    const result = await callGemini(prompt, systemInstruction);
    task.output_data = { review_feedback: result };
  }

  private async executeTestingTask(task: TaskItem): Promise<void> {
    console.log('  🧪 Executing testing task...');
    
    const prompt = `Create tests for the following code or functionality:

Input: ${JSON.stringify(task.input_data, null, 2)}

Testing requirements:
- Cover edge cases
- Include integration tests
- Follow testing best practices
- Use appropriate testing framework
- Return only test code`;

    const systemInstruction = 'You are an expert QA engineer. Generate comprehensive, well-structured tests.';
    
    const result = await callGemini(prompt, systemInstruction);
    task.output_data = { test_code: result };
    task.code = result;
  }

  private async reviewTask(task: TaskItem): Promise<void> {
    console.log('  🔍 Reviewing task results...');
    
    const prompt = `Review the following task execution results:

Task: ${task.title}
Description: ${task.description}
Output: ${JSON.stringify(task.output_data, null, 2)}
${task.code ? `Code: ${task.code}` : ''}

Provide a brief review of:
1. Quality of execution
2. Any potential improvements
3. Next steps or recommendations

Keep it concise and actionable.`;

    const systemInstruction = 'You are an expert reviewer. Provide brief, constructive feedback.';
    
    const result = await callGemini(prompt, systemInstruction);
    console.log(`  📋 Review: ${result.substring(0, 200)}...`);
  }

  async runFullWorkflow(goal: string, inputContext?: any): Promise<TaskList> {
    console.log(`\n🚀 Starting full synthesis workflow for: ${goal}`);
    
    // Step 1: Create todo list
    const taskList = await this.createTaskList(goal, inputContext);
    
    // Step 2-5: Execute and review tasks in loop
    let completedTasks = 0;
    const totalTasks = taskList.tasks.length;
    
    while (taskList.status === 'active') {
      const task = await this.processNextTask();
      if (!task) break; // All tasks completed or no more available tasks
      
      completedTasks++;
      console.log(`\n📊 Progress: ${completedTasks}/${totalTasks} tasks completed`);
      
      // Brief pause between tasks
      await sleep(2000);
    }
    
    console.log(`\n🎉 Workflow completed! ${completedTasks} tasks processed.`);
    return taskList;
  }

  getTaskList(id?: string): TaskList | null {
    return id ? this.taskLists.get(id) || null : this.currentTaskList;
  }

  getProgress(): any {
    if (!this.currentTaskList) return null;
    
    const tasks = this.currentTaskList.tasks;
    return {
      total: tasks.length,
      completed: tasks.filter(t => t.status === 'completed').length,
      failed: tasks.filter(t => t.status === 'failed').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      pending: tasks.filter(t => t.status === 'pending').length
    };
  }

  async saveTaskList(taskList: TaskList): Promise<void> {
    const tasksDir = CONFIG.TASKS_DIR;
    await mkdir(tasksDir, { recursive: true });
    
    const filePath = join(tasksDir, `${taskList.id}.json`);
    await writeFile(filePath, JSON.stringify(taskList, null, 2));
    console.log(`💾 Task list saved: ${filePath}`);
  }
}

// Integration with existing HTML converter
async function enhancedHTMLToNextJSConversion(htmlFilePath: string): Promise<void> {
  const taskManager = new TaskSynthesisManager();
  
  // Create a task list for the conversion
  const taskList = await taskManager.createTaskList(
    `Convert HTML file to Next.js components: ${basename(htmlFilePath)}`,
    { 
      input_file: htmlFilePath,
      target_framework: 'Next.js',
      target_language: 'TypeScript'
    }
  );

  // Add specific conversion tasks
  const additionalTasks: TaskItem[] = [
    {
      id: generateId(),
      title: 'Read and analyze HTML file',
      description: 'Read the HTML file and extract structure, scripts, and styles',
      type: 'analysis',
      status: 'pending',
      priority: 'high',
      dependencies: [],
      estimated_time: 10
    },
    {
      id: generateId(),
      title: 'Merge HTML with local resources',
      description: 'Inline all CSS and JavaScript files into the HTML',
      type: 'conversion',
      status: 'pending',
      priority: 'high',
      dependencies: ['task_1'],
      estimated_time: 15
    },
    {
      id: generateId(),
      title: 'Apply basic transformations',
      description: 'Convert HTML attributes to JSX format (class -> className, etc.)',
      type: 'conversion',
      status: 'pending',
      priority: 'medium',
      dependencies: ['task_2'],
      estimated_time: 20
    },
    {
      id: generateId(),
      title: 'Analyze component structure',
      description: 'Use AI to identify reusable components in the HTML',
      type: 'analysis',
      status: 'pending',
      priority: 'high',
      dependencies: ['task_3'],
      estimated_time: 30
    },
    {
      id: generateId(),
      title: 'Convert to Next.js components',
      description: 'Transform HTML sections into TypeScript React components',
      type: 'conversion',
      status: 'pending',
      priority: 'high',
      dependencies: ['task_4'],
      estimated_time: 60
    },
    {
      id: generateId(),
      title: 'Create main page',
      description: 'Generate the main page.tsx that imports and uses all components',
      type: 'code_generation',
      status: 'pending',
      priority: 'medium',
      dependencies: ['task_5'],
      estimated_time: 20
    },
    {
      id: generateId(),
      title: 'Review and test output',
      description: 'Review the generated code for quality and test for errors',
      type: 'review',
      status: 'pending',
      priority: 'medium',
      dependencies: ['task_6'],
      estimated_time: 15
    }
  ];

  // Update task list with additional tasks
  taskList.tasks = [...taskList.tasks, ...additionalTasks];
  
  // Save and run the workflow
  await taskManager.saveTaskList(taskList);
  await taskManager.runFullWorkflow(
    `Convert ${basename(htmlFilePath)} to Next.js components`,
    { input_file: htmlFilePath }
  );
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🚀 Task Synthesis System
========================

Workflow: Create todo list → Input to task → Execute code → Review → Repeat

Commands:
  1. Interactive goal setting:
     bun run task_synthesis_system.ts

  2. Convert HTML to Next.js:
     bun run task_synthesis_system.ts convert <html-file-path>

  3. Run custom workflow:
     bun run task_synthesis_system.ts workflow "<goal description>"

  4. Show task list progress:
     bun run task_synthesis_system.ts status

Examples:
  bun run task_synthesis_system.ts convert ./input/index.html
  bun run task_synthesis_system.ts workflow "Build a todo app with React and TypeScript"

Features:
- AI-powered task list generation
- Automated code execution and review
- Progress tracking and error handling
- Integration with existing HTML converter
- Support for multiple task types
    `);
    return;
  }

  const command = args[0];
  const taskManager = new TaskSynthesisManager();

  try {
    switch (command) {
      case 'convert':
        if (!args[1]) {
          console.error('❌ Please provide HTML file path');
          process.exit(1);
        }
        await enhancedHTMLToNextJSConversion(args[1]);
        break;

      case 'workflow':
        if (!args[1]) {
          console.error('❌ Please provide goal description');
          process.exit(1);
        }
        await taskManager.runFullWorkflow(args[1]);
        break;

      case 'status':
        const progress = taskManager.getProgress();
        if (progress) {
          console.log('\n📊 Current Task List Progress:');
          console.log(`   Total: ${progress.total}`);
          console.log(`   Completed: ${progress.completed}`);
          console.log(`   In Progress: ${progress.in_progress}`);
          console.log(`   Failed: ${progress.failed}`);
          console.log(`   Pending: ${progress.pending}`);
        } else {
          console.log('❌ No active task list');
        }
        break;

      default:
        console.log('🎯 Interactive Mode - Setting up synthesis workflow...');
        console.log('Please provide a goal or task description:');
        console.log('Example: "Convert my website to Next.js" or "Build a REST API"');
        
        // For interactive mode, you would implement readline here
        console.log('\n💡 Use specific commands for automation:');
        console.log('  - "convert <file>" for HTML to Next.js conversion');
        console.log('  - "workflow <goal>" for custom goal-based workflows');
    }

  } catch (error: any) {
    console.error('\n💥 Error:', error.message);
    process.exit(1);
  }
}

main();