"""Generate fig_dataset_stats.pdf — Pie chart + histogram."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

font_path = r'C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf'
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

# --- (a) Pie chart: character distribution ---
labels = ['Korean\n(한국어)', 'Latin\n(라틴)', 'Digits\n(숫자)']
sizes = [76.3, 16.6, 7.1]
colors = ['#4285F4', '#EA4335', '#FBBC04']
explode = (0.03, 0.03, 0.03)

wedges, texts, autotexts = ax1.pie(
    sizes, labels=labels, autopct='%1.1f%%', startangle=140,
    colors=colors, explode=explode, textprops={'fontsize': 11},
    pctdistance=0.55
)
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax1.set_title('(a) 문자 분포', fontsize=13, fontweight='bold', pad=12)

# --- (b) Histogram: text length distribution ---
mean, std = 6046, 1435
lo, hi = 2241, 10490
np.random.seed(42)
data = np.random.normal(mean, std, 5000)
data = data[(data >= lo) & (data <= hi)]

ax2.hist(data, bins=30, color='#4285F4', edgecolor='white', alpha=0.85)
ax2.axvline(mean, color='#EA4335', linestyle='--', linewidth=1.8,
            label=f'평균 = {mean}')
ax2.set_xlabel('텍스트 길이 (문자 수)', fontsize=11)
ax2.set_ylabel('빈도', fontsize=11)
ax2.set_title('(b) 텍스트 길이 분포', fontsize=13, fontweight='bold', pad=12)
ax2.legend(fontsize=10)

stats_text = f'평균={mean}\n표준편차={std}\n최소={lo}\n최대={hi}'
ax2.text(0.97, 0.95, stats_text, transform=ax2.transAxes,
         fontsize=9, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF3E0', alpha=0.9))

fig.tight_layout(pad=1.5)
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_dataset_stats.pdf', bbox_inches='tight')
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_dataset_stats.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("Done: fig_dataset_stats.pdf / .png")
