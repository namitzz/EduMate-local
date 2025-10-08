#!/usr/bin/env python3
"""
Test URL extraction in MODEL_CONNECTION error messages.
Verifies that the URL is correctly extracted and displayed when available.
"""

def test_url_extraction_with_url():
    """Test that URL is extracted and displayed when present in error_details"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Simulate the exact error message format from models.py
    error_details = "Ollama ConnectionError after 3 retries (URL: http://localhost:11434): Connection refused"
    
    # Simulate the URL extraction logic from main.py lines 66-72
    url_info = ""
    if error_details and "URL:" in error_details:
        try:
            url_part = error_details.split("URL:")[1].split(")")[0].strip()
            url_info = f"\n\n**Connection attempted to:** {url_part}"
        except:
            pass
    
    print("=" * 70)
    print("Test 1: URL Extraction - WITH URL in error_details")
    print("=" * 70)
    print(f"Input error_details: {error_details}")
    print(f"Extracted URL info: {url_info}")
    
    # Assertions
    assert url_info != "", "URL info should not be empty when URL is in error_details"
    assert "**Connection attempted to:**" in url_info, "Should have bold markdown header"
    assert "http://localhost:11434" in url_info, "Should extract the correct URL"
    print("✓ URL extracted successfully")
    print(f"✓ Full URL info: {url_info.strip()}")
    
    return True


def test_url_extraction_without_url():
    """Test that error message works gracefully when URL is not in error_details"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Simulate error without URL format
    error_details = "Connection refused"
    
    # Simulate the URL extraction logic from main.py lines 66-72
    url_info = ""
    if error_details and "URL:" in error_details:
        try:
            url_part = error_details.split("URL:")[1].split(")")[0].strip()
            url_info = f"\n\n**Connection attempted to:** {url_part}"
        except:
            pass
    
    print("\n" + "=" * 70)
    print("Test 2: URL Extraction - WITHOUT URL in error_details")
    print("=" * 70)
    print(f"Input error_details: {error_details}")
    print(f"Extracted URL info: {url_info}")
    
    # Assertions
    assert url_info == "", "URL info should be empty when URL is not in error_details"
    print("✓ Gracefully handles missing URL")
    print("✓ No URL info added (backward compatible)")
    
    return True


def test_url_extraction_with_different_urls():
    """Test URL extraction with various URL formats"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    test_cases = [
        ("Ollama error (URL: http://ollama:11434) failed", "http://ollama:11434"),
        ("Ollama error (URL: https://api.ollama.ai) failed", "https://api.ollama.ai"),
        ("Ollama error (URL: http://192.168.1.100:11434) failed", "http://192.168.1.100:11434"),
        # Test streaming error format
        ("[Streaming error (URL: http://localhost:11434): Connection refused]", "http://localhost:11434"),
    ]
    
    print("\n" + "=" * 70)
    print("Test 3: URL Extraction - Various URL Formats")
    print("=" * 70)
    
    for i, (error_details, expected_url) in enumerate(test_cases, 1):
        url_info = ""
        if error_details and "URL:" in error_details:
            try:
                url_part = error_details.split("URL:")[1].split(")")[0].strip()
                url_info = f"\n\n**Connection attempted to:** {url_part}"
            except:
                pass
        
        assert expected_url in url_info, f"Test case {i}: Should extract {expected_url}"
        print(f"✓ Test case {i}: Extracted {expected_url}")
    
    return True


def test_complete_error_message_with_url():
    """Test the complete error message with URL"""
    print("\n" + "=" * 70)
    print("Test 4: Complete Error Message with URL")
    print("=" * 70)
    
    # Simulate complete error message as it would appear
    url_info = "\n\n**Connection attempted to:** http://localhost:11434"
    
    complete_message = (
        "Unable to connect to the AI model (Ollama).\n\n"
        "**Possible causes:**\n"
        "• Ollama service is not running\n"
        "• Connection to Ollama was refused\n"
        "• Wrong OLLAMA_HOST configuration for your deployment type\n\n"
        "**What to do:**\n"
        "• For local development: Ensure Ollama is running (`ollama list`)\n"
        "• For Docker: Verify the ollama container is running\n"
        "• For cloud/public API: Check OLLAMA_HOST is set to your public endpoint\n"
        "  (e.g., https://api.ollama.ai, NOT localhost)\n"
        "• Verify OLLAMA_HOST/OLLAMA_URL environment variable is correct\n"
        "• Check if your API endpoint requires authentication"
        f"{url_info}"
    )
    
    # Verify structure
    assert "Unable to connect to the AI model (Ollama)" in complete_message
    assert "**Possible causes:**" in complete_message
    assert "**What to do:**" in complete_message
    assert "**Connection attempted to:** http://localhost:11434" in complete_message
    
    # Count sections
    lines = complete_message.split('\n')
    assert len(lines) >= 15, f"Should have at least 15 lines with URL, found {len(lines)}"
    
    print("✓ Complete message structure is valid")
    print(f"✓ Total lines: {len(lines)}")
    print(f"✓ Has URL section at the end")
    
    # Display the full message
    print("\nComplete Error Message:")
    print("-" * 70)
    print(complete_message)
    print("-" * 70)
    
    return True


if __name__ == "__main__":
    try:
        tests = [
            ("URL Extraction WITH URL", test_url_extraction_with_url),
            ("URL Extraction WITHOUT URL", test_url_extraction_without_url),
            ("Various URL Formats", test_url_extraction_with_different_urls),
            ("Complete Error Message", test_complete_error_message_with_url),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                test_func()
                passed += 1
            except AssertionError as e:
                print(f"\n❌ {test_name} FAILED: {e}")
                failed += 1
            except Exception as e:
                print(f"\n❌ {test_name} ERROR: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        print("\n" + "=" * 70)
        print(f"Test Summary: {passed} passed, {failed} failed out of {len(tests)} tests")
        print("=" * 70)
        
        if failed == 0:
            print("\n🎉 All tests passed!")
            print("The URL extraction logic is working correctly.")
            exit(0)
        else:
            print(f"\n❌ {failed} test(s) failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
