#!/usr/bin/env python3
"""
Start Services Script
=====================

This script starts all the services required for the AI Tutor Orchestrator system.
It can start the main orchestrator service and all mock educational tools.
"""

import subprocess
import sys
import time
import signal
import os
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages starting and stopping of all services."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.services = {
            "orchestrator": {
                "command": ["python", "main.py"],
                "port": 8000,
                "description": "AI Tutor Orchestrator"
            },
            "note_maker": {
                "command": ["python", "mock_tools/note_maker.py"],
                "port": 8001,
                "description": "Note Maker Tool"
            },
            "flashcard_generator": {
                "command": ["python", "mock_tools/flashcard_generator.py"],
                "port": 8002,
                "description": "Flashcard Generator Tool"
            },
            "concept_explainer": {
                "command": ["python", "mock_tools/concept_explainer.py"],
                "port": 8003,
                "description": "Concept Explainer Tool"
            }
        }
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service_config = self.services[service_name]
        
        try:
            logger.info(f"Starting {service_config['description']} on port {service_config['port']}")
            
            process = subprocess.Popen(
                service_config["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            logger.info(f"Started {service_config['description']} with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {service_config['description']}: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all services."""
        logger.info("Starting all AI Tutor Orchestrator services...")
        
        success = True
        for service_name in self.services.keys():
            if not self.start_service(service_name):
                success = False
        
        if success:
            logger.info("All services started successfully!")
            logger.info("Services running:")
            for service_name, config in self.services.items():
                logger.info(f"  - {config['description']}: http://localhost:{config['port']}")
        else:
            logger.error("Some services failed to start")
        
        return success
    
    def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped process with PID {process.pid}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing process with PID {process.pid}")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping process {process.pid}: {e}")
        
        self.processes.clear()
        logger.info("All services stopped")
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        if service_name not in self.services:
            return False
        
        port = self.services[service_name]["port"]
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def wait_for_services(self, timeout: int = 30) -> bool:
        """Wait for all services to be ready."""
        logger.info(f"Waiting for services to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_ready = True
            
            for service_name in self.services.keys():
                if not self.check_service_health(service_name):
                    all_ready = False
                    break
            
            if all_ready:
                logger.info("All services are ready!")
                return True
            
            time.sleep(1)
        
        logger.error("Timeout waiting for services to be ready")
        return False
    
    def show_status(self):
        """Show status of all services."""
        logger.info("Service Status:")
        logger.info("=" * 50)
        
        for service_name, config in self.services.items():
            status = "✓ Running" if self.check_service_health(service_name) else "✗ Not Running"
            logger.info(f"{config['description']:<25} {status:<12} Port {config['port']}")
    
    def run_demo(self):
        """Run a demo scenario."""
        logger.info("Running demo scenario...")
        
        try:
            import httpx
            import asyncio
            
            async def demo():
                # Demo conversation context
                context = {
                    "user_info": {
                        "user_id": "demo_student",
                        "name": "Demo Student",
                        "grade_level": "10",
                        "learning_style_summary": "Visual learner, prefers examples",
                        "emotional_state_summary": "Focused and motivated",
                        "mastery_level_summary": "Level 6 - Good understanding"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I need help with calculus"},
                        {"role": "assistant", "content": "I'd be happy to help with calculus!"}
                    ],
                    "current_message": "Can you create flashcards for derivatives?",
                    "teaching_style": "visual",
                    "emotional_state": "focused",
                    "mastery_level": 6
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    logger.info("Sending demo request to orchestrator...")
                    response = await client.post(
                        "http://localhost:8000/orchestrate",
                        json=context
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info("Demo successful!")
                        logger.info(f"Intent: {result.get('educational_intent', {}).get('intent_type', 'unknown')}")
                        logger.info(f"Tool: {result.get('educational_intent', {}).get('suggested_tool', 'unknown')}")
                        logger.info(f"Success: {result.get('success', False)}")
                    else:
                        logger.error(f"Demo failed with status {response.status_code}")
                        logger.error(response.text)
            
            asyncio.run(demo())
            
        except ImportError:
            logger.error("httpx not available for demo. Install with: pip install httpx")
        except Exception as e:
            logger.error(f"Demo failed: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    service_manager.stop_all_services()
    sys.exit(0)

def main():
    """Main function."""
    global service_manager
    service_manager = ServiceManager()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if service_manager.start_all_services():
                service_manager.wait_for_services()
                service_manager.show_status()
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Shutting down...")
                    service_manager.stop_all_services()
        
        elif command == "status":
            service_manager.show_status()
        
        elif command == "demo":
            service_manager.show_status()
            service_manager.run_demo()
        
        elif command == "stop":
            service_manager.stop_all_services()
        
        else:
            print("Usage: python start_services.py [start|status|demo|stop]")
    
    else:
        print("AI Tutor Orchestrator Service Manager")
        print("====================================")
        print("Usage: python start_services.py [command]")
        print("")
        print("Commands:")
        print("  start  - Start all services")
        print("  status - Show service status")
        print("  demo   - Run demo scenario")
        print("  stop   - Stop all services")
        print("")
        print("Services:")
        for service_name, config in service_manager.services.items():
            print(f"  {service_name:<20} - {config['description']} (Port {config['port']})")

if __name__ == "__main__":
    main()
