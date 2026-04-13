"""Generate fig_pipeline.pdf — System architecture diagram."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches

font_path = r'C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf'
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 3))
ax.set_xlim(0, 14)
ax.set_ylim(0, 3)
ax.axis('off')

boxes = [
    ("KOSHA\nAPI", 1.0),
    ("XML Parsing\n& GHS Conv.", 3.6),
    ("Korean Braille\nEncoder", 6.2),
    ("Web\nService", 8.8),
    ("User\nBrowser", 11.4),
]

box_w, box_h = 2.2, 1.6
y_center = 1.5

for label, x in boxes:
    rect = mpatches.FancyBboxPatch(
        (x - box_w / 2, y_center - box_h / 2), box_w, box_h,
        boxstyle="round,pad=0.15",
        facecolor='#E8F0FE', edgecolor='#1A73E8', linewidth=2
    )
    ax.add_patch(rect)
    ax.text(x, y_center, label, ha='center', va='center',
            fontsize=11, fontweight='bold', color='#202124')

# Arrows between boxes
arrow_style = dict(arrowstyle='->', color='#1A73E8', lw=2.0,
                   connectionstyle='arc3,rad=0')
for i in range(len(boxes) - 1):
    x_start = boxes[i][1] + box_w / 2
    x_end = boxes[i + 1][1] - box_w / 2
    ax.annotate('', xy=(x_end, y_center), xytext=(x_start, y_center),
                arrowprops=arrow_style)

fig.tight_layout(pad=0.3)
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_pipeline.pdf', bbox_inches='tight')
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_pipeline.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("Done: fig_pipeline.pdf / .png")
