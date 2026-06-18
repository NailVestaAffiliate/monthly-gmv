import streamlit as st
import pandas as pd

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
    return "—" if v is None or pd.isna(v) else f"${v:,.2f}"

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

<br><br>

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

Top10 達人 GMV：<b>${TOP10_GMV:,}</b>

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

st.markdown("""
<div class="analysis-box">

<b>6月：</b> 夏季美甲開始進入旺季，預估 <b>$105k-$115k</b><br>
<b>7月：</b> 暑假流量，預估 <b>$110k-$125k</b><br>
<b>8月：</b> Back to School，預估 <b>$120k-$135k</b><br>
<b>9月：</b> 通常小回落，預估 <b>$110k-$125k</b><br>
<b>10月：</b> Halloween，預估 <b>$125k-$145k</b><br>
<b>11月：</b> Black Friday，預估 <b>$180k-$250k</b><br>
<b>12月：</b> Christmas，預估 <b>$200k-$300k</b>

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

NailVesta 在 2026 下半年有機會穩定突破 <b>每月 $150k+ GMV</b>，11月到12月有機會挑戰 <b>$250k+ 單月 GMV</b>。

</div>
""", unsafe_allow_html=True)
