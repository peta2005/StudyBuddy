"""Full end-to-end test: login -> upload PDF -> ask question."""
import requests

SUPABASE_URL = 'https://awqsmukaidmtxdcheemh.supabase.co'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3cXNtdWthaWRtdHhkY2hlZW1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODY0MzMsImV4cCI6MjA5NjQ2MjQzM30.qRMaeeMpwVWVT8MX-j6U_0cpBR2KTLiotih3pBe0Xds'
BACKEND = 'http://localhost:5000'

# Step 1: Login
print("=== Step 1: Login ===")
resp = requests.post(
    f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
    headers={'apikey': ANON_KEY, 'Content-Type': 'application/json'},
    json={'email': 'p.mashubb2005@gmail.com', 'password': 'p.mashubb'}
)
print("Status:", resp.status_code)
if resp.status_code != 200:
    print("FAILED:", resp.text)
    exit(1)
token = resp.json()['access_token']
print("Token OK:", token[:50], "...")
headers_auth = {'Authorization': f'Bearer {token}'}

# Step 2: Upload
print()
print("=== Step 2: Upload PDF ===")
with open('test_upload.pdf', 'rb') as f:
    up = requests.post(
        f'{BACKEND}/upload',
        headers=headers_auth,
        files={'pdf': ('test_upload.pdf', f, 'application/pdf')}
    )
print("Status:", up.status_code)
print("Response:", up.json())

if up.status_code != 200:
    print("UPLOAD FAILED - stopping here.")
    exit(1)

# Step 3: Ask question
print()
print("=== Step 3: Ask Question ===")
ask = requests.post(
    f'{BACKEND}/ask',
    headers={**headers_auth, 'Content-Type': 'application/json'},
    json={'query': 'Who created Python and when?'}
)
print("Status:", ask.status_code)
data = ask.json()
print("Answer:", data.get('answer', 'N/A'))
print("Sources:", data.get('sources', []))
print()
print("=== ALL TESTS PASSED! ===")
