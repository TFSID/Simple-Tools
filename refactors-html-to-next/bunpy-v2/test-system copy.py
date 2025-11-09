#!/usr/bin/env python3
"""
Test the Enhanced Task Synthesis System
"""

import asyncio
import json
import time
from enhanced_task_synthesis_system import TaskSynthesisManager, FileOperation, Priority

async def test_enhanced_system():
    """Test the enhanced task synthesis system"""
    print("🧪 Testing Enhanced Task Synthesis System")
    print("=" * 50)
    
    # Create task manager
    manager = TaskSynthesisManager()
    print(f"🆔 Session ID: {manager.session_id}")
    print(f"📁 Log file: {manager.log_file}")
    
    # Test file operations tracking
    print("\n📁 Testing file operations tracking...")
    
    # Create a simple task list
    try:
        task_list = await manager.create_task_list(
            "Create a simple Python calculator",
            {"language": "Python", "features": ["basic operations", "error handling"]}
        )
        
        print(f"✅ Task list created: {task_list.title}")
        print(f"📋 Tasks: {len(task_list.tasks)}")
        
        # Show file operations
        file_ops_summary = task_list.get_file_operations_summary()
        print(f"📁 File operations found:")
        for op_type, ops in file_ops_summary.items():
            if ops:
                print(f"  {op_type.upper()}: {len(ops)} files")
                for op in ops:
                    print(f"    - {op.operation.value}: {op.file_path}")
        
        # Test processing one task
        print(f"\n🔄 Testing task processing...")
        next_task = await manager.process_next_task()
        
        if next_task:
            print(f"✅ Task processed: {next_task.title}")
            if next_task.output:
                print(f"📄 Output created: {len(next_task.output.content)} chars")
                print(f"📋 Summary: {next_task.output.summary}")
        
        # Test output list generation
        output_list = task_list.generate_output_list()
        print(f"📋 Output list generated: {len(output_list)} items")
        
        print(f"\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_system())
    exit(0 if success else 1)