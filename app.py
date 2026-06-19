import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="NailVesta GMV Dashboard", layout="wide")

st.title("NailVesta TikTok Shop GMV 分析 Dashboard")

# =========================================================
# 可調整參數區（每月更新就改這裡）
# =========================================================

# 月度 GMV 預設值（也可以在左側側邊欄直接編輯 / 新增月份）
DEFAULT_DATA = {
    "月份": ["1月", "2月", "3月", "4月", "5月"],
    "GMV": [125296.69, 110102.54, 100055.38, 95443.74, 103197.84],
}

# 達人結構
COLLAB_CREATORS = 1061   # 合作創作者
ORDER_CREATORS = 392     # 出單創作者
TOP10_GMV = 44621        # Top10 達人 GMV

# 內容結構（Week76 影片支數）
VIDEO = {"S": 51, "AK": 42, "AS": 30, "C": 47}

# 結論用的關鍵指標
DEEP_GMV_SHARE = 72.2    # 深達 GMV 佔比 (%)
UNCONVERTED_BROAD = 124  # 尚未轉化的廣達數量

# 下半年預測
FORECAST_DATA = {
    "月份": ["6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    "低預估": [105000, 110000, 120000, 110000, 125000, 180000, 200000],
    "高預估": [115000, 125000, 135000, 125000, 145000, 250000, 300000],
}

CATEGORY_AUP = 18.57  # 2025 美國 TikTok Shop 美妝品類平均單價（公開數據）

# 競品逐月數據（來源：FastMoss，2026-06-18 擷取）
# 之後要加競品，照同樣格式往字典裡新增即可
COMPETITORS = {
    "Nailphoria": {
        "月份":  ["1月",   "2月",   "3月",   "4月",   "5月"],
        "GMV":   [465700,  421500,  360200,  330800,  344400],
        "销量":  [11700,   11300,   10700,   9639,    10600],
        "达人数": [537,     573,     341,     302,     247],
        "直播数": [415,     220,     187,     408,     413],
        "视频数": [625,     656,     439,     122,     91],
    },
    "NailHaven": {
        "月份":  ["1月",   "2月",   "3月",   "4月",   "5月"],
        "GMV":   [316700,  315800,  294200,  342700,  398700],
        "销量":  [27400,   27100,   26000,   29300,   34700],
        "达人数": [138,     139,     167,     166,     201],
        "直播数": [148,     181,     156,     316,     396],
        "视频数": [262,     245,     314,     158,     210],
    },
}

# 店舖層級體質（FastMoss 店舖詳情頁，2026-06-18）
STORE_META = {
    "NailVesta":  {"定位": "高端·內容/自播均衡", "月榜": "#192", "评分": "4.9", "48h出货": "74%"},
    "Nailphoria": {"定位": "高端·自播驅動",       "月榜": "#209", "评分": "4.8", "48h出货": "87%"},
    "NailHaven":  {"定位": "低價·走量/商品卡",     "月榜": "#178", "评分": "4.8", "48h出货": "87%"},
}
# NailHaven 成交結構（FastMoss 聚合值，%）— 與你形成強烈對比
NAILHAVEN_CHANNEL = {"商品卡": 66.81, "店铺自营号": 2.36, "达人带货": 30.83}

# NailVesta 的 FastMoss「全店」數據（與競品同口徑，用於競品對比）
# 注意：這與側邊欄你輸入的「內部 GMV」是兩個不同口徑，差距見下方說明
NAILVESTA_FASTMOSS = {
    "月份":  ["1月",   "2月",   "3月",   "4月",   "5月"],
    "GMV":   [433100,  366500,  385500,  313200,  363900],
    "销量":  [10600,   9231,    10300,   9417,    10900],
    "达人数": [922,     882,     745,     1009,    867],
    "直播数": [331,     378,     277,     426,     439],
    "视频数": [1266,    1210,    1010,    428,     199],
}

# NailVesta 成交結構（FastMoss 聚合值，%）
NAILVESTA_CHANNEL = {"商品卡": 29.34, "店铺自营号": 30.29, "达人带货": 40.37}
NAILVESTA_METHOD = {"视频": 39.32, "直播": 31.34, "商品卡": 29.34}
# 自家官方號近28天：销售额、直播 GPM、视频 GPM
NV_OWN = {"销售额": 109300, "直播GPM": "$20.5–$23.58", "视频GPM": "$2.99–$4.45"}

# =========================================================
# 側邊欄：可編輯的月度數據
# =========================================================

st.sidebar.header("📝 月度數據")
st.sidebar.caption("在這裡編輯每月 GMV，主畫面會自動重新計算。")

input_df = st.sidebar.data_editor(
    pd.DataFrame(DEFAULT_DATA),
    column_config={
        "月份": st.column_config.TextColumn("月份"),
        "GMV": st.column_config.NumberColumn("GMV", format="$%.2f", min_value=0),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="gmv_editor",
)

# 清理空白列並重新計算衍生欄位
df = input_df.dropna(subset=["GMV"]).reset_index(drop=True)
df = df[df["月份"].astype(str).str.strip() != ""].reset_index(drop=True)

df["月增率"] = df["GMV"].pct_change() * 100
df["GMV佔比"] = df["GMV"] / df["GMV"].sum() * 100

# =========================================================
# 小工具
# =========================================================

def usd(v):
    # 跳脫 $，避免 Streamlit markdown 把 $...$ 當成 LaTeX 數學式
    return "—" if v is None or pd.isna(v) else f"\\${v:,.2f}"

def pct(v):
    return "—" if v is None or pd.isna(v) else f"{v:.2f}%"

total_gmv = df["GMV"].sum()
avg_gmv = df["GMV"].mean()
max_month = df.loc[df["GMV"].idxmax()]
min_month = df.loc[df["GMV"].idxmin()]

# 月份對照表（分析段落用，按月份名稱取值，編輯後仍正確）
gmv_map = dict(zip(df["月份"], df["GMV"]))
mom_map = dict(zip(df["月份"], df["月增率"]))

jan = gmv_map.get("1月")
apr = gmv_map.get("4月")
may = gmv_map.get("5月")

total_drop = (apr - jan) / jan * 100 if jan and apr else None
feb_mom = mom_map.get("2月")
mar_mom = mom_map.get("3月")
apr_mom = mom_map.get("4月")
may_growth = mom_map.get("5月")

# 達人 / 內容衍生指標
conv_rate = ORDER_CREATORS / COLLAB_CREATORS * 100 if COLLAB_CREATORS else 0
top10_share = TOP10_GMV / may * 100 if may else None

video_total = sum(VIDEO.values())
s_ak = VIDEO["S"] + VIDEO["AK"]
s_ak_ratio = s_ak / video_total * 100 if video_total else 0

# =========================================================
# 樣式
# =========================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}

[data-testid="stMetricValue"] {
    font-size: 24px;
}

.analysis-box {
    background: #fff8f5;
    padding: 22px 26px;
    border-radius: 18px;
    border: 1px solid #f0d8cf;
    line-height: 1.8;
    font-size: 15.5px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 10px;
}

.small-note {
    color: #666;
    font-size: 14px;
}

.highlight-box {
    background: linear-gradient(135deg, #fff1ec 0%, #ffe6dc 100%);
    border-left: 6px solid #e8623c;
    padding: 26px 30px;
    border-radius: 14px;
    margin: 18px 0 8px 0;
    box-shadow: 0 4px 14px rgba(232, 98, 60, 0.12);
}

.highlight-title {
    font-size: 26px;
    font-weight: 800;
    color: #c8401f;
    line-height: 1.5;
    margin-bottom: 14px;
}

.highlight-point {
    font-size: 17px;
    line-height: 1.9;
    margin: 4px 0;
}

.tag {
    display: inline-block;
    background: #e8623c;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 指標卡
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("總 GMV", f"${total_gmv:,.2f}")
col2.metric("平均月 GMV", f"${avg_gmv:,.2f}")
col3.metric("最高月份", max_month["月份"], f"${max_month['GMV']:,.2f}", delta_color="off")
col4.metric("最低月份", min_month["月份"], f"${min_month['GMV']:,.2f}", delta_color="off")

st.divider()

# =========================================================
# 數據表
# =========================================================

st.subheader("GMV 數據表")

display_df = df.copy()
display_df["GMV"] = display_df["GMV"].map(lambda x: f"${x:,.2f}")
display_df["月增率"] = display_df["月增率"].map(lambda x: "-" if pd.isna(x) else f"{x:.2f}%")
display_df["GMV佔比"] = display_df["GMV佔比"].map(lambda x: f"{x:.2f}%")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# =========================================================
# 圖表
# =========================================================

left, right = st.columns(2)

with left:
    st.subheader("GMV 趨勢圖")
    chart_df = df.set_index("月份")[["GMV"]]
    st.line_chart(chart_df, height=280)

with right:
    st.subheader("月增率變化")
    growth_df = df.dropna(subset=["月增率"]).set_index("月份")[["月增率"]]
    st.bar_chart(growth_df, height=280)

st.divider()

# =========================================================
# 趨勢分析
# =========================================================

st.subheader("專業趨勢分析")

st.markdown(f"""
<div class="analysis-box">

<div class="section-title">第一階段：1月 → 4月連續下滑</div>

從 1月的 <b>{usd(jan)}</b> 下降到 4月的 <b>{usd(apr)}</b>。

<br><br>

總跌幅：

<br>

<b>({apr:,.2f} - {jan:,.2f}) / {jan:,.2f} = {pct(total_drop)}</b>

<br><br>

代表前四個月累積下滑約 <b>{pct(total_drop)}</b>。

<br><br>

這其實非常符合 TikTok Shop 美國市場的季節性規律。

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="highlight-box">
<div class="highlight-title">📌 重點：這完全符合 TikTok Shop 美國市場的季節性規律</div>

<div class="highlight-point"><span class="tag">Q1</span><b>1月最強</b>：節後流量 + Holiday 庫存內容延續出單，全平台美妝普遍是全年高點之一。</div>

<div class="highlight-point"><span class="tag">Q1→Q2</span><b>2–4月走弱</b>：帳單壓力、無大型購物節、CPM 下降，是全行業的淡季，不是你品牌獨有。</div>

<div class="highlight-point"><span class="tag">夏季</span><b>5月起回升</b>：美甲本身有夏季旺季（假期、活動、出遊），這跟你 5月反彈與下半年預測同向。</div>

<div class="highlight-point"><span class="tag">Q4</span><b>11–12月爆發</b>：BFCM + 聖誕,2025 TikTok Shop 美國光 BFCM 四天就破 5億美元 GMV,是全年最大波。</div>

<div class="highlight-point" style="margin-top:12px; color:#7a3b2a;">➡️ <b>結論：你 1→4月的下滑是「市場節奏」而非「品牌衰退」,真正能拉開差距的是淡季的深達擴張與內容品質。</b></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="analysis-box">

<b>1月：</b><br>
聖誕節後流量仍在，許多品牌延續 Holiday 流量，Creator 庫存內容持續出單，所以通常是 Q1 最強月份。

<br><br>

<b>2月：</b><br>
開始進入淡季。原因包括消費者信用卡帳單開始出現、節日消費結束、TikTok CPM 通常下降、整體消費意願變弱。  
<br>
你的跌幅為 <b>{pct(feb_mom)}</b>，屬於正常範圍。

<br><br>

<b>3月：</b><br>
通常是全年第二個低谷。原因包括沒有大型購物節、稅務季、消費者支出保守。  
<br>
你的跌幅為 <b>{pct(mar_mom)}</b>，也是正常。

<br><br>

<b>4月：</b><br>
理論上應該開始回升，但你仍下降 <b>{pct(apr_mom)}</b>。  
<br>
這值得注意，代表問題可能不只是市場，而是品牌本身。

<br><br>

可能出現的原因：

<ul>
<li>深達數量不足</li>
<li>爆款影片減少</li>
<li>廣達轉化率下降</li>
<li>新款刺激不足</li>
</ul>

這跟之前分析的「廣達佔比高、中腰部轉化弱、S級內容不足」其實完全吻合。

<br>

<div class="section-title">第二階段：5月反彈</div>

4月 GMV：<b>{usd(apr)}</b><br>
5月 GMV：<b>{usd(may)}</b>

<br><br>

成長率：

<br>

<b>({may:,.2f} - {apr:,.2f}) / {apr:,.2f} = {pct(may_growth)}</b>

<br><br>

代表：

<ul>
<li>品牌已經停止下跌</li>
<li>開始重新進入成長</li>
</ul>

</div>
""", unsafe_allow_html=True)

# =========================================================
# TikTok Shop 頭部品牌對照
# =========================================================

st.subheader("TikTok Shop 競品對照（FastMoss 全店實數）")

st.markdown("""
<div class="analysis-box">
這裡只留我們有 FastMoss 實數的兩個<b>直接競品</b>：Nailphoria（跟你同走高端）和 NailHaven（低價走量、對照組）。
下表數字皆為 FastMoss 全店口徑、1–5月。
</div>
""", unsafe_allow_html=True)

def _ta(g, u):
    t = sum(g)
    return t, t / sum(u)

_nvt, _nva = _ta(NAILVESTA_FASTMOSS["GMV"], NAILVESTA_FASTMOSS["销量"])
_npt, _npa = _ta(COMPETITORS["Nailphoria"]["GMV"], COMPETITORS["Nailphoria"]["销量"])
_nht, _nha = _ta(COMPETITORS["NailHaven"]["GMV"], COMPETITORS["NailHaven"]["销量"])

competitor_df = pd.DataFrame({
    "品牌": ["NailVesta（你）", "Nailphoria", "NailHaven"],
    "類別 / 定位": ["高端手工穿戴甲", "高端手工穿戴甲", "低價走量穿戴甲"],
    "5個月 GMV": [f"${_nvt:,.0f}", f"${_npt:,.0f}", f"${_nht:,.0f}"],
    "件單價": [f"${_nva:.1f}", f"${_npa:.1f}", f"${_nha:.1f}"],
    "主力打法": [
        "達人40% / 自播30% / 商品卡29%，均衡",
        "自播驅動（官方號近28天 $20萬）",
        "商品卡/搜尋 67%，低價鋪量",
    ],
    "美妝月榜(05)": [
        STORE_META["NailVesta"]["月榜"], STORE_META["Nailphoria"]["月榜"], STORE_META["NailHaven"]["月榜"],
    ],
})
st.dataframe(competitor_df, use_container_width=True, hide_index=True)

st.markdown(r"""
<div class="analysis-box">
<b>一句話讀法</b>：三家 GMV 都在 \$1.6M–1.9M 同級距。Nailphoria 跟你同價位、靠自播衝量；
NailHaven 是另一種物種——\$11 低價、靠商品卡搜尋走量，季節走勢還跟你相反。詳細拆解見下方圖表。
</div>
""", unsafe_allow_html=True)

# =========================================================
# 賽道定位圖
# =========================================================

st.subheader("賽道定位圖：件單價 × GMV（真實數據）")

# 用真實數據建點：X = 平均件單價(ASP)，Y = 5個月總 GMV
pos_rows = []
_all = {"NailVesta": NAILVESTA_FASTMOSS, **COMPETITORS}
for b, d in _all.items():
    tot = sum(d["GMV"])
    asp = tot / sum(d["销量"])
    pos_rows.append({"品牌": b, "件單價": round(asp, 1), "GMV": tot})
pos_df = pd.DataFrame(pos_rows)

pos_brands = ["NailVesta"] + list(COMPETITORS.keys())
pos_colors = ["#e8623c", "#7b4fc0", "#2a9d8f", "#e9b949", "#3a7bd5"][:len(pos_brands)]
pos_color = alt.Color("品牌:N", scale=alt.Scale(domain=pos_brands, range=pos_colors),
                      legend=alt.Legend(title="", orient="top-right"))

points = alt.Chart(pos_df).mark_circle(size=600, opacity=0.85).encode(
    x=alt.X("件單價:Q", title="平均件單價 ASP（USD）", scale=alt.Scale(domain=[0, 45])),
    y=alt.Y("GMV:Q", title="1–5月總 GMV（USD）", scale=alt.Scale(domain=[0, 2200000])),
    color=pos_color,
    tooltip=["品牌", alt.Tooltip("件單價:Q", format=".1f"), alt.Tooltip("GMV:Q", format=",.0f")],
)

labels = alt.Chart(pos_df).mark_text(dy=-26, fontSize=13, fontWeight="bold").encode(
    x="件單價:Q", y="GMV:Q", text="品牌", color=pos_color,
)

aup_rule = alt.Chart(pd.DataFrame({"x": [CATEGORY_AUP]})).mark_rule(
    strokeDash=[6, 4], color="#3a7bd5", size=2
).encode(x="x:Q")

aup_label = alt.Chart(
    pd.DataFrame({"x": [CATEGORY_AUP], "y": [2100000], "t": [f"品類平均單價 ${CATEGORY_AUP}"]})
).mark_text(align="left", dx=6, color="#3a7bd5", fontSize=12, fontWeight="bold").encode(
    x="x:Q", y="y:Q", text="t:N"
)

chart = (points + labels + aup_rule + aup_label).properties(height=440)
st.altair_chart(chart, use_container_width=True)

st.markdown(r"""
<div class="analysis-box">

<b>圖怎麼讀：</b>越往右件單價越高，越往上 5個月 GMV 越大。三個點 GMV 高度差不多，但左右拉得很開。

<ul>
<li><b>你和 Nailphoria 擠在右上角</b>：件單價都約 \$36、GMV 都約 \$1.9M——同價位、同量級的貼身對手。</li>
<li><b>NailHaven 在左邊</b>：件單價只有 \$11.5（低於品類平均 \$18.57 的藍線），卻做到跟你們差不多的 GMV——靠的是 3 倍件數的低價走量。</li>
<li><b>關鍵</b>：同樣的 GMV 高度可以用「高價低量」或「低價高量」達成。你站在右邊（高價），護住毛利；要長大是往「上」衝量，而不是往「左」降價。</li>
</ul>

<span class="small-note">全部為 FastMoss 全店 1–5月實數（件單價 = 總GMV ÷ 總銷量）。藍線為品類平均單價 $18.57。</span>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 競品對比（真實月度數據）
# =========================================================

st.subheader("競品對比：NailVesta vs 競品（1–5月）")

month_sort = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
brand_colors = ["#e8623c", "#7b4fc0", "#2a9d8f", "#e9b949", "#3a7bd5"]

# 攤平：NailVesta（FastMoss 全店，與競品同口徑）＋ 各競品
rows = []
nv_fm = dict(zip(NAILVESTA_FASTMOSS["月份"], NAILVESTA_FASTMOSS["GMV"]))
for m, g in zip(NAILVESTA_FASTMOSS["月份"], NAILVESTA_FASTMOSS["GMV"]):
    rows.append({"月份": m, "品牌": "NailVesta", "GMV": float(g)})
for brand, d in COMPETITORS.items():
    for m, g in zip(d["月份"], d["GMV"]):
        rows.append({"月份": m, "品牌": brand, "GMV": float(g)})

comp_df = pd.DataFrame(rows)
comp_df["_sort"] = comp_df["月份"].map({m: i for i, m in enumerate(month_sort)})
comp_df = comp_df.sort_values(["品牌", "_sort"])
comp_df["指數"] = comp_df.groupby("品牌")["GMV"].transform(lambda s: s / s.iloc[0] * 100)

domain_brands = ["NailVesta"] + list(COMPETITORS.keys())
color_enc = alt.Color("品牌:N", scale=alt.Scale(domain=domain_brands, range=brand_colors[:len(domain_brands)]))

# ---- 先講口徑落差 ----
nv_internal_map = dict(zip(df["月份"], df["GMV"]))
internal_may = nv_internal_map.get("5月")
fm_may = nv_fm.get("5月")
gap_ratio = (fm_may / internal_may) if internal_may else None

st.markdown(f"""
<div class="highlight-box">
<div class="highlight-title">⚠️ 先注意：兩個 GMV 口徑差了約 {gap_ratio:.1f} 倍</div>
<div class="highlight-point">你側邊欄輸入的「內部 GMV」5月是 <b>{usd(internal_may)}</b>，
但 FastMoss 看到的 NailVesta「全店 TikTok Shop GMV」5月是 <b>{usd(fm_may)}</b>。</div>
<div class="highlight-point">FastMoss 是第三方估算會有誤差，但 {gap_ratio:.1f} 倍太大、不像單純誤差。
對照你的成交結構：達人帶貨只佔 <b>40.37%</b>，另外 <b>商品卡 29.34% + 自營號 30.29%</b>。
很可能你內部那個數字主要抓的是<b>達人歸因的單</b>，漏掉了商品卡與自播——這正是你之前提過的「歸因落差」。</div>
<div class="highlight-point" style="color:#7a3b2a;">➡️ 下面競品對比<b>兩邊都用 FastMoss 全店口徑</b>，才公平。你內部真實全店 GMV 多少你最清楚，若接近 FastMoss，那是好消息。</div>
</div>
""", unsafe_allow_html=True)

st.markdown("**① 絕對 GMV（FastMoss 全店口徑）**")
abs_chart = alt.Chart(comp_df).mark_line(point=True, strokeWidth=3).encode(
    x=alt.X("月份:N", sort=month_sort, title="月份"),
    y=alt.Y("GMV:Q", title="月 GMV (USD)"),
    color=color_enc,
    tooltip=["品牌", "月份", alt.Tooltip("GMV:Q", format=",.0f")],
).properties(height=340)
st.altair_chart(abs_chart, use_container_width=True)

st.markdown("**② 指數化（1月=100，看季節形狀）**")
idx_lines = alt.Chart(comp_df).mark_line(point=True, strokeWidth=3).encode(
    x=alt.X("月份:N", sort=month_sort, title="月份"),
    y=alt.Y("指數:Q", title="指數（1月=100）", scale=alt.Scale(domain=[60, 110])),
    color=color_enc,
    tooltip=["品牌", "月份", alt.Tooltip("指數:Q", format=".1f")],
)
base_rule = alt.Chart(pd.DataFrame({"y": [100]})).mark_rule(
    strokeDash=[4, 4], color="#bbb"
).encode(y="y:Q")
st.altair_chart((idx_lines + base_rule).properties(height=340), use_container_width=True)

# 指標對照表（兩邊都 FastMoss 口徑）
def metrics_for(g_map):
    drop = (g_map["4月"] - g_map["1月"]) / g_map["1月"] * 100 if "1月" in g_map and "4月" in g_map else None
    may = (g_map["5月"] - g_map["4月"]) / g_map["4月"] * 100 if "4月" in g_map and "5月" in g_map else None
    return sum(g_map.values()), sum(g_map.values()) / len(g_map), drop, may

nv_total, nv_avg, nv_drop, nv_may = metrics_for(nv_fm)
nv_units = sum(NAILVESTA_FASTMOSS["销量"])
nv_asp = nv_total / nv_units if nv_units else 0

np_map = dict(zip(COMPETITORS["Nailphoria"]["月份"], COMPETITORS["Nailphoria"]["GMV"]))
np_total, np_avg, np_drop, np_may = metrics_for(np_map)
np_units = sum(COMPETITORS["Nailphoria"]["销量"])
np_asp = np_total / np_units if np_units else 0

nh_map = dict(zip(COMPETITORS["NailHaven"]["月份"], COMPETITORS["NailHaven"]["GMV"]))
nh_total, nh_avg, nh_drop, nh_may = metrics_for(nh_map)
nh_units = sum(COMPETITORS["NailHaven"]["销量"])
nh_asp = nh_total / nh_units if nh_units else 0

# 動態建表：NailVesta + 所有競品
def brand_units(b):
    return sum(NAILVESTA_FASTMOSS["销量"]) if b == "NailVesta" else sum(COMPETITORS[b]["销量"])

def brand_gmap(b):
    return nv_fm if b == "NailVesta" else dict(zip(COMPETITORS[b]["月份"], COMPETITORS[b]["GMV"]))

table = {"指標": ["1–5月總 GMV", "平均月 GMV", "件單價(ASP)", "1→4月變化", "5月環比",
                 "美妝月榜(05)", "店舖評分", "48h出貨率", "定位"]}
for b in ["NailVesta"] + list(COMPETITORS.keys()):
    gm = brand_gmap(b)
    tot, avg, drp, mayv = metrics_for(gm)
    asp = tot / brand_units(b)
    meta = STORE_META.get(b, {})
    table[b] = [
        f"${tot:,.0f}", f"${avg:,.0f}", f"${asp:,.1f}", pct(drp), pct(mayv),
        meta.get("月榜", "—"), meta.get("评分", "—"), meta.get("48h出货", "—"), meta.get("定位", "—"),
    ]
st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="analysis-box">

<div class="section-title">三家其實是「兩種打法」</div>

<b>1. GMV 三家同量級，但你和 Nailphoria 是一組、NailHaven 是另一組</b><br>
5個月總 GMV：你 <b>${nv_total:,.0f}</b>、Nailphoria <b>${np_total:,.0f}</b>、NailHaven <b>${nh_total:,.0f}</b>——
規模都在 $1.6M–1.9M，差距不到 15%。但件單價天差地遠：你和它約 <b>$36</b>，NailHaven 只有 <b>${nh_asp:,.1f}</b>。
NailHaven 是用 <b>3 倍的件數、1/3 的單價</b>做到同樣的 GMV——典型低價走量。

<br><br>

<b>2. 季節性其實分「兩種」，不是整個賽道一致（修正上一輪）</b><br>
你和 Nailphoria（高端內容型）都是 1月高→4月底→5月回升；
但 NailHaven <b>反過來</b>：1→4月還 <b>{pct(nh_drop)}</b>（上升）、5月再 <b>{pct(nh_may)}</b>，5月是它全期最高。
原因是它 <b>66.81% GMV 來自商品卡（搜尋/自然流）</b>，需求不靠達人內容,所以沒有 Q1 內容紅利的退潮,
反而吃到夏季美甲的自然搜尋成長。<b>所以那條季節曲線是「高端內容型」的特性,不是全品類鐵律。</b>

<br><br>

<b>3. 它最該讓你注意的不是價格，是「商品卡」</b><br>
NailHaven 商品卡佔 66.81%、你只有 29.34%。它靠少量常青款（命名都叫 "Continued Collection"）長期吃搜尋流量;
你走的是一波波「系列上新」,偏內容驅動。<b>你在搜尋/商品卡這條自然流量上是吃虧的</b>,
這也是為什麼你比較吃季節（內容退潮就掉），它比較穩（搜尋需求全年都在）。

<div class="section-title">給你的取捨</div>
<ul>
<li><b>不要去拼 NailHaven 的低價走量</b>：那會毀掉你 $36 的高端定位和毛利,不是你的戰場。</li>
<li><b>但要偷它的「常青款 + 商品卡」打法</b>：留幾個長賣不退的款式做 SEO/搜尋承接,把 29% 的商品卡佔比往上拉,
就能在淡季（內容紅利退潮時）墊住 GMV,降低你對季節的敏感度。</li>
<li><b>它在美妝月榜 #178 比你（#192）和 Nailphoria（#209）都前面</b>——靠的是走量帶來的高件數/高動銷,提醒你榜單權重看「量」。</li>
</ul>

<span class="small-note">三品牌均為 FastMoss 2026-06-18 月度卡片（全店口徑）。成交結構為 FastMoss 聚合值。</span>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 直播 / 成交結構分析
# =========================================================

st.subheader("直播 & 成交結構：你的自播其實不弱")

method_df = pd.DataFrame({
    "方式": list(NAILVESTA_METHOD.keys()),
    "佔比": list(NAILVESTA_METHOD.values()),
})
method_chart = alt.Chart(method_df).mark_bar().encode(
    x=alt.X("佔比:Q", title="佔總 GMV %"),
    y=alt.Y("方式:N", sort="-x", title=""),
    color=alt.Color("方式:N", scale=alt.Scale(
        domain=["视频", "直播", "商品卡"], range=["#7b4fc0", "#e8623c", "#9aa0a6"]), legend=None),
    tooltip=["方式", alt.Tooltip("佔比:Q", format=".2f")],
).properties(height=160)
labels = alt.Chart(method_df).mark_text(align="left", dx=4, fontWeight="bold").encode(
    x="佔比:Q", y=alt.Y("方式:N", sort="-x"), text=alt.Text("佔比:Q", format=".1f"),
)
st.markdown("**NailVesta 成交方式分布**")
st.altair_chart(method_chart + labels, use_container_width=True)

st.markdown(f"""
<div class="analysis-box">

之前我說「自播是你最大缺口」——看了真實數據要<b>修正</b>：你的自播一點都不弱。

<ul>
<li><b>直播已佔你 GMV 的 {NAILVESTA_METHOD['直播']}%</b>，自營號管道佔 {NAILVESTA_CHANNEL['店铺自营号']}%，你早就有在做自播。</li>
<li><b>而且你的直播效率很高</b>：自家官方號直播 GPM <b>{NV_OWN['直播GPM']}</b>，影片 GPM 只有 {NV_OWN['视频GPM']}——
直播每千次觀看的成交是影片的 <b>5–7 倍</b>。</li>
<li>對照 Nailphoria：它官方號近28天帶 <b>$201,800</b>、你帶 <b>${NV_OWN['销售额']:,}</b>（約它的一半），
但它的直播 GPM 只有 $10.94–$14.23，<b>反而比你低</b>。也就是說它靠「量」（更多場、更大號），你靠「效率」。</li>
</ul>

<b>結論：你該做的不是「從零建自播」，而是「把已經很賺的自播放大」</b>——
你每場直播的轉化比 Nailphoria 好，缺的只是場次、時長與觀看量。
把資源從低效的影片(GPM 只有 $3–4)往直播挪，是現成的增長槓桿。

<span class="small-note">成交結構為 FastMoss 聚合值；GPM、自營號銷售額為近28天數據。</span>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 達人結構分析
# =========================================================
# 達人結構分析
# =========================================================

st.subheader("達人結構分析")

st.markdown(f"""
<div class="analysis-box">

你之前提供：

<ul>
<li>合作創作者：<b>{COLLAB_CREATORS:,}</b></li>
<li>出單創作者：<b>{ORDER_CREATORS:,}</b></li>
</ul>

轉化率：

<br>

<b>{ORDER_CREATORS} / {COLLAB_CREATORS} = {conv_rate:.2f}%</b>

<br><br>

這個轉化率其實非常健康，問題不在於合作數量，而在於 <b>頭部貢獻過高</b>。

<br><br>

Top10 達人 GMV：<b>\\${TOP10_GMV:,}</b>

<br><br>

佔整體（以 5月 GMV 為基準）：

<br>

<b>{TOP10_GMV:,} / {may:,.0f} = {top10_share:.1f}%</b>

<br><br>

代表接近一半 GMV 來自 10 位達人，這個風險非常大。

</div>
""", unsafe_allow_html=True)

# =========================================================
# 下半年預測
# =========================================================

st.subheader("下半年 GMV 預測")

forecast_df = pd.DataFrame(FORECAST_DATA).set_index("月份")
st.line_chart(forecast_df, height=320)

st.markdown(r"""
<div class="analysis-box">

<b>6月：</b> 夏季美甲開始進入旺季，預估 <b>\$105k-\$115k</b><br>
<b>7月：</b> 暑假流量，預估 <b>\$110k-\$125k</b><br>
<b>8月：</b> Back to School，預估 <b>\$120k-\$135k</b><br>
<b>9月：</b> 通常小回落，預估 <b>\$110k-\$125k</b><br>
<b>10月：</b> Halloween，預估 <b>\$125k-\$145k</b><br>
<b>11月：</b> Black Friday，預估 <b>\$180k-\$250k</b><br>
<b>12月：</b> Christmas，預估 <b>\$200k-\$300k</b>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 經營結論
# =========================================================

st.subheader("企業經營角度結論")

st.markdown(f"""
<div class="analysis-box">

目前 NailVesta 最大的問題不是流量，而是：

<br><br>

<b>1. 深達數量不足</b><br>
目前 {DEEP_GMV_SHARE}% GMV 來自深達，代表深達是核心引擎。

<br><br>

<b>2. 新深達養成速度太慢</b><br>
你之前數據顯示 {UNCONVERTED_BROAD} 位廣達未轉化，這是最大的增長空間。

<br><br>

<b>3. S級影片比例不夠高</b><br>
Week76 數據：

<ul>
<li>S：{VIDEO['S']}支</li>
<li>AK：{VIDEO['AK']}支</li>
<li>AS：{VIDEO['AS']}支</li>
<li>C：{VIDEO['C']}支</li>
</ul>

S + AK 佔比：

<br>

<b>{s_ak} / {video_total} = {s_ak_ratio:.1f}%</b>

<br><br>

如果能提升到 <b>60%-65%</b>，GMV 通常還有 <b>15%-30%</b> 成長空間。

<br><br>

<b>總結：</b><br>
從目前數據來看，1月到4月下跌符合市場季節性，5月已出現反轉訊號，品牌沒有衰退跡象。真正瓶頸在於 <b>深達擴張速度</b> 和 <b>高品質內容比例</b>。

<br><br>

如果 6月到8月能做到：

<ul>
<li>深達規模提升 20%</li>
<li>S + AK 影片比例提升到 60%以上</li>
<li>每月新增 10-15 位穩定出單深達</li>
</ul>

NailVesta 在 2026 下半年有機會穩定突破 <b>每月 \\$150k+ GMV</b>，11月到12月有機會挑戰 <b>\\$250k+ 單月 GMV</b>。

</div>
""", unsafe_allow_html=True)
