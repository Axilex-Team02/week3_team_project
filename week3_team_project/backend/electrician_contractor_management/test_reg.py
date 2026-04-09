import urllib.request
import urllib.parse
import urllib.error

def test_registration(username, email, password):
    url = 'http://127.0.0.1:5000/register'
    data = {
        'username': username,
        'email': email,
        'password': password,
        'phone': '1234567890',
        'role': 'admin'
    }
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded_data, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            print(f"URL: {response.geturl()}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response body: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    print("Testing registration for 'Bhoomika'...")
    test_registration('Bhoomika', 'bhoomi3109@gmail.com', 'mypassword')
