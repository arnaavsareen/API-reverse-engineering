"""Test script to verify backend functionality."""

import json
import sys
import os

# Add backend to path
sys.path.append('backend')

from har_parser import parse_har_file, filter_api_requests, create_request_summary
from curl_generator import generate_curl_command


def test_har_parsing():
    """Test HAR file parsing with example files."""
    print("Testing HAR parsing...")
    
    # Test with recipescal HAR file
    with open('Examples/recipescal.com.har', 'r') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    print(f"   Found {len(entries)} total entries")
    
    # Filter API requests
    api_requests = filter_api_requests(entries)
    print(f"   Filtered to {len(api_requests)} API requests")
    
    # Create summaries
    summaries = [create_request_summary(req) for req in api_requests]
    print(f"   Created {len(summaries)} request summaries")
    
    # Show first few summaries
    print("\n   First 3 API requests:")
    for i, summary in enumerate(summaries[:3]):
        print(f"   [{i}] {summary['method']} {summary['url']}")
        print(f"       Content-Type: {summary['content_type']}")
        if summary['response_preview']:
            preview = summary['response_preview'][:100]
            print(f"       Preview: {preview}...")
        print()
    
    return api_requests, summaries


def test_curl_generation(api_requests):
    """Test cURL command generation."""
    print("Testing cURL generation...")
    
    if not api_requests:
        print("   No API requests to test")
        return
    
    # Generate cURL for first API request
    first_request = api_requests[0]
    curl_command = generate_curl_command(first_request)
    
    print(f"   Generated cURL command:")
    print(f"   {curl_command[:200]}...")
    print()


def main():
    """Run all tests."""
    print("Testing API Reverse Engineering Backend")
    print("=" * 50)
    
    try:
        # Test HAR parsing
        api_requests, summaries = test_har_parsing()
        
        # Test cURL generation
        test_curl_generation(api_requests)
        
        print("All tests passed!")
        print("\nNext steps:")
        print("   1. Set OPENAI_API_KEY in backend/.env")
        print("   2. Run: cd backend && python main.py")
        print("   3. Run: cd frontend && npm run dev")
        print("   4. Open http://localhost:3000")
        
    except Exception as e:
        print(f"Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
