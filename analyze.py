import json
from collections import Counter

with open("results_raw.json") as f:
    results = json.load(f)

auth_counts = Counter()
for r in results:
    for m in r.get("auth_methods", []):
        auth_counts[m] += 1

gate_by_category = {}
for r in results:
    cat = r.get("category", "unknown")
    gate_by_category.setdefault(cat, Counter())[r.get("self_serve", "unclear")] += 1

blocker_counts = Counter(r.get("blocker", "none") for r in results if r.get("blocker"))

patterns = {
    "auth_distribution": dict(auth_counts),
    "self_serve_by_category": {k: dict(v) for k, v in gate_by_category.items()},
    "top_blockers": blocker_counts.most_common(10),
}

with open("patterns.json", "w") as f:
    json.dump(patterns, f, indent=2)
print(json.dumps(patterns, indent=2))