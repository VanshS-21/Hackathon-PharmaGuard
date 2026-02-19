"""Quick end-to-end test for VCF parser + risk engine."""
from vcf_parser import parse_vcf
from risk_engine import assess_risk

# Read sample VCF
with open("../sample/sample_patient.vcf", "r") as f:
    vcf_text = f.read()

# Parse
parsed = parse_vcf(vcf_text)
print("Patient:", parsed["patient_id"])
print("Variants found:", len(parsed["variants"]))
print()

# Show diplotypes
for gene, info in parsed["gene_diplotypes"].items():
    print(f"  {gene}: {info['diplotype']} -> {info['phenotype']}")
print()

# Assess risk for all drugs
for drug in ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"]:
    result = assess_risk(drug, parsed["variants"], parsed["gene_diplotypes"])
    print(f"  {drug}: {result['risk_label']} (severity={result['severity']}, confidence={result['confidence_score']})")

print()
print("=== END-TO-END TEST PASSED ===")
