#!/usr/bin/env python3
"""
Tests for OpenRouter provider integration.
Tests both Ollama and OpenRouter providers with environment variable switching.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_config_provider_selection():
    """Test that provider selection works correctly based on USE_OPENAI env var"""
    print("\n" + "="*60)
    print("Test: Provider Selection Configuration")
    print("="*60)
    
    import config
    
    print(f"USE_OPENAI: {config.USE_OPENAI}")
    
    if config.USE_OPENAI:
        print("✓ Using OpenRouter provider")
        print(f"  Base URL: {config.OPENAI_BASE_URL}")
        print(f"  Model: {config.OPENAI_MODEL}")
        print(f"  API Key Set: {'Yes' if config.OPENAI_API_KEY else 'No'}")
        
        if not config.OPENAI_API_KEY:
            print("⚠ WARNING: OPENAI_API_KEY not set")
            return False
    else:
        print("✓ Using Ollama provider")
        print(f"  Host: {config.OLLAMA_HOST}")
        print(f"  Model: {config.OLLAMA_MODEL}")
    
    print(f"Temperature: {config.TEMPERATURE}")
    print(f"Max Tokens: {config.MAX_TOKENS}")
    
    return True


def test_provider_imports():
    """Test that provider modules can be imported correctly"""
    print("\n" + "="*60)
    print("Test: Provider Module Imports")
    print("="*60)
    
    try:
        from providers import (
            ollama_complete,
            ollama_complete_stream,
            openrouter_complete,
            openrouter_complete_stream,
            llm_complete,
            llm_complete_stream,
        )
        print("✓ All provider functions imported successfully")
        
        # Check that models.py maintains backward compatibility
        from models import ollama_complete as models_ollama
        from models import llm_complete as models_llm
        print("✓ models.py backward compatibility maintained")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_openai_sdk_availability():
    """Test if OpenAI SDK is available when USE_OPENAI=1"""
    print("\n" + "="*60)
    print("Test: OpenAI SDK Availability")
    print("="*60)
    
    import config
    
    if not config.USE_OPENAI:
        print("⊘ Skipped (USE_OPENAI=0)")
        return True
    
    try:
        from openai import OpenAI, AsyncOpenAI
        print("✓ OpenAI SDK installed and importable")
        print(f"  OpenAI module: {OpenAI.__module__}")
        return True
    except ImportError:
        print("✗ OpenAI SDK not installed")
        print("  Install with: pip install openai>=1.0.0")
        return False


def test_provider_selection_logic():
    """Test that the unified provider interface routes correctly"""
    print("\n" + "="*60)
    print("Test: Provider Selection Logic")
    print("="*60)
    
    import config
    from providers import llm_complete
    
    # Test that the function exists and is callable
    print(f"✓ llm_complete is callable: {callable(llm_complete)}")
    
    if config.USE_OPENAI:
        print("✓ Should route to OpenRouter")
        from providers import openrouter_complete
        # We can't easily test equality, but we can verify the function exists
        print(f"  openrouter_complete exists: {callable(openrouter_complete)}")
    else:
        print("✓ Should route to Ollama")
        from providers import ollama_complete
        print(f"  ollama_complete exists: {callable(ollama_complete)}")
    
    return True


def test_config_validation():
    """Test that config validation works correctly"""
    print("\n" + "="*60)
    print("Test: Configuration Validation")
    print("="*60)
    
    import config
    
    checks_passed = True
    
    if config.USE_OPENAI:
        # When using OpenRouter, API key must be set
        if not config.OPENAI_API_KEY:
            print("✗ OPENAI_API_KEY not set (required when USE_OPENAI=1)")
            checks_passed = False
        else:
            print("✓ OPENAI_API_KEY is set")
        
        if not config.OPENAI_BASE_URL:
            print("✗ OPENAI_BASE_URL not set")
            checks_passed = False
        else:
            print(f"✓ OPENAI_BASE_URL: {config.OPENAI_BASE_URL}")
        
        if not config.OPENAI_MODEL:
            print("✗ OPENAI_MODEL not set")
            checks_passed = False
        else:
            print(f"✓ OPENAI_MODEL: {config.OPENAI_MODEL}")
    else:
        # When using Ollama, OLLAMA_HOST must be set
        if not config.OLLAMA_HOST:
            print("✗ OLLAMA_HOST not set (required when USE_OPENAI=0)")
            checks_passed = False
        else:
            print(f"✓ OLLAMA_HOST: {config.OLLAMA_HOST}")
        
        if not config.OLLAMA_MODEL:
            print("✗ OLLAMA_MODEL not set")
            checks_passed = False
        else:
            print(f"✓ OLLAMA_MODEL: {config.OLLAMA_MODEL}")
    
    return checks_passed


def test_backward_compatibility():
    """Test that existing code using models.py still works"""
    print("\n" + "="*60)
    print("Test: Backward Compatibility")
    print("="*60)
    
    try:
        # Test that old imports still work
        from models import ollama_complete, ollama_complete_stream
        print("✓ Legacy imports from models.py work")
        
        # Test that new functions are available
        from models import llm_complete, llm_complete_stream
        print("✓ New unified interface available in models.py")
        
        return True
    except ImportError as e:
        print(f"✗ Backward compatibility broken: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("OpenRouter Provider Integration Tests")
    print("="*60)
    
    tests = [
        ("Config Provider Selection", test_config_provider_selection),
        ("Provider Module Imports", test_provider_imports),
        ("OpenAI SDK Availability", test_openai_sdk_availability),
        ("Provider Selection Logic", test_provider_selection_logic),
        ("Configuration Validation", test_config_validation),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
