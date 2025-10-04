#!/usr/bin/env python3
"""
Simple Startup Script
=====================

This script provides a simple way to start the AI Tutor Orchestrator system.
"""

import subprocess
import sys
import time
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import langchain
        import langgraph
        import openai
        import httpx
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_orchestrator():
    """Start the main orchestrator service."""
    print("Starting AI Tutor Orchestrator...")
    try:
        process = subprocess.Popen([sys.executable, "main.py"])
        print(f"✓ Orchestrator started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"✗ Failed to start orchestrator: {e}")
        return None

def start_mock_tools():
    """Start all mock educational tools."""
    tools = [
        ("Note Maker", "mock_tools/note_maker.py"),
        ("Flashcard Generator", "mock_tools/flashcard_generator.py"),
        ("Concept Explainer", "mock_tools/concept_explainer.py")
    ]
    
    processes = []
    
    for tool_name, script_path in tools:
        print(f"Starting {tool_name}...")
        try:
            process = subprocess.Popen([sys.executable, script_path])
            processes.append((tool_name, process))
            print(f"✓ {tool_name} started with PID {process.pid}")
        except Exception as e:
            print(f"✗ Failed to start {tool_name}: {e}")
    
    return processes

def main():
    """Main function."""
    print("AI Tutor Orchestrator - Simple Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠ Warning: .env file not found")
        print("Please copy env.example to .env and configure your settings")
        print("Continuing with default settings...")
    
    # Start services
    orchestrator_process = start_orchestrator()
    if not orchestrator_process:
        sys.exit(1)
    
    tool_processes = start_mock_tools()
    
    print("\n" + "=" * 40)
    print("Services Started Successfully!")
    print("=" * 40)
    print("Main Orchestrator: http://localhost:8000")
    print("Note Maker Tool: http://localhost:8001")
    print("Flashcard Generator: http://localhost:8002")
    print("Concept Explainer: http://localhost:8003")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if orchestrator is still running
            if orchestrator_process.poll() is not None:
                print("✗ Orchestrator stopped unexpectedly")
                break
            
            # Check tool processes
            for tool_name, process in tool_processes:
                if process.poll() is not None:
                    print(f"✗ {tool_name} stopped unexpectedly")
    
    except KeyboardInterrupt:
        print("\nShutting down services...")
        
        # Stop orchestrator
        if orchestrator_process:
            orchestrator_process.terminate()
            orchestrator_process.wait()
            print("✓ Orchestrator stopped")
        
        # Stop tools
        for tool_name, process in tool_processes:
            process.terminate()
            process.wait()
            print(f"✓ {tool_name} stopped")
        
        print("All services stopped")

if __name__ == "__main__":
    main()
