"""
Direct backend API test for test_data/sample.vcf + CODEINE
Bypasses the frontend to confirm what the backend returns.
"""
import urllib.request
import json

VCF_PATH = r"d:\hackathon-pharmaguard\test_data\sample.vcf"
API_URL = "http://localhost:8000/api/analyze"

print(f"Testing backend API directly with: {VCF_PATH}")
print(f"Drug: CODEINE\n")

# Build multipart form data manually
boundary = "----PharmaGuardBoundary7834561"

with open(VCF_PATH, "rb") as f:
    vcf_bytes = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="vcf_file"; filename="sample.vcf"\r\n'
    f"Content-Type: text/plain\r\n\r\n"
).encode() + vcf_bytes + (
    f"\r\n--{boundary}\r\n"
    f'Content-Disposition: form-data; name="drugs"\r\n\r\n'
    f"CODEINE\r\n"
    f"--{boundary}--\r\n"
).encode()

req = urllib.request.Request(
    API_URL,
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

import time
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        elapsed = time.time() - start
        data = json.loads(resp.read())
        print(f"✅ HTTP {resp.status} in {elapsed:.1f}s")
        for result in data.get("results", []):
            print(f"\nDrug: {result['drug']}")
            print(f"  Risk label:  {result['risk_assessment']['risk_label']}")
            print(f"  Primary gene:{result['pharmacogenomic_profile']['primary_gene']}")
            print(f"  Phenotype:   {result['pharmacogenomic_profile']['phenotype']}")
            print(f"  Diplotype:   {result['pharmacogenomic_profile']['diplotype']}")
            llm = result.get("llm_generated_explanation", {})
            print(f"  LLM summary: {llm.get('summary', 'N/A')[:80]}...")
except urllib.error.HTTPError as e:
    elapsed = time.time() - start
    body_text = e.read().decode()
    print(f"FAIL: HTTP {e.code} in {elapsed:.1f}s")
    print(f"   Error: {body_text}")
except Exception as e:
    elapsed = time.time() - start
    print(f"FAIL: Exception after {elapsed:.1f}s: {e}")
