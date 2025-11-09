#!/usr/bin/env python3
"""
Enhanced Task Synthesis System - Python Version
===============================================

Workflow: Create todo list → Input to task → Execute code → Review → Repeat

Features:
- Comprehensive request/response logging with full dumps
- File operation tracking (create, read, delete files)
- Output list generation when task lists are updated
- Actual task result output
- Detailed audit trail
"""

import asyncio
import json
import time
import uuid
import os
import sys
import traceback
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from contextlib import contextmanager
import aiofiles
import tempfile

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    GEMINI_API_URL = "http://localhost:8017/v1/generate"
    GEMINI_API_KEY = "sk-e0dde619-2dd3-4018-aad1-e7f602d58534"
    MODEL_NAME = "gemini-2.5-flash-preview-05-20"
    TASKS_DIR = Path("./task-lists")
    OUTPUT_DIR = Path("./output")
    LOGS_DIR = Path("./logs")
    AUDIT_DIR = Path("./audit")
    MAX_RETRIES = 3
    INITIAL_DELAY = 1.0
    MAX_DELAY = 10.0
    BACKOFF_MULTIPLIER = 2
    REQUEST_DUMP_SIZE = 50000  # Max size for dumping request/response content
    MAX_LOG_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Ensure directories exist
for dir_path in [Config.TASKS_DIR, Config.OUTPUT_DIR, Config.LOGS_DIR, Config.AUDIT_DIR]:
    dir_path.mkdir(exist_ok=True)

class TaskType(Enum):
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CONVERSION = "conversion"
    REVIEW = "review"
    TESTING = "testing"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FileOperation(Enum):
    CREATE = "create"
    READ = "read"
    DELETE = "delete"
    MODIFY = "modify"
    EXECUTE = "execute"

@dataclass
class FileOperationItem:
    """Track file operations for task execution"""
    operation: FileOperation
    file_path: str
    description: str
    priority: Priority
    dependencies: List[str] = field(default_factory=list)
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class TaskOutput:
    """Enhanced task output with file operations"""
    task_id: str
    content: str
    file_operations: List[FileOperationItem] = field(default_factory=list)
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class TaskItem:
    id: str
    title: str
    description: str
    type: TaskType
    status: TaskStatus
    priority: Priority
    dependencies: List[str]
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    output: Optional[TaskOutput] = None
    code: Optional[str] = None
    errors: Optional[List[str]] = None
    estimated_time: Optional[int] = None
    actual_time: Optional[int] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    file_operations: List[FileOperationItem] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class TaskList:
    id: str
    title: str
    description: str
    created_at: str
    tasks: List[TaskItem]
    current_task_index: int
    goals: List[str]
    status: str
    progress: Optional[Dict[str, int]] = None
    file_operations: List[FileOperationItem] = field(default_factory=list)
    output_list: List[TaskOutput] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.progress:
            self._update_progress()

    def _update_progress(self):
        """Update progress statistics"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        failed = sum(1 for task in self.tasks if task.status == TaskStatus.FAILED)
        in_progress = sum(1 for task in self.tasks if task.status == TaskStatus.IN_PROGRESS)
        pending = sum(1 for task in self.tasks if task.status == TaskStatus.PENDING)
        
        self.progress = {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending
        }

    def generate_output_list(self) -> List[TaskOutput]:
        """Generate comprehensive output list from all completed tasks"""
        self.output_list.clear()
        
        for task in self.tasks:
            if task.status == TaskStatus.COMPLETED and task.output:
                self.output_list.append(task.output)
        
        return self.output_list

    def get_file_operations_summary(self) -> Dict[str, List[FileOperationItem]]:
        """Get summary of all file operations organized by type"""
        summary = {
            "create": [],
            "read": [],
            "delete": [],
            "modify": [],
            "execute": []
        }
        
        for task in self.tasks:
            for file_op in task.file_operations:
                summary[file_op.operation.value].append(file_op)
        
        return summary

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass

class AuditLogger:
    """Enhanced audit logging with file dumps"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.request_count = 0
        self.log_file = Config.AUDIT_DIR / f"audit_{self.session_id}.jsonl"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure audit log file exists"""
        if not self.log_file.exists():
            with open(self.log_file, 'w') as f:
                f.write("")
    
    def log_api_request(self, prompt: str, system_instruction: str, request_data: Dict[str, Any], response_data: Dict[str, Any], success: bool, duration_ms: int, error: Optional[str] = None):
        """Log API request and response with full dumps"""
        self.request_count += 1
        
        # Calculate checksums for content verification
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        response_hash = hashlib.sha256(str(response_data).encode()).hexdigest()[:16] if response_data else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": f"req_{self.request_count:06d}",
            "type": "api_call",
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
            "prompt_hash": prompt_hash,
            "response_hash": response_hash,
            "prompt_size": len(prompt),
            "response_size": len(str(response_data)) if response_data else 0,
            "system_instruction": system_instruction[:200] + "..." if len(system_instruction) > 200 else system_instruction,
            "metadata": {
                "model": request_data.get('model_name'),
                "temperature": request_data.get('temperature'),
                "max_tokens": request_data.get('max_output_tokens')
            }
        }
        
        # Write to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Detailed console logging
        status = "✓" if success else "✗"
        logger.info(f"{status} API Request {self.request_count} [{duration_ms}ms] | {prompt_hash}")
        
        if success:
            logger.info(f"  📤 Request: {len(prompt)} chars -> 📥 Response: {len(str(response_data))} chars")
        else:
            logger.error(f"  ❌ Error: {error}")

    def log_task_execution(self, task: TaskItem, status: str, details: Dict[str, Any]):
        """Log task execution events"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "type": "task_execution",
            "task_id": task.id,
            "task_title": task.title,
            "status": status,
            "duration_ms": task.actual_time,
            "details": details
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        status_icon = {"start": "▶️", "complete": "✅", "error": "❌", "fail": "💥"}[status]
        logger.info(f"{status_icon} Task: {task.title} [{task.type.value}]")

    def log_file_operation(self, operation: FileOperationItem, status: str, result: Optional[str] = None):
        """Log file operation events"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "type": "file_operation",
            "operation": operation.operation.value,
            "file_path": operation.file_path,
            "description": operation.description,
            "status": status,
            "result": result,
            "size_bytes": operation.size_bytes,
            "checksum": operation.checksum
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        op_icon = {
            FileOperation.CREATE: "📄",
            FileOperation.READ: "📖", 
            FileOperation.DELETE: "🗑️",
            FileOperation.MODIFY: "✏️",
            FileOperation.EXECUTE: "⚡"
        }
        
        status_icon = "✅" if status == "success" else "❌"
        logger.info(f"{op_icon[operation.operation]} {status_icon} {operation.file_path}: {operation.description}")

class TaskSynthesisManager:
    """
    Enhanced task synthesis manager with comprehensive logging and file tracking
    """
    
    def __init__(self):
        self.task_lists: Dict[str, TaskList] = {}
        self.current_task_list: Optional[TaskList] = None
        self.session_id = str(uuid.uuid4())
        self.audit_logger = AuditLogger()
        
        # Create session log file
        self.log_file = Config.LOGS_DIR / f"session_{self.session_id}.log"
    
    def generate_id(self) -> str:
        """Generate a unique ID"""
        return f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text that may contain markdown, explanations, or other content
        """
        # Remove common markdown code block indicators
        text = text.strip()
        text = text.replace('```json', '')
        text = text.replace('```typescript', '')
        text = text.replace('```tsx', '')
        text = text.replace('```ts', '')
        text = text.replace('```javascript', '')
        text = text.replace('```jsx', '')
        text = text.replace('```js', '')
        text = text.replace('```', '')
        
        # Remove any text before the first '{'
        first_brace = text.find('{')
        if first_brace > 0:
            text = text[first_brace:]
        
        # Remove any text after the last '}'
        last_brace = text.rfind('}')
        if last_brace >= 0 and last_brace < len(text) - 1:
            text = text[:last_brace + 1]
        
        # Remove any leading/trailing whitespace and newlines
        text = text.strip()
        
        # Remove any remaining markdown or text
        lines = text.split('\n')
        cleaned_lines = []
        brace_count = 0
        in_json = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If we find a line that starts with '{' and we're not in JSON yet
            if line.startswith('{') and not in_json:
                in_json = True
                cleaned_lines.append(line)
                brace_count += line.count('{') - line.count('}')
            elif in_json:
                cleaned_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                # If we've balanced all braces, we can stop
                if brace_count <= 0:
                    break
            # Skip lines that don't look like JSON content
            elif in_json and (line.startswith('"') or line.startswith(':') or line.startswith(',') or line.startswith('}') or line.startswith('{')):
                cleaned_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    break
        
        if not cleaned_lines:
            # Fallback: try to find the first complete JSON object
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
            if json_match:
                return json_match.group(0)
            else:
                raise ValueError(f"Could not extract valid JSON from: {text[:200]}...")
        
        return '\n'.join(cleaned_lines)
    
    def _truncate_content(self, content: str, max_size: int) -> str:
        """Truncate content for logging purposes"""
        if len(content) <= max_size:
            return content
        return content[:max_size // 2] + f"\n... [{len(content) - max_size} chars truncated] ...\n" + content[-max_size // 2:]
    
    async def call_gemini(
        self, 
        prompt: str, 
        system_instruction: str = "",
        retry_count: int = 0
    ) -> str:
        """
        Call Gemini API with comprehensive logging and retry logic
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 Calling Gemini API (attempt {retry_count + 1}/{Config.MAX_RETRIES + 1})...")
            logger.info(f"📝 Prompt preview: {self._truncate_content(prompt, 300)}")
            
            import aiohttp
            
            request_data = {
                'prompt': self._truncate_content(prompt, Config.REQUEST_DUMP_SIZE),
                'model_name': Config.MODEL_NAME,
                'temperature': 1,
                'top_p': 0.95,
                'max_output_tokens': 65536,
                'system_instruction': system_instruction,
                'user_metadata': ''
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    Config.GEMINI_API_URL,
                    headers={
                        'accept': 'application/json',
                        'x-api-key': Config.GEMINI_API_KEY,
                        'Content-Type': 'application/json'
                    },
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        duration = int((time.time() - start_time) * 1000)
                        
                        # Log failed request
                        self.audit_logger.log_api_request(
                            prompt, system_instruction, request_data, 
                            {"error": error_text}, False, duration, error_text
                        )
                        
                        logger.error(f"❌ API Error [{response.status}]: {self._truncate_content(error_text, 500)}")
                        raise GeminiAPIError(f"API Error [{response.status}]: {error_text}")
                    
                    data = await response.json()
                    duration = int((time.time() - start_time) * 1000)
                    
                    if not data.get('output_text'):
                        self.audit_logger.log_api_request(
                            prompt, system_instruction, request_data, 
                            data, False, duration, "Empty response from API"
                        )
                        raise GeminiAPIError('Empty response from Gemini API')
                    
                    # Clean the response
                    cleaned_output = data['output_text'].strip()
                    cleaned_output = (
                        cleaned_output
                        .replace('```typescript\n', '')
                        .replace('```tsx\n', '')
                        .replace('```ts\n', '')
                        .replace('```javascript\n', '')
                        .replace('```jsx\n', '')
                        .replace('```js\n', '')
                        .replace('```\n', '')
                        .replace('\n```', '')
                        .replace('```', '')
                        .strip()
                    )
                    
                    tokens = data.get('usage', {}).get('total_tokens', 0)
                    
                    # Log successful request
                    self.audit_logger.log_api_request(
                        prompt, system_instruction, request_data, 
                        {"output_text": cleaned_output, "tokens": tokens}, True, duration
                    )
                    
                    logger.info(f"✓ Success ({tokens} tokens, {duration}ms)")
                    logger.info(f"📥 Response preview: {self._truncate_content(cleaned_output, 200)}")
                    
                    return cleaned_output
                    
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            self.audit_logger.log_api_request(
                prompt, system_instruction, request_data, 
                {}, False, duration, str(error)
            )
            
            if retry_count < Config.MAX_RETRIES:
                delay = min(
                    Config.INITIAL_DELAY * (Config.BACKOFF_MULTIPLIER ** retry_count),
                    Config.MAX_DELAY
                )
                logger.info(f"⏳ Retrying in {delay}s...")
                await asyncio.sleep(delay)
                return await self.call_gemini(prompt, system_instruction, retry_count + 1)
            else:
                raise GeminiAPIError(f"API call failed after {retry_count + 1} attempts: {str(error)}")
    
    async def create_task_list(
        self, 
        goal: str, 
        input_context: Optional[Dict[str, Any]] = None
    ) -> TaskList:
        """
        Create a new task list from a goal with enhanced logging
        """
        logger.info(f"\n🎯 Creating task list for goal: {goal}")
        
        prompt = f"""Create a comprehensive task list for the following goal: "{goal}"

Input context: {json.dumps(input_context, indent=2) if input_context else 'None'}

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
- Include realistic time estimates
- Specify what files will be created, read, or modified

For each task, include a "file_operations" section specifying:
- What files will be created (with paths)
- What files will be read
- What files will be modified
- What files will be deleted (if any)

Return ONLY valid JSON in this exact format:
{{
  "id": "generated_unique_id",
  "title": "Task List Title",
  "description": "Overall description of what will be accomplished",
  "tasks": [
    {{
      "id": "task_1",
      "title": "Task Title",
      "description": "What this task accomplishes",
      "type": "conversion",
      "priority": "high",
      "dependencies": [],
      "estimated_time": 30,
      "file_operations": [
        {{
          "operation": "create",
          "file_path": "./output/converted_file.tsx",
          "description": "Converted React component",
          "priority": "high"
        }},
        {{
          "operation": "read", 
          "file_path": "./input/source.html",
          "description": "Source HTML file to read",
          "priority": "high"
        }}
      ]
    }}
  ],
  "goals": ["primary_goal", "secondary_goal_1", "secondary_goal_2"]
}}

Task types: code_generation, analysis, conversion, review, testing
Priority levels: high, medium, low
File operations: create, read, delete, modify, execute"""

        system_instruction = "You are an expert project manager and developer. Return ONLY valid JSON without markdown formatting. Include comprehensive file operation specifications for each task."

        try:
            result = await self.call_gemini(prompt, system_instruction)
            
            # Log the raw task list creation
            logger.info(f"Raw API response for task list: {self._truncate_content(result, 500)}")
            
            # Robust JSON extraction - handle various formats
            json_data = self._extract_json(result)
            logger.info(f"Extracted JSON for task list: {self._truncate_content(json_data, 500)}")
            
            task_data = json.loads(json_data)
            
            # Process file operations for each task
            tasks = []
            for task in task_data['tasks']:
                file_operations = []
                for file_op in task.get('file_operations', []):
                    file_op_item = FileOperationItem(
                        operation=FileOperation(file_op['operation']),
                        file_path=file_op['file_path'],
                        description=file_op['description'],
                        priority=Priority(file_op['priority'])
                    )
                    file_operations.append(file_op_item)
                
                task_item = TaskItem(
                    id=task['id'],
                    title=task['title'],
                    description=task['description'],
                    type=TaskType(task['type']),
                    status=TaskStatus.PENDING,
                    priority=Priority(task['priority']),
                    dependencies=task.get('dependencies', []),
                    estimated_time=task.get('estimated_time'),
                    file_operations=file_operations
                )
                tasks.append(task_item)
            
            task_list = TaskList(
                id=task_data.get('id', self.generate_id()),
                title=task_data['title'],
                description=task_data['description'],
                created_at=datetime.now(timezone.utc).isoformat(),
                tasks=tasks,
                current_task_index=0,
                goals=task_data.get('goals', [goal]),
                status='active'
            )
            
            # Add task list to global tracking
            self.task_lists[task_list.id] = task_list
            self.current_task_list = task_list
            
            # Log task list creation with file operations summary
            logger.info(f"✓ Created task list with {len(task_list.tasks)} tasks")
            file_ops_summary = task_list.get_file_operations_summary()
            for op_type, ops in file_ops_summary.items():
                if ops:
                    logger.info(f"  📁 {op_type.capitalize()} operations: {len(ops)} files")
            
            return task_list
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed after extraction")
            logger.error(f"Raw response: {self._truncate_content(result, 500) if 'result' in locals() else 'None'}")
            logger.error(f"Extracted JSON: {self._truncate_content(json_data, 500) if 'json_data' in locals() else 'None'}")
            logger.error(f"JSON Error details: {str(e)}")
            raise ValueError(f"Failed to parse AI response as JSON. Raw response: {self._truncate_content(result, 200) if 'result' in locals() else 'None'}...")
        except Exception as error:
            logger.error(f"Failed to create task list: {error}")
            logger.error(f"Response was: {self._truncate_content(result, 200) if 'result' in locals() else 'None'}")
            raise
    
    async def process_next_task(self) -> Optional[TaskItem]:
        """
        Process the next available task in the current task list with comprehensive logging
        """
        if not self.current_task_list:
            raise ValueError("No active task list")
        
        task_list = self.current_task_list
        
        # Find next pending task with all dependencies satisfied
        next_task = None
        for task in task_list.tasks:
            if (task.status == TaskStatus.PENDING and 
                all(dep_id in [t.id for t in task_list.tasks if t.status == TaskStatus.COMPLETED] 
                    for dep_id in task.dependencies)):
                next_task = task
                break
        
        if not next_task:
            logger.info("🎉 All tasks completed or no available tasks")
            task_list.status = 'completed'
            
            # Generate final output list
            output_list = task_list.generate_output_list()
            logger.info(f"📋 Generated output list with {len(output_list)} items")
            
            # Save output list to file
            await self._save_output_list(task_list)
            
            return None
        
        logger.info(f"\n🔄 Processing task: {next_task.title}")
        logger.info(f"   Description: {next_task.description}")
        logger.info(f"   Type: {next_task.type.value}, Priority: {next_task.priority.value}")
        
        if next_task.file_operations:
            logger.info(f"   📁 File operations: {len(next_task.file_operations)}")
            for file_op in next_task.file_operations:
                logger.info(f"      {file_op.operation.value}: {file_op.file_path}")
        
        # Log task start
        self.audit_logger.log_task_execution(next_task, "start", {"description": next_task.description})
        
        # Update task status
        next_task.status = TaskStatus.IN_PROGRESS
        next_task.actual_time = int(time.time() * 1000)
        
        try:
            # Execute the task based on its type
            await self._execute_task(next_task)
            
            next_task.status = TaskStatus.COMPLETED
            next_task.actual_time = int(time.time() * 1000) - next_task.actual_time
            next_task.completed_at = datetime.now(timezone.utc).isoformat()
            
            # Update task list progress
            task_list._update_progress()
            
            # Log task completion
            self.audit_logger.log_task_execution(next_task, "complete", {
                "output_size": len(str(next_task.output_data)) if next_task.output_data else 0,
                "file_operations": len(next_task.file_operations)
            })
            
            logger.info(f"✅ Task completed in {next_task.actual_time}ms")
            
            # Auto-review the result
            await self._review_task(next_task)
            
            return next_task
            
        except Exception as error:
            next_task.status = TaskStatus.FAILED
            next_task.errors = [str(error)]
            next_task.actual_time = int(time.time() * 1000) - next_task.actual_time
            
            # Log task failure
            self.audit_logger.log_task_execution(next_task, "error", {"error": str(error)})
            
            logger.error(f"❌ Task failed: {error}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise
    
    async def _save_output_list(self, task_list: TaskList):
        """Save the output list to a file"""
        output_file = Config.OUTPUT_DIR / f"output_{task_list.id}.json"
        
        output_data = {
            "task_list_id": task_list.id,
            "title": task_list.title,
            "description": task_list.description,
            "created_at": task_list.created_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "outputs": [asdict(output) for output in task_list.output_list],
            "file_operations_summary": task_list.get_file_operations_summary(),
            "progress": task_list.progress
        }
        
        async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(output_data, indent=2, ensure_ascii=False))
        
        logger.info(f"💾 Output list saved: {output_file}")
    
    async def _execute_task(self, task: TaskItem) -> None:
        """
        Execute a task based on its type with file operation tracking
        """
        task_type_handlers = {
            TaskType.CONVERSION: self._execute_conversion_task,
            TaskType.CODE_GENERATION: self._execute_code_generation_task,
            TaskType.ANALYSIS: self._execute_analysis_task,
            TaskType.REVIEW: self._execute_review_task,
            TaskType.TESTING: self._execute_testing_task
        }
        
        handler = task_type_handlers.get(task.type)
        if not handler:
            raise ValueError(f"Unknown task type: {task.type}")
        
        await handler(task)
    
    async def _execute_conversion_task(self, task: TaskItem) -> None:
        """Execute a conversion task with file operations"""
        logger.info("  🔄 Executing conversion task...")
        
        # Track file operations
        for file_op in task.file_operations:
            if file_op.operation == FileOperation.READ:
                await self._handle_file_read_operation(file_op)
            elif file_op.operation == FileOperation.CREATE:
                await self._handle_file_create_operation(file_op)
        
        prompt = f"""Convert the following input to the target format:

Input: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input data provided'}

Requirements:
- Follow modern best practices
- Include proper error handling
- Add type hints if applicable
- Use clean, readable code
- Return only the converted content, no explanations
- Create the files specified in the task file operations"""

        system_instruction = "You are an expert developer specializing in code conversion and transformation."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Conversion task completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"converted_content": result}
        task.code = result
        
        # Save created files
        for file_op in task.file_operations:
            if file_op.operation == FileOperation.CREATE and result:
                await self._save_generated_file(file_op, result)
    
    async def _execute_code_generation_task(self, task: TaskItem) -> None:
        """Execute a code generation task with file operations"""
        logger.info("  💻 Executing code generation task...")
        
        prompt = f"""Generate code for the following requirement:

{task.description}

Input context: {json.dumps(task.input_data, indent=2) if task.input_data else 'None'}

Requirements:
- Use modern language features
- Include error handling
- Add docstrings/comments for clarity
- Follow PEP 8 and best practices
- Return only the code, no explanations
- Create the files specified in the task file operations"""

        system_instruction = "You are an expert software developer. Generate clean, production-ready code."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Code generation completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"generated_code": result}
        task.code = result
        
        # Save generated files
        for file_op in task.file_operations:
            if file_op.operation == FileOperation.CREATE and result:
                await self._save_generated_file(file_op, result)
    
    async def _execute_analysis_task(self, task: TaskItem) -> None:
        """Execute an analysis task with file operations"""
        logger.info("  🔍 Executing analysis task...")
        
        prompt = f"""Analyze the following input and provide insights:

Input: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input provided'}

Analysis requirements:
- Identify key patterns and insights
- Highlight potential issues or opportunities
- Provide actionable recommendations
- Structure the analysis clearly"""

        system_instruction = "You are an expert analyst. Provide thorough, actionable analysis."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Analysis completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"analysis": result}
    
    async def _execute_review_task(self, task: TaskItem) -> None:
        """Execute a review task with file operations"""
        logger.info("  👀 Executing review task...")
        
        prompt = f"""Review the following work and provide feedback:

Input to review: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input provided'}

Review criteria:
- Code quality and best practices
- Potential issues or bugs
- Performance considerations
- Security concerns
- Maintainability

Provide constructive feedback and specific recommendations."""

        system_instruction = "You are an expert code reviewer. Provide thorough, constructive feedback."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Review completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"review_feedback": result}
    
    async def _execute_testing_task(self, task: TaskItem) -> None:
        """Execute a testing task with file operations"""
        logger.info("  🧪 Executing testing task...")
        
        prompt = f"""Create tests for the following code or functionality:

Input: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input provided'}

Testing requirements:
- Cover edge cases and error conditions
- Include unit and integration tests
- Follow testing best practices
- Use pytest or unittest framework
- Return only the test code
- Create the test files specified in the task file operations"""

        system_instruction = "You are an expert QA engineer. Generate comprehensive, well-structured tests."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Testing completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"test_code": result}
        task.code = result
        
        # Save test files
        for file_op in task.file_operations:
            if file_op.operation == FileOperation.CREATE and result:
                await self._save_generated_file(file_op, result)
    
    async def _handle_file_read_operation(self, file_op: FileOperationItem):
        """Handle file read operation with logging"""
        try:
            file_path = Path(file_op.file_path)
            if file_path.exists():
                file_size = file_path.stat().st_size
                file_op.size_bytes = file_size
                file_op.checksum = hashlib.md5(file_path.read_bytes()).hexdigest()[:16]
                self.audit_logger.log_file_operation(file_op, "success", f"Read {file_size} bytes")
            else:
                self.audit_logger.log_file_operation(file_op, "error", "File not found")
        except Exception as e:
            self.audit_logger.log_file_operation(file_op, "error", str(e))
    
    async def _handle_file_create_operation(self, file_op: FileOperationItem):
        """Handle file create operation with logging"""
        try:
            file_path = Path(file_op.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.audit_logger.log_file_operation(file_op, "pending", "File creation scheduled")
        except Exception as e:
            self.audit_logger.log_file_operation(file_op, "error", str(e))
    
    async def _save_generated_file(self, file_op: FileOperationItem, content: str):
        """Save generated content to file with proper logging"""
        try:
            file_path = Path(file_op.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            file_size = file_path.stat().st_size
            file_op.size_bytes = file_size
            file_op.checksum = hashlib.md5(file_path.read_bytes()).hexdigest()[:16]
            file_op.completed_at = datetime.now(timezone.utc).isoformat()
            
            self.audit_logger.log_file_operation(file_op, "success", f"Created {file_size} bytes")
            
        except Exception as e:
            self.audit_logger.log_file_operation(file_op, "error", str(e))
    
    async def _review_task(self, task: TaskItem) -> None:
        """Review task execution results with comprehensive logging"""
        logger.info("  🔍 Reviewing task results...")
        
        prompt = f"""Review the following task execution results:

Task: {task.title}
Description: {task.description}
Output: {json.dumps(task.output_data, indent=2) if task.output_data else 'No output'}
Code: {task.code[:500] + '...' if task.code and len(task.code) > 500 else task.code if task.code else 'No code'}
File Operations: {len(task.file_operations)} operations
Output Summary: {task.output.summary if task.output else 'No summary'}

Provide a brief review of:
1. Quality of execution
2. Any potential improvements
3. Next steps or recommendations
4. File operations results

Keep it concise and actionable."""

        system_instruction = "You are an expert reviewer. Provide brief, constructive feedback."
        
        result = await self.call_gemini(prompt, system_instruction)
        review_summary = result[:200] + "..." if len(result) > 200 else result
        logger.info(f"  📋 Review: {review_summary}")
    
    async def run_full_workflow(
        self, 
        goal: str, 
        input_context: Optional[Dict[str, Any]] = None
    ) -> TaskList:
        """
        Run the complete synthesis workflow with comprehensive logging
        """
        logger.info(f"\n🚀 Starting full synthesis workflow for: {goal}")
        logger.info(f"🆔 Session ID: {self.session_id}")
        logger.info(f"📊 Log file: {self.log_file}")
        
        # Step 1: Create todo list
        task_list = await self.create_task_list(goal, input_context)
        
        # Step 2-5: Execute and review tasks in loop
        completed_tasks = 0
        total_tasks = len(task_list.tasks)
        failed_tasks = 0
        
        while task_list.status == 'active':
            task = await self.process_next_task()
            if not task:  # All tasks completed or no more available tasks
                break
            
            completed_tasks += 1
            if task.status == TaskStatus.FAILED:
                failed_tasks += 1
            
            logger.info(f"\n📊 Progress: {completed_tasks}/{total_tasks} tasks completed")
            logger.info(f"   Status: {task_list.progress}")
            logger.info(f"   Session log: {self.log_file}")
            
            # Brief pause between tasks
            await asyncio.sleep(1)
        
        # Final output generation
        output_list = task_list.generate_output_list()
        
        logger.info(f"\n🎉 Workflow completed!")
        logger.info(f"✅ Completed: {completed_tasks} tasks")
        logger.info(f"❌ Failed: {failed_tasks} tasks")
        logger.info(f"📋 Output items: {len(output_list)}")
        
        # Log session summary
        session_summary = {
            "session_id": self.session_id,
            "goal": goal,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "output_items": len(output_list),
            "start_time": task_list.created_at,
            "end_time": datetime.now(timezone.utc).isoformat(),
            "log_file": str(self.log_file),
            "audit_file": str(self.audit_logger.log_file)
        }
        
        summary_file = Config.LOGS_DIR / f"summary_{self.session_id}.json"
        async with aiofiles.open(summary_file, 'w') as f:
            await f.write(json.dumps(session_summary, indent=2))
        
        return task_list
    
    def get_task_list(self, task_list_id: Optional[str] = None) -> Optional[TaskList]:
        """Get a task list by ID or return current one"""
        if task_list_id:
            return self.task_lists.get(task_list_id)
        return self.current_task_list
    
    def get_progress(self) -> Optional[Dict[str, int]]:
        """Get current progress summary"""
        if not self.current_task_list:
            return None
        return self.current_task_list.progress
    
    async def save_task_list(self, task_list: TaskList) -> None:
        """Save task list to file with enhanced data"""
        file_path = Config.TASKS_DIR / f"{task_list.id}.json"
        
        # Convert to JSON-serializable format
        task_list_dict = asdict(task_list)
        
        # Convert enums to strings
        for task_dict in task_list_dict['tasks']:
            task_dict['type'] = task_dict['type'].value
            task_dict['status'] = task_dict['status'].value
            task_dict['priority'] = task_dict['priority'].value
            for file_op in task_dict.get('file_operations', []):
                file_op['operation'] = file_op['operation'].value
        
        for file_op in task_list_dict['file_operations']:
            file_op['operation'] = file_op['operation'].value
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(task_list_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Task list saved: {file_path}")

# HTML to Next.js Integration with Enhanced Logging
async def enhanced_html_to_nextjs_conversion(html_file_path: str) -> None:
    """
    Enhanced HTML to Next.js conversion using task synthesis with comprehensive logging
    """
    task_manager = TaskSynthesisManager()
    
    logger.info(f"🔄 Starting enhanced HTML to Next.js conversion")
    logger.info(f"📁 Input file: {html_file_path}")
    logger.info(f"🆔 Session ID: {task_manager.session_id}")
    
    # Create a task list for the conversion
    task_list = await task_manager.create_task_list(
        f"Convert HTML file to Next.js components: {Path(html_file_path).name}",
        {
            "input_file": html_file_path,
            "target_framework": "Next.js",
            "target_language": "TypeScript",
            "session_id": task_manager.session_id
        }
    )
    
    # Add specific conversion tasks with file operations
    additional_tasks = [
        TaskItem(
            id=task_manager.generate_id(),
            title="Read and analyze HTML file",
            description="Read the HTML file and extract structure, scripts, and styles",
            type=TaskType.ANALYSIS,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            estimated_time=10,
            file_operations=[
                FileOperationItem(
                    operation=FileOperation.READ,
                    file_path=html_file_path,
                    description="Source HTML file to analyze",
                    priority=Priority.HIGH
                )
            ]
        ),
        TaskItem(
            id=task_manager.generate_id(),
            title="Generate Next.js component structure",
            description="Create TypeScript React component files with proper structure",
            type=TaskType.CODE_GENERATION,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            estimated_time=30,
            file_operations=[
                FileOperationItem(
                    operation=FileOperation.CREATE,
                    file_path="./output/components/Header.tsx",
                    description="Header component",
                    priority=Priority.HIGH
                ),
                FileOperationItem(
                    operation=FileOperation.CREATE,
                    file_path="./output/components/Main.tsx",
                    description="Main content component",
                    priority=Priority.HIGH
                ),
                FileOperationItem(
                    operation=FileOperation.CREATE,
                    file_path="./output/page.tsx",
                    description="Next.js main page",
                    priority=Priority.HIGH
                )
            ]
        )
    ]
    
    # Update task list with additional tasks
    task_list.tasks.extend(additional_tasks)
    task_list._update_progress()
    
    # Save and run the workflow
    await task_manager.save_task_list(task_list)
    
    # Show file operations summary
    file_ops_summary = task_list.get_file_operations_summary()
    logger.info("\n📋 File Operations Summary:")
    for op_type, ops in file_ops_summary.items():
        if ops:
            logger.info(f"  {op_type.upper()}: {len(ops)} files")
            for op in ops[:3]:  # Show first 3
                logger.info(f"    - {op.file_path}")
            if len(ops) > 3:
                logger.info(f"    ... and {len(ops) - 3} more")
    
    await task_manager.run_full_workflow(
        f"Convert {Path(html_file_path).name} to Next.js components",
        {"input_file": html_file_path}
    )

# Enhanced CLI Interface
async def main():
    """Enhanced main CLI interface"""
    if len(sys.argv) < 2:
        print("""
🚀 Enhanced Task Synthesis System - Python Version
==================================================

Features:
- 📊 Comprehensive request/response logging with full dumps
- 📁 File operation tracking (create, read, delete, modify files)
- 📋 Output list generation when task lists are updated
- 🔍 Detailed audit trail with session tracking
- 💾 Automatic file generation and management

Workflow: Create todo list → Input to task → Execute code → Review → Repeat

Commands:
  1. Interactive goal setting:
     python enhanced_task_synthesis_system.py

  2. Convert HTML to Next.js:
     python enhanced_task_synthesis_system.py convert <html-file-path>

  3. Run custom workflow:
     python enhanced_task_synthesis_system.py workflow "<goal description>"

  4. Show task list progress:
     python enhanced_task_synthesis_system.py status

  5. Load existing task list:
     python enhanced_task_synthesis_system.py load <task-list-id>

  6. Show audit log:
     python enhanced_task_synthesis_system.py audit <session-id>

Examples:
  python enhanced_task_synthesis_system.py convert ./input/index.html
  python enhanced_task_synthesis_system.py workflow "Build a todo app with React and TypeScript"

Log Files:
  - ./logs/session_<session-id>.log - Session execution log
  - ./logs/audit_<session-id>.jsonl - Detailed audit trail
  - ./logs/summary_<session-id>.json - Session summary
  - ./output/output_<task-list-id>.json - Generated output list
        """)
        return
    
    command = sys.argv[1]
    task_manager = TaskSynthesisManager()
    
    try:
        if command == "convert":
            if len(sys.argv) < 3:
                print("❌ Please provide HTML file path")
                sys.exit(1)
            
            await enhanced_html_to_nextjs_conversion(sys.argv[2])
        
        elif command == "workflow":
            if len(sys.argv) < 3:
                print("❌ Please provide goal description")
                sys.exit(1)
            
            await task_manager.run_full_workflow(sys.argv[2])
        
        elif command == "status":
            progress = task_manager.get_progress()
            if progress:
                print("\n📊 Current Task List Progress:")
                print(f"   Total: {progress['total']}")
                print(f"   Completed: {progress['completed']}")
                print(f"   In Progress: {progress['in_progress']}")
                print(f"   Failed: {progress['failed']}")
                print(f"   Pending: {progress['pending']}")
                print(f"   Session ID: {task_manager.session_id}")
                print(f"   Log file: {task_manager.log_file}")
            else:
                print("❌ No active task list")
        
        elif command == "load":
            if len(sys.argv) < 3:
                print("❌ Please provide task list ID")
                sys.exit(1)
            
            loaded_task_list = await task_manager.load_task_list(sys.argv[2])
            if loaded_task_list:
                print(f"📁 Loaded task list: {loaded_task_list.title}")
                print(f"   Description: {loaded_task_list.description}")
                print(f"   Status: {loaded_task_list.status}")
                print(f"   Tasks: {len(loaded_task_list.tasks)}")
                
                # Show file operations summary
                file_ops_summary = loaded_task_list.get_file_operations_summary()
                print(f"   File operations: {sum(len(ops) for ops in file_ops_summary.values())}")
                
                # Ask if user wants to continue
                response = input("\nContinue with this task list? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    await task_manager.run_full_workflow(
                        loaded_task_list.title,
                        {"loaded_task_list": loaded_task_list.id}
                    )
        
        elif command == "audit":
            if len(sys.argv) < 3:
                print("❌ Please provide session ID")
                sys.exit(1)
            
            session_id = sys.argv[2]
            audit_file = Config.AUDIT_DIR / f"audit_{session_id}.jsonl"
            if audit_file.exists():
                print(f"\n📊 Audit Log for Session: {session_id}")
                with open(audit_file, 'r') as f:
                    for line in f:
                        log_entry = json.loads(line)
                        print(f"  {log_entry['timestamp']} - {log_entry['type']}: {log_entry.get('status', 'unknown')}")
            else:
                print("❌ Audit log not found")
        
        else:
            print("🎯 Interactive Mode - Setting up enhanced synthesis workflow...")
            print("Please provide a goal or task description:")
            print('Example: "Convert my website to Next.js" or "Build a REST API"')
            
            print("\n💡 Use specific commands for automation:")
            print('  - "convert <file>" for HTML to Next.js conversion')
            print('  - "workflow <goal>" for custom goal-based workflows')
            print('  - "status" to show current progress')
            print('  - "audit <session-id>" to view audit logs')
    
    except Exception as error:
        logger.error(f"\n💥 Error: {error}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())