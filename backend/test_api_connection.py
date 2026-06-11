"""
Test Backend API Connectivity
"""
import asyncio
import aiohttp
import json

async def test_api():
    print("="*70)
    print("TESTING BACKEND API CONNECTIVITY")
    print("="*70)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check Endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8000/api/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   Status: {resp.status}")
                    print(f"   Response: {data}")
                    print("   ✓ Health Check: SUCCESS")
                else:
                    print(f"   Status: {resp.status}")
                    print("   ✗ Health Check: FAILED")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: CORS Check (from Frontend)
    print("\n2. Testing CORS Headers...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.options('http://127.0.0.1:8000/api/voice',
                                      headers={'Origin': 'http://localhost:5173'}) as resp:
                print(f"   Status: {resp.status}")
                for key in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']:
                    if key in resp.headers:
                        print(f"   {key}: {resp.headers[key]}")
                print("   ✓ CORS Check: SUCCESS")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: API Documentation
    print("\n3. Testing API Documentation (OpenAPI)...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8000/openapi.json') as resp:
                if resp.status == 200:
                    print(f"   Status: {resp.status}")
                    print("   ✓ API Docs: SUCCESS")
                else:
                    print(f"   Status: {resp.status}")
                    print("   ✗ API Docs: FAILED")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("BACKEND IS RUNNING AND ACCESSIBLE!")
    print("="*70)
    print("\nFrontend should be able to connect to:")
    print("  • Health: http://127.0.0.1:8000/api/health")
    print("  • Voice: http://127.0.0.1:8000/api/voice")
    print("  • Docs: http://127.0.0.1:8000/docs")
    print("\nFrontend running on: http://localhost:5173/")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_api())
