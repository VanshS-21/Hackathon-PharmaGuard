import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vcf_parser import parse_vcf

sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample")
p = 0; f = 0

files = ["sample_patient.vcf"] + ["sample%d.vcf" % n for n in range(2, 13)]
for fname in files:
    fpath = os.path.join(sample_dir, fname)
    with open(fpath, "r", encoding="utf-8") as ff:
        text = ff.read()
    try:
        result = parse_vcf(text)
        p += 1
        vlist = ", ".join("%s %s" % (v["gene"], v["star_allele"]) for v in result["variants"])
        print("[PASS] %-22s %d variants: %s" % (fname, len(result["variants"]), vlist))
    except Exception as e:
        f += 1
        print("[FAIL] %-22s %s" % (fname, e))

print()
print("=" * 50)
print("RESULTS: %d/%d PASSED" % (p, p + f))
if f == 0:
    print("ALL TESTS PASSED")
print("=" * 50)
