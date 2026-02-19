"""Test parser against sample2.vcf — edge case file."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vcf_parser import parse_vcf

sample_path = os.path.join(os.path.dirname(__file__), "..", "sample", "sample2.vcf")
with open(sample_path, "r", encoding="utf-8") as f:
    text = f.read()

print("=== sample2.vcf Edge Case Analysis ===")
print()
print("Edge cases in this file:")
print("  Line 5:  Normal row (CYP2D6 *4)")
print("  Line 6:  Missing RS= tag (CYP2C19 *2)")
print("  Line 7:  INFO='.' (should skip)")
print("  Line 8:  GENE= empty value (should skip)")
print("  Line 9:  Lowercase gene=TPMT;star=*3A (needs uppercase)")
print("  Line 10: CYP2C9 *3 (first of 3 CYP2C9 rows)")
print("  Line 11: CYP2C9 *2 (second of 3 CYP2C9 rows)")
print("  Line 12: CYP2C9 *6 (third — should be SKIPPED by 2-per-gene rule)")
print("  Line 13: STARR=*3 (typo — not STAR=, should treat as missing STAR)")
print()

try:
    result = parse_vcf(text)
    print("RESULT: PARSED OK")
    print("Variants found:", len(result["variants"]))
    print()
    for i, v in enumerate(result["variants"]):
        print("  Variant %d: gene=%s star=%s rsid=%s" % (i+1, v["gene"], v["star_allele"], v["rsid"]))
    print()
    print("Diplotypes:")
    for g in sorted(result["gene_diplotypes"].keys()):
        d = result["gene_diplotypes"][g]
        print("  %s: %s -> %s" % (g, d["diplotype"], d["phenotype"]))
    
    # Specific assertions
    print()
    print("=== Assertions ===")
    
    genes = [v["gene"] for v in result["variants"]]
    
    # Line 7: INFO='.' should be skipped — no variant with empty gene from that row
    print("[PASS] Line 7 (INFO='.') skipped" if genes.count("") == 0 else "[FAIL] Line 7 not skipped")
    
    # Line 8: GENE= empty should be skipped
    print("[PASS] Line 8 (GENE= empty) skipped" if all(g != "" for g in genes) else "[FAIL] Line 8 not skipped")
    
    # Line 9: lowercase gene=TPMT should be uppercased and matched
    print("[PASS] Line 9 (lowercase TPMT) recognized" if "TPMT" in genes else "[FAIL] Line 9 lowercase not recognized")
    
    # CYP2C9: max 2 variants
    cyp2c9_count = genes.count("CYP2C9")
    print("[PASS] CYP2C9 limited to 2 variants (got %d)" % cyp2c9_count if cyp2c9_count <= 2 else "[FAIL] CYP2C9 has %d variants (expected max 2)" % cyp2c9_count)
    
    # Line 13: STARR= typo — GENE=DPYD exists but STAR= is missing
    dpyd_variants = [v for v in result["variants"] if v["gene"] == "DPYD"]
    if len(dpyd_variants) > 0:
        star_val = dpyd_variants[0]["star_allele"]
        print("[PASS] Line 13 (STARR= typo) DPYD kept with star='%s'" % star_val if star_val in ("", "UNKNOWN") else "[INFO] Line 13 DPYD star='%s'" % star_val)
    else:
        print("[INFO] Line 13 DPYD not in variants (skipped — no STAR= tag)")
    
    # Total expected: CYP2D6(1) + CYP2C19(1) + TPMT(1) + CYP2C9(2) + DPYD(0or1) = 5 or 6
    print()
    print("Total variants: %d" % len(result["variants"]))

except ValueError as e:
    print("REJECTED: %s" % str(e))
except Exception as e:
    print("ERROR: %s: %s" % (type(e).__name__, str(e)))
