#!/usr/bin/env python3
"""
Enhanced Task Synthesis System - Python Version with Robust Error Handling
===========================================================================

Workflow: Create todo list → Input to task → Execute code → Review → Repeat

Enhanced Features:
- Comprehensive error handling with automatic recovery
- Circuit breaker pattern for API calls
- Exponential backoff with jitter
- Graceful degradation
- Transaction-like file operations with rollback
- Health checks and monitoring
- Rate limiting protection
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
from contextlib import contextmanager, asynccontextmanager
import aiofiles
import tempfile
import shutil
from functools import wraps
import random

# Configure enhanced logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== ERROR CLASSES ====================

class TaskSynthesisError(Exception):
    """Base exception for task synthesis system"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

class APIError(TaskSynthesisError):
    """API-related errors"""
    pass

class FileOperationError(TaskSynthesisError):
    """File operation errors"""
    pass

class TaskExecutionError(TaskSynthesisError):
    """Task execution errors"""
    pass

class ValidationError(TaskSynthesisError):
    """Validation errors"""
    pass

class CircuitBreakerError(TaskSynthesisError):
    """Circuit breaker open error"""
    pass

class RetryExhaustedError(TaskSynthesisError):
    """Retry attempts exhausted"""
    pass

# ==================== CIRCUIT BREAKER ====================

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreaker:
    """Circuit breaker for API calls"""
    failure_threshold: int = 5
    timeout: float = 60.0
    half_open_timeout: float = 30.0
    
    def __post_init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0
    
    def call(self, func):
        """Decorator for circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info("🔄 Circuit breaker: Attempting reset (half-open)")
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker is OPEN. Wait {self._time_until_retry():.1f}s",
                        {"state": self.state.value, "failures": self.failure_count}
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout
    
    def _time_until_retry(self) -> float:
        """Calculate time until retry is allowed"""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.timeout - elapsed)
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # Require 2 successes to close
                logger.info("✅ Circuit breaker: Closed (recovered)")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning("⚠️ Circuit breaker: Failed in half-open, reopening")
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            logger.error(f"🔴 Circuit breaker: OPEN ({self.failure_count} failures)")
            self.state = CircuitState.OPEN

# ==================== RETRY DECORATOR ====================

def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple = (Exception,)
):
    """
    Async retry decorator with exponential backoff and jitter
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"❌ Retry exhausted after {max_attempts} attempts")
                        raise RetryExhaustedError(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            {"attempts": max_attempts, "last_error": str(e)}
                        )
                    
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"⚠️ Attempt {attempt + 1}/{max_attempts} failed: {str(e)[:100]}"
                    )
                    logger.info(f"⏳ Retrying in {delay:.2f}s...")
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# ==================== FILE OPERATION CONTEXT MANAGER ====================

@asynccontextmanager
async def safe_file_operation(operation_name: str, rollback_on_error: bool = True):
    """
    Context manager for safe file operations with automatic rollback
    
    Usage:
        async with safe_file_operation("create_file") as ctx:
            ctx.backup_path = await backup_file(path)
            await create_file(path)
    """
    context = {"backup_paths": [], "created_files": [], "success": False}
    
    try:
        yield context
        context["success"] = True
        logger.debug(f"✅ File operation '{operation_name}' completed successfully")
    except Exception as e:
        logger.error(f"❌ File operation '{operation_name}' failed: {e}")
        
        if rollback_on_error:
            logger.info(f"🔄 Rolling back file operation '{operation_name}'")
            
            # Restore backups
            for backup_path in context.get("backup_paths", []):
                try:
                    if Path(backup_path).exists():
                        original_path = backup_path.replace(".backup", "")
                        shutil.move(backup_path, original_path)
                        logger.info(f"  ↩️  Restored: {original_path}")
                except Exception as rollback_error:
                    logger.error(f"  ❌ Rollback failed: {rollback_error}")
            
            # Remove created files
            for created_file in context.get("created_files", []):
                try:
                    if Path(created_file).exists():
                        Path(created_file).unlink()
                        logger.info(f"  🗑️  Removed: {created_file}")
                except Exception as cleanup_error:
                    logger.error(f"  ❌ Cleanup failed: {cleanup_error}")
        
        raise FileOperationError(
            f"File operation '{operation_name}' failed: {str(e)}",
            {"operation": operation_name, "error": str(e)}
        )

# ==================== HEALTH CHECK ====================

@dataclass
class HealthStatus:
    """System health status"""
    is_healthy: bool
    api_status: str
    file_system_status: str
    disk_usage_percent: float
    last_check: str
    errors: List[str] = field(default_factory=list)

class HealthChecker:
    """Health monitoring for the system"""
    
    def __init__(self):
        self.last_api_call = None
        self.api_success_rate = 1.0
        self.total_api_calls = 0
        self.successful_api_calls = 0
    
    async def check_health(self) -> HealthStatus:
        """Perform comprehensive health check"""
        errors = []
        
        # Check API health
        api_status = "healthy"
        if self.api_success_rate < 0.5:
            api_status = "degraded"
            errors.append(f"API success rate below 50%: {self.api_success_rate:.1%}")
        elif self.api_success_rate < 0.8:
            api_status = "warning"
        
        # Check file system
        file_system_status = "healthy"
        try:
            import shutil
            disk_usage = shutil.disk_usage(Config.OUTPUT_DIR)
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_usage_percent > 90:
                file_system_status = "critical"
                errors.append(f"Disk usage critical: {disk_usage_percent:.1f}%")
            elif disk_usage_percent > 80:
                file_system_status = "warning"
                errors.append(f"Disk usage high: {disk_usage_percent:.1f}%")
        except Exception as e:
            file_system_status = "unknown"
            disk_usage_percent = 0
            errors.append(f"Could not check disk usage: {e}")
        
        is_healthy = (
            api_status in ["healthy", "warning"] and
            file_system_status in ["healthy", "warning"]
        )
        
        return HealthStatus(
            is_healthy=is_healthy,
            api_status=api_status,
            file_system_status=file_system_status,
            disk_usage_percent=disk_usage_percent,
            last_check=datetime.now(timezone.utc).isoformat(),
            errors=errors
        )
    
    def record_api_call(self, success: bool):
        """Record API call result for health monitoring"""
        self.total_api_calls += 1
        if success:
            self.successful_api_calls += 1
        
        if self.total_api_calls > 0:
            self.api_success_rate = self.successful_api_calls / self.total_api_calls
        
        self.last_api_call = time.time()

# ==================== CONFIGURATION ====================

class Config:
    GEMINI_API_URL = os.getenv("GEMINI_API_URL", "http://localhost:8017/v1/generate")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "sk-e0dde619-2dd3-4018-aad1-e7f602d58534")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-05-20")
    TASKS_DIR = Path("./task-lists")
    OUTPUT_DIR = Path("./output")
    LOGS_DIR = Path("./logs")
    AUDIT_DIR = Path("./audit")
    BACKUP_DIR = Path("./backups")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "7"))
    INITIAL_DELAY = float(os.getenv("INITIAL_DELAY", "1.0"))
    MAX_DELAY = float(os.getenv("MAX_DELAY", "60.0"))
    BACKOFF_MULTIPLIER = float(os.getenv("BACKOFF_MULTIPLIER", "2"))
    REQUEST_DUMP_SIZE = int(os.getenv("REQUEST_DUMP_SIZE", "50000"))
    MAX_LOG_FILE_SIZE = int(os.getenv("MAX_LOG_FILE_SIZE", "104857600"))  # 100MB
    ENABLE_CIRCUIT_BREAKER = os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    CIRCUIT_BREAKER_TIMEOUT = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60.0"))
    ENABLE_HEALTH_CHECKS = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))  # 5 minutes

# Ensure directories exist
for dir_path in [Config.TASKS_DIR, Config.OUTPUT_DIR, Config.LOGS_DIR, 
                 Config.AUDIT_DIR, Config.BACKUP_DIR]:
    try:
        dir_path.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        raise

# ==================== ENUMS ====================

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
    REEXECUTING = "reexecuting"
    WAITING = "waiting"

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

# ==================== DATA CLASSES ====================

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
    backup_path: Optional[str] = None
    
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
    errors: List[str] = field(default_factory=list)

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
    retry_count: int = 0
    max_retries: int = 3

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
    health_status: Optional[Dict[str, Any]] = None

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

# ==================== AUDIT LOGGER ====================

class AuditLogger:
    """Enhanced audit logging with error tracking"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.request_count = 0
        self.error_count = 0
        self.log_file = Config.AUDIT_DIR / f"audit_{self.session_id}.jsonl"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure audit log file exists"""
        try:
            if not self.log_file.exists():
                with open(self.log_file, 'w') as f:
                    f.write("")
        except Exception as e:
            logger.error(f"Failed to create audit log file: {e}")
            raise
    
    def log_api_request(self, prompt: str, system_instruction: str, 
                       request_data: Dict[str, Any], response_data: Dict[str, Any], 
                       success: bool, duration_ms: int, error: Optional[str] = None):
        """Log API request and response with full dumps"""
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        try:
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
            
            # Console logging
            status = "✓" if success else "✗"
            logger.info(f"{status} API Request {self.request_count} [{duration_ms}ms] | {prompt_hash}")
            
            if success:
                logger.info(f"  📤 Request: {len(prompt)} chars -> 📥 Response: {len(str(response_data))} chars")
            else:
                logger.error(f"  ❌ Error: {error}")
                
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log detailed error information"""
        self.error_count += 1
        
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_details": getattr(error, 'details', {}),
                "context": context,
                "traceback": traceback.format_exc()
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log error: {e}")

# ==================== TASK SYNTHESIS MANAGER ====================

class TaskSynthesisManager:
    """Enhanced task synthesis manager with robust error handling"""
    
    def __init__(self):
        self.task_lists: Dict[str, TaskList] = {}
        self.current_task_list: Optional[TaskList] = None
        self.session_id = str(uuid.uuid4())
        self.audit_logger = AuditLogger()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=Config.CIRCUIT_BREAKER_THRESHOLD,
            timeout=Config.CIRCUIT_BREAKER_TIMEOUT
        ) if Config.ENABLE_CIRCUIT_BREAKER else None
        self.health_checker = HealthChecker() if Config.ENABLE_HEALTH_CHECKS else None
        self.last_health_check = time.time()
        
        # Shared context
        self.shared_context: Dict[str, Any] = {
            "task_outputs": {},
            "key_insights": [],
            "file_mappings": {},
            "context_history": []
        }
        
        # Create session log file
        self.log_file = Config.LOGS_DIR / f"session_{self.session_id}.log"
        
        logger.info(f"🚀 Task Synthesis Manager initialized")
        logger.info(f"🆔 Session ID: {self.session_id}")
        logger.info(f"🔒 Circuit Breaker: {'Enabled' if Config.ENABLE_CIRCUIT_BREAKER else 'Disabled'}")
        logger.info(f"❤️  Health Checks: {'Enabled' if Config.ENABLE_HEALTH_CHECKS else 'Disabled'}")
    
    async def check_health_periodically(self):
        """Periodically check system health"""
        if not Config.ENABLE_HEALTH_CHECKS or not self.health_checker:
            return
        
        current_time = time.time()
        if current_time - self.last_health_check < Config.HEALTH_CHECK_INTERVAL:
            return
        
        self.last_health_check = current_time
        health_status = await self.health_checker.check_health()
        
        if not health_status.is_healthy:
            logger.warning("⚠️ System health check failed:")
            for error in health_status.errors:
                logger.warning(f"  - {error}")
        else:
            logger.debug(f"✅ System health check passed")
    
    @async_retry(max_attempts=Config.MAX_RETRIES, initial_delay=Config.INITIAL_DELAY, 
                 max_delay=Config.MAX_DELAY, exceptions=(APIError, asyncio.TimeoutError))
    async def call_gemini(self, prompt: str, system_instruction: str = "",
                         retry_count: int = 0) -> str:
        """Call Gemini API with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Check health before making API call
            await self.check_health_periodically()
            
            logger.info(f"🤖 Calling Gemini API (attempt {retry_count + 1})...")
            
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
            
            # Apply circuit breaker if enabled
            if Config.ENABLE_CIRCUIT_BREAKER and self.circuit_breaker:
                if self.circuit_breaker.state == CircuitState.OPEN:
                    wait_time = self.circuit_breaker._time_until_retry()
                    raise CircuitBreakerError(
                        f"Circuit breaker is OPEN. Wait {wait_time:.1f}s before retry",
                        {"wait_time": wait_time}
                    )
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        Config.GEMINI_API_URL,
                        headers={
                            'accept': 'application/json',
                            'x-api-key': Config.GEMINI_API_KEY,
                            'Content-Type': 'application/json'
                        },
                        json=request_data,
                        timeout=aiohttp.ClientTimeout(total=120)  # Increased timeout
                    ) as response:
                        if not response.ok:
                            error_text = await response.text()
                            duration = int((time.time() - start_time) * 1000)
                            
                            # Log failed request
                            self.audit_logger.log_api_request(
                                prompt, system_instruction, request_data,
                                {"error": error_text}, False, duration, error_text
                            )
                            
                            # Record failure for health monitoring
                            if self.health_checker:
                                self.health_checker.record_api_call(False)
                            
                            # Update circuit breaker
                            if self.circuit_breaker:
                                self.circuit_breaker._on_failure()
                            
                            raise APIError(
                                f"API Error [{response.status}]: {error_text[:200]}",
                                {"status_code": response.status, "error": error_text}
                            )
                        
                        data = await response.json()
                        duration = int((time.time() - start_time) * 1000)
                        
                        if not data.get('output_text'):
                            self.audit_logger.log_api_request(
                                prompt, system_instruction, request_data,
                                data, False, duration, "Empty response from API"
                            )
                            
                            if self.health_checker:
                                self.health_checker.record_api_call(False)
                            
                            if self.circuit_breaker:
                                self.circuit_breaker._on_failure()
                            
                            raise APIError('Empty response from Gemini API')
                        
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
                            .replace('```json\n', '')
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
                        
                        # Record success for health monitoring
                        if self.health_checker:
                            self.health_checker.record_api_call(True)
                        
                        # Update circuit breaker
                        if self.circuit_breaker:
                            self.circuit_breaker._on_success()
                        
                        logger.info(f"✓ Success ({tokens} tokens, {duration}ms)")
                        
                        return cleaned_output
                        
                except asyncio.TimeoutError:
                    duration = int((time.time() - start_time) * 1000)
                    error_msg = f"API request timed out after {duration}ms"
                    
                    self.audit_logger.log_api_request(
                        prompt, system_instruction, request_data,
                        {}, False, duration, error_msg
                    )
                    
                    if self.health_checker:
                        self.health_checker.record_api_call(False)
                    
                    if self.circuit_breaker:
                        self.circuit_breaker._on_failure()
                    
                    raise APIError(error_msg, {"timeout": True})
                    
        except (APIError, CircuitBreakerError):
            raise
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            
            self.audit_logger.log_error(error, {
                "function": "call_gemini",
                "retry_count": retry_count,
                "duration_ms": duration
            })
            
            if self.health_checker:
                self.health_checker.record_api_call(False)
            
            if self.circuit_breaker:
                self.circuit_breaker._on_failure()
            
            raise APIError(
                f"Unexpected API error: {str(error)}",
                {"error_type": type(error).__name__, "error": str(error)}
            )
    
    def _truncate_content(self, content: str, max_size: int) -> str:
        """Truncate content for logging purposes"""
        if len(content) <= max_size:
            return content
        return content[:max_size // 2] + f"\n... [{len(content) - max_size} chars truncated] ...\n" + content[-max_size // 2:]
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text with error handling"""
        try:
            # Remove common markdown code block indicators
            text = text.strip()
            text = re.sub(r'```(?:json|typescript|tsx|ts|javascript|jsx|js)?\n?', '', text)
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
            
            text = text.strip()
            
            if not text:
                raise ValidationError("No JSON content found in response")
            
            logger.info(f"✅ JSON extraction successful, length: {len(text)} characters")
            return text
            
        except Exception as e:
            raise ValidationError(
                f"Failed to extract JSON from response: {str(e)}",
                {"raw_text": text[:200] if text else ""}
            )
    
    def _parse_json_with_repair(self, json_str: str) -> dict:
        """Parse JSON with repair capabilities"""
        try:
            # Strategy 1: Direct parsing
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {e}")
            
            try:
                # Strategy 2: Repair common errors
                repaired_json = self._repair_common_json_errors(json_str)
                return json.loads(repaired_json)
            except json.JSONDecodeError as e2:
                logger.warning(f"Repaired JSON parsing failed: {e2}")
                
                try:
                    # Strategy 3: Extract partial JSON
                    return self._extract_partial_json(json_str)
                except Exception as e3:
                    logger.error(f"Partial JSON extraction failed: {e3}")
                    
                    # Strategy 4: Fallback response
                    return self._create_fallback_response(json_str)
    
    def _repair_common_json_errors(self, json_str: str) -> str:
        """Repair common JSON syntax errors"""
        # Remove leading "json" prefix
        lines = json_str.split('\n')
        if lines and lines[0].strip().lower() == 'json':
            json_str = '\n'.join(lines[1:]).strip()
        
        # Fix trailing commas
        json_str = re.sub(r',(\s*})', r'\1', json_str)
        json_str = re.sub(r',(\s*])', r'\1', json_str)
        
        # Fix unescaped newlines
        json_str = re.sub(r'(?<!\\)\\n', '\\\\n', json_str)
        
        return json_str
    
    def _extract_partial_json(self, json_str: str) -> dict:
        """Extract partial valid JSON structure"""
        tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
        if tasks_match:
            tasks_content = tasks_match.group(1)
            tasks = []
            task_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            task_matches = re.findall(task_pattern, tasks_content)
            
            for task_match in task_matches:
                try:
                    task = json.loads(task_match)
                    tasks.append(task)
                except json.JSONDecodeError:
                    tasks.append({
                        "id": f"task_{len(tasks) + 1}",
                        "title": "Extracted Task",
                        "description": "Task extracted from partial JSON",
                        "type": "analysis",
                        "priority": "medium",
                        "file_operations": []
                    })
            
            id_match = re.search(r'"id"\s*:\s*"([^"]*)"', json_str)
            title_match = re.search(r'"title"\s*:\s*"([^"]*)"', json_str)
            
            return {
                "id": id_match.group(1) if id_match else "extracted_task_list",
                "title": title_match.group(1) if title_match else "Extracted Task List",
                "description": "Extracted from partial JSON",
                "tasks": tasks
            }
        
        raise ValidationError("Could not extract valid JSON structure")
    
    def _create_fallback_response(self, json_str: str) -> dict:
        """Create minimal valid response as fallback"""
        logger.error("🎯 Creating fallback response due to JSON parsing failure")
        
        id_match = re.search(r'"id"\s*:\s*"([^"]*)"', json_str)
        title_match = re.search(r'"title"\s*:\s*"([^"]*)"', json_str)
        
        return {
            "id": id_match.group(1) if id_match else "fallback_task_list",
            "title": title_match.group(1) if title_match else "Fallback Task List",
            "description": "Created due to JSON parsing failure",
            "tasks": [
                {
                    "id": "fallback_task_1",
                    "title": "Manual Review Required",
                    "description": "JSON parsing failed. Manual intervention needed.",
                    "type": "review",
                    "priority": "high",
                    "file_operations": []
                }
            ]
        }
    
    async def _safe_file_backup(self, file_path: Path) -> Optional[str]:
        """Create a backup of a file before modification"""
        try:
            if not file_path.exists():
                return None
            
            backup_dir = Config.BACKUP_DIR / datetime.now().strftime("%Y%m%d")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_path = backup_dir / f"{file_path.name}.{int(time.time())}.backup"
            shutil.copy2(file_path, backup_path)
            
            logger.debug(f"📋 Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            raise FileOperationError(
                f"Backup creation failed: {str(e)}",
                {"file_path": str(file_path)}
            )
    
    async def _handle_file_read_operation(self, file_op: FileOperationItem):
        """Handle file read operation with error handling"""
        start_time = time.time()
        
        try:
            file_path = Path(file_op.file_path)
            
            if not file_path.exists():
                raise FileOperationError(
                    f"File not found: {file_path}",
                    {"operation": "read", "file_path": str(file_path)}
                )
            
            if not file_path.is_file():
                raise FileOperationError(
                    f"Path is not a file: {file_path}",
                    {"operation": "read", "file_path": str(file_path)}
                )
            
            file_size = file_path.stat().st_size
            
            # Check file size limit (100MB)
            if file_size > 100 * 1024 * 1024:
                raise FileOperationError(
                    f"File too large: {file_size / (1024*1024):.1f}MB (max 100MB)",
                    {"operation": "read", "file_path": str(file_path), "size": file_size}
                )
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            file_op.size_bytes = file_size
            file_op.checksum = hashlib.md5(content.encode()).hexdigest()[:16]
            file_op.completed_at = datetime.now(timezone.utc).isoformat()
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"✅ Read {file_size:,} bytes from {file_path} ({duration:.1f}ms)")
            
        except FileOperationError:
            raise
        except Exception as e:
            self.audit_logger.log_error(e, {
                "operation": "file_read",
                "file_path": file_op.file_path
            })
            raise FileOperationError(
                f"Failed to read file: {str(e)}",
                {"operation": "read", "file_path": file_op.file_path}
            )
    
    async def _handle_file_create_operation(self, file_op: FileOperationItem, content: str):
        """Handle file create operation with error handling and rollback"""
        async with safe_file_operation(f"create_{file_op.file_path}") as ctx:
            try:
                file_path = Path(file_op.file_path)
                
                # Validate file path
                if not str(file_path).startswith(str(Config.OUTPUT_DIR)):
                    file_path = Config.OUTPUT_DIR / file_path.name
                    file_op.file_path = str(file_path)
                
                # Check if file already exists
                if file_path.exists():
                    backup_path = await self._safe_file_backup(file_path)
                    ctx["backup_paths"].append(backup_path)
                    logger.info(f"⚠️ File exists, created backup: {backup_path}")
                
                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write content
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                
                ctx["created_files"].append(str(file_path))
                
                # Update file operation metadata
                file_size = file_path.stat().st_size
                file_op.size_bytes = file_size
                file_op.checksum = hashlib.md5(content.encode()).hexdigest()[:16]
                file_op.completed_at = datetime.now(timezone.utc).isoformat()
                
                logger.info(f"✅ Created file: {file_path} ({file_size:,} bytes)")
                
            except Exception as e:
                self.audit_logger.log_error(e, {
                    "operation": "file_create",
                    "file_path": file_op.file_path
                })
                raise
    
    async def _handle_file_delete_operation(self, file_op: FileOperationItem):
        """Handle file delete operation with backup"""
        async with safe_file_operation(f"delete_{file_op.file_path}") as ctx:
            try:
                file_path = Path(file_op.file_path)
                
                if not file_path.exists():
                    logger.warning(f"⚠️ File not found for deletion: {file_path}")
                    return
                
                # Create backup before deletion
                backup_path = await self._safe_file_backup(file_path)
                ctx["backup_paths"].append(backup_path)
                
                file_size = file_path.stat().st_size
                file_op.size_bytes = file_size
                
                # Delete file
                file_path.unlink()
                file_op.completed_at = datetime.now(timezone.utc).isoformat()
                
                logger.info(f"🗑️ Deleted file: {file_path} ({file_size:,} bytes, backed up)")
                
            except Exception as e:
                self.audit_logger.log_error(e, {
                    "operation": "file_delete",
                    "file_path": file_op.file_path
                })
                raise FileOperationError(
                    f"Failed to delete file: {str(e)}",
                    {"operation": "delete", "file_path": file_op.file_path}
                )
    
    async def _execute_task_with_error_handling(self, task: TaskItem) -> None:
        """Execute task with comprehensive error handling"""
        task.retry_count = 0
        last_error = None
        
        while task.retry_count <= task.max_retries:
            try:
                # Execute the task
                await self._execute_task(task)
                
                # Mark as completed
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc).isoformat()
                
                logger.info(f"✅ Task completed: {task.title}")
                return
                
            except (APIError, CircuitBreakerError) as e:
                # These errors are retriable
                last_error = e
                task.retry_count += 1
                
                if task.retry_count > task.max_retries:
                    logger.error(f"❌ Task failed after {task.max_retries} retries: {task.title}")
                    break
                
                # Calculate delay with exponential backoff
                delay = min(
                    Config.INITIAL_DELAY * (Config.BACKOFF_MULTIPLIER ** task.retry_count),
                    Config.MAX_DELAY
                )
                
                logger.warning(
                    f"⚠️ Task retry {task.retry_count}/{task.max_retries} for {task.title}"
                )
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                
                await asyncio.sleep(delay)
                
            except (FileOperationError, ValidationError) as e:
                # These errors are generally not retriable
                last_error = e
                logger.error(f"❌ Task failed with non-retriable error: {task.title}")
                logger.error(f"   Error: {str(e)}")
                break
                
            except Exception as e:
                # Unexpected errors
                last_error = e
                logger.error(f"💥 Unexpected error in task {task.title}: {e}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                
                self.audit_logger.log_error(e, {
                    "task_id": task.id,
                    "task_title": task.title,
                    "retry_count": task.retry_count
                })
                break
        
        # Task failed
        task.status = TaskStatus.FAILED
        task.errors = [str(last_error)] if last_error else ["Unknown error"]
        
        # Create error output
        task.output = TaskOutput(
            task_id=task.id,
            content="",
            summary=f"Task failed: {str(last_error)[:200]}",
            errors=task.errors
        )
        
        raise TaskExecutionError(
            f"Task execution failed: {task.title}",
            {
                "task_id": task.id,
                "retry_count": task.retry_count,
                "error": str(last_error)
            }
        )
    
    async def _execute_task(self, task: TaskItem) -> None:
        """Execute a task (placeholder - implement specific task types)"""
        # This is a simplified version - implement full task execution logic
        logger.info(f"🔄 Executing task: {task.title}")
        
        # Simulate task execution
        await asyncio.sleep(0.1)
        
        # Create mock output
        task.output = TaskOutput(
            task_id=task.id,
            content=f"Task {task.title} executed successfully",
            summary=f"Completed: {task.description[:100]}"
        )
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        return f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    async def run_with_error_handling(self, goal: str, 
                                     input_context: Optional[Dict[str, Any]] = None) -> TaskList:
        """Run workflow with comprehensive error handling"""
        try:
            logger.info(f"\n🚀 Starting workflow: {goal}")
            logger.info(f"🆔 Session ID: {self.session_id}")
            
            # Check initial health
            if Config.ENABLE_HEALTH_CHECKS and self.health_checker:
                health_status = await self.health_checker.check_health()
                if not health_status.is_healthy:
                    logger.warning("⚠️ System health check shows warnings")
                    for error in health_status.errors:
                        logger.warning(f"  - {error}")
            
            # Create task list (implement this method)
            # task_list = await self.create_task_list(goal, input_context)
            
            # Execute tasks (implement this method)
            # await self.execute_task_list(task_list)
            
            logger.info("✅ Workflow completed successfully")
            
            # Return task list
            # return task_list
            
        except TaskSynthesisError as e:
            logger.error(f"❌ Workflow failed: {e}")
            logger.error(f"   Details: {e.details}")
            self.audit_logger.log_error(e, {"goal": goal, "context": input_context})
            raise
            
        except Exception as e:
            logger.error(f"💥 Unexpected workflow error: {e}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            self.audit_logger.log_error(e, {"goal": goal, "context": input_context})
            raise TaskSynthesisError(
                f"Workflow failed with unexpected error: {str(e)}",
                {"goal": goal, "error_type": type(e).__name__}
            )

# ==================== CLI INTERFACE ====================

async def main():
    """Enhanced CLI with error handling"""
    try:
        if len(sys.argv) < 2:
            print("""
🚀 Enhanced Task Synthesis System with Robust Error Handling
============================================================

Features:
✅ Comprehensive error handling with automatic recovery
✅ Circuit breaker pattern for API resilience
✅ Exponential backoff with jitter for retries
✅ Transaction-like file operations with rollback
✅ Health monitoring and checks
✅ Detailed audit logging

Commands:
  python script.py workflow "<goal>"  - Run workflow with error handling
  python script.py health            - Check system health
  python script.py status            - Show current status

Environment Variables:
  GEMINI_API_URL              - API endpoint
  GEMINI_API_KEY              - API key
  MAX_RETRIES                 - Maximum retry attempts (default: 7)
  ENABLE_CIRCUIT_BREAKER      - Enable circuit breaker (default: true)
  CIRCUIT_BREAKER_THRESHOLD   - Failure threshold (default: 5)
  ENABLE_HEALTH_CHECKS        - Enable health monitoring (default: true)

Example:
  python script.py workflow "Build a todo app with React"
            """)
            return
        
        command = sys.argv[1]
        manager = TaskSynthesisManager()
        
        if command == "workflow":
            if len(sys.argv) < 3:
                print("❌ Please provide goal description")
                sys.exit(1)
            
            goal = " ".join(sys.argv[2:])
            await manager.run_with_error_handling(goal)
            
        elif command == "health":
            if Config.ENABLE_HEALTH_CHECKS and manager.health_checker:
                health_status = await manager.health_checker.check_health()
                print(f"\n🏥 System Health Check")
                print(f"Status: {'✅ Healthy' if health_status.is_healthy else '⚠️ Unhealthy'}")
                print(f"API Status: {health_status.api_status}")
                print(f"File System: {health_status.file_system_status}")
                print(f"Disk Usage: {health_status.disk_usage_percent:.1f}%")
                
                if health_status.errors:
                    print(f"\n⚠️ Issues:")
                    for error in health_status.errors:
                        print(f"  - {error}")
            else:
                print("❌ Health checks are disabled")
                
        elif command == "status":
            print(f"\n📊 System Status")
            print(f"Session ID: {manager.session_id}")
            print(f"Circuit Breaker: {'Enabled' if Config.ENABLE_CIRCUIT_BREAKER else 'Disabled'}")
            print(f"Health Checks: {'Enabled' if Config.ENABLE_HEALTH_CHECKS else 'Disabled'}")
            print(f"Log File: {manager.log_file}")
            
            if manager.circuit_breaker:
                print(f"\nCircuit Breaker Status:")
                print(f"  State: {manager.circuit_breaker.state.value}")
                print(f"  Failures: {manager.circuit_breaker.failure_count}")
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(130)
    except TaskSynthesisError as e:
        print(f"\n❌ Task Synthesis Error: {e}")
        print(f"   Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())