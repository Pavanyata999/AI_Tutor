#!/usr/bin/env python3
"""
Test Runner Script
==================

This script runs the comprehensive test suite for the AI Tutor Orchestrator.
It provides different test modes and generates coverage reports.
"""

import subprocess
import sys
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRunner:
    """Test runner for the AI Tutor Orchestrator."""
    
    def __init__(self):
        self.test_dir = "tests"
        self.coverage_dir = "htmlcov"
        self.test_files = [
            "test_system.py",
            "test_context_analyzer.py", 
            "test_parameter_extractor.py",
            "test_tool_orchestrator.py",
            "test_schema_validator.py",
            "test_state_manager.py"
        ]
    
    def run_tests(self, test_file: str = None, verbose: bool = True, coverage: bool = False) -> bool:
        """Run tests with specified options."""
        cmd = ["python", "-m", "pytest"]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
        
        if test_file:
            cmd.append(os.path.join(self.test_dir, test_file))
        else:
            cmd.append(self.test_dir)
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Tests failed with return code {e.returncode}")
            return False
        except FileNotFoundError:
            logger.error("pytest not found. Install with: pip install pytest")
            return False
    
    def run_specific_test(self, test_name: str) -> bool:
        """Run a specific test by name."""
        cmd = ["python", "-m", "pytest", "-v", "-k", test_name, self.test_dir]
        
        logger.info(f"Running specific test: {test_name}")
        
        try:
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Test failed with return code {e.returncode}")
            return False
    
    def run_with_coverage(self) -> bool:
        """Run tests with coverage report."""
        logger.info("Running tests with coverage analysis...")
        
        success = self.run_tests(coverage=True)
        
        if success and os.path.exists(self.coverage_dir):
            logger.info(f"Coverage report generated in {self.coverage_dir}/index.html")
        
        return success
    
    def lint_code(self) -> bool:
        """Run code linting."""
        logger.info("Running code linting...")
        
        try:
            # Run flake8
            result = subprocess.run(["flake8", "."], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Linting errors found:")
                print(result.stdout)
                return False
            
            logger.info("Code linting passed")
            return True
            
        except FileNotFoundError:
            logger.warning("flake8 not found. Install with: pip install flake8")
            return True
    
    def type_check(self) -> bool:
        """Run type checking."""
        logger.info("Running type checking...")
        
        try:
            result = subprocess.run(["mypy", "."], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Type checking errors found:")
                print(result.stdout)
                return False
            
            logger.info("Type checking passed")
            return True
            
        except FileNotFoundError:
            logger.warning("mypy not found. Install with: pip install mypy")
            return True
    
    def format_code(self) -> bool:
        """Format code with black."""
        logger.info("Formatting code...")
        
        try:
            result = subprocess.run(["black", "."], check=True)
            logger.info("Code formatting completed")
            return True
            
        except FileNotFoundError:
            logger.warning("black not found. Install with: pip install black")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Code formatting failed with return code {e.returncode}")
            return False
    
    def run_all_checks(self) -> bool:
        """Run all quality checks."""
        logger.info("Running all quality checks...")
        
        checks = [
            ("Code Formatting", self.format_code),
            ("Code Linting", self.lint_code),
            ("Type Checking", self.type_check),
            ("Tests", lambda: self.run_tests()),
            ("Coverage", self.run_with_coverage)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            logger.info(f"Running {check_name}...")
            if not check_func():
                logger.error(f"{check_name} failed")
                all_passed = False
            else:
                logger.info(f"{check_name} passed")
        
        return all_passed
    
    def list_tests(self):
        """List available test files."""
        logger.info("Available test files:")
        for i, test_file in enumerate(self.test_files, 1):
            file_path = os.path.join(self.test_dir, test_file)
            exists = "✓" if os.path.exists(file_path) else "✗"
            logger.info(f"  {i}. {test_file} {exists}")
    
    def show_help(self):
        """Show help information."""
        print("AI Tutor Orchestrator Test Runner")
        print("=" * 40)
        print("Usage: python run_tests.py [options]")
        print("")
        print("Options:")
        print("  --all              Run all quality checks")
        print("  --tests            Run all tests")
        print("  --coverage         Run tests with coverage")
        print("  --lint             Run code linting")
        print("  --type-check       Run type checking")
        print("  --format           Format code")
        print("  --file FILE        Run specific test file")
        print("  --test NAME        Run specific test by name")
        print("  --list             List available test files")
        print("  --help             Show this help")
        print("")
        print("Examples:")
        print("  python run_tests.py --all")
        print("  python run_tests.py --coverage")
        print("  python run_tests.py --file test_context_analyzer.py")
        print("  python run_tests.py --test test_detect_intent")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Tutor Orchestrator Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all quality checks")
    parser.add_argument("--tests", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--type-check", action="store_true", help="Run type checking")
    parser.add_argument("--format", action="store_true", help="Format code")
    parser.add_argument("--file", help="Run specific test file")
    parser.add_argument("--test", help="Run specific test by name")
    parser.add_argument("--list", action="store_true", help="List available test files")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        runner.list_tests()
        return
    
    if args.all:
        success = runner.run_all_checks()
    elif args.tests:
        success = runner.run_tests()
    elif args.coverage:
        success = runner.run_with_coverage()
    elif args.lint:
        success = runner.lint_code()
    elif args.type_check:
        success = runner.type_check()
    elif args.format:
        success = runner.format_code()
    elif args.file:
        success = runner.run_tests(test_file=args.file)
    elif args.test:
        success = runner.run_specific_test(args.test)
    else:
        runner.show_help()
        return
    
    if success:
        logger.info("All operations completed successfully")
        sys.exit(0)
    else:
        logger.error("Some operations failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
