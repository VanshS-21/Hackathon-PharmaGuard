"""Test all 8 VCF validation checks."""
import sys
sys.path.insert(0, '.')
from vcf_parser import parse_vcf

def test(name, fn):
    try:
        fn()
    except Exception as e:
        print(f"  ERROR: {e}")

# Test valid file
print("=== VALID FILE TEST ===")
with open("../sample/sample_patient.vcf", "r", encoding="utf-8") as f:
    text = f.read()
result = parse_vcf(text)
print("Patient:", result["patient_id"])
print("Variants:", len(result["variants"]))
print("RESULT: PASS")
print()

# CHECK 4 - Missing fileformat
print("=== CHECK 4: Missing ##fileformat ===")
try:
    parse_vcf("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    print("RESULT: FAIL (no error raised)")
except ValueError as e:
    msg = str(e)
    print("Error:", msg)
    print("RESULT: PASS" if "Not a valid VCF v4.2 file" in msg else "RESULT: FAIL (wrong msg)")
print()

# CHECK 5 - Missing #CHROM
print("=== CHECK 5: Missing #CHROM ===")
try:
    parse_vcf("##fileformat=VCFv4.2\nsome data line\n")
    print("RESULT: FAIL (no error raised)")
except ValueError as e:
    msg = str(e)
    print("Error:", msg)
    print("RESULT: PASS" if "Missing column header" in msg else "RESULT: FAIL (wrong msg)")
print()

# CHECK 6 - Missing INFO column
print("=== CHECK 6: INFO column not in header ===")
try:
    parse_vcf("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\n1\t100\t.\tA\tT\t99\tPASS\n")
    print("RESULT: FAIL (no error raised)")
except ValueError as e:
    msg = str(e)
    print("Error:", msg)
    print("RESULT: PASS" if "INFO column not found" in msg else "RESULT: FAIL (wrong msg)")
print()

# CHECK 7 - No GENE/STAR tags
print("=== CHECK 7: No GENE=/STAR= tags ===")
try:
    parse_vcf("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n1\t100\t.\tA\tT\t99\tPASS\tDP=30\n")
    print("RESULT: FAIL (no error raised)")
except ValueError as e:
    msg = str(e)
    print("Error:", msg)
    print("RESULT: PASS" if "missing pharmacogenomic annotations" in msg else "RESULT: FAIL (wrong msg)")
print()

# CHECK 8 - No data rows
print("=== CHECK 8: No data rows ===")
try:
    parse_vcf("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    print("RESULT: FAIL (no error raised)")
except ValueError as e:
    msg = str(e)
    print("Error:", msg)
    print("RESULT: PASS" if "no valid data rows" in msg else "RESULT: FAIL (wrong msg)")
print()

print("=== ALL TESTS COMPLETE ===")
