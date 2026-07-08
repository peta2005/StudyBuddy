import requests, time, jwt
from jwt.algorithms import ECAlgorithm
from dotenv import load_dotenv
import os

load_dotenv(".env")

SUPABASE_URL = 'https://awqsmukaidmtxdcheemh.supabase.co'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3cXNtdWthaWRtdHhkY2hlZW1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODY0MzMsImV4cCI6MjA5NjQ2MjQzM30.qRMaeeMpwVWVT8MX-j6U_0cpBR2KTLiotih3pBe0Xds'

# Login
print("Logging in...")
resp = requests.post(
    f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
    headers={'apikey': ANON_KEY, 'Content-Type': 'application/json'},
    json={'email': 'p.mashubb2005@gmail.com', 'password': 'p.mashubb'}
)
print("Login status:", resp.status_code)
if resp.status_code != 200:
    print("Login failed:", resp.text)
    exit(1)
token = resp.json()['access_token']

# Decode without verification
header = jwt.get_unverified_header(token)
claims = jwt.decode(token, options={"verify_signature": False})

local_now = int(time.time())
token_iat = claims['iat']
token_exp = claims['exp']

print()
print("=== Clock Analysis ===")
print("Local time (unix):", local_now)
print("Token iat  (unix):", token_iat)
print("Token exp  (unix):", token_exp)
skew = token_iat - local_now
print()
print(f"Clock skew: {skew} seconds")
if skew > 0:
    print(f"  => Your clock is {skew}s BEHIND Supabase")
    print(f"  => Token iat is in the FUTURE relative to your clock")
    if skew <= 60:
        print(f"  => leeway=60 should be ENOUGH to cover this")
    else:
        print(f"  => leeway=60 is NOT ENOUGH, need at least leeway={skew + 5}")
else:
    print(f"  => Clock is fine (ahead by {abs(skew)}s)")

print()
print("=== Token Header ===")
print("alg:", header.get('alg'))
print("kid:", header.get('kid'))

# Now try to actually verify it the same way auth_utils does
print()
print("=== Trying JWKS Verification ===")
jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
jwks_resp = requests.get(jwks_url, timeout=10)
print("JWKS status:", jwks_resp.status_code)
keys = jwks_resp.json().get("keys", [])
print("Keys available:", [k.get("kid") for k in keys])

token_kid = header.get("kid", "default")
key_entry = None
for k in keys:
    if k.get("kid") == token_kid:
        key_entry = k
        break

if not key_entry:
    print("ERROR: kid not found in JWKS!")
    exit(1)

pub_key = ECAlgorithm.from_jwk(key_entry)

# Try with leeway=60
print()
print("Trying decode with leeway=60 ...")
try:
    payload = jwt.decode(
        token, pub_key,
        algorithms=["ES256"],
        audience="authenticated",
        options={"require": ["exp", "sub"]},
        leeway=60
    )
    print("SUCCESS! Token decoded OK")
    print("sub:", payload.get("sub"))
    print("email:", payload.get("email"))
except Exception as e:
    print("FAILED with leeway=60:", type(e).__name__, str(e))

# Try with leeway=300
print()
print("Trying decode with leeway=300 ...")
try:
    payload = jwt.decode(
        token, pub_key,
        algorithms=["ES256"],
        audience="authenticated",
        options={"require": ["exp", "sub"]},
        leeway=300
    )
    print("SUCCESS! Token decoded OK with leeway=300")
except Exception as e:
    print("FAILED with leeway=300:", type(e).__name__, str(e))

# Try with no leeway restrictions at all
print()
print("Trying decode with no iat validation ...")
try:
    payload = jwt.decode(
        token, pub_key,
        algorithms=["ES256"],
        audience="authenticated",
        options={"require": ["exp", "sub"], "verify_iat": False},
        leeway=0
    )
    print("SUCCESS! Token decoded OK without iat validation")
except Exception as e:
    print("FAILED without iat validation:", type(e).__name__, str(e))
