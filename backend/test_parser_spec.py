"""Strict VCF Parser Tests — verifies reject-on-any-error behavior."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vcf_parser import parse_vcf

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
    status = "PASS" if condition else "FAIL"
    extra = " -- %s" % detail if detail else ""
    print("  [%s] %s%s" % (status, name, extra))

def expect_reject(name, vcf_text, expected_msg=""):
    """Expect parse_vcf to raise ValueError."""
    global PASS, FAIL
    try:
        parse_vcf(vcf_text)
        FAIL += 1
        print("  [FAIL] %s -- no error raised (should have been rejected)" % name)
    except ValueError as e:
        msg = str(e)
        if expected_msg and expected_msg not in msg:
            FAIL += 1
            print("  [FAIL] %s -- wrong message: %s" % (name, msg))
        else:
            PASS += 1
            print("  [PASS] %s -- rejected: %s" % (name, msg))

def expect_pass(name, vcf_text):
    """Expect parse_vcf to succeed."""
    global PASS, FAIL
    try:
        result = parse_vcf(vcf_text)
        PASS += 1
        print("  [PASS] %s -- parsed %d variants" % (name, len(result["variants"])))
        return result
    except Exception as e:
        FAIL += 1
        print("  [FAIL] %s -- unexpected error: %s" % (name, e))
        return None

# A valid minimal VCF for reference
VALID_VCF = (
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1\n"
    "22\t42524947\trs3892097\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4;RS=rs3892097\tGT\t0/1\n"
)

print("=" * 60)
print("SECTION A: FILE-LEVEL VALIDATION CHECKS")
print("=" * 60)

print("\n--- CHECK 3: ##fileformat=VCFv4.2 ---")
expect_reject("Empty string", "", "Not a valid VCF v4.2 file")
expect_reject("Wrong version", "##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS\n", "Not a valid VCF v4.2 file")
expect_reject("Garbage content", "random garbage\n", "Not a valid VCF v4.2 file")

print("\n--- CHECK 4: #CHROM header ---")
expect_reject("Missing #CHROM", "##fileformat=VCFv4.2\nsome data\n", "Missing column header")

print("\n--- CHECK 5: Missing PGx annotations ---")
expect_reject("No GENE=/STAR= tags",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "1\t100\t.\tA\tT\t99\tPASS\tDP=30\tGT\t0/1\n",
    "missing GENE= tag")

print("\n--- CHECK 6: No data rows ---")
expect_reject("Header only, no data",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n",
    "no valid data rows")

print("\n--- CHECK: Missing FORMAT/sample columns ---")
expect_reject("Header with only 8 columns",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
    "22\t100\t.\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4\n",
    "Missing FORMAT or sample columns")

print("\n" + "=" * 60)
print("SECTION B: STRICT PER-ROW VALIDATION (reject entire file)")
print("=" * 60)

print("\n--- INFO = '.' ---")
expect_reject("Row with INFO='.'",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4\tGT\t0/1\n"
    "7\t200\trs222\tC\tT\t99\tPASS\t.\tGT\t0/1\n",
    "INFO column is empty or '.'")

print("\n--- Missing GENE= tag ---")
expect_reject("Row without GENE=",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tSTAR=*4;RS=rs111\tGT\t0/1\n",
    "missing GENE= tag")

print("\n--- Missing STAR= tag ---")
expect_reject("Row without STAR=",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=CYP2D6;RS=rs111\tGT\t0/1\n",
    "missing STAR= tag")

print("\n--- Empty GENE= value ---")
expect_reject("GENE= with empty value",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=;STAR=*4\tGT\t0/1\n",
    "GENE= tag has empty value")

print("\n--- Lowercase INFO keys (gene= instead of GENE=) ---")
expect_reject("Lowercase 'gene=' key",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tgene=CYP2D6;star=*4\tGT\t0/1\n",
    "missing GENE= tag")

print("\n--- Unrecognized gene ---")
expect_reject("Unknown gene name",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=XYZ123;STAR=*1\tGT\t0/1\n",
    "unrecognized gene")

print("\n--- REF allele = '.' ---")
expect_reject("Missing REF allele",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\t.\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4\tGT\t0/1\n",
    "REF allele is '.'")

print("\n--- >2 variants for same gene ---")
expect_reject("3 CYP2D6 variants",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4\tGT\t0/1\n"
    "22\t200\trs222\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*2\tGT\t0/1\n"
    "22\t300\trs333\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*3\tGT\t0/1\n",
    "Maximum 2 variants per gene")

print("\n--- Row with < 10 columns ---")
expect_reject("Short row in data",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4\n",
    "expected at least 10")

print("\n" + "=" * 60)
print("SECTION C: VALID FILES THAT MUST PASS")
print("=" * 60)

print("\n--- Minimal valid VCF ---")
expect_pass("Minimal valid VCF", VALID_VCF)

print("\n--- Valid 2-variant VCF ---")
expect_pass("Two variants, same gene",
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    "22\t100\trs111\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*4;RS=rs111\tGT\t0/1\n"
    "22\t200\trs222\tG\tA\t99\tPASS\tGENE=CYP2D6;STAR=*2;RS=rs222\tGT\t0/0\n")

print("\n--- sample_patient.vcf ---")
sample_path = os.path.join(os.path.dirname(__file__), "..", "sample", "sample_patient.vcf")
if os.path.exists(sample_path):
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()
    r = expect_pass("sample_patient.vcf", text)
    if r:
        check("Patient ID", r["patient_id"] == "PATIENT_001", r["patient_id"])
        check("9 variants", len(r["variants"]) == 9, "%d variants" % len(r["variants"]))
        check("6 genes", len(r["gene_diplotypes"]) == 6, "%d genes" % len(r["gene_diplotypes"]))

print("\n" + "=" * 60)
print("SECTION D: sample2.vcf MUST BE REJECTED")
print("=" * 60)

sample2_path = os.path.join(os.path.dirname(__file__), "..", "sample", "sample2.vcf")
if os.path.exists(sample2_path):
    with open(sample2_path, "r", encoding="utf-8") as f:
        text2 = f.read()
    expect_reject("sample2.vcf rejected entirely", text2)

print("\n" + "=" * 60)
total = PASS + FAIL
print("RESULTS: %d/%d PASSED, %d/%d FAILED" % (PASS, total, FAIL, total))
if FAIL == 0:
    print("ALL TESTS PASSED")
else:
    print("%d TEST(S) FAILED" % FAIL)
print("=" * 60)
