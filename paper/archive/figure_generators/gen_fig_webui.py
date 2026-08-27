"""Generate fig_webui.pdf — Mock web UI screenshot."""
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

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')
fig.patch.set_facecolor('#F5F5F5')

# --- Header bar ---
header = mpatches.FancyBboxPatch((0.2, 7.0), 11.6, 0.8,
    boxstyle="round,pad=0.05", facecolor='#1A73E8', edgecolor='none')
ax.add_patch(header)
ax.text(6.0, 7.4, 'MSDS 점자 변환', ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# --- Search bar ---
search_bg = mpatches.FancyBboxPatch((2.5, 6.15), 7.0, 0.55,
    boxstyle="round,pad=0.08", facecolor='white', edgecolor='#DADCE0', linewidth=1.5)
ax.add_patch(search_bg)
ax.text(3.0, 6.42, '벤젠', fontsize=13, va='center', color='#202124')
# search icon placeholder
search_btn = mpatches.FancyBboxPatch((8.7, 6.18), 0.7, 0.48,
    boxstyle="round,pad=0.05", facecolor='#1A73E8', edgecolor='none')
ax.add_patch(search_btn)
ax.text(9.05, 6.42, '검색', ha='center', va='center',
        fontsize=10, color='white', fontweight='bold')

# --- Left panel: chemical list ---
left_bg = mpatches.FancyBboxPatch((0.3, 0.3), 3.4, 5.5,
    boxstyle="round,pad=0.1", facecolor='white', edgecolor='#DADCE0', linewidth=1.2)
ax.add_patch(left_bg)
ax.text(2.0, 5.55, '화학물질 목록', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#202124')

chemicals = ['벤젠 (Benzene)', '톨루엔 (Toluene)', '아세톤 (Acetone)',
             '메탄올 (Methanol)', '에탄올 (Ethanol)', '자일렌 (Xylene)',
             '포름알데히드 (Formaldehyde)']
for i, chem in enumerate(chemicals):
    y = 5.1 - i * 0.6
    if i == 0:  # highlight selected
        sel_bg = mpatches.FancyBboxPatch((0.5, y - 0.2), 3.0, 0.45,
            boxstyle="round,pad=0.04", facecolor='#E8F0FE', edgecolor='none')
        ax.add_patch(sel_bg)
        color = '#1A73E8'
        weight = 'bold'
    else:
        color = '#5F6368'
        weight = 'normal'
    ax.text(0.6, y, chem, fontsize=9.5, va='center', color=color, fontweight=weight)

# --- Right panel: detail view ---
right_bg = mpatches.FancyBboxPatch((4.0, 0.3), 7.7, 5.5,
    boxstyle="round,pad=0.1", facecolor='white', edgecolor='#DADCE0', linewidth=1.2)
ax.add_patch(right_bg)
ax.text(7.85, 5.55, '벤젠 — 상세 정보', ha='center', va='center',
        fontsize=13, fontweight='bold', color='#202124')

# Divider
ax.plot([4.3, 11.4], [5.2, 5.2], color='#DADCE0', linewidth=1)

# Side-by-side: Korean text | Braille
ax.text(6.0, 4.85, '한국어 텍스트', ha='center', fontsize=11,
        fontweight='bold', color='#1A73E8')
ax.text(9.8, 4.85, '점자 변환', ha='center', fontsize=11,
        fontweight='bold', color='#1A73E8')

# Vertical divider
ax.plot([7.85, 7.85], [0.5, 4.65], color='#DADCE0', linewidth=1, linestyle='--')

korean_lines = [
    '물질명: 벤젠',
    '분자식: C₆H₆',
    'CAS 번호: 71-43-2',
    '유해성: 발암성 물질',
    '취급 주의사항:',
    '  - 흡입 시 신선한 공기로 이동',
    '  - 피부 접촉 시 물로 세척',
    '  - 화기 엄금',
]

braille_lines = [
    '\u2830\u2825\u2807\u2815\u2811\u2809: \u2830\u2811\u2801\u2811\u2805',
    '\u2830\u2825\u2805\u2801\u2811\u2807: C₆H₆',
    'CAS \u2830\u2811\u2805\u2833: 71-43-2',
    '\u2825\u2833\u2811\u2831\u2805: \u2830\u2801\u2807\u2801\u2837\u2831\u2805',
    '\u2807\u2825\u2805 \u2801\u2825\u2811\u2831\u2811\u2833:',
    '  - \u2833\u2811\u2837 \u2811 \u2831\u2811\u2805\u2831\u2801\u2805',
    '  - \u2819\u2825\u2819\u2825 \u2801\u2805\u2813\u2807\u2825\u2831',
    '  - \u2833\u2801\u2831\u2811 \u2801\u2837\u2831\u2805',
]

for i, (kr, br) in enumerate(zip(korean_lines, braille_lines)):
    y = 4.4 - i * 0.5
    ax.text(4.5, y, kr, fontsize=9.5, va='center', color='#202124',
            fontfamily=font_name)
    ax.text(8.1, y, br, fontsize=9.5, va='center', color='#5F6368',
            fontfamily='DejaVu Sans')

fig.tight_layout(pad=0.5)
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_webui.pdf', bbox_inches='tight')
fig.savefig(r'C:\Users\USER\Desktop\Braille\paper\fig_webui.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("Done: fig_webui.pdf / .png")
