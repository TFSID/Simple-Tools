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
import re
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
    CLEANUP = "cleanup"
    MAINTENANCE = "maintenance"
    OPTIMIZATION = "optimization"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REEXECUTING = "reexecuting"  # New: for tasks that need to be re-executed
    WAITING = "waiting"  # New: for tasks waiting for dynamic insertion

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
        """Get summary of all file operations organized by type (for logging/debugging)"""
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

    def get_file_operations_for_audit(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get serializable file operations summary for audit logging"""
        summary = {
            "create": [],
            "read": [],
            "delete": [],
            "modify": [],
            "execute": []
        }
        
        for task in self.tasks:
            for file_op in task.file_operations:
                # Convert FileOperationItem to dict with enum values converted
                file_op_dict = asdict(file_op)
                file_op_dict['operation'] = file_op.operation.value
                file_op_dict['priority'] = file_op.priority.value
                summary[file_op.operation.value].append(file_op_dict)
        
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

    def log_file_operation(self, operation: FileOperationItem, status: str, result: Optional[str] = None, duration_ms: Optional[float] = None):
        """Log file operation events with comprehensive real-time tracking"""
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
            "checksum": operation.checksum,
            "duration_ms": duration_ms,
            "output_folder": str(Config.OUTPUT_DIR) if str(operation.file_path).startswith(str(Config.OUTPUT_DIR)) else "external"
        }
        
        # Write to detailed log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Real-time console logging with detailed formatting
        op_icon = {
            FileOperation.CREATE: "📄",
            FileOperation.READ: "📖", 
            FileOperation.DELETE: "🗑️",
            FileOperation.MODIFY: "✏️",
            FileOperation.EXECUTE: "⚡"
        }
        
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        
        # Enhanced real-time logging with timestamps and details
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Millisecond precision
        folder_info = f" [{Config.OUTPUT_DIR.name}/]" if str(operation.file_path).startswith(str(Config.OUTPUT_DIR)) else ""
        size_info = f" ({operation.size_bytes:,} bytes)" if operation.size_bytes else ""
        duration_info = f" [{duration_ms:.1f}ms]" if duration_ms else ""
        
        log_message = f"{timestamp} {op_icon[operation.operation]}{status_icon} {operation.file_path}{folder_info}: {operation.description}{size_info}{duration_info}"
        
        if result:
            log_message += f" | {result}"
            
        # Console output with appropriate level based on status
        if status == "error":
            logger.error(log_message)
        elif status in ["pending", "in_progress"]:
            logger.info(log_message) 
        else:
            logger.info(log_message)
    
    def log_file_operation_start(self, operation: FileOperationItem) -> float:
        """Log file operation start and return start time"""
        start_time = time.time()
        self.log_file_operation(operation, "pending", "File operation starting")
        return start_time
    
    def log_file_operation_end(self, operation: FileOperationItem, status: str, result: Optional[str] = None, start_time: Optional[float] = None):
        """Log file operation completion with duration calculation"""
        duration_ms = None
        if start_time:
            duration_ms = (time.time() - start_time) * 1000
        self.log_file_operation(operation, status, result, duration_ms)

class TaskSynthesisManager:
    """
    Enhanced task synthesis manager with comprehensive logging and file tracking
    """
    
    def __init__(self):
        self.task_lists: Dict[str, TaskList] = {}
        self.current_task_list: Optional[TaskList] = None
        self.session_id = str(uuid.uuid4())
        self.audit_logger = AuditLogger()
        
        # Shared context/scratchpad for maintaining continuity between tasks
        self.shared_context: Dict[str, Any] = {
            "task_outputs": {},  # Store outputs from completed tasks
            "key_insights": [],  # Store key insights and discoveries
            "file_mappings": {},  # Store file transformations and mappings
            "context_history": []  # Track context evolution over time
        }
        
        # Create session log file
        self.log_file = Config.LOGS_DIR / f"session_{self.session_id}.log"
    
    def save_task_output_to_context(self, task_id: str, task_output: Any, task_type: str = "general"):
        """
        Save task output to shared context for future tasks to use
        
        Args:
            task_id: Unique identifier for the task
            task_output: The output/content from the completed task
            task_type: Type of task for categorization
        """
        try:
            # Save to task_outputs
            self.shared_context["task_outputs"][task_id] = {
                "content": task_output,
                "type": task_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id
            }
            
            # Add to context history
            self.shared_context["context_history"].append({
                "action": "task_output_saved",
                "task_id": task_id,
                "task_type": task_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"📝 Task output saved to context: {task_id} ({task_type})")
            
        except Exception as e:
            logger.error(f"❌ Failed to save task output to context: {e}")
    
    def add_key_insight(self, insight: str, source_task: str = None):
        """
        Add a key insight to the shared context
        
        Args:
            insight: The insight or discovery to store
            source_task: Optional task ID that generated this insight
        """
        try:
            insight_entry = {
                "insight": insight,
                "source_task": source_task,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.shared_context["key_insights"].append(insight_entry)
            
            # Add to context history
            self.shared_context["context_history"].append({
                "action": "insight_added",
                "insight": insight[:100] + "..." if len(insight) > 100 else insight,
                "source_task": source_task,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"💡 Key insight added to context: {insight[:80]}{'...' if len(insight) > 80 else ''}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add key insight: {e}")
    
    def save_file_mapping(self, original_path: str, new_path: str, transformation_type: str = "migration"):
        """
        Save file transformation mapping for future reference
        
        Args:
            original_path: Original file path
            new_path: New/migrated file path
            transformation_type: Type of transformation (migration, refactor, etc.)
        """
        try:
            if original_path not in self.shared_context["file_mappings"]:
                self.shared_context["file_mappings"][original_path] = []
            
            mapping_entry = {
                "new_path": new_path,
                "transformation_type": transformation_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.shared_context["file_mappings"][original_path].append(mapping_entry)
            
            # Add to context history
            self.shared_context["context_history"].append({
                "action": "file_mapping_saved",
                "original_path": original_path,
                "new_path": new_path,
                "transformation_type": transformation_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"🗂️ File mapping saved: {original_path} → {new_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save file mapping: {e}")
    
    def get_relevant_context(self, task_type: str = None, task_id: str = None, max_items: int = 10) -> Dict[str, Any]:
        """
        Get relevant context for a specific task
        
        Args:
            task_type: Type of task to get context for
            task_id: Specific task ID to get context for
            max_items: Maximum number of items to return
            
        Returns:
            Dictionary with relevant context sections
        """
        relevant_context = {
            "task_outputs": {},
            "key_insights": [],
            "file_mappings": {},
            "recent_history": []
        }
        
        try:
            # Get recent task outputs (last few)
            recent_outputs = list(self.shared_context["task_outputs"].items())[-max_items:]
            relevant_context["task_outputs"] = dict(recent_outputs)
            
            # Get recent insights (last few)
            relevant_context["key_insights"] = self.shared_context["key_insights"][-max_items:]
            
            # Get file mappings
            relevant_context["file_mappings"] = self.shared_context["file_mappings"]
            
            # Get recent history
            relevant_context["recent_history"] = self.shared_context["context_history"][-max_items:]
            
            logger.info(f"🔍 Retrieved relevant context for task type: {task_type or 'general'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to get relevant context: {e}")
        
        return relevant_context
    
    def generate_context_summary(self) -> str:
        """Generate a human-readable summary of the shared context"""
        try:
            summary_parts = []
            
            # Task outputs summary
            if self.shared_context["task_outputs"]:
                summary_parts.append(f"📋 Completed Tasks ({len(self.shared_context['task_outputs'])}):")
                for task_id, task_data in list(self.shared_context["task_outputs"].items())[-5:]:  # Last 5
                    content_preview = str(task_data["content"])[:100] + "..." if len(str(task_data["content"])) > 100 else str(task_data["content"])
                    summary_parts.append(f"  - {task_id}: {task_data['type']} → {content_preview}")
            
            # Key insights summary
            if self.shared_context["key_insights"]:
                summary_parts.append(f"\n💡 Key Insights ({len(self.shared_context['key_insights'])}):")
                for insight_data in self.shared_context["key_insights"][-5:]:  # Last 5
                    insight_preview = insight_data["insight"][:80] + "..." if len(insight_data["insight"]) > 80 else insight_data["insight"]
                    source = f" (from {insight_data['source_task']})" if insight_data["source_task"] else ""
                    summary_parts.append(f"  - {insight_preview}{source}")
            
            # File mappings summary
            if self.shared_context["file_mappings"]:
                summary_parts.append(f"\n🗂️ File Mappings ({len(self.shared_context['file_mappings'])}):")
                for orig_path, mappings in list(self.shared_context["file_mappings"].items())[-3:]:  # Last 3
                    latest_mapping = mappings[-1]  # Get latest mapping
                    summary_parts.append(f"  - {orig_path} → {latest_mapping['new_path']}")
            
            return "\n".join(summary_parts) if summary_parts else "📝 No context available yet"
            
        except Exception as e:
            logger.error(f"❌ Failed to generate context summary: {e}")
            return f"❌ Error generating context summary: {e}"
    
    def enhance_prompt_with_context(self, base_prompt: str, task: TaskItem = None) -> str:
        """
        Enhance a prompt with relevant shared context
        
        Args:
            base_prompt: The original prompt to enhance
            task: Optional task to get context for
            
        Returns:
            Enhanced prompt with context
        """
        try:
            # Get relevant context
            task_type = task.type.value if task else "general"
            task_id = task.id if task else None
            relevant_context = self.get_relevant_context(task_type=task_type, task_id=task_id, max_items=10)
            
            context_section = "\n=== SHARED CONTEXT FROM PREVIOUS TASKS ===\n"
            
            # Add recent task outputs
            if relevant_context["task_outputs"]:
                context_section += "Recent Task Outputs:\n"
                for task_id, task_data in relevant_context["task_outputs"].items():
                    content_preview = str(task_data["content"])[:200] + "..." if len(str(task_data["content"])) > 200 else str(task_data["content"])
                    context_section += f"- {task_id} ({task_data['type']}): {content_preview}\n"
                context_section += "\n"
            
            # Add key insights
            if relevant_context["key_insights"]:
                context_section += "Key Insights:\n"
                for insight_data in relevant_context["key_insights"]:
                    insight_preview = insight_data["insight"][:150] + "..." if len(insight_data["insight"]) > 150 else insight_data["insight"]
                    source = f" (from {insight_data['source_task']})" if insight_data["source_task"] else ""
                    context_section += f"- {insight_preview}{source}\n"
                context_section += "\n"
            
            # Add file mappings
            if relevant_context["file_mappings"]:
                context_section += "File Mappings:\n"
                for orig_path, mappings in relevant_context["file_mappings"].items():
                    latest_mapping = mappings[-1]  # Get latest mapping
                    context_section += f"- {orig_path} → {latest_mapping['new_path']} ({latest_mapping['transformation_type']})\n"
                context_section += "\n"
            
            if len(context_section.strip()) > 50:  # Only add if there's substantial context
                enhanced_prompt = base_prompt + context_section
                logger.info(f"  🔗 Enhanced prompt with {len(relevant_context['task_outputs'])} outputs, {len(relevant_context['key_insights'])} insights")
                return enhanced_prompt
            else:
                return base_prompt
                
        except Exception as e:
            logger.error(f"❌ Failed to enhance prompt with context: {e}")
            return base_prompt
    
    def generate_id(self) -> str:
        """Generate a unique ID"""
        return f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    def get_file_operations_realtime_status(self) -> Dict[str, Any]:
        """Get comprehensive real-time file operations status with folder organization"""
        status = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "output_directory": {
                "path": str(Config.OUTPUT_DIR),
                "exists": Config.OUTPUT_DIR.exists(),
                "files": []
            },
            "logs_directory": {
                "path": str(Config.LOGS_DIR),
                "exists": Config.LOGS_DIR.exists(),
                "log_files": []
            },
            "folder_organization": {
                "outputs_go_to": str(Config.OUTPUT_DIR),
                "logs_go_to": str(Config.LOGS_DIR),
                "auto_redirect": True
            },
            "realtime_logging": {
                "enabled": True,
                "features": [
                    "Timestamp logging with millisecond precision",
                    "Real-time console output with emojis",
                    "File operation progress tracking",
                    "Duration measurement for all operations",
                    "Checksum verification for file integrity",
                    "Size tracking for all file operations",
                    "Error handling with detailed error messages",
                    "Audit trail with JSON logging"
                ]
            },
            "file_operations_supported": [
                "CREATE - Create new files with content",
                "READ - Read existing files with validation",
                "DELETE - Remove files with safety checks",
                "MODIFY - Update file contents",
                "EXECUTE - Run executable files (Python)"
            ]
        }
        
        # Scan output directory for files
        if Config.OUTPUT_DIR.exists():
            for file_path in Config.OUTPUT_DIR.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        status["output_directory"]["files"].append({
                            "name": file_path.name,
                            "path": str(file_path.relative_to(Config.OUTPUT_DIR)),
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Could not read file stats for {file_path}: {e}")
        
        # Scan logs directory for log files
        if Config.LOGS_DIR.exists():
            for file_path in Config.LOGS_DIR.glob('*'):
                if file_path.is_file() and file_path.suffix == '.log':
                    try:
                        stat = file_path.stat()
                        status["logs_directory"]["log_files"].append({
                            "name": file_path.name,
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Could not read log file stats for {file_path}: {e}")
        
        return status
    
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
        
        # Handle API response that starts with "json" prefix
        lines = text.split('\n')
        if lines and lines[0].strip().lower() == 'json':
            logger.info("🔧 Detected 'json' prefix in API response, removing it")
            text = '\n'.join(lines[1:]).strip()
        
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
        
        result = '\n'.join(cleaned_lines)
        logger.info(f"✅ JSON extraction successful, length: {len(result)} characters")
        return result
    
    def _parse_json_with_repair(self, json_str: str) -> dict:
        """
        Parse JSON with repair capabilities and multiple fallback strategies
        """
        import re
        
        # Strategy 1: Try direct parsing
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {e}")
            
        # Strategy 2: Try common JSON repairs
        repaired_json = self._repair_common_json_errors(json_str)
        try:
            return json.loads(repaired_json)
        except json.JSONDecodeError as e:
            logger.warning(f"Repaired JSON parsing failed: {e}")
            
        # Strategy 3: Try to extract a smaller, valid JSON object
        try:
            return self._extract_partial_json(json_str)
        except Exception as e:
            logger.warning(f"Partial JSON extraction failed: {e}")
            
        # Strategy 4: Create a minimal valid response as last resort
        logger.error("💥 All JSON parsing strategies failed. Creating minimal valid response.")
        return self._create_fallback_response(json_str)
    
    def _repair_common_json_errors(self, json_str: str) -> str:
        """
        Repair common JSON syntax errors
        """
        import re
        
        # Remove leading "json" prefix if present
        lines = json_str.split('\n')
        if lines and lines[0].strip().lower() == 'json':
            json_str = '\n'.join(lines[1:])
            json_str = json_str.strip()
        
        # Fix common trailing comma issues
        json_str = re.sub(r',(\s*})', r'\1', json_str)
        json_str = re.sub(r',(\s*])', r'\1', json_str)
        
        # Fix unescaped newlines in strings
        json_str = re.sub(r'(?<!\\)\\n', '\\\\n', json_str)
        
        # Fix missing commas before closing brackets
        json_str = re.sub(r'(\w+)\s*}\s*{', r'\1}, {', json_str)
        json_str = re.sub(r'(\w+)\s*]\s*{', r'\1], {', json_str)
        
        return json_str
    
    def _extract_partial_json(self, json_str: str) -> dict:
        """
        Extract a partial valid JSON structure, focusing on the main task list
        """
        import re
        
        # Try to find the "tasks" array and extract it
        tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
        if tasks_match:
            tasks_content = tasks_match.group(1)
            # Try to parse individual tasks
            tasks = []
            task_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            task_matches = re.findall(task_pattern, tasks_content)
            
            for task_match in task_matches:
                try:
                    task = json.loads(task_match)
                    tasks.append(task)
                except json.JSONDecodeError:
                    # If individual task parsing fails, create a minimal valid task
                    tasks.append({
                        "id": f"task_{len(tasks) + 1}",
                        "title": "Extracted Task",
                        "description": "Task extracted from partial JSON",
                        "type": "analysis",
                        "priority": "medium",
                        "file_operations": []
                    })
            
            return {
                "id": "html_to_nextjs_conversion",
                "title": "Convert index.html to Next.js Components", 
                "description": "This project aims to convert a static HTML file into a dynamic Next.js application.",
                "tasks": tasks
            }
        
        # If we can't find tasks, try to extract a minimal structure
        id_match = re.search(r'"id"\s*:\s*"([^"]*)"', json_str)
        title_match = re.search(r'"title"\s*:\s*"([^"]*)"', json_str)
        
        return {
            "id": id_match.group(1) if id_match else "html_to_nextjs_conversion",
            "title": title_match.group(1) if title_match else "Convert index.html to Next.js Components",
            "description": "Extracted from partial JSON due to parsing errors",
            "tasks": []
        }
    
    def _create_fallback_response(self, json_str: str) -> dict:
        """
        Create a minimal valid response when all parsing fails
        """
        logger.error("🎯 Creating fallback response due to complete JSON parsing failure")
        
        # Extract any useful information from the failed JSON
        import re
        id_match = re.search(r'"id"\s*:\s*"([^"]*)"', json_str)
        title_match = re.search(r'"title"\s*:\s*"([^"]*)"', json_str)
        
        return {
            "id": id_match.group(1) if id_match else "html_to_nextjs_conversion",
            "title": title_match.group(1) if title_match else "Convert index.html to Next.js Components",
            "description": "Basic conversion task - detailed parsing failed",
            "tasks": [
                {
                    "id": "setup_nextjs",
                    "title": "Setup Next.js Project",
                    "description": "Initialize Next.js project with TypeScript and Tailwind CSS",
                    "type": "setup",
                    "priority": "high",
                    "file_operations": [
                        {
                            "operation": "create",
                            "file_path": "package.json",
                            "description": "Create Next.js package.json with dependencies"
                        }
                    ]
                },
                {
                    "id": "analyze_html",
                    "title": "Analyze HTML Structure", 
                    "description": "Extract and analyze the HTML structure for component conversion",
                    "type": "analysis",
                    "priority": "high",
                    "file_operations": []
                }
            ]
        }
    
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
        Create a new task list from a goal with enhanced logging and shared context
        """
        logger.info(f"\n🎯 Creating task list for goal: {goal}")
        
        # Get relevant shared context for this task creation
        relevant_context = self.get_relevant_context(task_type="task_creation", max_items=20)
        context_summary = self.generate_context_summary()
        
        # Check if this involves HTML file processing
        html_files = []
        if input_context:
            if 'html_file' in input_context:
                html_files.append(input_context['html_file'])
            if 'input_file' in input_context:
                html_files.append(input_context['input_file'])
            if 'file_path' in input_context:
                html_files.append(input_context['file_path'])
            
        prompt = f"""Create a comprehensive task list for the following goal: "{goal}"

=== INPUT CONTEXT ===
{json.dumps(input_context, indent=2) if input_context else 'None'}

=== SHARED CONTEXT (Previous Task Outputs & Insights) ===
{context_summary}

=== HTML FILES TO PROCESS ===
{json.dumps(html_files, indent=2) if html_files else 'None'}

=== CRITICAL REQUIREMENT: HTML INPUT READING ===
{f'''MUST start with TaskType.ANALYSIS for file reading:
Tugas 1: "Analisis dan Baca File HTML" (TaskType.ANALYSIS)
- Membaca konten file HTML yang sebenarnya
- Mengekstrak struktur, CSS, JavaScript yang tertanam
- Mengidentifikasi komponen-komponen utama (header, nav, main, footer, dll)
- Menyimpan hasil analisis ke shared context
- Contoh deskripsi: "Baca dan analisis index.html dari direktori input, ekstrak bagian <nav>, <footer>, dan <main>, identifikasi CSS dan JavaScript yang tertanam"''' if html_files else 'No HTML files to process'}

=== WORKFLOW ===
Create tasks that follow this workflow:
1. Create todo list
2. Input to task 
3. Execute code
4. Review results
5. Repeat for next task

=== REQUIREMENTS ===
Each task should be:
- Specific and actionable
- Have clear input and output expectations
- Include error handling considerations
- Be executable and testable
- Include realistic time estimates
- Specify what files will be created, read, or modified
- Build upon previous task outputs when relevant
- {f'First task MUST be TaskType.ANALYSIS to read and analyze HTML files' if html_files else ''}

**PERINGATAN PENTING - ENHANCED SINGLE FILE CREATION RULE:**
Untuk tugas code_generation atau conversion:
- **File Creation**: Setiap tugas HANYA boleh memiliki SATU (1) FileOperation dengan operasi "create" untuk FILES
- **Directory Creation**: BOLEH membuat MULTIPLE direktori dalam satu tugas (contoh: src/app, src/components, src/styles, public)
- Jika Anda perlu membuat Component.tsx dan Component.module.css, Anda HARUS membuat DUA TUGAS TERPISAH
- Satu tugas = satu file creation ATAU multiple directory creation
- Multiple file creation (bukan direktori) harus dipisah menjadi multiple tasks dengan dependencies

For each task, include a "file_operations" section specifying:
- What files will be created (with paths)
- What files will be read
- What files will be modified
- What files will be deleted (if any)

=== RESPONSE FORMAT ===
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
            
            # Enhanced JSON parsing with repair and fallback strategies
            try:
                task_data = self._parse_json_with_repair(json_data)
            except Exception as e:
                logger.error(f"💥 Critical JSON parsing error: {e}")
                logger.error(f"JSON Error details: {e}")
                raise ValueError(f"Failed to parse AI response as JSON. Error: {e}") from e
            
            # Process file operations for each task
            tasks = []
            for task in task_data['tasks']:
                file_operations = []
                for file_op in task.get('file_operations', []):
                    # Map API response fields to FileOperationItem fields
                    # Handle different possible field names
                    file_path = file_op.get('file_path') or file_op.get('path') or file_op.get('target_path') or file_op.get('target')
                    description = file_op.get('description') or file_op.get('desc') or f"File operation: {file_op.get('operation', 'unknown')}"
                    operation = file_op.get('operation', 'create')
                    priority = file_op.get('priority', 'medium')
                    
                    if not file_path:
                        logger.warning(f"Missing file_path in file operation: {file_op}")
                        continue
                    
                    file_op_item = FileOperationItem(
                        operation=FileOperation(operation),
                        file_path=file_path,
                        description=description,
                        priority=Priority(priority)
                    )
                    file_operations.append(file_op_item)
                
                # Log file operations for debugging
                if file_operations:
                    logger.debug(f"Task '{task.get('title', 'Unknown')}' has {len(file_operations)} file operations")
                    for i, fo in enumerate(file_operations):
                        logger.debug(f"  [{i+1}] {fo.operation.value}: {fo.file_path} - {fo.description}")
                
                # Validate enhanced single file creation rule for code_generation and conversion tasks
                task_type_for_validation = task.get('type', '').lower()
                if task_type_for_validation in ['code_generation', 'conversion']:
                    create_operations = [fo for fo in file_operations if fo.operation == FileOperation.CREATE]
                    if len(create_operations) > 1:
                        # Enhanced rule: allow multiple create operations if they are all directory creation
                        directory_operations = [fo for fo in create_operations if self._is_directory_path(fo.file_path)]
                        file_operations_list = [fo for fo in create_operations if not self._is_directory_path(fo.file_path)]
                        
                        if len(directory_operations) > 0 and len(file_operations_list) == 0:
                            # All operations are directory creation - allow multiple
                            logger.info(f"  📁 Allowing multiple directory creation operations in task '{task.get('title', 'Unknown')}': {len(directory_operations)} directories")
                        elif len(file_operations_list) > 1:
                            # Multiple file creation - not allowed
                            create_files = [fo.file_path for fo in file_operations_list]
                            raise ValueError(
                                f"Task '{task.get('title', 'Unknown')}' of type '{task_type_for_validation}' "
                                f"has {len(file_operations_list)} file creation operations. According to the single file creation rule, "
                                f"each code_generation/conversion task must create only ONE file. "
                                f"Found multiple file creation operations: {create_files}. "
                                f"Please split this into separate tasks."
                            )
                        else:
                            # Single file or mixed with directories - allowed
                            pass
                
                # Safely create TaskType with fallback for unknown types
                try:
                    task_type = TaskType(task['type'])
                except ValueError:
                    logger.warning(f"⚠️ Unknown task type '{task['type']}' found in task '{task.get('title', 'Unknown')}'. Using ANALYSIS as fallback.")
                    task_type = TaskType.ANALYSIS
                
                # Safely create Priority with fallback
                try:
                    priority = Priority(task['priority'])
                except ValueError:
                    logger.warning(f"⚠️ Unknown priority '{task.get('priority', 'None')}' found in task '{task.get('title', 'Unknown')}'. Using MEDIUM as fallback.")
                    priority = Priority.MEDIUM
                
                task_item = TaskItem(
                    id=task['id'],
                    title=task['title'],
                    description=task['description'],
                    type=task_type,
                    status=TaskStatus.PENDING,
                    priority=priority,
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
            "file_operations_summary": task_list.get_file_operations_for_audit(),
            "progress": task_list.progress
        }
        
        async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(output_data, indent=2, ensure_ascii=False))
        
        logger.info(f"💾 Output list saved: {output_file}")
    
    async def _execute_task(self, task: TaskItem) -> None:
        """
        Execute a task based on its type with file operation tracking and context saving
        """
        task_type_handlers = {
            TaskType.CONVERSION: self._execute_conversion_task,
            TaskType.CODE_GENERATION: self._execute_code_generation_task,
            TaskType.ANALYSIS: self._execute_analysis_task,
            TaskType.REVIEW: self._execute_review_task,
            TaskType.TESTING: self._execute_testing_task,
            TaskType.CLEANUP: self._execute_cleanup_task,
            TaskType.MAINTENANCE: self._execute_maintenance_task,
            TaskType.OPTIMIZATION: self._execute_optimization_task
        }
        
        handler = task_type_handlers.get(task.type)
        if not handler:
            logger.warning(f"⚠️ Unknown or unsupported task type: {task.type}. Task will be marked as completed with note.")
            # Mark task as completed but with a note about unsupported type
            task.output = TaskOutput(
                task_id=task.id,
                content=f"Task type '{task.type}' is not yet implemented in this version.",
                summary=f"Task marked as completed - unsupported type: {task.type}",
                file_operations=task.file_operations
            )
            task.output_data = {"status": "unsupported_type", "note": f"Task type '{task.type}' not implemented"}
            return
        
        logger.info(f"  🔄 Executing {task.type.value} task: {task.title}")
        
        # Get relevant context for this task
        relevant_context = self.get_relevant_context(task_type=task.type.value, task_id=task.id)
        logger.info(f"  📋 Using context: {len(relevant_context['task_outputs'])} previous outputs, {len(relevant_context['key_insights'])} insights")
        
        try:
            await handler(task)
            
            # Save task output to shared context after successful execution
            if task.output and task.output.content:
                self.save_task_output_to_context(
                    task_id=task.id,
                    task_output=task.output.content,
                    task_type=task.type.value
                )
                
                # Add key insights if available
                if task.output.summary:
                    self.add_key_insight(
                        insight=f"Task '{task.title}': {task.output.summary}",
                        source_task=task.id
                    )
                
                # Log file mappings from file operations
                if task.file_operations:
                    for file_op in task.file_operations:
                        if file_op.operation == FileOperation.CREATE:
                            self.save_file_mapping(
                                original_path="new_file",
                                new_path=file_op.file_path,
                                transformation_type="creation"
                            )
                        elif file_op.operation == FileOperation.MODIFY:
                            self.save_file_mapping(
                                original_path=file_op.file_path,
                                new_path=file_op.file_path + ".modified",
                                transformation_type="modification"
                            )
            
            logger.info(f"  ✅ Task completed and context saved: {task.id}")
            
        except Exception as e:
            logger.error(f"  ❌ Task execution failed: {e}")
            # Still save partial context even if task fails
            error_content = f"Task failed with error: {str(e)}"
            task.output = TaskOutput(
                task_id=task.id,
                content=error_content,
                summary=f"Task execution failed: {e}",
                file_operations=task.file_operations
            )
            self.save_task_output_to_context(
                task_id=task.id,
                task_output=error_content,
                task_type=task.type.value
            )
            raise
    
    async def _execute_conversion_task(self, task: TaskItem) -> None:
        """Execute a conversion task with strict single-file handling"""
        logger.info("  🔄 Executing conversion task (STRICT SINGLE-FILE MODE)...")
        logger.info(f"  📁 Output directory: {Config.OUTPUT_DIR}")
        logger.info(f"  📂 Logs directory: {Config.LOGS_DIR}")
        
        # STRICT: Validate single file creation rule
        await self._validate_single_file_rule(task, "conversion")
        
        # Handle input file operations (read operations)
        await self._handle_input_file_operations(task.file_operations)
        
        # Prepare single output file
        output_file = self._get_single_output_file(task.file_operations)
        if not output_file:
            raise ValueError(f"Conversion task '{task.title}' must have exactly one CREATE file operation")
        
        prompt = f"""Convert the following input to the target format:

Input: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input data provided'}

Requirements:
- Follow modern best practices
- Include proper error handling
- Add type hints if applicable
- Use clean, readable code
- Return only the converted content, no explanations
- Create exactly ONE file: {output_file.file_path}
- Focus on the single output file only"""

        system_instruction = f"Anda adalah konverter file ahli. Tugas Anda adalah menulis konten mentah untuk file yang diminta. JANGAN menulis skrip Python, file setup.py, atau alat bantu. Tulis HANYA konten yang sudah dikonversi untuk file {output_file.file_path}. Fokus pada hasil konversi murni tanpa dokumentasi tambahan."
        
        # Enhance prompt with shared context
        enhanced_prompt = self.enhance_prompt_with_context("conversion", prompt)
        
        result = await self.call_gemini(enhanced_prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Conversion task completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"converted_content": result}
        task.code = result
        
        # STRICT: Save only ONE file, no loops
        logger.info(f"  📝 Saving single output file: {output_file.file_path}")
        await self._save_generated_file(output_file, result)
        logger.info(f"  ✅ Single file saved successfully: {output_file.file_path}")
        
        # Verify only one file was created
        create_ops = [fo for fo in task.file_operations if fo.operation == FileOperation.CREATE]
        logger.info(f"  📊 Final verification: {len(create_ops)} CREATE operation(s) processed")
    
    async def _execute_code_generation_task(self, task: TaskItem) -> None:
        """Execute a code generation task with strict single-file handling"""
        logger.info("  💻 Executing code generation task (STRICT SINGLE-FILE MODE)...")
        logger.info(f"  📁 Output directory: {Config.OUTPUT_DIR}")
        logger.info(f"  📂 Logs directory: {Config.LOGS_DIR}")
        
        # STRICT: Validate single file creation rule
        await self._validate_single_file_rule(task, "code_generation")
        
        # Handle input file operations (read operations)
        await self._handle_input_file_operations(task.file_operations)
        
        # Prepare single output file
        output_file = self._get_single_output_file(task.file_operations)
        if not output_file:
            raise ValueError(f"Code generation task '{task.title}' must have exactly one CREATE file operation")
        
        # Enhanced prompt with context
        base_prompt = f"""Generate code for the following requirement:

{task.description}

Input context: {json.dumps(task.input_data, indent=2) if task.input_data else 'None'}

Requirements:
- Use modern language features
- Include error handling
- Add docstrings/comments for clarity
- Follow PEP 8 and best practices
- Return only the code, no explanations
- Create exactly ONE file: {output_file.file_path}
- Focus on the single output file only

IMPORTANT: Use the HTML analysis context below to understand the original structure."""

        prompt = self.enhance_prompt_with_context("code_generation", base_prompt)

        system_instruction = f"Anda adalah konverter file ahli. Tugas Anda adalah menulis konten mentah untuk file yang diminta. JANGAN menulis skrip Python, file setup.py, atau alat bantu. Tulis HANYA kode (TSX, CSS, dll.) untuk file {output_file.file_path}. Fokus pada konten murni file tanpa dokumentasi tambahan."
        
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
        
        # STRICT: Save only ONE file, no loops
        logger.info(f"  📝 Saving single output file: {output_file.file_path}")
        await self._save_generated_file(output_file, result)
        logger.info(f"  ✅ Single file saved successfully: {output_file.file_path}")
        
        # Verify only one file was created
        create_ops = [fo for fo in task.file_operations if fo.operation == FileOperation.CREATE]
        logger.info(f"  📊 Final verification: {len(create_ops)} CREATE operation(s) processed")
    
    async def _execute_analysis_task(self, task: TaskItem) -> None:
        """Execute an analysis task with file operations and HTML reading"""
        logger.info("  🔍 Executing analysis task...")
        
        # Check if this task involves reading HTML files
        html_content = None
        read_files = []
        
        # Process file operations to read files
        for file_op in task.file_operations:
            if file_op.operation == FileOperation.READ:
                try:
                    if file_op.file_path.endswith('.html'):
                        content = await self._read_html_file(file_op.file_path)
                        if content:
                            html_content = content
                            read_files.append(file_op.file_path)
                            logger.info(f"  📄 Read HTML file: {file_op.file_path}")
                    else:
                        # Read other file types
                        content = await self._read_generic_file(file_op.file_path)
                        read_files.append(file_op.file_path)
                        logger.info(f"  📄 Read file: {file_op.file_path}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Failed to read file {file_op.file_path}: {e}")
        
        # Analyze HTML content if available
        if html_content:
            logger.info("  🔍 Performing HTML structure analysis...")
            analysis_result = await self._analyze_html_structure(html_content, task)
            
            # Store analysis results in shared context
            self.add_key_insight(
                f"HTML Analysis - File: {', '.join(read_files)}", 
                source_task=task.id
            )
            self.add_key_insight(
                f"HTML Structure: {analysis_result.get('structure_summary', 'Unknown structure')}", 
                source_task=task.id
            )
            
            # Store raw HTML snippets for component extraction
            components = analysis_result.get('components', {})
            for component_name, component_html in components.items():
                self.add_key_insight(
                    f"HTML Component - {component_name}: {component_html[:200]}...",
                    source_task=task.id
                )
            
            # Add analysis to task output
            task.output_data = {
                "analysis": analysis_result.get('detailed_analysis', 'Analysis completed'),
                "html_content": html_content,
                "file_read": read_files,
                "components": components,
                "shared_context_keys": len(self.shared_context["key_insights"])
            }
        else:
            # General analysis without HTML
            prompt = f"""Analyze the following input and provide insights:

Input: {json.dumps(task.input_data, indent=2) if task.input_data else 'No input provided'}
Files read: {read_files}

Analysis requirements:
- Identify key patterns and insights
- Highlight potential issues or opportunities
- Provide actionable recommendations
- Structure the analysis clearly"""

            system_instruction = f"Anda adalah analis file ahli. Tugas Anda adalah menganalisis file {output_file.file_path} dan menyediakan analisis yang terstruktur dan actionable. Fokus pada hasil analisis yang bersih dan spesifik tanpa deskripsi yang tidak perlu."
            result = await self.call_gemini(prompt, system_instruction)
            task.output_data = {"analysis": result}
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=task.output_data.get("analysis", "Analysis completed"),
            summary=f"Analysis completed: {task.title}",
            file_operations=task.file_operations
        )
        
        logger.info(f"  ✅ Analysis task completed. Found {len(read_files)} files.")
    
    async def _read_html_file(self, file_path: str) -> Optional[str]:
        """Read and return HTML file content"""
        try:
            full_path = Path(file_path)
            if not full_path.exists():
                # Try relative to workspace
                relative_path = Path("./") / full_path
                if relative_path.exists():
                    full_path = relative_path
                else:
                    logger.error(f"  ❌ HTML file not found: {file_path}")
                    return None
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                logger.info(f"  📖 Successfully read {len(content)} characters from {file_path}")
                return content
                
        except Exception as e:
            logger.error(f"  ❌ Failed to read HTML file {file_path}: {e}")
            return None
    
    async def _read_generic_file(self, file_path: str) -> str:
        """Read any text file content"""
        try:
            full_path = Path(file_path)
            if not full_path.exists():
                # Try relative to workspace
                relative_path = Path("./") / full_path
                if relative_path.exists():
                    full_path = relative_path
                else:
                    logger.error(f"  ❌ File not found: {file_path}")
                    return ""
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return content
                
        except Exception as e:
            logger.error(f"  ❌ Failed to read file {file_path}: {e}")
            return ""
    
    async def _analyze_html_structure(self, html_content: str, task: TaskItem) -> Dict[str, Any]:
        """Analyze HTML structure and extract components"""
        try:
            prompt = f"""Analyze this HTML content and extract structured information:

HTML Content:
{html_content[:20000]}  # Limit to prevent token overflow

Provide analysis in this JSON format:
{{
  "detailed_analysis": "Comprehensive analysis of the HTML structure",
  "structure_summary": "Brief summary of the overall structure",
  "components": {{
    "header_html": "Raw HTML content of <header> or top navigation",
    "nav_html": "Raw HTML content of <nav> or navigation elements",
    "main_html": "Raw HTML content of <main> or primary content area",
    "footer_html": "Raw HTML content of <footer> or bottom section",
    "sidebar_html": "Raw HTML content of <aside> or sidebar elements",
    "forms_html": "Raw HTML content of <form> elements",
    "scripts_html": "Raw HTML content of <script> tags",
    "styles_css": "Raw CSS content from <style> tags or linked stylesheets"
  }},
  "metadata": {{
    "has_responsive_design": true/false,
    "contains_forms": true/false,
    "has_javascript": true/false,
    "has_external_css": true/false,
    "estimated_complexity": "low/medium/high"
  }}
}}

Instructions:
- Extract RAW HTML snippets for each component (not modified, just copy the original)
- Be very specific about structure and layout
- Identify any embedded CSS and JavaScript
- Note any framework indicators (React, Vue, Angular, etc.)"""

            system_instruction = "Anda adalah analis HTML ahli. Tugas Anda adalah mengekstrak komponen HTML mentah dan memberikan analisis struktural yang detail. Fokus pada ekstraksi komponen bersih dan terstruktur tanpa deskripsi tambahan."
            result = await self.call_gemini(prompt, system_instruction)
            
            # Parse the JSON response
            try:
                # Extract JSON from the response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group(0))
                    logger.info("  🏗️ Successfully parsed HTML structure analysis")
                    return analysis_data
                else:
                    # Fallback to text analysis
                    return {
                        "detailed_analysis": result,
                        "structure_summary": "HTML analysis completed",
                        "components": {},
                        "metadata": {"estimated_complexity": "medium"}
                    }
            except json.JSONDecodeError as e:
                logger.warning(f"  ⚠️ JSON parsing failed, using text analysis: {e}")
                return {
                    "detailed_analysis": result,
                    "structure_summary": "HTML analysis completed (text format)",
                    "components": {},
                    "metadata": {"estimated_complexity": "medium"}
                }
                
        except Exception as e:
            logger.error(f"  ❌ Failed to analyze HTML structure: {e}")
            return {
                "detailed_analysis": f"Analysis failed: {e}",
                "structure_summary": "Analysis failed",
                "components": {},
                "metadata": {"estimated_complexity": "unknown"}
            }
    
    def enhance_prompt_with_context(self, task_type: str, custom_prompt: str = "") -> str:
        """Enhance prompt with relevant context from shared_context"""
        relevant_context = self.get_relevant_context(task_type=task_type, max_items=10)
        context_summary = self.generate_context_summary()
        
        enhanced_prompt = f"""{custom_prompt}

=== RELEVANT CONTEXT FROM SHARED CONTEXT ===
{context_summary}

=== HTML ANALYSIS INSIGHTS ===
"""
        
        # Add HTML-specific context
        html_insights = [insight for insight in self.shared_context["key_insights"] 
                        if "HTML" in insight["insight"] or "html" in insight["insight"].lower()]
        
        for i, insight in enumerate(html_insights[-5:], 1):  # Last 5 HTML insights
            enhanced_prompt += f"{i}. {insight['insight']}\n"
        
        enhanced_prompt += f"""
Use this context to enhance your understanding and provide more accurate outputs.
Focus on HTML structure and components identified in previous analysis tasks.
"""
        
        return enhanced_prompt
    
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

        system_instruction = "Anda adalah reviewer file ahli. Tugas Anda adalah memberikan review yang konstruktif dan spesifik untuk file yang diminta. Fokus pada feedback yang actionable tanpa deskripsi yang berlebihan."
        
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

        system_instruction = f"Anda adalah QA engineer ahli. Tugas Anda adalah menulis konten mentah untuk file test yang diminta. JANGAN menulis skrip Python, file setup.py, atau alat bantu. Tulis HANYA kode test untuk file yang diminta. Fokus pada konten test yang bersih dan terstruktur."
        
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
    
    async def _execute_cleanup_task(self, task: TaskItem) -> None:
        """Execute a cleanup task with file operations"""
        logger.info("  🧹 Executing cleanup task...")
        
        # Pre-process file operations
        if task.file_operations:
            logger.info(f"  📋 Processing {len(task.file_operations)} file operations...")
            for i, file_op in enumerate(task.file_operations, 1):
                logger.info(f"  [{i}/{len(task.file_operations)}] Processing: {file_op.file_path}")
                
                if file_op.operation == FileOperation.DELETE:
                    await self._handle_file_delete_operation(file_op)
                elif file_op.operation == FileOperation.MODIFY:
                    await self._handle_file_modify_operation(file_op)
                elif file_op.operation == FileOperation.READ:
                    await self._handle_file_read_operation(file_op)
        
        prompt = f"""Clean up the following based on the requirements:

Task: {task.title}
Description: {task.description}
Input data: {json.dumps(task.input_data, indent=2) if task.input_data else 'None'}

Cleanup requirements:
- Remove unnecessary files or code
- Fix formatting and style issues
- Ensure proper file organization
- Clean up unused imports or variables
- Follow best practices for code maintenance

Provide a summary of cleanup actions performed."""

        system_instruction = "You are an expert in code cleanup and maintenance. Focus on practical cleanup actions."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Cleanup completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"cleanup_actions": result}
    
    async def _execute_maintenance_task(self, task: TaskItem) -> None:
        """Execute a maintenance task with file operations"""
        logger.info("  🔧 Executing maintenance task...")
        
        # Pre-process file operations
        if task.file_operations:
            logger.info(f"  📋 Processing {len(task.file_operations)} file operations...")
            for i, file_op in enumerate(task.file_operations, 1):
                logger.info(f"  [{i}/{len(task.file_operations)}] Processing: {file_op.file_path}")
                
                if file_op.operation == FileOperation.READ:
                    await self._handle_file_read_operation(file_op)
                elif file_op.operation == FileOperation.MODIFY:
                    await self._handle_file_modify_operation(file_op)
                elif file_op.operation == FileOperation.CREATE:
                    await self._handle_file_create_operation(file_op)
        
        prompt = f"""Perform maintenance on the following:

Task: {task.title}
Description: {task.description}
Input data: {json.dumps(task.input_data, indent=2) if task.input_data else 'None'}

Maintenance actions:
- Update dependencies and packages
- Fix deprecated code patterns
- Improve error handling
- Add logging and monitoring
- Optimize performance bottlenecks
- Update documentation
- Ensure security best practices

Provide a detailed maintenance report."""

        system_instruction = "You are an expert in software maintenance and DevOps. Focus on practical maintenance improvements."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Maintenance completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"maintenance_report": result}
    
    async def _execute_optimization_task(self, task: TaskItem) -> None:
        """Execute an optimization task with file operations"""
        logger.info("  ⚡ Executing optimization task...")
        
        # Pre-process file operations
        if task.file_operations:
            logger.info(f"  📋 Processing {len(task.file_operations)} file operations...")
            for i, file_op in enumerate(task.file_operations, 1):
                logger.info(f"  [{i}/{len(task.file_operations)}] Processing: {file_op.file_path}")
                
                if file_op.operation == FileOperation.READ:
                    await self._handle_file_read_operation(file_op)
                elif file_op.operation == FileOperation.MODIFY:
                    await self._handle_file_modify_operation(file_op)
        
        prompt = f"""Optimize the following for better performance:

Task: {task.title}
Description: {task.description}
Input data: {json.dumps(task.input_data, indent=2) if task.input_data else 'None'}

Optimization focus:
- Code performance improvements
- Memory usage optimization
- Algorithm efficiency
- Database query optimization
- Caching strategies
- Resource utilization
- Loading time improvements
- Concurrent processing opportunities

Provide specific optimization recommendations and improvements."""

        system_instruction = "You are an expert in performance optimization. Focus on measurable performance improvements."
        
        result = await self.call_gemini(prompt, system_instruction)
        
        # Create task output
        task.output = TaskOutput(
            task_id=task.id,
            content=result,
            summary=f"Optimization completed: {task.title}",
            file_operations=task.file_operations
        )
        
        task.output_data = {"optimization_report": result}
    
    async def _handle_file_read_operation(self, file_op: FileOperationItem):
        """Handle file read operation with comprehensive real-time logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            logger.info(f"  📖 Reading file: {file_path}")
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                file_op.size_bytes = file_size
                file_op.checksum = hashlib.md5(file_path.read_bytes()).hexdigest()[:16]
                self.audit_logger.log_file_operation_end(file_op, "success", f"Successfully read {file_size:,} bytes", start_time)
                logger.info(f"  ✅ File read completed: {file_size:,} bytes | Checksum: {file_op.checksum}")
            else:
                error_msg = "File not found"
                self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
                logger.error(f"  ❌ File not found: {file_path}")
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File read error: {file_path} - {error_msg}")
    
    async def _handle_file_create_operation(self, file_op: FileOperationItem):
        """Handle file create operation with comprehensive real-time logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            
            # Ensure output directory structure
            if not str(file_path).startswith(str(Config.OUTPUT_DIR)):
                # Redirect to output directory if not already there
                relative_path = file_path.name
                new_path = Config.OUTPUT_DIR / relative_path
                logger.info(f"  📁 Redirecting file to output directory: {new_path}")
                file_path = new_path
                file_op.file_path = str(new_path)
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"  📄 Creating file: {file_path}")
            logger.info(f"  📁 Output directory: {Config.OUTPUT_DIR}")
            
            # Mark as in progress
            self.audit_logger.log_file_operation_end(file_op, "pending", "File creation ready - awaiting content", start_time)
            logger.info(f"  ⏳ File creation prepared: {file_path}")
            
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File creation error: {error_msg}")
    
    # STRICT SINGLE-FILE HANDLER HELPER METHODS
    
    def _is_directory_path(self, file_path: str) -> bool:
        """Determine if a file path represents a directory creation operation"""
        if not file_path:
            return False
        
        # Clean the path
        clean_path = file_path.strip()
        
        # First check for explicit directory indicators
        if (clean_path.endswith('/') or clean_path.endswith('\\')):
            return True
        
        # Check if it looks like a complete file with extension
        # Get the last part after the final slash
        last_part = clean_path.split('/')[-1].split('\\')[-1]
        
        # If the last part has a file extension (like .tsx, .ts, .js, .jsx, .css, .json, etc.)
        # then it's likely a file, not a directory
        file_extensions = [
            '.tsx', '.ts', '.js', '.jsx', '.css', '.scss', '.sass', '.less',
            '.json', '.yaml', '.yml', '.xml', '.html', '.htm',
            '.md', '.txt', '.py', '.java', '.cpp', '.c', '.h', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.sql',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.rar', '.7z'
        ]
        
        # Check if the last part has a known file extension
        for ext in file_extensions:
            if last_part.lower().endswith(ext.lower()):
                return False  # This is a file, not a directory
        
        # If no file extension detected, likely a directory
        # But let's be more specific about common directory patterns
        directory_patterns = [
            'src', 'components', 'pages', 'app', 'public', 'styles', 'assets',
            'lib', 'utils', 'types', 'hooks', 'context', 'store', 'test', 'tests',
            'spec', '__tests__', 'node_modules', 'dist', 'build', 'coverage',
            '.next', '.nuxt', '.vscode', 'docs', 'scripts', 'config'
        ]
        
        # Check if the last part matches common directory names
        if last_part in directory_patterns:
            return True
        
        # Check if it contains common directory indicators
        path_lower = clean_path.lower()
        if any(pattern in path_lower for pattern in directory_patterns):
            # But only if it doesn't look like a file path
            if not any(ext in path_lower for ext in ['.', '/', '\\']):
                return True
        
        # If it doesn't have any dots in the last part and is not a file extension
        # and doesn't contain typical file patterns, it's likely a directory
        return '.' not in last_part and len(last_part) > 0
    
    async def _validate_single_file_rule(self, task: TaskItem, task_type: str):
        """Validate single file creation rule for code generation and conversion tasks"""
        # Count both CREATE operations and directory-creating EXECUTE operations
        create_operations = [fo for fo in task.file_operations if fo.operation == FileOperation.CREATE]
        directory_execute_operations = [fo for fo in task.file_operations if fo.operation == FileOperation.EXECUTE and self._is_directory_path(fo.file_path)]
        
        # Treat directory-creating EXECUTE operations as equivalent to CREATE operations
        all_create_equivalent = create_operations + directory_execute_operations
        
        if task_type in ['code_generation', 'conversion']:
            if len(all_create_equivalent) == 0:
                raise ValueError(f"Task '{task.title}' of type '{task_type}' must have exactly one CREATE operation")
            elif len(all_create_equivalent) > 1:
                # Check if all operations are directory creation
                directory_operations = [fo for fo in all_create_equivalent if self._is_directory_path(fo.file_path)]
                file_operations_list = [fo for fo in all_create_equivalent if not self._is_directory_path(fo.file_path)]
                
                if len(directory_operations) > 0 and len(file_operations_list) == 0:
                    # All operations are directory creation - allowed
                    logger.info(f"  ✅ Directory-only operations allowed: {len(directory_operations)} directories")
                else:
                    # Multiple file operations or mixed - not allowed
                    create_files = [fo.file_path for fo in all_create_equivalent]
                    raise ValueError(
                        f"Task '{task.title}' of type '{task_type}' has {len(all_create_equivalent)} create operations. "
                        f"According to strict single-file rule, each task must create only ONE file. "
                        f"Found multiple create files: {create_files}. "
                        f"Please split this into separate tasks."
                    )
            else:
                # Single operation (CREATE or directory-creating EXECUTE)
                op = all_create_equivalent[0]
                if op.operation == FileOperation.EXECUTE:
                    logger.info(f"  ✅ Single file rule validated (directory creation): {op.file_path}")
                else:
                    logger.info(f"  ✅ Single file rule validated: {op.file_path}")
        else:
            # For other task types, allow multiple operations but log the count
            logger.info(f"  ℹ️ Task type '{task_type}' allows {len(all_create_equivalent)} create operations")

    async def _handle_input_file_operations(self, file_operations: List[FileOperationItem]):
        """Handle input file operations (read, modify) - no output operations"""
        input_ops = [fo for fo in file_operations if fo.operation != FileOperation.CREATE]
        
        if not input_ops:
            logger.info("  ℹ️ No input file operations to process")
            return
            
        logger.info(f"  📋 Processing {len(input_ops)} input file operations...")
        
        for i, file_op in enumerate(input_ops, 1):
            logger.info(f"  [{i}/{len(input_ops)}] Processing: {file_op.operation.value} - {file_op.file_path}")
            
            if file_op.operation == FileOperation.READ:
                await self._handle_file_read_operation(file_op)
            elif file_op.operation == FileOperation.MODIFY:
                await self._handle_file_modify_operation(file_op)
            elif file_op.operation == FileOperation.DELETE:
                await self._handle_file_delete_operation(file_op)
            elif file_op.operation == FileOperation.EXECUTE:
                await self._handle_file_execute_operation(file_op)
            else:
                logger.warning(f"  ⚠️ Unknown input operation type: {file_op.operation}")
        
        logger.info(f"  ✅ Input file operations completed: {len(input_ops)} operations")

    def _get_single_output_file(self, file_operations: List[FileOperationItem]) -> Optional[FileOperationItem]:
        """Get the single output file (CREATE operation) from file operations with enhanced single file rule support"""
        create_operations = [fo for fo in file_operations if fo.operation == FileOperation.CREATE]
        
        if len(create_operations) == 1:
            return create_operations[0]
        elif len(create_operations) == 0:
            return None
        else:
            # Enhanced single file rule: Check if all operations are directory creation
            directory_operations = [fo for fo in create_operations if self._is_directory_path(fo.file_path)]
            file_operations_list = [fo for fo in create_operations if not self._is_directory_path(fo.file_path)]
            
            if len(directory_operations) > 0 and len(file_operations_list) == 0:
                # All operations are directory creation - return the first one for compatibility
                # This is a special case where we have multiple directories but no files
                return directory_operations[0]
            elif len(file_operations_list) > 1:
                # Multiple file operations - not allowed
                create_files = [fo.file_path for fo in create_operations]
                raise ValueError(
                    f"Expected exactly one CREATE operation, but found {len(create_operations)}: {create_files}"
                )
            elif len(file_operations_list) == 1 and len(directory_operations) > 0:
                # Mixed operations (file + directories) - not allowed
                create_files = [fo.file_path for fo in create_operations]
                raise ValueError(
                    f"Expected exactly one CREATE operation, but found {len(create_operations)}: {create_files}"
                )
            else:
                # Should not reach here, but handle gracefully
                create_files = [fo.file_path for fo in create_operations]
                raise ValueError(
                    f"Expected exactly one CREATE operation, but found {len(create_operations)}: {create_files}"
                )

    # ENHANCED FILE HANDLING METHODS

    async def _save_generated_file(self, file_op: FileOperationItem, content: str):
        """Save generated content to file with comprehensive real-time logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            
            # Ensure output directory structure
            if not str(file_path).startswith(str(Config.OUTPUT_DIR)):
                # Redirect to output directory
                relative_path = file_path.name
                new_path = Config.OUTPUT_DIR / relative_path
                logger.info(f"  📁 Redirecting generated file to output directory: {new_path}")
                file_path = new_path
                file_op.file_path = str(new_path)
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"  📝 Writing content to file: {file_path}")
            logger.info(f"  📊 Content size: {len(content):,} characters")
            
            # Write content to file
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            # Get file statistics
            file_size = file_path.stat().st_size
            file_op.size_bytes = file_size
            file_op.checksum = hashlib.md5(file_path.read_bytes()).hexdigest()[:16]
            file_op.completed_at = datetime.now(timezone.utc).isoformat()
            
            success_msg = f"Created {file_size:,} bytes in {Config.OUTPUT_DIR.name}/"
            self.audit_logger.log_file_operation_end(file_op, "success", success_msg, start_time)
            
            logger.info(f"  ✅ File created successfully: {file_path}")
            logger.info(f"  📁 Output location: {Config.OUTPUT_DIR}")
            logger.info(f"  📊 Final file size: {file_size:,} bytes")
            logger.info(f"  🔐 Checksum: {file_op.checksum}")
            
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File creation error: {error_msg}")
    
    async def _handle_file_delete_operation(self, file_op: FileOperationItem):
        """Handle file delete operation with comprehensive logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            logger.info(f"  🗑️ Deleting file: {file_path}")
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                file_op.size_bytes = file_size
                file_path.unlink()
                
                self.audit_logger.log_file_operation_end(file_op, "success", f"Deleted {file_size:,} bytes", start_time)
                logger.info(f"  ✅ File deleted successfully: {file_size:,} bytes")
            else:
                error_msg = "File not found"
                self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
                logger.warning(f"  ⚠️ File not found for deletion: {file_path}")
                
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File deletion error: {error_msg}")
    
    async def _handle_file_modify_operation(self, file_op: FileOperationItem):
        """Handle file modify operation with comprehensive logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            logger.info(f"  ✏️ Modifying file: {file_path}")
            
            if file_path.exists():
                old_size = file_path.stat().st_size
                file_op.size_bytes = old_size
                logger.info(f"  📊 Original file size: {old_size:,} bytes")
                
                # Apply modifications if content is provided
                if hasattr(file_op, 'content') and file_op.content:
                    new_content = file_op.content
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(new_content)
                    
                    new_size = file_path.stat().st_size
                    self.audit_logger.log_file_operation_end(file_op, "success", f"Modified {old_size} → {new_size} bytes", start_time)
                    logger.info(f"  ✅ File modified: {old_size:,} → {new_size:,} bytes")
                else:
                    self.audit_logger.log_file_operation_end(file_op, "success", f"File ready for modification", start_time)
                    logger.info(f"  ⏳ File prepared for modification")
            else:
                error_msg = "File not found"
                self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
                logger.error(f"  ❌ File not found for modification: {file_path}")
                
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File modification error: {error_msg}")
    
    async def _handle_file_execute_operation(self, file_op: FileOperationItem):
        """Handle file execute operation with comprehensive logging"""
        start_time = self.audit_logger.log_file_operation_start(file_op)
        file_op.created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            file_path = Path(file_op.file_path)
            logger.info(f"  ⚡ Executing file: {file_path}")
            
            if file_path.exists():
                if file_path.suffix == '.py':
                    # Execute Python file
                    import subprocess
                    result = subprocess.run([sys.executable, str(file_path)], 
                                          capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.audit_logger.log_file_operation_end(file_op, "success", f"Execution completed successfully", start_time)
                        logger.info(f"  ✅ Python file executed successfully")
                        if result.stdout:
                            logger.info(f"  📤 Output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
                    else:
                        error_msg = f"Execution failed: {result.stderr}"
                        self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
                        logger.error(f"  ❌ Execution failed: {result.stderr}")
                else:
                    # For other file types, just mark as executable
                    self.audit_logger.log_file_operation_end(file_op, "success", "File marked as executable", start_time)
                    logger.info(f"  ✅ File marked as executable")
            else:
                error_msg = "File not found"
                self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
                logger.error(f"  ❌ File not found for execution: {file_path}")
                
        except Exception as e:
            error_msg = str(e)
            self.audit_logger.log_file_operation_end(file_op, "error", error_msg, start_time)
            logger.error(f"  ❌ File execution error: {error_msg}")
    
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

        system_instruction = "Anda adalah reviewer ahli. Tugas Anda adalah memberikan feedback yang singkat dan konstruktif. Fokus pada review yang actionable tanpa deskripsi yang berlebihan."
        
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
        
        # Generate and log context summary
        context_summary = self.generate_context_summary()
        
        logger.info(f"\n🎉 Workflow completed!")
        logger.info(f"✅ Completed: {completed_tasks} tasks")
        logger.info(f"❌ Failed: {failed_tasks} tasks")
        logger.info(f"📋 Output items: {len(output_list)}")
        
        # Display shared context summary
        logger.info(f"\n📝 Shared Context Summary:")
        logger.info("=" * 60)
        logger.info(context_summary)
        logger.info("=" * 60)
        
        # Log session summary with context
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
            "audit_file": str(self.audit_logger.log_file),
            "shared_context": self.shared_context
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
        
        # Convert enums to strings recursively
        def convert_enums_recursive(obj):
            """Recursively convert enums to JSON-serializable values"""
            if hasattr(obj, 'value') and hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
                # This is an enum
                return obj.value
            elif isinstance(obj, dict):
                return {key: convert_enums_recursive(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums_recursive(item) for item in obj]
            else:
                return obj
        
        # Convert all enums in the task list
        task_list_dict = convert_enums_recursive(task_list_dict)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(task_list_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Task list saved: {file_path}")
    
    # ==================== LINEAR CONTROL FLOW & DYNAMIC TASK MANAGEMENT ====================
    
    async def run_linear_workflow(
        self, 
        goal: str, 
        input_context: Optional[Dict[str, Any]] = None,
        max_cycles: int = 5
    ) -> TaskList:
        """
        Run synthesis workflow with LINEAR control flow and dynamic task insertion
        
        Linear Execution: Task 1 -> Task 2 -> Task 3 (sequential)
        Dynamic Insertion: If review finds issues, insert fix tasks or re-execute with new instructions
        
        Args:
            goal: Primary goal for the workflow
            input_context: Additional context for task creation
            max_cycles: Maximum number of review-improvement cycles
        """
        logger.info(f"\n🚀 Starting LINEAR workflow for: {goal}")
        logger.info(f"🆔 Session ID: {self.session_id}")
        logger.info(f"📊 Max cycles: {max_cycles}")
        logger.info(f"📋 Log file: {self.log_file}")
        
        # Step 1: Create initial task list
        task_list = await self.create_task_list(goal, input_context)
        
        if not task_list.tasks:
            raise ValueError("No tasks generated in initial task list")
        
        logger.info(f"📋 Initial task list created with {len(task_list.tasks)} tasks")
        
        # Step 2: Execute tasks in LINEAR order
        cycle_count = 0
        completed_tasks = 0
        total_tasks = len(task_list.tasks)
        
        while task_list.status == 'active' and cycle_count < max_cycles:
            # Find the next linear task (sequential execution)
            next_task = await self._get_next_linear_task(task_list)
            
            if not next_task:
                logger.info("🎉 All tasks completed or no more available tasks")
                task_list.status = 'completed'
                break
            
            # Execute the task
            logger.info(f"\n{'='*80}")
            logger.info(f"🔄 EXECUTING TASK {completed_tasks + 1}/{total_tasks} (Cycle {cycle_count + 1})")
            logger.info(f"📋 Title: {next_task.title}")
            logger.info(f"📝 Description: {next_task.description}")
            logger.info(f"🏷️ Type: {next_task.type.value}, Priority: {next_task.priority.value}")
            
            try:
                # Execute the task
                next_task.status = TaskStatus.IN_PROGRESS
                next_task.actual_time = int(time.time() * 1000)
                
                await self._execute_task(next_task)
                
                # Mark as completed
                next_task.status = TaskStatus.COMPLETED
                next_task.actual_time = int(time.time() * 1000) - next_task.actual_time
                next_task.completed_at = datetime.now(timezone.utc).isoformat()
                
                completed_tasks += 1
                logger.info(f"✅ Task completed in {next_task.actual_time}ms")
                
                # Save to shared context
                if next_task.output:
                    self.save_task_output_to_context(
                        next_task.id, 
                        next_task.output.content, 
                        next_task.type.value
                    )
                
                # Step 3: Enhanced review with issue detection
                issues_found = await self._enhanced_review_with_issue_detection(next_task)
                
                # Step 4: Handle issues with dynamic task insertion
                if issues_found:
                    cycle_count += 1
                    logger.info(f"🔧 Issues detected! Starting cycle {cycle_count} of {max_cycles}")
                    
                    # Dynamically insert tasks or mark for re-execution
                    await self._handle_issues_dynamically(task_list, issues_found, next_task)
                    
                    # Update total tasks count
                    total_tasks = len(task_list.tasks)
                    logger.info(f"📊 Task list updated: {total_tasks} total tasks")
                
                # Update progress
                task_list._update_progress()
                logger.info(f"📈 Progress: {completed_tasks}/{total_tasks} tasks completed")
                
                # Brief pause
                await asyncio.sleep(0.5)
                
            except Exception as error:
                next_task.status = TaskStatus.FAILED
                next_task.errors = [str(error)]
                next_task.actual_time = int(time.time() * 1000) - next_task.actual_time
                
                logger.error(f"❌ Task failed: {error}")
                
                # For failed tasks, always attempt to create fix tasks
                logger.info("🔧 Creating fix tasks for failed task...")
                await self._create_fix_tasks_for_failure(task_list, next_task, str(error))
                
                cycle_count += 1
        
        # Finalize workflow
        output_list = task_list.generate_output_list()
        context_summary = self.generate_context_summary()
        
        logger.info(f"\n🎉 LINEAR WORKFLOW COMPLETED!")
        logger.info(f"✅ Completed: {completed_tasks} tasks")
        logger.info(f"🔄 Total cycles: {cycle_count}")
        logger.info(f"📋 Total tasks: {len(task_list.tasks)}")
        logger.info(f"📋 Output items: {len(output_list)}")
        
        logger.info(f"\n📝 Final Context Summary:")
        logger.info("=" * 80)
        logger.info(context_summary)
        logger.info("=" * 80)
        
        return task_list
    
    async def _get_next_linear_task(self, task_list: TaskList) -> Optional[TaskItem]:
        """
        Get the next task in linear order (sequential execution)
        """
        # Sort tasks by their order in the list to maintain linear sequence
        pending_tasks = [task for task in task_list.tasks 
                        if task.status in [TaskStatus.PENDING, TaskStatus.WAITING]]
        
        if not pending_tasks:
            return None
        
        # Get the earliest pending task (linear order)
        next_task = min(pending_tasks, key=lambda t: task_list.tasks.index(t))
        
        # Check if dependencies are satisfied
        if next_task.dependencies:
            completed_ids = {t.id for t in task_list.tasks if t.status == TaskStatus.COMPLETED}
            if not all(dep_id in completed_ids for dep_id in next_task.dependencies):
                # Dependencies not satisfied, look for next available task
                for task in pending_tasks:
                    if not task.dependencies or all(dep_id in completed_ids for dep_id in task.dependencies):
                        return task
                return None  # No task with satisfied dependencies
        
        return next_task
    
    async def _enhanced_review_with_issue_detection(self, task: TaskItem) -> List[Dict[str, Any]]:
        """
        Enhanced review that detects issues and returns them for dynamic task insertion
        """
        logger.info("  🔍 Running enhanced review with issue detection...")
        
        # Check for common issues
        issues = []
        
        # 1. Check for code quality issues
        if task.code:
            code_issues = await self._detect_code_issues(task.code, task.title)
            if code_issues:
                issues.extend(code_issues)
        
        # 2. Check for file operation issues
        if task.file_operations:
            file_issues = await self._detect_file_issues(task.file_operations, task.title)
            if file_issues:
                issues.extend(file_issues)
        
        # 3. Check for output quality issues
        if task.output and task.output.content:
            content_issues = await self._detect_content_issues(task.output.content, task.title)
            if content_issues:
                issues.extend(content_issues)
        
        # 4. Check for logic/flow issues
        logic_issues = await self._detect_logic_issues(task, None)  # Will be handled by caller
        if logic_issues:
            issues.extend(logic_issues)
        
        if issues:
            logger.info(f"  ⚠️  Detected {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                logger.info(f"    {i}. {issue['type']}: {issue['description']}")
                if 'suggested_fix' in issue:
                    logger.info(f"       💡 Suggestion: {issue['suggested_fix']}")
        else:
            logger.info("  ✅ No issues detected")
        
        return issues
    
    async def _detect_code_issues(self, code: str, task_title: str) -> List[Dict[str, Any]]:
        """Detect common code quality issues"""
        issues = []
        
        # Check for console.log statements
        if 'console.log' in code:
            issues.append({
                'type': 'code_quality',
                'description': f"Console.log statements found in {task_title}",
                'severity': 'medium',
                'suggested_fix': 'Remove console.log statements or replace with proper logging',
                'task_type': TaskType.OPTIMIZATION,
                'target_file': None
            })
        
        # Check for TODO comments
        todo_matches = re.findall(r'//\s*TODO.*', code, re.IGNORECASE)
        if todo_matches:
            issues.append({
                'type': 'code_completeness',
                'description': f"TODO comments found in {task_title}",
                'severity': 'low',
                'suggested_fix': 'Complete or remove TODO comments',
                'task_type': TaskType.MAINTENANCE,
                'target_file': None
            })
        
        # Check for hardcoded values that should be configurable
        if 'http://' in code or 'https://' in code:
            issues.append({
                'type': 'hardcoded_values',
                'description': f"Hardcoded URLs found in {task_title}",
                'severity': 'medium',
                'suggested_fix': 'Move URLs to configuration or environment variables',
                'task_type': TaskType.OPTIMIZATION,
                'target_file': None
            })
        
        return issues
    
    async def _detect_file_issues(self, file_operations: List[FileOperationItem], task_title: str) -> List[Dict[str, Any]]:
        """Detect file operation issues"""
        issues = []
        
        for file_op in file_operations:
            # Check for missing directories
            file_path = Path(file_op.file_path)
            if file_op.operation == FileOperation.CREATE and not file_path.parent.exists():
                issues.append({
                    'type': 'missing_directory',
                    'description': f"Parent directory missing for {file_op.file_path}",
                    'severity': 'high',
                    'suggested_fix': f"Create directory structure: {file_path.parent}",
                    'task_type': TaskType.CLEANUP,
                    'target_file': str(file_path.parent)
                })
            
            # Check for potential file conflicts
            if file_op.operation == FileOperation.CREATE and file_path.exists():
                issues.append({
                    'type': 'file_conflict',
                    'description': f"File already exists: {file_op.file_path}",
                    'severity': 'medium',
                    'suggested_fix': f"Use backup/rename strategy for {file_op.file_path}",
                    'task_type': TaskType.CLEANUP,
                    'target_file': str(file_path)
                })
        
        return issues
    
    async def _detect_content_issues(self, content: str, task_title: str) -> List[Dict[str, Any]]:
        """Detect content quality issues"""
        issues = []
        
        # Check for placeholder content
        placeholder_patterns = [
            r'lorem ipsum',
            r'tODO',
            r'FIXME',
            r'placeholder',
            r'coming soon',
            r'not implemented'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'type': 'placeholder_content',
                    'description': f"Placeholder content found in {task_title}",
                    'severity': 'high',
                    'suggested_fix': 'Replace placeholder content with actual implementation',
                    'task_type': TaskType.CODE_GENERATION,
                    'target_file': None
                })
                break
        
        # Check for very short content (might be incomplete)
        if len(content.strip()) < 50:
            issues.append({
                'type': 'incomplete_content',
                'description': f"Very short content in {task_title} ({len(content)} chars)",
                'severity': 'medium',
                'suggested_fix': 'Expand content with more detail or functionality',
                'task_type': TaskType.OPTIMIZATION,
                'target_file': None
            })
        
        return issues
    
    async def _detect_logic_issues(self, task: TaskItem, task_list: Optional[TaskList]) -> List[Dict[str, Any]]:
        """Detect logical flow issues"""
        issues = []
        
        # This is a placeholder - you can implement more sophisticated logic detection
        # For now, we'll detect if a task has no output but should have produced something
        if task.type in [TaskType.CODE_GENERATION, TaskType.CONVERSION] and not task.output:
            issues.append({
                'type': 'missing_output',
                'description': f"No output generated for {task.title}",
                'severity': 'high',
                'suggested_fix': 'Re-execute task with more detailed instructions',
                'task_type': TaskType.CODE_GENERATION,
                'target_file': None,
                'reexecute_with_new_instructions': True
            })
        
        return issues
    
    async def _handle_issues_dynamically(self, task_list: TaskList, issues: List[Dict[str, Any]], current_task: TaskItem) -> None:
        """
        Handle issues by dynamically inserting tasks or marking tasks for re-execution
        """
        logger.info(f"  🔧 Handling {len(issues)} issues dynamically...")
        
        for issue in issues:
            if issue.get('reexecute_with_new_instructions', False):
                # Mark current task for re-execution with new instructions
                await self._mark_task_for_reexecution(task_list, current_task, issue)
            else:
                # Create new task to fix the issue
                await self._create_dynamic_fix_task(task_list, issue, current_task)
    
    async def _mark_task_for_reexecution(self, task_list: TaskList, task: TaskItem, issue: Dict[str, Any]) -> None:
        """Mark a task for re-execution with enhanced instructions"""
        # Create enhanced instructions based on the issue
        enhanced_instructions = self._generate_enhanced_instructions(task, issue)
        
        # Reset task status and update description
        task.status = TaskStatus.REEXECUTING
        task.dependencies = []  # Clear dependencies for re-execution
        task.description = f"{task.description}\n\n[RE-EXECUTION DUE TO ISSUES]\nIssue: {issue['description']}\nEnhanced Instructions: {enhanced_instructions}"
        
        logger.info(f"  🔄 Marked for re-execution: {task.title}")
        logger.info(f"     Issue: {issue['description']}")
        logger.info(f"     Enhanced instructions added")
    
    async def _create_dynamic_fix_task(self, task_list: TaskList, issue: Dict[str, Any], current_task: TaskItem) -> None:
        """Create a new task to fix the detected issue"""
        fix_task = TaskItem(
            id=self.generate_id(),
            title=f"Fix: {issue['description']}",
            description=f"""
Fix the following issue in previous work:
Original Task: {current_task.title}
Issue: {issue['description']}
Suggested Fix: {issue['suggested_fix']}

This task should resolve the detected issue and ensure proper implementation.
""".strip(),
            type=issue.get('task_type', TaskType.CLEANUP),
            status=TaskStatus.PENDING,
            priority=Priority.HIGH if issue.get('severity') == 'high' else Priority.MEDIUM,
            dependencies=[current_task.id],  # Depends on the task that had the issue
            estimated_time=10,
            file_operations=[]
        )
        
        # Add file operations if target file is specified
        if issue.get('target_file'):
            fix_task.file_operations.append(FileOperationItem(
                operation=FileOperation.MODIFY,
                file_path=issue['target_file'],
                description=f"Fix issue: {issue['description']}",
                priority=Priority.HIGH if issue.get('severity') == 'high' else Priority.MEDIUM,
                dependencies=[]
            ))
        
        # Insert the task after the current task
        current_index = task_list.tasks.index(current_task)
        task_list.tasks.insert(current_index + 1, fix_task)
        
        logger.info(f"  ✅ Created fix task: {fix_task.title}")
        logger.info(f"     Position: After {current_task.title}")
        logger.info(f"     Type: {fix_task.type.value}")
        logger.info(f"     Priority: {fix_task.priority.value}")
    
    def _generate_enhanced_instructions(self, task: TaskItem, issue: Dict[str, Any]) -> str:
        """Generate enhanced instructions for task re-execution"""
        base_enhancements = {
            'code_quality': "Ensure all code follows best practices. Remove debugging statements.",
            'code_completeness': "Complete all TODO items and ensure full implementation.",
            'hardcoded_values': "Use configuration files or environment variables for all hardcoded values.",
            'missing_directory': "Create all necessary directory structures before creating files.",
            'file_conflict': "Implement proper file backup/rename strategy to avoid conflicts.",
            'placeholder_content': "Replace all placeholder content with actual, meaningful implementation.",
            'incomplete_content': "Provide comprehensive, detailed content and functionality.",
            'missing_output': "Ensure the task produces meaningful, complete output."
        }
        
        enhancement = base_enhancements.get(issue['type'], "Address the identified issues thoroughly.")
        
        return f"""
Enhanced Requirements:
- {enhancement}
- Test thoroughly to ensure no regressions
- Follow the original task requirements plus these improvements
- Generate clear, documented output
""".strip()
    
    async def _create_fix_tasks_for_failure(self, task_list: TaskList, failed_task: TaskItem, error_message: str) -> None:
        """Create fix tasks when a task fails with an error"""
        logger.info(f"  🔧 Creating fix tasks for failed task: {failed_task.title}")
        
        # Create a diagnostic task
        diagnostic_task = TaskItem(
            id=self.generate_id(),
            title=f"Diagnose: {failed_task.title}",
            description=f"""
Analyze why the following task failed and propose solutions:
Failed Task: {failed_task.title}
Error: {error_message}

Provide:
1. Root cause analysis
2. Proposed solution approach
3. Preventative measures
""".strip(),
            type=TaskType.ANALYSIS,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[failed_task.id],
            estimated_time=5,
            file_operations=[]
        )
        
        # Create a recovery task
        recovery_task = TaskItem(
            id=self.generate_id(),
            title=f"Recover: {failed_task.title}",
            description=f"""
Implement a solution to recover from the failure:
Failed Task: {failed_task.title}
Error: {error_message}

Base the solution on the diagnostic analysis from the previous task.
""".strip(),
            type=TaskType.CODE_GENERATION,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[failed_task.id],
            estimated_time=15,
            file_operations=[]
        )
        
        # Insert both tasks after the failed task
        failed_index = task_list.tasks.index(failed_task)
        task_list.tasks.insert(failed_index + 1, diagnostic_task)
        task_list.tasks.insert(failed_index + 2, recovery_task)
        
        logger.info(f"  ✅ Created diagnostic task: {diagnostic_task.title}")
        logger.info(f"  ✅ Created recovery task: {recovery_task.title}")
    
    def generate_linear_workflow_summary(self, task_list: TaskList) -> str:
        """Generate a detailed summary of the linear workflow execution"""
        summary_lines = []
        summary_lines.append("LINEAR WORKFLOW EXECUTION SUMMARY")
        summary_lines.append("=" * 50)
        
        # Task execution summary
        task_stats = {
            'total': len(task_list.tasks),
            'completed': len([t for t in task_list.tasks if t.status == TaskStatus.COMPLETED]),
            'failed': len([t for t in task_list.tasks if t.status == TaskStatus.FAILED]),
            'reexecuting': len([t for t in task_list.tasks if t.status == TaskStatus.REEXECUTING])
        }
        
        summary_lines.append(f"📊 TASK STATISTICS:")
        summary_lines.append(f"  Total Tasks: {task_stats['total']}")
        summary_lines.append(f"  Completed: {task_stats['completed']}")
        summary_lines.append(f"  Failed: {task_stats['failed']}")
        summary_lines.append(f"  Re-executed: {task_stats['reexecuting']}")
        summary_lines.append("")
        
        # Linear execution order
        summary_lines.append("🔄 LINEAR EXECUTION ORDER:")
        for i, task in enumerate(task_list.tasks, 1):
            status_emoji = {
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.REEXECUTING: "🔁",
                TaskStatus.PENDING: "⏳"
            }.get(task.status, "❓")
            
            summary_lines.append(f"  {i:2d}. {status_emoji} {task.title} ({task.type.value})")
            
            if task.status == TaskStatus.REEXECUTING:
                summary_lines.append(f"      └─ Re-execution with enhanced instructions")
            elif task.dependencies:
                deps = [d[:8] for d in task.dependencies]  # Show partial IDs
                summary_lines.append(f"      └─ Depends on: {', '.join(deps)}")
        
        summary_lines.append("")
        summary_lines.append("📋 DYNAMIC TASK INSERTION:")
        
        # Show dynamically added tasks
        dynamic_tasks = [t for t in task_list.tasks if "Fix:" in t.title or "Diagnose:" in t.title or "Recover:" in t.title]
        if dynamic_tasks:
            for task in dynamic_tasks:
                summary_lines.append(f"  🔧 {task.title}")
        else:
            summary_lines.append("  ✅ No dynamic tasks were inserted")
        
        return "\n".join(summary_lines)

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
    
    # Task list is now created intelligently by LLM via create_task_list
    # No additional_tasks needed - trust the enhanced AI to create all necessary tasks
    # The create_task_list now automatically detects HTML files and creates ANALYSIS tasks first
    
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
    
    async def _execute_task_with_file_operations(self, file_operations):
        """Execute a list of file operations directly with comprehensive logging"""
        logger.info(f"🚀 Executing {len(file_operations)} file operations...")
        logger.info(f"  📁 Output directory: {Config.OUTPUT_DIR}")
        logger.info(f"  📂 Logs directory: {Config.LOGS_DIR}")
        
        results = []
        start_time = time.time()
        
        for i, file_op in enumerate(file_operations, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"📄 Operation {i}/{len(file_operations)}: {file_op.operation.value.upper()}")
            logger.info(f"📁 Target: {file_op.file_path}")
            logger.info(f"📝 Description: {file_op.description}")
            
            op_start_time = time.time()
            
            try:
                if file_op.operation == FileOperation.READ:
                    await self._handle_file_read_operation(file_op)
                elif file_op.operation == FileOperation.CREATE:
                    await self._handle_file_create_operation(file_op)
                    # Save content if provided
                    if hasattr(file_op, 'content') and file_op.content:
                        await self._save_generated_file(file_op, file_op.content)
                elif file_op.operation == FileOperation.DELETE:
                    await self._handle_file_delete_operation(file_op)
                elif file_op.operation == FileOperation.MODIFY:
                    await self._handle_file_modify_operation(file_op)
                elif file_op.operation == FileOperation.EXECUTE:
                    await self._handle_file_execute_operation(file_op)
                else:
                    raise ValueError(f"Unsupported operation: {file_op.operation}")
                
                duration = (time.time() - op_start_time) * 1000
                result = {
                    "operation": file_op.operation.value,
                    "file_path": file_op.file_path,
                    "status": "success",
                    "duration_ms": duration,
                    "result": f"Completed {file_op.operation.value} operation"
                }
                results.append(result)
                
                logger.info(f"✅ Operation {i} completed successfully ({duration:.1f}ms)")
                
            except Exception as e:
                duration = (time.time() - op_start_time) * 1000
                error_msg = f"Error processing {file_op.file_path}: {str(e)}"
                logger.error(f"❌ Operation {i} failed ({duration:.1f}ms): {error_msg}")
                
                results.append({
                    "operation": file_op.operation.value,
                    "file_path": file_op.file_path,
                    "status": "error",
                    "duration_ms": duration,
                    "error": error_msg
                })
        
        # Summary statistics
        total_duration = (time.time() - start_time) * 1000
        successful_ops = len([r for r in results if r["status"] == "success"])
        failed_ops = len([r for r in results if r["status"] == "error"])
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 File Operations Summary:")
        logger.info(f"✅ Successful: {successful_ops}/{len(file_operations)}")
        logger.info(f"❌ Failed: {failed_ops}/{len(file_operations)}")
        logger.info(f"⏱️ Total duration: {total_duration:.1f}ms")
        logger.info(f"📁 Output location: {Config.OUTPUT_DIR}")
        logger.info(f"📂 Logs location: {Config.LOGS_DIR}")
        logger.info(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results

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
        
        elif command == "linear":
            if len(sys.argv) < 3:
                print("❌ Please provide goal description")
                print('Usage: python enhanced_task_synthesis_system.py linear "<goal description>"')
                sys.exit(1)
            
            goal = " ".join(sys.argv[2:])
            max_cycles = int(sys.argv[3]) if len(sys.argv) > 3 else 3
            await task_manager.run_linear_workflow(goal, max_cycles=max_cycles)
        
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
            print('  - "linear <goal>" for LINEAR workflow with dynamic task insertion')
            print('  - "status" to show current progress')
            print('  - "audit <session-id>" to view audit logs')
    
    except Exception as error:
        logger.error(f"\n💥 Error: {error}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())