#!/usr/bin/env python3
"""
AI SaaS Compass — Open 5-Pillar Scorecard Formula Verifier
Audits all CSV benchmark files in /datasets/ to verify that every product's
published score matches the exact weighted formula:
  Rating = round(0.30 * Reliability + 0.25 * Integration + 0.20 * Security + 0.15 * UX + 0.10 * TCO_Value, 1)
"""
import csv
import glob
import os
import sys

def verify_all_csvs(directory="."):
    csv_files = sorted(glob.glob(os.path.join(directory, "*-benchmark.csv")))
    total_products = 0
    errors = 0
    for path in csv_files:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f))
        in_section_1 = False
        for row in reader:
            if not row:
                if in_section_1:
                    break
                continue
            if row[0].startswith("=== SECTION 1:"):
                in_section_1 = True
                continue
            if in_section_1 and row[0] != "Platform Name":
                name = row[0]
                rel, integ, sec, ux, val = map(float, row[1:6])
                published_sum = float(row[6])
                published_rating = float(row[7])
                calc_sum = round(0.30 * rel + 0.25 * integ + 0.20 * sec + 0.15 * ux + 0.10 * val, 3)
                calc_rating = round(calc_sum, 1)
                total_products += 1
                if abs(calc_sum - published_sum) > 0.005 or abs(calc_rating - published_rating) > 0.05:
                    print(f"[MISMATCH] {os.path.basename(path)} -> {name}: calc={calc_rating} vs pub={published_rating}")
                    errors += 1
    print(f"Verified {total_products} product scorecards across {len(csv_files)} benchmark datasets. Formula mismatches: {errors}")
    return errors == 0

if __name__ == "__main__":
    ok = verify_all_csvs(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(0 if ok else 1)
