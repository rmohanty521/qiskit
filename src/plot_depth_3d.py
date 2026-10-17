"""3D view of success probability vs puzzle size N and number of layers p.

Run from the repo root:   python -m src.plot_depth_3d
Reads the main puzzle of each size (results/depth_to_50_N<n>.json; N = 4 also uses the
p = 1..12 sweep in results/summary.json) and saves results/fig_depth_3d.png.
Each curve is one puzzle size, grown one layer at a time; the grey plane is 50% success.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

TEAL, AMBER, INK, GREY = "#0E9488", "#C2772A", "#1B2433", "#5B6575"
COLOURS = {4: "#0E9488", 5: "#3B82F6", 6: "#8B5CF6", 7: "#DB4B92", 8: "#C2772A"}


def curves():
    out = {}
    for n in range(4, 9):
        rows = json.load(open(f"results/depth_to_50_N{n}.json"))["rows"]
        out[n] = [(r["p"], r["P"]) for r in rows]
    core = json.load(open("results/summary.json"))["core"]          # N = 4 tuned to p = 12
    out[4] = [(r["p"], r["P"]) for r in core]
    return out


def main(path="results/fig_depth_3d.png"):
    data = curves()
    p_max = max(p for c in data.values() for p, _ in c)
    fig = plt.figure(figsize=(9, 6.2))
    ax = fig.add_subplot(projection="3d")

    # the 50% success plane
    plane = [[(0, 3.6, 0.5), (p_max + 2, 3.6, 0.5), (p_max + 2, 8.4, 0.5), (0, 8.4, 0.5)]]
    ax.add_collection3d(Poly3DCollection(plane, facecolor=GREY, alpha=0.12, edgecolor="none"))

    for n, c in data.items():
        p, prob = np.array(c).T
        y = np.full_like(p, n)
        col = COLOURS[n]
        # a ribbon down to zero makes each curve read as a solid shape in depth
        ax.add_collection3d(Poly3DCollection([list(zip(p, y, prob)) + [(p[-1], n, 0), (p[0], n, 0)]],
                                             facecolor=col, alpha=0.18, edgecolor="none"))
        hit = next((i for i, v in enumerate(prob) if v >= 0.5), None)
        label = f"N = {n}: 50% at p = {int(p[hit])}" if hit is not None else f"N = {n}"
        ax.plot(p, y, prob, color=col, lw=2.4, label=label)
        if hit is not None:
            ax.scatter([p[hit]], [n], [prob[hit]], color=col, s=55, edgecolor="white", depthshade=False, zorder=5)

    ax.set_xlabel("layers p", color=INK, labelpad=8)
    ax.set_ylabel("N cubes", color=INK, labelpad=8)
    ax.set_zlabel("P(correct tower)", color=INK, labelpad=8)
    ax.set_xlim(0, p_max + 2)
    ax.set_ylim(3.6, 8.4)
    ax.set_zlim(0, 0.8)
    ax.set_yticks(range(4, 9))
    ax.set_zticks([0, 0.25, 0.5, 0.75])
    ax.set_zticklabels(["0%", "25%", "50%", "75%"])
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_alpha(0.0)
        axis._axinfo["grid"]["color"] = (0.85, 0.85, 0.85, 1)
    ax.tick_params(colors=GREY, labelsize=9)
    ax.view_init(elev=22, azim=-58)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), frameon=False, fontsize=10, labelcolor=INK)
    ax.set_title("Bigger puzzles need more layers to reach 50% success", color=INK, fontsize=13, pad=4)
    fig.text(0.5, 0.04, "Grey plane = 50% success. Dot = first layer count that reaches it. "
             "One puzzle per size; exact simulation.", ha="center", color=GREY, fontsize=9)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote", path)


if __name__ == "__main__":
    main()
