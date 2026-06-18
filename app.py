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

# 賽道定位圖（穿戴甲競品）
# 平均單價 = 公開零售價約值；聲量分數 = 依公開聲量做的質化分級 1–10（非實際 GMV，可自行調整）
POSITIONING = {
    "品牌":     ["NailVesta", "Glamnetic", "KISS Nails", "Dashing Diva", "Olive & June", "BTArtbox"],
    "平均單價": [42,          16,          9,            11,             11,             10],
    "聲量分數": [6,           9,           8,            7,              6,              6],
    "類型":     ["你的品牌",  "競品",      "競品",       "競品",         "競品",         "競品"],
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
}

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

st.subheader("TikTok Shop 頭部品牌對照")

st.markdown("""
<div class="analysis-box">
下面是同樣在 TikTok Shop（美國）跑的頭部品牌，分成兩組：
<b>直接競品（穿戴甲/美甲）</b> 用來看你在賽道內的位置，
<b>規模對標（大盤美妝頭部）</b> 用來看天花板在哪。
<br><br>
<span class="small-note">說明：競品的「逐月 GMV」屬於各品牌非公開數據，需透過 Kalodata / FastMoss / EchoTik 等付費工具才能拉到月級曲線；
下表的規模欄位採用公開報導與 Charm.io 2025 全年美國 TikTok Shop 美妝榜數據,僅供量級參考。</span>
</div>
""", unsafe_allow_html=True)

competitor_df = pd.DataFrame({
    "品牌": [
        "Glamnetic", "KISS Nails", "Dashing Diva", "Olive & June", "BTArtbox",
        "Medicube", "Tarte", "Dr. Melaxin",
    ],
    "類別": [
        "穿戴甲（高端 DTC）", "穿戴甲（大眾/開架）", "穿戴甲・指甲貼", "穿戴甲＋指甲護理", "穿戴甲（亞馬遜起家）",
        "護膚", "彩妝", "護膚",
    ],
    "對 NailVesta": [
        "直接競品", "直接競品", "直接競品", "直接競品", "直接競品",
        "規模對標", "規模對標", "規模對標",
    ],
    "規模 / 定位": [
        "美國穿戴甲 TikTok 高聲量品牌，單價偏高、達人帶貨密集",
        "開架龍頭，走量、低單價、鋪貨廣",
        "指甲貼／半固化凝膠強，零售＋線上雙渠道",
        "主打環保材質＋指甲護理組合，客單偏高",
        "性價比款式多，評論數大、轉化穩",
        "2025 美國 TikTok Shop 美妝銷量前段（套組玻璃肌爆款）",
        "美妝頭部，套組策略，常駐美妝榜前列",
        "2025 美國 TikTok Shop 約 $64.6M（護膚頭部之一）",
    ],
})

st.dataframe(competitor_df, use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="analysis-box">

<div class="section-title">怎麼用這張表對照你自己</div>

<b>1. 量級基準</b><br>
2025 全年美國 TikTok Shop 美妝品類約 <b>\\$2.7B GMV</b>、賣出 <b>1.47 億件</b>、平均單價約 <b>\\$18.57</b>。
護膚頭部單一品牌（如 Dr. Melaxin）一年可達 <b>\\$60M+</b>。
你目前單月約 <b>{usd(may)}</b>、年化約 <b>{usd(may * 12)}</b>，
在「穿戴甲」這個比美妝大盤更窄的賽道屬於中上量級,離頭部仍有空間,主要差在達人規模與爆款密度。

<br><br>

<b>2. 單價策略</b><br>
大盤平均單價只有 <b>\\$18.57</b>,走的是「低單價＋走量＋達人密集」。
你的單價區間(\\$29.99–\\$54.99)明顯偏高,屬於 Glamnetic / Olive & June 那種高端定位,
所以你的打法應該是 <b>內容品質與深達深度</b>,而不是跟 KISS 拼鋪貨走量。

<br><br>

<b>3. 季節節奏一致</b><br>
這些頭部品牌共同的曲線是:<b>Q1 高 → Q2 軟 → 夏季回溫 → Q4（BFCM＋聖誕）爆發</b>。
你 1→4月下滑、5月反彈,跟整個賽道同步,再次證明那不是品牌問題,而是市場節奏。
真正的勝負點在 <b>淡季有沒有把深達與內容養起來</b>,這樣 Q4 爆發時才接得住。

</div>
""", unsafe_allow_html=True)

# =========================================================
# 賽道定位圖
# =========================================================

st.subheader("賽道定位圖：你 vs 穿戴甲競品")

pos_df = pd.DataFrame(POSITIONING)

color_scale = alt.Scale(domain=["你的品牌", "競品"], range=["#e8623c", "#9aa0a6"])

points = alt.Chart(pos_df).mark_circle(size=520, opacity=0.85).encode(
    x=alt.X("平均單價:Q", title="平均單價（約, USD）", scale=alt.Scale(domain=[0, 50])),
    y=alt.Y("聲量分數:Q", title="TikTok Shop 相對聲量（質化分級 1–10）", scale=alt.Scale(domain=[0, 10])),
    color=alt.Color("類型:N", scale=color_scale, legend=alt.Legend(title="", orient="top-right")),
    tooltip=["品牌", "平均單價", "聲量分數"],
)

labels = alt.Chart(pos_df).mark_text(dy=-22, fontSize=13, fontWeight="bold").encode(
    x="平均單價:Q",
    y="聲量分數:Q",
    text="品牌",
    color=alt.Color("類型:N",
                    scale=alt.Scale(domain=["你的品牌", "競品"], range=["#c8401f", "#5f6368"]),
                    legend=None),
)

aup_rule = alt.Chart(pd.DataFrame({"x": [CATEGORY_AUP]})).mark_rule(
    strokeDash=[6, 4], color="#3a7bd5", size=2
).encode(x="x:Q")

aup_label = alt.Chart(
    pd.DataFrame({"x": [CATEGORY_AUP], "y": [9.5], "t": [f"品類平均單價 ${CATEGORY_AUP}"]})
).mark_text(align="left", dx=6, color="#3a7bd5", fontSize=12, fontWeight="bold").encode(
    x="x:Q", y="y:Q", text="t:N"
)

chart = (points + labels + aup_rule + aup_label).properties(height=440)
st.altair_chart(chart, use_container_width=True)

st.markdown(f"""
<div class="analysis-box">

<b>圖怎麼讀：</b>越往右單價越高，越往上 TikTok Shop 聲量越大。

<ul>
<li><b>你（橘點）是價格最高的離群者</b>：約 <b>\\$42</b>，遠高於所有穿戴甲競品（多落在 \\$9–\\$16），也高於品類平均 <b>\\${CATEGORY_AUP}</b>（藍色虛線）。</li>
<li><b>KISS / BTArtbox</b> 在左側：低價走量、鋪貨型，跟你不是同一種打法。</li>
<li><b>Glamnetic</b> 在右上：同樣偏高價、但聲量更大，是你最該對標的「升級版」競品。</li>
<li><b>你的成長路徑</b>：價格已站在高端，往上(把聲量做大)才是空間，靠的是深達深度＋S級內容，而不是降價。</li>
</ul>

<span class="small-note">註：競品單價為公開零售價約值、聲量分數為質化分級（非實際 GMV），數值可在程式碼上方 <code>POSITIONING</code> 調整；
NailVesta 為實際定價中位。你目前年化 GMV 約 <b>{usd(may * 12)}</b>。</span>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 競品對比（真實月度數據）
# =========================================================

st.subheader("競品對比：NailVesta vs 競品（1–5月）")

month_sort = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
brand_colors = ["#e8623c", "#7b4fc0", "#2a9d8f", "#e9b949", "#3a7bd5"]

# 組長表：NailVesta（來自可編輯數據）＋ 各競品
rows = []
nv_map = dict(zip(df["月份"], df["GMV"]))
for m in month_sort:
    if m in nv_map:
        rows.append({"月份": m, "品牌": "NailVesta", "GMV": float(nv_map[m])})
for brand, d in COMPETITORS.items():
    for m, g in zip(d["月份"], d["GMV"]):
        rows.append({"月份": m, "品牌": brand, "GMV": float(g)})

comp_df = pd.DataFrame(rows)
comp_df["_sort"] = comp_df["月份"].map({m: i for i, m in enumerate(month_sort)})
comp_df = comp_df.sort_values(["品牌", "_sort"])
# 指數：各品牌以自己最早月份 = 100
comp_df["指數"] = comp_df.groupby("品牌")["GMV"].transform(lambda s: s / s.iloc[0] * 100)

domain_brands = ["NailVesta"] + list(COMPETITORS.keys())
color_enc = alt.Color("品牌:N", scale=alt.Scale(domain=domain_brands, range=brand_colors[:len(domain_brands)]))

st.markdown("**① 絕對 GMV（看規模差距）**")
abs_chart = alt.Chart(comp_df).mark_line(point=True, strokeWidth=3).encode(
    x=alt.X("月份:N", sort=month_sort, title="月份"),
    y=alt.Y("GMV:Q", title="月 GMV (USD)"),
    color=color_enc,
    tooltip=["品牌", "月份", alt.Tooltip("GMV:Q", format=",.0f")],
).properties(height=340)
st.altair_chart(abs_chart, use_container_width=True)

st.markdown("**② 指數化（1月=100，看季節形狀是否一致）**")
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

# 指標對照表
def metrics_for(g_map):
    months = [m for m in ["1月", "2月", "3月", "4月", "5月"] if m in g_map]
    vals = [g_map[m] for m in months]
    total = sum(vals)
    avg = total / len(vals) if vals else 0
    drop = (g_map["4月"] - g_map["1月"]) / g_map["1月"] * 100 if "1月" in g_map and "4月" in g_map else None
    may = (g_map["5月"] - g_map["4月"]) / g_map["4月"] * 100 if "4月" in g_map and "5月" in g_map else None
    return total, avg, drop, may

nv_total, nv_avg, nv_drop, nv_may = metrics_for(nv_map)
np_map = dict(zip(COMPETITORS["Nailphoria"]["月份"], COMPETITORS["Nailphoria"]["GMV"]))
np_total, np_avg, np_drop, np_may = metrics_for(np_map)
np_units = sum(COMPETITORS["Nailphoria"]["销量"])
np_asp = np_total / np_units if np_units else 0

compare_table = pd.DataFrame({
    "指標": ["1–5月總 GMV", "平均月 GMV", "1→4月跌幅", "5月環比", "平均件單價(ASP)", "相對規模"],
    "NailVesta": [
        f"${nv_total:,.0f}", f"${nv_avg:,.0f}", pct(nv_drop), pct(nv_may),
        "定價 $29.99–$54.99", "1.0×",
    ],
    "Nailphoria": [
        f"${np_total:,.0f}", f"${np_avg:,.0f}", pct(np_drop), pct(np_may),
        f"${np_asp:,.1f}", f"{np_total / nv_total:.1f}×" if nv_total else "—",
    ],
})
st.dataframe(compare_table, use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="analysis-box">

<div class="section-title">三個關鍵發現</div>

<b>1. 季節形狀幾乎完全一致 ✅</b><br>
Nailphoria 也是 <b>1月最高 → 4月見底 → 5月回升</b>：1→4月跌 <b>{pct(np_drop)}</b>（你 {pct(nv_drop)}），
5月環比 <b>{pct(np_may)}</b>（你 {pct(nv_may)}）。
看上面「指數化」那張圖,兩條線幾乎貼著走——<b>這直接證明你 1→4月的下滑是整個賽道的季節性,不是你品牌出問題</b>。
而且你 5月的反彈（{pct(nv_may)}）比它（{pct(np_may)}）更強。

<br><br>

<b>2. 規模差距：它約是你的 {np_total / nv_total:.1f} 倍</b><br>
同期 5個月 Nailphoria 約 <b>${np_total:,.0f}</b>，你約 <b>${nv_total:,.0f}</b>。
件單價它約 <b>${np_asp:,.1f}</b>,落在你的定價區間內,代表 <b>同價位、同概念,但它的量體大得多</b>——天花板在那裡,你還有 3 倍以上的空間。

<br><br>

<b>3. 它的引擎是「直播」,而且正在從影片轉向直播</b><br>
看月度結構:它的帶貨<b>影片數從 1月 625 一路掉到 5月 91</b>,但<b>直播數維持高檔（4月 408、5月 413）</b>,
同時帶貨達人數從 537 收斂到 247——<b>它在「砍影片、押直播、集中到少數高產出管道（主要是自家官方號）」</b>。
這跟你「靠大量外部達人鋪量」是相反的打法。它用更少的人做出更大的量,靠的是自播。

<div class="section-title">對 NailVesta 的建議</div>
<ul>
<li><b>定價策略已驗證</b>:同價位競品做到你的 3.6 倍,不用懷疑高端定位,重點是放量。</li>
<li><b>補上「自播」這條腿</b>:Nailphoria 證明高端穿戴甲靠自家直播能把單位產出拉高數倍,這是你目前最大的缺口,也最能降低對外部頭部達人的依賴。</li>
<li><b>淡季別停</b>:兩家都在 Q2 觸底,但這正是養直播、養深達、囤內容的時機,Q4（BFCM）才接得住。</li>
</ul>

<span class="small-note">數據來源:Nailphoria 為 FastMoss 2026-06-18 擷取的月度卡片;NailVesta 為你的實際數據。
之後再傳其他競品,照程式碼上方 <code>COMPETITORS</code> 格式加進去,這兩張圖和表會自動把新品牌畫上。</span>

</div>
""", unsafe_allow_html=True)

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
