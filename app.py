import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NailVesta GMV Dashboard", layout="wide")

st.title("NailVesta TikTok Shop GMV 分析 Dashboard")

data = {
    "月份": ["1月", "2月", "3月", "4月", "5月"],
    "GMV": [125296.69, 110102.54, 100055.38, 95443.74, 103197.84]
}

df = pd.DataFrame(data)
df["月增率"] = df["GMV"].pct_change() * 100
df["GMV佔比"] = df["GMV"] / df["GMV"].sum() * 100

total_gmv = df["GMV"].sum()
avg_gmv = df["GMV"].mean()
max_month = df.loc[df["GMV"].idxmax()]
min_month = df.loc[df["GMV"].idxmin()]

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}
.metric-card {
    background: #ffffff;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #eee;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}
.analysis-box {
    background: #fff8f5;
    padding: 22px 26px;
    border-radius: 18px;
    border: 1px solid #f0d8cf;
    line-height: 1.8;
}
.small-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("總 GMV", f"${total_gmv:,.2f}")
col2.metric("平均月 GMV", f"${avg_gmv:,.2f}")
col3.metric("最高月份", f"{max_month['月份']}", f"${max_month['GMV']:,.2f}")
col4.metric("最低月份", f"{min_month['月份']}", f"${min_month['GMV']:,.2f}")

st.divider()

st.subheader("GMV 數據表")

display_df = df.copy()
display_df["GMV"] = display_df["GMV"].map(lambda x: f"${x:,.2f}")
display_df["月增率"] = display_df["月增率"].map(lambda x: "-" if pd.isna(x) else f"{x:.2f}%")
display_df["GMV佔比"] = display_df["GMV佔比"].map(lambda x: f"{x:.2f}%")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("GMV 趨勢圖")
    fig = px.line(
        df,
        x="月份",
        y="GMV",
        markers=True,
        text=df["GMV"].map(lambda x: f"${x/1000:.1f}k"),
        title=""
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="GMV",
        xaxis_title="月份",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("月增率變化")
    growth_df = df.dropna()

    fig2 = px.bar(
        growth_df,
        x="月份",
        y="月增率",
        text=growth_df["月增率"].map(lambda x: f"{x:.2f}%"),
        title=""
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="月增率 %",
        xaxis_title="月份",
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("專業趨勢分析")

st.markdown("""
<div class="analysis-box">

<div class="small-title">第一階段：1月 → 4月連續下滑</div>

從 1月的 <b>$125,296.69</b> 下降到 4月的 <b>$95,443.74</b>。

<br><br>

總跌幅：

<b>(95,443.74 - 125,296.69) / 125,296.69 = -23.83%</b>

<br><br>

代表前四個月累積下滑約 <b>23.8%</b>。

<br><br>

這其實非常符合 TikTok Shop 美國市場的季節性規律。

<br><br>

<b>1月：</b><br>
聖誕節後流量仍在，許多品牌延續 Holiday 流量，Creator 庫存內容持續出單，所以通常是 Q1 最強月份。

<br><br>

<b>2月：</b><br>
開始進入淡季。原因包括消費者信用卡帳單開始出現、節日消費結束、TikTok CPM 通常下降、整體消費意願變弱。  
<br>
你的跌幅為 <b>-12.13%</b>，屬於正常範圍。

<br><br>

<b>3月：</b><br>
通常是全年第二個低谷。原因包括沒有大型購物節、稅務季、消費者支出保守。  
<br>
你的跌幅為 <b>-9.13%</b>，也是正常。

<br><br>

<b>4月：</b><br>
理論上應該開始回升，但你仍下降 <b>-4.61%</b>。  
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

<div class="small-title">第二階段：5月反彈</div>

4月 GMV：<b>$95,443.74</b><br>
5月 GMV：<b>$103,197.84</b>

<br><br>

成長率：

<b>(103,197.84 - 95,443.74) / 95,443.74 = 8.13%</b>

<br><br>

代表：

<ul>
<li>品牌已經停止下跌</li>
<li>開始重新進入成長</li>
</ul>

</div>
""", unsafe_allow_html=True)

st.subheader("達人結構分析")

st.markdown("""
<div class="analysis-box">

你之前提供：

<ul>
<li>合作創作者：<b>1,061</b></li>
<li>出單創作者：<b>392</b></li>
</ul>

轉化率：

<b>392 / 1,061 = 36.95%</b>

<br><br>

這個轉化率其實非常健康，問題不在於合作數量，而在於 <b>頭部貢獻過高</b>。

<br><br>

Top10 達人 GMV：<b>$44,621</b>

<br><br>

佔整體：

<b>44,621 / 103,197 = 43.2%</b>

<br><br>

代表接近一半 GMV 來自 10 位達人，這個風險非常大。

</div>
""", unsafe_allow_html=True)

st.subheader("下半年 GMV 預測")

forecast_data = {
    "月份": ["6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    "低預估": [105000, 110000, 120000, 110000, 125000, 180000, 200000],
    "高預估": [115000, 125000, 135000, 125000, 145000, 250000, 300000]
}

forecast_df = pd.DataFrame(forecast_data)

fig3 = px.line(
    forecast_df,
    x="月份",
    y=["低預估", "高預估"],
    markers=True,
    title=""
)

fig3.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis_title="預估 GMV",
    xaxis_title="月份",
    template="plotly_white",
    legend_title_text="預測區間"
)

st.plotly_chart(fig3, use_container_width=True)

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

st.subheader("企業經營角度結論")

st.markdown("""
<div class="analysis-box">

目前 NailVesta 最大的問題不是流量，而是：

<br><br>

<b>1. 深達數量不足</b><br>
目前 72.2% GMV 來自深達，代表深達是核心引擎。

<br><br>

<b>2. 新深達養成速度太慢</b><br>
你之前數據顯示 124 位廣達未轉化，這是最大的增長空間。

<br><br>

<b>3. S級影片比例不夠高</b><br>
Week76 數據：

<ul>
<li>S：51支</li>
<li>AK：42支</li>
<li>AS：30支</li>
<li>C：47支</li>
</ul>

S + AK 佔比：

<b>93 / 189 = 49.2%</b>

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
