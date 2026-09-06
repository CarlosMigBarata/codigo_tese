import re
import matplotlib.pyplot as plt

RESULTS_FILE = "z_ltn_check/all_results.txt"
OUTPUT_FILE = "z_ltn_check/concept_ablation_invert.pdf"
MODE = "invert"

LINE_RE = re.compile(
    r"\[SAT CHECK\] (\w+) (\w+): mean_sat=([\d.]+) delta=([+-][\d.]+) "
    r"changes=(\d+) ltn_inconsistent=(\d+)/(\d+)"
)


def load_results(path):
    results = []
    with open(path) as f:
        for line in f:
            m = LINE_RE.match(line)
            if not m:
                continue
            concept, mode, sat, delta, changes, incon, total = m.groups()
            results.append({"concept": concept, "mode": mode, "delta": float(delta)})
    return results


def main():
    results = [r for r in load_results(RESULTS_FILE) if r["mode"] == MODE]
    results.sort(key=lambda r: r["delta"])

    concepts = [r["concept"] for r in results]
    deltas = [r["delta"] for r in results]
    colors = ["#e34948" if d < 0 else "#2a78d6" for d in deltas]

    fig, ax = plt.subplots(figsize=(7, max(3, 0.35 * len(concepts))))
    ax.barh(concepts, deltas, color=colors)
    ax.invert_yaxis()  # most disruptive concept at top
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(f"change in mean axiom satisfaction ({MODE} mode)")
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
