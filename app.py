# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

col1, col2, col3, col4 = st.columns(4)

col1.metric("總 GMV", f"${total_gmv:,.2f}")
col2.metric("平均月 GMV", f"${avg_gmv:,.2f}")
col3.metric("最高月份", f"{max_month['月份']}", f"${max_month['GMV']:,.2f}")
col4.metric("最低月份", f"{min_month['月份']}", f"${min_month['GMV']:,.2f}")

st.subheader("GMV 數據表")

display_df = df.copy()
display_df["GMV"] = display_df["GMV"].map(lambda x: f"${x:,.2f}")
display_df["月增率"] = display_df["月增率"].map(lambda x: "-" if pd.isna(x) else f"{x:.2f}%")
display_df["GMV佔比"] = display_df["GMV佔比"].map(lambda x: f"{x:.2f}%")

st.dataframe(display_df, use_container_width=True)

st.subheader("GMV 趨勢圖")

fig, ax = plt.subplots()
ax.plot(df["月份"], df["GMV"], marker="o")
ax.set_xlabel("月份")
ax.set_ylabel("GMV")
ax.set_title("Monthly GMV Trend")

for i, value in enumerate(df["GMV"]):
    ax.text(i, value, f"${value:,.0f}", ha="center", va="bottom")

st.pyplot(fig)

st.subheader("月增率分析")

growth_df = df.dropna()

fig2, ax2 = plt.subplots()
ax2.bar(growth_df["月份"], growth_df["月增率"])
ax2.axhline(0)
ax2.set_xlabel("月份")
ax2.set_ylabel("月增率 %")
ax2.set_title("Month-over-Month Growth Rate")

for i, value in enumerate(growth_df["月增率"]):
    ax2.text(i, value, f"{value:.2f}%", ha="center", va="bottom" if value >= 0 else "top")

st.pyplot(fig2)

st.subheader("專業分析結論")

st.write(f"""
從目前 1月到5月 GMV 來看，NailVesta 總 GMV 為 **${total_gmv:,.2f}**，
平均每月 GMV 為 **${avg_gmv:,.2f}**。

最高收益月份是 **{max_month['月份']}**，GMV 為 **${max_month['GMV']:,.2f}**。

最低收益月份是 **{min_month['月份']}**，GMV 為 **${min_month['GMV']:,.2f}**。

整體趨勢是：1月最高，2月到4月連續下降，5月開始反彈。
這代表前期受到淡季影響，但5月已經出現恢復成長的訊號。
""")

st.subheader("經營建議")

st.markdown("""
### 1. 5月已經出現回升
4月到5月 GMV 成長，代表品牌不是持續衰退，而是進入修復期。

### 2. 需要重點放大高品質達人內容
如果能提高 S / AK 類影片比例，GMV 有機會繼續往上拉。

### 3. 6月到8月可以主打夏季款
美甲類產品在夏季、度假、婚禮季會有較強需求。

### 4. 10月到12月要提前布局
Halloween、Black Friday、Christmas 是 TikTok Shop 美妝類全年最重要的收益高峰。
""")
