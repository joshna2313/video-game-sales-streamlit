import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")

# ---------------- TITLE ----------------
st.title("Video Game Sales & Ratings Dashboard")

st.markdown("""
This interactive dashboard explores global video game sales across
different years, genres, and platforms.
Use the filters on the left to explore trends and top-performing games.
""")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("Video_Games_Sales_as_at_22_Dec_2016-checkpoint.csv")
    return df

df = load_data()
df.columns = df.columns.str.lower()

# ---------------- CLEAN DATA ----------------
df['user_score'] = df['user_score'].replace('tbd', pd.NA)
df['user_score'] = pd.to_numeric(df['user_score'])
df = df.dropna(subset=['year_of_release', 'global_sales'])
df['year_of_release'] = df['year_of_release'].astype(int)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df['year_of_release'].min()),
    int(df['year_of_release'].max()),
    (2000, 2015)
)

genres = st.sidebar.multiselect(
    "Select Genre(s)",
    options=df['genre'].unique(),
    default=df['genre'].unique()
)

platforms = st.sidebar.multiselect(
    "Select Platform(s)",
    options=df['platform'].unique(),
    default=df['platform'].unique()
)

filtered_df = df[
    (df['year_of_release'] >= year_range[0]) &
    (df['year_of_release'] <= year_range[1]) &
    (df['genre'].isin(genres)) &
    (df['platform'].isin(platforms))
]

# ---------------- KPIs ----------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

total_sales = filtered_df['global_sales'].sum()

top_genre = (
    filtered_df.groupby('genre')['global_sales'].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

top_platform = (
    filtered_df.groupby('platform')['global_sales'].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

col1.metric("Total Global Sales (M)", f"{total_sales:.2f}")
col2.metric("Top Genre", top_genre)
col3.metric("Top Platform", top_platform)

# ---------------- CHARTS ----------------
st.subheader("Sales Overview")

col1, col2 = st.columns(2)

# Sales over time
with col1:
    sales_by_year = (
        filtered_df.groupby('year_of_release')['global_sales']
        .sum()
        .reset_index()
    )

    fig1, ax1 = plt.subplots()
    ax1.plot(
        sales_by_year['year_of_release'],
        sales_by_year['global_sales'],
        color='steelblue'
    )
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Global Sales (M)")
    st.pyplot(fig1)

# Sales by genre
with col2:
    genre_sales = (
        filtered_df.groupby('genre')['global_sales']
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots()
    ax2.bar(
        genre_sales.index,
        genre_sales.values,
        color='teal'
    )
    ax2.set_xlabel("Genre")
    ax2.set_ylabel("Global Sales (M)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

#sales by Platform
    st.subheader("Sales by Platform")
platform_sales = (
    filtered_df
    .groupby('platform')['global_sales']
    .sum()
    .sort_values(ascending=False)
)

fig3, ax3 = plt.subplots()
ax3.bar(
    platform_sales.index,
    platform_sales.values,
    color='darkorange'
)
plt.xticks(rotation=90)
ax3.set_xlabel("Platform")
ax3.set_ylabel("Global Sales (M)")
st.pyplot(fig3)

# critic score vs gloabal sales
st.subheader("Critic Score vs Global Sales")

fig4, ax4 = plt.subplots()
ax4.scatter(
    filtered_df['critic_score'],
    filtered_df['global_sales'],
    alpha=0.6,
    color='purple'
)
ax4.set_xlabel("Critic Score")
ax4.set_ylabel("Global Sales")
st.pyplot(fig4)




# ---------------- TABLE ----------------
st.subheader("Top 10 Games by Global Sales")

top_games = (
    filtered_df
    .groupby('name')['global_sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(top_games)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Data Source: Kaggle – Video Game Sales with Ratings")
