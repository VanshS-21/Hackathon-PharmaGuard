"""Quick verification of variant_database.json against CPIC API."""
import asyncio, json, httpx

CPIC = "https://api.cpicpgx.org/v1"

FUNC_MAP = {
    "no function": "no_function",
    "decreased function": "decreased_function",
    "increased function": "increased_function",
    "normal function": "normal_function",
    "uncertain function": "unknown_function",
}

async def main():
    db = json.load(open("variant_database.json", encoding="utf-8"))
    rules = json.load(open("drug_rules.json", encoding="utf-8"))

    async with httpx.AsyncClient(timeout=30) as c:
        # 1. Star allele functions
        print("=== STAR ALLELE FUNCTIONS ===")
        func_section = db.get("_star_allele_functions", {})
        errs, oks = 0, 0

        for gene in ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]:
            r = await c.get(f"{CPIC}/allele", params={
                "genesymbol": f"eq.{gene}",
                "select": "name,functionalstatus,clinicalfunctionalstatus",
            })
            cpic = {}
            for a in r.json():
                val = (a.get("clinicalfunctionalstatus") or a.get("functionalstatus") or "").lower()
                cpic[a["name"]] = val

            gene_stars = {}
            for k, v in func_section.items():
                if k.startswith(f"{gene}:") and not k.startswith("_"):
                    gene_stars[k.split(":", 1)[1]] = v

            print(f"\n{gene} ({len(gene_stars)} entries):")
            for star in sorted(gene_stars):
                our_func = gene_stars[star]
                cpic_func = cpic.get(star, "NOT_FOUND")
                expected = FUNC_MAP.get(cpic_func, f"unmapped:{cpic_func}")
                if expected == our_func:
                    oks += 1
                    tag = "OK"
                else:
                    errs += 1
                    tag = "MISMATCH"
                print(f"  {tag:8s} {star:6s}: ours={our_func:25s} cpic={cpic_func}")

        print(f"\nStar allele totals: {oks} OK, {errs} mismatches")

        # 2. rsID entries
        print("\n=== RSID ENTRIES ===")
        for gene in ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]:
            gene_data = db.get(gene, {})
            for rsid, info in gene_data.items():
                print(f"  {gene} {rsid}: star={info['star']}, effect={info['effect']}")

        # 3. Drug-gene pairs + levels
        print("\n=== DRUG-GENE CPIC LEVELS ===")
        for drug, info in rules.items():
            if drug.startswith("_"):
                continue
            r = await c.get(f"{CPIC}/pair_view", params={
                "drugname": f"eq.{drug.lower()}",
                "genesymbol": f"eq.{info['gene']}",
                "select": "cpiclevel,guidelinename",
            })
            if r.status_code == 200 and r.json():
                p = r.json()[0]
                print(f"  {drug:15s} - {info['gene']:8s}: Level {p.get('cpiclevel', '?')}")
            else:
                print(f"  {drug:15s} - {info['gene']:8s}: NOT FOUND in CPIC")

        # 4. Level A drugs we're missing
        print("\n=== CPIC LEVEL A DRUGS WE ARE MISSING ===")
        our = set(d.lower() for d in rules if not d.startswith("_"))
        r = await c.get(f"{CPIC}/pair_view", params={
            "cpiclevel": "eq.A",
            "select": "drugname,genesymbol,guidelinename",
            "order": "drugname.asc",
        })
        all_a = r.json()
        seen = set()
        for p in all_a:
            d = p["drugname"]
            if d not in our and d not in seen:
                seen.add(d)
                print(f"  {d:25s} - {p['genesymbol']:10s} ({p.get('guidelinename', '')})")
        in_both = our.intersection(set(p["drugname"] for p in all_a))
        print(f"\nWe cover {len(in_both)}/{len(in_both) + len(seen)} Level A drugs. Missing: {len(seen)}")


if __name__ == "__main__":
    asyncio.run(main())
