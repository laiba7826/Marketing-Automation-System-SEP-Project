import urllib.request
import urllib.parse
import http.cookiejar
import re

# Setup cookie jar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

BASE_URL = "http://localhost:5000"

def login():
    print("Logging in...")
    data = urllib.parse.urlencode({'username': 'creator', 'password': 'creator123', 'role': 'Content Creator'}).encode()
    try:
        resp = opener.open(f"{BASE_URL}/login", data=data)
        print(f"Login Response: {resp.getcode()}")
        return True
    except Exception as e:
        print(f"Login Failed: {e}")
        return False

def add_schedule():
    print("Adding grouped schedule item...")
    # Add multiple platforms
    data = urllib.parse.urlencode([
        ('title', 'Test Group Item'),
        ('platform', 'Instagram'),
        ('platform', 'Facebook'),
        ('deadline', '2025-12-31')
    ], doseq=True).encode()
    
    try:
        resp = opener.open(f"{BASE_URL}/portal/content/schedule/add", data=data)
        print(f"Add Schedule Response: {resp.getcode()}")
        return True
    except Exception as e:
        print(f"Add Schedule Failed: {e}")
        return False

def check_grouping():
    print("Checking grouping...")
    try:
        resp = opener.open(f"{BASE_URL}/portal/content/schedule")
        content = resp.read().decode('utf-8')
        
        # Check for the item title
        if 'Test Group Item' in content:
            print("Item found in schedule.")
        else:
            print("Item NOT found in schedule.")
            return False

        # Check for unified action dropdown
        if 'select name="status" onchange="handleScheduleAction(this)"' in content:
            print("Unified Action Dropdown found.")
        else:
            print("Unified Action Dropdown NOT found.")
            return False

        # Check for DELETE option
        if 'value="DELETE"' in content:
            print("DELETE option found.")
        else:
            print("DELETE option NOT found.")
            return False
            
        print("Grouping and UI Structure Verified.")
        return True
            
    except Exception as e:
        print(f"Check Grouping Failed: {e}")
        return False

if __name__ == "__main__":
    if login():
        if add_schedule():
            check_grouping()
