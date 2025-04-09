import streamlit as st
import pandas as pd 
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go 
import altair as alt
st.set_page_config(layout="wide")

def show_descriptive_statistics():
    # Read Data
    file_path = "med_data_export.xlsx"
    xls = pd.ExcelFile(file_path)

    EXCLUDE_SHEETS = {"user_information", "users", "insomnia_web", "isma_web"}

    st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)
    image = Image.open('mnums.png')

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        st.image(image,width=100)

    html_title = """
        <style>
        .title-test {
        font-weight:bold;
        padding:5px;
        border-radius:6px
        }
        </style>
        <center><h1 class="title-test">Хүн амын эрүүл мэндийн их өгөгдөл</h1></center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    col3, col4, col5 = st.columns([0.1,0.45,0.45])
    with col3:
        box_date = str(datetime.datetime.now().strftime("%d %B, %Y"))
        st.write(f"Last updated by: \n {box_date}")

    def get_sheets():
        """Excel файлын sheet-үүдийг авах (шаардлагагүйг хасах)."""
        return [sheet for sheet in xls.sheet_names if sheet not in EXCLUDE_SHEETS]

    def fetch_data(sheet_name):
        """Сонгосон sheet-ээс өгөгдлийг унших."""
        return pd.read_excel(xls, sheet_name=sheet_name)

    def descriptive_stats(df):
        """Статистик тооцоолол хийх (user_id баганыг хасах)."""
        df = df.drop(columns=["user_id"], errors="ignore")
        return df.describe().T


    def plot_stacked_bar_altair(df, sheet_name):
        """0, 1 гэсэн утгуудын нийлбэрээр Altair ашиглан stacked bar chart үүсгэх."""
        df = df.select_dtypes(include=['number']).drop(columns=["user_id"], errors="ignore")
        if df.empty:
            st.warning(f"'{sheet_name}' хүснэгтэд тоон өгөгдөл алга.")
            return
    
        counts = df.apply(lambda col: col.value_counts().reindex([0, 1], fill_value=0)).T
        counts = counts.reset_index().melt(id_vars="index", var_name="Value", value_name="Count")
        counts["Value"] = counts["Value"].map({0: "Үгүй", 1: "Тийм"})

        # Side Bar
        chart_type = st.radio("График төрөл сонгох:", ["Bar Chart", "Line Chart", "Scatter Plot"])
        height = len(counts["index"].unique())*25 # Баганын тоогоор өндөр тогтоох. Багана тус бүр 25px гэж тооцно. 

        # if chart_type == "Bar Chart":
        #     chart = alt.Chart(counts).mark_bar(size=15).encode(
        #         x=alt.X("Count:Q", title="Count"),
        #         y=alt.Y("index:N", title="Columns", sort=None),
        #         color=alt.Color("Value:N", scale=alt.Scale(domain=["Үгүй", "Тийм"], range=["blue", "red"])),
        #         tooltip=["index", "Value", "Count"]
        #     ).properties(
        #         width=1000,
        #         height=height,
        #         title=f"{sheet_name} - хүснэгтийн график"
        #     ).configure_view(
        #         strokeWidth=0.1
        #     ).interactive()
        if chart_type == "Bar Chart":
            bar = alt.Chart(counts).mark_bar(size=15).encode(
                x=alt.X("Count:Q", title="Count"),
                y=alt.Y("index:N", title="Columns", sort=None),
                color=alt.Color("Value:N", scale=alt.Scale(domain=["Үгүй", "Тийм"], range=["blue","red"])),
                tooltip=["index", "Value", "Count"]
            )

            text = alt.Chart(counts).mark_text(
                align="left",
                baseline="middle",
                dx=5, 
                color="white"
            ).encode(
                x=alt.X("Count:Q"),
                y=alt.Y("index:N", sort="-x"),
                detail="Value:N",
                text=alt.Text("Count:Q")
            )

            chart = (bar+text).properties(
                width=1000,
                height=height,
                title=f"{sheet_name}-Хүснэгтийн график"
            ).configure_view(
                strokeWidth=0.1
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Line Chart":
            chart = alt.Chart(counts).mark_line().encode(
                x=alt.X("Count:Q", title="Count"),
                y=alt.Y("index:N", title="Columns", sort="-x"),
                color=alt.Color("Value:N", scale=alt.Scale(domain=["Тийм","Үгүй"], range=["blue","red"])),
                tooltip=["index","Value","Count"]
            ).properties(
                width=1000,
                height=height,
                title=f"{sheet_name} - хүснэгтийн график"
            ).interactive()
    
            st.altair_chart(chart, use_container_width=True)

        else:
            chart = alt.Chart(counts).mark_circle(size=60).encode(
                x=alt.X("Count:Q", title="Count"),
                y=alt.Y("index:N", title="Columns", sort="-x"),
                color=alt.Color("Value:N", scale=alt.Scale(domain=["Тийм","Үгүй"], range=["blue","red"])),
                tooltip=["index","Value","Count"]
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

    # Streamlit UI
    st.title("Эрүүл мэндийн их өгөгдлийн Descriptive Statistics (Excel)")
    sheets = get_sheets()
    selected_sheet = st.selectbox("Select a sheet", sheets, key="select_desc")

    if selected_sheet:
        with col4:
            with st.expander("Өгөгдлийн хүснэгтийг харах"):
                data = fetch_data(selected_sheet)
                st.write("### Raw Data", data.head())

        with col5:
            with st.expander("Descriptive Statistics -ийн хүснэгтийг харах"):
                stats = descriptive_stats(data)
                st.write("### Descriptive Statistics", stats)

        plot_stacked_bar_altair(data, selected_sheet)


