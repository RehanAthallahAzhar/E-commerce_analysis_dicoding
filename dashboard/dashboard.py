import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_revenue_resume(df):
    # Mengubah index menjadi nama bulan
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    five_monthly_orders_ago_df = df.resample(rule='M', on='order_approved_at').agg({
    "order_id": "nunique",
    "price": "sum"
    }).sort_values(by=("order_approved_at"), ascending=False)[1:6]
    five_monthly_orders_ago_df = five_monthly_orders_ago_df.sort_values(by=("order_approved_at"), ascending=True)
    five_monthly_orders_ago_df.index = five_monthly_orders_ago_df.index.strftime('%Y-%m')
    five_monthly_orders_ago_df = five_monthly_orders_ago_df.reset_index()
    five_monthly_orders_ago_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)


    # Mengubah index menjadi nama bulan
    five_monthly_orders_ago_df['order_approved_at'] = pd.to_datetime(five_monthly_orders_ago_df['order_approved_at']).dt.strftime('%B')

    return five_monthly_orders_ago_df

def filter_best_product(df):
    # Membuat pivot table untuk menghitung jumlah penjualan (order_id) per kategori dan rating
    pivot_table = df.pivot_table(
        index='product_category_name_english',  
        columns='review_score', 
        values='order_id', 
        aggfunc='nunique',  
        fill_value=0 
    )

    pivot_table['total_sales'] = pivot_table.sum(axis=1)

    # Menghitung rata-rata rating untuk setiap kategori produk
    average_rating = df.groupby('product_category_name_english')['review_score'].mean()

    pivot_table['average_rating'] = average_rating

    pivot_table_sorted = pivot_table.sort_values(by='total_sales', ascending=False)

    pivot_table_sorted.index = pivot_table_sorted.index.str.replace('_', ' ')

    return pivot_table_sorted

def create_popular_payment_type(df):
    # Mengelompokkan data berdasarkan 'payment_type'
    grouped_data = df.groupby(by="payment_type").agg({
        "order_id": "nunique",  # Jumlah unik order
        "price": "mean"  # Rata-rata harga
    })

    return grouped_data

def create_cust_demo_by_state(df):
    # customer by state
    disp_cust_by_state = df.groupby(by="customer_state").agg({
        "customer_id": "nunique",
    }).sort_values(by="customer_id", ascending=False)

    disp_cust_by_state.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return disp_cust_by_state

def create_cust_demo_by_city(df):
    # customer by city
    disp_cust_by_city = df.groupby(by="customer_city").agg({
        "customer_id": "nunique",
    }).sort_values(by="customer_id", ascending=False)

    disp_cust_by_city.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return disp_cust_by_city

def create_seller_demo_by_state(df):
    # seller by state
    disp_seller_by_state = df.groupby(by="seller_state").agg({
        "seller_id": "nunique",
    }).sort_values(by="seller_id", ascending=False)

    disp_seller_by_state.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)

    return disp_seller_by_state


def create_seller_demo_by_city(df):
    # seller by city
    disp_seller_by_city = df.groupby(by="seller_city").agg({
        "seller_id": "nunique",
    }).sort_values(by="seller_id", ascending=False)

    disp_seller_by_city.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)

    return disp_seller_by_city

def create_RFM_analysis(orders_df, order_items_df, order_payments_df):


    # Convert the 'order_purchase_timestamp' to datetime format
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

    # Filter for only delivered orders
    delivered_orders = orders_df[orders_df['order_status'] == 'delivered']

    # Merge order items to get price information
    order_items_merged = pd.merge(delivered_orders, order_items_df[['order_id', 'price']], on='order_id')

    # Merge with order payments to get the total payment value
    order_payments_merged = pd.merge(order_items_merged, order_payments_df[['order_id', 'payment_value']], on='order_id')

    # Group by customer to calculate RFM metrics
    rfm_df = order_payments_merged.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  
        "order_id": "nunique",              
        "payment_value": "sum"               
    })

    # Rename the columns to match RFM
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Calculate recency (days since last transaction)
    recent_date = orders_df['order_purchase_timestamp'].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].dt.date.apply(lambda x: (recent_date - x).days)

    # Drop the max_order_timestamp column
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    # Display the first few rows of the resulting RFM dataframe
    return rfm_df




all_df = pd.read_csv("main_data.csv")
orders_df = pd.read_csv("../data/orders_dataset.csv")
order_items_df = pd.read_csv("../data/order_items_dataset.csv")
order_payments_df = pd.read_csv("../data/order_payments_dataset.csv")

# with st.sidebar:
#     # Menambahkan logo perusahaan
#     st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

with st.sidebar:
    st.image("./logo/online-shop-logo.png", use_column_width=True)

    st.title("Company Performance Dashboard 🌟")

    st.markdown("---")

    st.write("""
    Welcome to the **Company's Performance Dashboard**.
    Here, you'll find key insights and visualizations 
    showcasing our growth and success over the last 5 months.
    """)

    st.markdown("---")

    st.markdown("""
    > "The only way to do great work is to love what you do."
    > \- Steve Jobs
    """)

    st.markdown("💼 📊 💡")
    
    st.markdown("---")


    st.write("Thank you for visiting our dashboard! 😊")


    
# create dataset
revenue_df = create_revenue_resume(all_df)
best_product_df = filter_best_product(all_df)
popular_payment_type_df = create_popular_payment_type(all_df)
cust_by_state_df = create_cust_demo_by_state(all_df)
cust_by_city_df = create_cust_demo_by_city(all_df)
seller_by_state_df = create_seller_demo_by_state(all_df)
seller_by_city_df = create_seller_demo_by_city(all_df)
RFM_analysis_df = create_RFM_analysis(orders_df, order_items_df, order_payments_df)


st.header("Company's Performance Last 5 Months :sparkles:")


# 1. Revenue Visualization
st.subheader('📈 Sales & Revenue Performance')

fig, ax = plt.subplots(figsize=(20, 10))
sns.lineplot(
    x="order_approved_at", 
    y="order_count",
    data=revenue_df,
    ax=ax
)

# Adjusting title, axis, and ticks
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

# Setting y-axis limit
ax.set_ylim(0, revenue_df["order_count"].max() + 1000)

# Displaying the plot
st.pyplot(fig)

# Add some space between charts
st.write("")

# 2. Bestseller Products Visualization
st.subheader('🏆 10 Bestseller Products')

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(x='average_rating', y='product_category_name_english', data=best_product_df.head(10), palette="Blues_d")

# Setting title and axis labels/ticks
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

# Displaying the plot
st.pyplot(fig)

st.write("")  # Adding space


# 3. Popular Payment Type Visualization
st.subheader('💳 Percentage of Orders by Payment Type')

labels = popular_payment_type_df.index 
sizes = popular_payment_type_df["order_id"] 

fig, ax = plt.subplots(figsize=(10, 10))
colors = sns.color_palette("pastel")
wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=colors)

# Adding legend and ensuring equal aspect ratio
ax.legend(wedges, labels, title="Payment Types", loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))
ax.axis('equal')

# Displaying the pie chart
st.pyplot(fig)

st.write("")  # Adding space

# 4. Customer Demographics by City and State
st.subheader('🌍 Customer Demographics by City and State')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3"]

# State demographics
sns.barplot(y="customer_state", x="customer_count", data=cust_by_state_df.head(10), palette=colors, ax=ax[0])
ax[0].set_title("By State", loc="center", fontsize=18, fontweight='bold')
ax[0].tick_params(axis='x', labelsize=12)

# City demographics
sns.barplot(y="customer_city", x="customer_count", data=cust_by_city_df.head(10), palette=colors, ax=ax[1])
ax[1].set_title("By City", loc="center", fontsize=18, fontweight='bold')
ax[1].invert_xaxis()
ax[1].tick_params(axis='x', labelsize=12)

# Displaying the chart
st.pyplot(fig)

st.write("")  # Adding space

# 5. Seller Demographics by City and State
st.subheader('🏢 Seller Demographics by City and State')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

# Seller state demographics
sns.barplot(y="seller_state", x="seller_count", data=seller_by_state_df.head(10), palette=colors, ax=ax[0])
ax[0].set_title("By State", loc="center", fontsize=18, fontweight='bold')
ax[0].tick_params(axis='x', labelsize=12)

# Seller city demographics
sns.barplot(y="seller_city", x="seller_count", data=seller_by_city_df.head(10), palette=colors, ax=ax[1])
ax[1].set_title("By City", loc="center", fontsize=18, fontweight='bold')
ax[1].invert_xaxis()
ax[1].tick_params(axis='x', labelsize=12)

# Displaying the chart
st.pyplot(fig)

st.write("")  # Adding space

# 6. RFM Analysis
st.subheader('🔍 RFM Analysis')

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
colors = ["#72BCD4"] * 5

# Recency plot
sns.barplot(y="recency", x="customer_id", data=RFM_analysis_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", loc="center", fontsize=18, fontweight='bold')
ax[0].tick_params(axis='x', labelsize=15)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45)

# Frequency plot
sns.barplot(y="frequency", x="customer_id", data=RFM_analysis_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", loc="center", fontsize=18, fontweight='bold')
ax[1].tick_params(axis='x', labelsize=15)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45)

# Monetary plot
sns.barplot(y="monetary", x="customer_id", data=RFM_analysis_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", loc="center", fontsize=18, fontweight='bold')
ax[2].tick_params(axis='x', labelsize=15)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45)

# Displaying the chart
st.pyplot(fig)