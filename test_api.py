import requests
import json
import time

# Wait for server to start
time.sleep(1)

print("=" * 50)
print("Testing API Endpoints")
print("=" * 50)

# Test gestures endpoint
print("\n1. GET /api/gestures:")
try:
    response = requests.get('http://localhost:5000/api/gestures?per_page=2')
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        for gesture in data['data']:
            print(f"   - {gesture['name']}: {gesture['image']}")
    else:
        print(f"   Error: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test image endpoint
print("\n2. GET /api/images/a:")
try:
    response = requests.get('http://localhost:5000/api/images/a')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Size: {len(response.content)} bytes")
except Exception as e:
    print(f"   Error: {e}")

# Test a few more letters
print("\n3. Testing multiple letters:")
for letter in ['b', 'z']:
    try:
        response = requests.get(f'http://localhost:5000/api/images/{letter}')
        print(f"   /{letter}: {response.status_code} ({len(response.content)} bytes)")
    except Exception as e:
        print(f"   /{letter}: Error - {e}")

print("\n✓ API tests complete")
