"""Fig 1 — System architecture diagram (English labels, evenly spaced)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

OUT_PDF = r"C:\Users\USER\Desktop\Braille\paper\archive\tex_source\fig_pipeline.pdf"
OUT_PNG = r"C:\Users\USER\Desktop\Braille\paper\archive\tex_source\fig_pipeline.png"

labels = [
    "KOSHA\nAPI",
    "XML Parsing\n& GHS Conv.",
    "Korean Braille\nEncoder",
    "Web\nService",
    "User\nBrowser",
]
n = len(labels)

# Uniform spacing
box_w, box_h = 2.4, 1.8
gap = 1.0
total_w = n * box_w + (n - 1) * gap
margin = 0.5
fig_w = total_w + 2 * margin
fig_h = box_h + 1.4

fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_xlim(0, fig_w)
ax.set_ylim(0, fig_h)
ax.axis("off")

centers = [margin + box_w / 2 + i * (box_w + gap) for i in range(n)]
y = fig_h / 2

for label, cx in zip(labels, centers):
    rect = mpatches.FancyBboxPatch(
        (cx - box_w / 2, y - box_h / 2),
        box_w, box_h,
        boxstyle="round,pad=0.15",
        facecolor="#E8F0FE",
        edgecolor="#1A73E8",
        linewidth=2,
    )
    ax.add_patch(rect)
    ax.text(cx, y, label, ha="center", va="center",
            fontsize=12, fontweight="bold", color="#202124")

for i in range(n - 1):
    x_start = centers[i] + box_w / 2
    x_end = centers[i + 1] - box_w / 2
    ax.annotate(
        "",
        xy=(x_end, y),
        xytext=(x_start, y),
        arrowprops=dict(arrowstyle="-|>", color="#1A73E8",
                        lw=2.2, mutation_scale=18),
    )

fig.savefig(OUT_PDF, bbox_inches="tight")
fig.savefig(OUT_PNG, bbox_inches="tight", dpi=300)
plt.close(fig)
print(f"Wrote {OUT_PDF} and {OUT_PNG}")
