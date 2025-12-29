"""
Diagnostic script to check OpenAI API configuration
Run this to verify your OpenAI API key and connectivity
"""

import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def check_openai_config():
    """Check OpenAI API configuration and connectivity"""
    
    print("=" * 70)
    print("OpenAI API Configuration Check")
    print("=" * 70)
    print()
    
    # Check .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print("✓ .env file found")
    else:
        print("✗ .env file NOT found")
        print(f"  Expected location: {env_path}")
        print("  Create it from env.example")
        return False
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        # Mask the key for display
        masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
        print(f"✓ OPENAI_API_KEY found: {masked_key}")
    else:
        print("✗ OPENAI_API_KEY not found in environment")
        print("  Add it to your .env file: OPENAI_API_KEY=your_key_here")
        return False
    
    # Check model
    model = os.getenv('OPENAI_MODEL', 'gpt-4.1')
    print(f"✓ Model: {model}")
    
    # Check base URL
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    print(f"✓ Base URL: {base_url}")
    
    print()
    print("Testing API connectivity...")
    print()
    
    # Test API call
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Simple test request
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': 'Say "test" if you can read this.'
                }
            ],
            'max_tokens': 10
        }
        
        response = requests.post(
            f'{base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ API connection successful!")
            result = response.json()
            print(f"  Response: {result['choices'][0]['message']['content']}")
            print()
            print("Your OpenAI configuration is working correctly!")
            return True
        else:
            print(f"✗ API request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', {}).get('message', 'Unknown error')
                print(f"  Error: {error_msg}")
                
                if response.status_code == 401:
                    print()
                    print("  Possible issues:")
                    print("  - Invalid API key")
                    print("  - API key expired")
                    print("  - Wrong API key format")
                elif response.status_code == 403:
                    print()
                    print("  Possible issues:")
                    print("  - API key doesn't have access to this model")
                    print("  - Account has no credits")
                    print("  - Account restrictions")
                elif response.status_code == 429:
                    print()
                    print("  Possible issues:")
                    print("  - Rate limit exceeded")
                    print("  - Quota exceeded")
            except:
                print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ API request timed out")
        print("  Check your internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to OpenAI API")
        print("  Check your internet connection and firewall settings")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_openai_config()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)

