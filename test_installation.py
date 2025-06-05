#!/usr/bin/env python3
"""
Installation Test Script for PhysioSOAP MVP

This script tests that all required dependencies are installed and importable.
Run this after installation to verify everything is working correctly.
"""

import sys
from datetime import date
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    
    print("🔍 Testing package imports...")
    
    # Core Python packages
    try:
        import asyncio
        import json
        import pathlib
        print("✓ Core Python packages")
    except ImportError as e:
        print(f"✗ Core Python packages: {e}")
        return False
    
    # Pydantic and settings
    try:
        from pydantic import BaseModel, Field
        from pydantic_settings import BaseSettings
        print("✓ Pydantic packages")
    except ImportError as e:
        print(f"✗ Pydantic packages: {e}")
        return False
    
    # OpenAI
    try:
        import openai
        print("✓ OpenAI package")
    except ImportError as e:
        print(f"✗ OpenAI package: {e}")
        return False
    
    # Jinja2
    try:
        from jinja2 import Environment, Template
        print("✓ Jinja2 package")
    except ImportError as e:
        print(f"✗ Jinja2 package: {e}")
        return False
    
    # WeasyPrint
    try:
        import weasyprint
        print("✓ WeasyPrint package")
    except ImportError as e:
        print(f"✗ WeasyPrint package: {e}")
        return False
    
    # Structlog
    try:
        import structlog
        print("✓ Structlog package")
    except ImportError as e:
        print(f"✗ Structlog package: {e}")
        return False
    
    # Rich
    try:
        from rich.console import Console
        from rich.panel import Panel
        print("✓ Rich package")
    except ImportError as e:
        print(f"✗ Rich package: {e}")
        return False
    
    # Tenacity
    try:
        from tenacity import retry
        print("✓ Tenacity package")
    except ImportError as e:
        print(f"✗ Tenacity package: {e}")
        return False
    
    # MCP packages
    try:
        from mcp.server import Server
        from mcp.types import Tool
        print("✓ MCP packages")
    except ImportError as e:
        print(f"✗ MCP packages: {e}")
        return False
    
    return True


def test_models():
    """Test that the SOAP model works correctly."""
    
    print("\n🧪 Testing SOAP model...")
    
    try:
        from models.soap import SoapModel
        
        # Create a test SOAP model
        test_soap = SoapModel(
            patient_name="Test Patient",
            session_date=date.today(),
            subjective="Patient reports mild lower back discomfort following yesterday's gardening activities.",
            objective="ROM: Lumbar flexion 80% of normal. No acute distress observed. Gait pattern normal.",
            assessment="Mild mechanical lower back pain, likely muscular in origin. Good functional capacity.",
            plan="Home exercise program focusing on lumbar mobility and core strengthening. Follow-up in 1 week.",
            session_duration=45,
            chief_complaint="Lower back discomfort"
        )
        
        # Test JSON serialization
        json_output = test_soap.model_dump_json()
        
        # Test validation
        validated = SoapModel.model_validate(test_soap.model_dump())
        
        print("✓ SOAP model creation and validation")
        return True
        
    except Exception as e:
        print(f"✗ SOAP model test failed: {e}")
        return False


def test_configuration():
    """Test that configuration loading works."""
    
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import settings
        print("✓ Configuration loading")
        
        # Check that required directories will be created
        print(f"  PDF output directory: {settings.pdf_output_dir}")
        print(f"  Audio input directory: {settings.audio_input_dir}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_logging():
    """Test that logging configuration works."""
    
    print("\n📝 Testing logging...")
    
    try:
        from app_logging import get_logger
        
        logger = get_logger("test")
        logger.info("Test log message")
        print("✓ Logging configuration")
        return True
        
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False


def test_directories():
    """Test that required directories exist or can be created."""
    
    print("\n📁 Testing directories...")
    
    try:
        # Check for required directories
        required_dirs = [
            Path("./audio"),
            Path("./output"),
            Path("./templates"),
            Path("./models"),
            Path("./clients"),
            Path("./servers")
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"✓ {dir_path} exists")
            else:
                print(f"✗ {dir_path} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Directory test failed: {e}")
        return False


def main():
    """Run all tests."""
    
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]PhysioSOAP MVP - Installation Test[/bold blue]\n"
        "Testing all dependencies and configurations",
        style="blue"
    ))
    
    tests = [
        ("Package Imports", test_imports),
        ("SOAP Models", test_models),
        ("Configuration", test_configuration),
        ("Logging", test_logging),
        ("Directories", test_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        console.print("\n[bold green]🎉 All tests passed! Installation looks good.[/bold green]")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Copy env.template to .env and configure your OpenAI API key")
        console.print("2. Place audio files in the ./audio directory")
        console.print("3. Run: python workflow.py ./audio/your_session.mp3")
        return 0
    else:
        console.print(f"\n[bold red]❌ {total - passed} tests failed. Please check the installation.[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 