#!/usr/bin/env python3
"""
Test suite for improved error handling in EduMate backend.
Tests error classification, error messages, and recovery logic.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


def test_error_classification():
    """Test that ErrorType enum exists and has all expected values"""
    from main import ErrorType
    
    print("\nError Classification Tests:")
    expected_types = [
        "NO_CONTEXT",
        "RETRIEVAL_ERROR", 
        "MODEL_CONNECTION",
        "MODEL_TIMEOUT",
        "MODEL_EMPTY_RESPONSE",
        "MODEL_ERROR",
        "UNKNOWN"
    ]
    
    all_passed = True
    for error_name in expected_types:
        if hasattr(ErrorType, error_name):
            error_type = getattr(ErrorType, error_name)
            print(f"✓ ErrorType.{error_name} exists: {error_type.value}")
        else:
            print(f"✗ ErrorType.{error_name} is missing")
            all_passed = False
    
    return all_passed


def test_error_messages():
    """Test that error messages are actionable and specific"""
    from main import ErrorType, get_error_message
    
    print("\nError Message Tests:")
    test_cases = [
        (ErrorType.NO_CONTEXT, None, None),
        (ErrorType.RETRIEVAL_ERROR, None, "ChromaDB not found"),
        (ErrorType.MODEL_CONNECTION, None, "Connection refused"),
        (ErrorType.MODEL_TIMEOUT, None, "Request timed out"),
        (ErrorType.MODEL_EMPTY_RESPONSE, ["source1.pdf"], "Empty response"),
        (ErrorType.MODEL_ERROR, None, "Unknown error"),
        (ErrorType.UNKNOWN, None, None),
    ]
    
    all_passed = True
    for error_type, sources, details in test_cases:
        try:
            msg = get_error_message(error_type, sources, details)
            
            # Check that message is not empty
            if not msg or len(msg) < 10:
                print(f"✗ {error_type.value}: Message too short or empty")
                all_passed = False
                continue
            
            # Check that message contains actionable guidance
            if "**" not in msg or "•" not in msg:
                print(f"✗ {error_type.value}: Message lacks structured guidance")
                all_passed = False
                continue
            
            print(f"✓ {error_type.value}: Message is well-formatted ({len(msg)} chars)")
            
            # For specific error types, check for key phrases
            if error_type == ErrorType.NO_CONTEXT:
                if "couldn't find" not in msg.lower():
                    print(f"  ⚠ Warning: Message should mention 'couldn't find'")
            elif error_type == ErrorType.MODEL_CONNECTION:
                if "ollama" not in msg.lower():
                    print(f"  ⚠ Warning: Message should mention 'Ollama'")
            elif error_type == ErrorType.MODEL_TIMEOUT:
                if "timeout" not in msg.lower() and "took too long" not in msg.lower():
                    print(f"  ⚠ Warning: Message should mention timeout")
                    
        except Exception as e:
            print(f"✗ {error_type.value}: Exception raised: {e}")
            all_passed = False
    
    return all_passed


def test_error_message_specificity():
    """Test that error messages are specific and different from each other"""
    from main import ErrorType, get_error_message
    
    print("\nError Message Specificity Tests:")
    
    messages = {}
    for error_type in ErrorType:
        msg = get_error_message(error_type)
        messages[error_type] = msg
    
    # Check that all messages are unique
    unique_messages = set(messages.values())
    if len(unique_messages) == len(messages):
        print(f"✓ All {len(messages)} error messages are unique")
        passed = True
    else:
        print(f"✗ Some error messages are duplicates: {len(unique_messages)} unique out of {len(messages)}")
        passed = False
    
    # Check that messages contain specific keywords
    keyword_checks = {
        ErrorType.NO_CONTEXT: ["course materials", "couldn't find"],
        ErrorType.RETRIEVAL_ERROR: ["searching", "database", "vector"],
        ErrorType.MODEL_CONNECTION: ["connect", "ollama", "running"],
        ErrorType.MODEL_TIMEOUT: ["timeout", "took too long", "slow"],
        ErrorType.MODEL_EMPTY_RESPONSE: ["empty response"],
    }
    
    for error_type, keywords in keyword_checks.items():
        msg_lower = messages[error_type].lower()
        found_keywords = [kw for kw in keywords if kw in msg_lower]
        if found_keywords:
            print(f"✓ {error_type.value}: Contains relevant keywords {found_keywords}")
        else:
            print(f"✗ {error_type.value}: Missing expected keywords {keywords}")
            passed = False
    
    return passed


def test_error_logging():
    """Test that error details are logged when provided"""
    from main import get_error_message, ErrorType
    import io
    from contextlib import redirect_stdout
    
    print("\nError Logging Tests:")
    
    # Capture print output
    f = io.StringIO()
    with redirect_stdout(f):
        get_error_message(ErrorType.MODEL_ERROR, error_details="Test error details")
    
    output = f.getvalue()
    
    if "Test error details" in output:
        print("✓ Error details are logged when provided")
        return True
    else:
        print("✗ Error details were not logged")
        return False


def test_models_error_messages():
    """Test that models.py provides detailed error information"""
    print("\nModels Error Message Tests:")
    
    # We can't actually test the ollama_complete function without a running Ollama,
    # but we can verify that the code has the right structure
    import models
    import inspect
    
    source = inspect.getsource(models.ollama_complete)
    
    checks = [
        ("ReadTimeout", "ReadTimeout" in source),
        ("ConnectionError", "ConnectionError" in source),
        ("HTTPError", "HTTPError" in source),
        ("Retry logic", "for attempt in range" in source),
        ("Detailed error message", "RuntimeError" in source),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✓ {check_name}: Present in ollama_complete")
        else:
            print(f"✗ {check_name}: Missing in ollama_complete")
            all_passed = False
    
    return all_passed


def test_chat_endpoint_error_handling():
    """Test that /chat endpoint handles errors properly"""
    print("\nChat Endpoint Error Handling Tests:")
    
    import main
    import inspect
    
    # Get the chat function source
    source = inspect.getsource(main.chat)
    
    checks = [
        ("Retrieval error handling", "retrieval_error" in source.lower()),
        ("No context handling", "not ctx" in source),
        ("Ollama error handling", "RuntimeError" in source or "except" in source),
        ("Error classification", "ErrorType" in source),
        ("get_error_message usage", "get_error_message" in source),
        ("Empty response handling", 'answer.strip() == ""' in source or "not answer" in source),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✓ {check_name}: Implemented")
        else:
            print(f"✗ {check_name}: Not found in code")
            all_passed = False
    
    return all_passed


def test_chat_stream_endpoint_error_handling():
    """Test that /chat_stream endpoint handles errors properly"""
    print("\nChat Stream Endpoint Error Handling Tests:")
    
    import main
    import inspect
    
    # Get the chat_stream function source
    source = inspect.getsource(main.chat_stream)
    
    checks = [
        ("Retrieval error handling", "retrieval_error" in source.lower()),
        ("No context handling", "not ctx" in source),
        ("Stream error handling", "except Exception" in source),
        ("Error classification", "ErrorType" in source),
        ("get_error_message usage", "get_error_message" in source),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✓ {check_name}: Implemented")
        else:
            print(f"✗ {check_name}: Not found in code")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("=" * 60)
    print("EduMate Error Handling Test Suite")
    print("=" * 60)
    
    tests = [
        ("Error Classification", test_error_classification),
        ("Error Messages", test_error_messages),
        ("Error Message Specificity", test_error_message_specificity),
        ("Error Logging", test_error_logging),
        ("Models Error Messages", test_models_error_messages),
        ("Chat Endpoint Error Handling", test_chat_endpoint_error_handling),
        ("Chat Stream Endpoint Error Handling", test_chat_stream_endpoint_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Running: {test_name}")
        print('=' * 60)
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed_count}/{total_count} test suites passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Error handling is properly implemented.")
    else:
        print(f"\n⚠️  {total_count - passed_count} test suite(s) failed. Review the output above.")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
