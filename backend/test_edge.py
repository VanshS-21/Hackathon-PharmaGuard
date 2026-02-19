import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vcf_parser import parse_vcf

vcf = """##fileformat=VCFv4.2
##INFO=<ID=GENE,Number=1,Type=String,Description="Gene name">
Name,Age,City
John,25,Mumbai
Jane,30,Delhi"""

try:
    r = parse_vcf(vcf)
    print("FAIL: should have been rejected, got %d variants" % len(r["variants"]))
except ValueError as e:
    print("PASS: rejected -- %s" % e)
