import json

d = json.load(open('coverage.json'))
files = d['files']
top = sorted(files.items(), key=lambda x: x[1]['summary']['missing_lines'], reverse=True)[:10]

print("Top 10 files with most missing coverage:")
print("=" * 80)
for k, v in top:
    filename = k.split('\\')[-1]
    missing = v['summary']['missing_lines']
    covered_pct = v['summary']['percent_covered']
    print(f"{filename:40s}: {missing:4d} missing lines ({covered_pct:5.1f}% covered)")

print("\n" + "=" * 80)
print(f"TOTAL COVERAGE: {d['totals']['percent_covered']:.2f}%")
print(f"Target: 85%")
print(f"Gap: {85 - d['totals']['percent_covered']:.2f} percentage points")
