"""Test CPIC enrichment in the full /api/analyze pipeline."""
import urllib.request, json

# Build multipart form data manually
import io, mimetypes

# Read sample VCF
vcf_path = "../sample/sample_patient.vcf"
with open(vcf_path, "rb") as f:
    vcf_data = f.read()

# Build multipart body
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = b""
body += f"--{boundary}\r\n".encode()
body += b"Content-Disposition: form-data; name=\"vcf_file\"; filename=\"sample_patient.vcf\"\r\n"
body += b"Content-Type: text/plain\r\n\r\n"
body += vcf_data + b"\r\n"
body += f"--{boundary}\r\n".encode()
body += b"Content-Disposition: form-data; name=\"drugs\"\r\n\r\n"
body += b"CODEINE\r\n"
body += f"--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:8000/api/analyze",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

try:
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    result = data["results"][0]

    print("=== RISK ASSESSMENT ===")
    print(f"Drug: {result['drug']}")
    print(f"Risk: {result['risk_assessment']['risk_label']}")
    print(f"Severity: {result['risk_assessment']['severity']}")
    print(f"Gene: {result['pharmacogenomic_profile']['primary_gene']}")
    print(f"Phenotype: {result['pharmacogenomic_profile']['phenotype']}")
    print(f"Diplotype: {result['pharmacogenomic_profile']['diplotype']}")

    print("\n=== CPIC DATA ===")
    cpic = result.get("cpic_data", {})
    print(f"Data Source: {cpic.get('data_source', 'N/A')}")
    print(f"Evidence Level: {cpic.get('evidence_level', 'N/A')}")
    print(f"Guideline: {cpic.get('guideline_name', 'N/A')}")
    print(f"URL: {cpic.get('guideline_url', 'N/A')}")
    print(f"CPIC Recommendation: {cpic.get('recommendation', 'N/A')}")
    print(f"Classification: {cpic.get('classification', 'N/A')}")

    print("\nSUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
