"""Test samples 3-7 against strict parser."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vcf_parser import parse_vcf

sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample")

for n in range(3, 8):
    fname = "sample%d.vcf" % n
    fpath = os.path.join(sample_dir, fname)
    if not os.path.exists(fpath):
        print("[SKIP] %s not found" % fname)
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        result = parse_vcf(text)
        print("[PASS] %s -- parsed OK, %d variants" % (fname, len(result["variants"])))
    except ValueError as e:
        print("[REJECTED] %s -- %s" % (fname, str(e)))
    except Exception as e:
        print("[ERROR] %s -- %s: %s" % (fname, type(e).__name__, str(e)))
