import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import os
st.set_page_config(layout="wide")

def show_hool_bolovsruulalt():
    st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)
    image = Image.open('mnums.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)

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

    html_title2 = """
        <style>
        .title-test2 {
        font-weight:bold;
        padding:5px;
        border-radius:6px
        }
        </style>
        <center><h3 class="title-test2">Өвчний ач холбогдол бүхий хүснэгтийн өгөгдөл</h3></center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
        st.markdown(html_title2, unsafe_allow_html=True)

    col3, col4 = st.columns([0.50, 0.50])

    # st.markdown("Таарсан багануудын утгуудыг Stacked Bar Chart-р харуулах")

    # 📂 disease_analysis файлын sheet-үүдийг шалгах
    xls_disease = pd.ExcelFile("disease_analysis_results 2.xlsx")
    k_sheets = [s for s in xls_disease.sheet_names if s.startswith('K')]

    with col3:
        selected_k_sheet = st.selectbox("📑 Хоол боловсруулах эрхтэн тогтолцооны өвчлөл сонгох (K...):", k_sheets, key = "k_selection")

    # Сонгосон K sheet-ийг унших
    df1 = pd.read_excel(xls_disease, sheet_name=selected_k_sheet)

    # first_col баганын нэрийг шалгах
    if df1.empty:
        st.warning("Энд өгөгдөл байхгүй байна.")
    else:
        first_col = df1.columns[0]
        df1[first_col] = df1[first_col].astype(str).str.strip().str.lower()
        values1 = df1[first_col]  # values1 зөв үүсгэх

        # p, rr, or, ppv баганууд шалгах
        disease_columns = ['p_value', 'odds_ratio', 'adjusted_RR', 'ppv']
        disease_columns_existing = [col for col in disease_columns if col in df1.columns]

        # 📂 med_data файл унших
        xls = pd.ExcelFile("med_data_export.xlsx")
        matched_columns = []

        # Таарсан багануудыг хайх
        for sheet_name in xls.sheet_names:
            df2 = pd.read_excel(xls, sheet_name=sheet_name)

            # Хоосон sheet-ийг шалгах
            if df2.empty:
                continue  # Хоосон sheet-ийг үл тооцно

            # Өгөгдлийг зөв цэвэрлэж, урд болон ард байгаа орон зайг устгана
            for v in values1:
                v_clean = v.strip().lower()  # value1 утгыг цэвэрлэх
                for col in df2.columns:
                    col_clean = col.strip().lower()  # column нэрийг цэвэрлэх
                    if v_clean in col_clean:
                        matched_columns.append((sheet_name, col))

        # ✅ UI сонголтууд
        if matched_columns:
            with col3:
                sheet_options = sorted(set([sheet for sheet, _ in matched_columns]))
                selected_sheet = st.selectbox("Хамаарах хүснэгт сонгох:", sheet_options, key="table_selection")

            # with col4:
                filtered_columns = [col for sheet, col in matched_columns if sheet == selected_sheet]
                selected_columns = st.multiselect("Графикаар харах багануудыг сонгох:", filtered_columns)

            if selected_columns:
                # Өмнө нь нэг багана сонгож байсан бол, одоо бүх сонгогдсон багануудыг нэгэн зэрэг графикт харуулна
                chart_df_list = []
                for selected_column in selected_columns:
                    df_selected = pd.read_excel(xls, sheet_name=selected_sheet)
                    values = df_selected[selected_column].astype(str).str.strip()
                    counts = values.value_counts().sort_index()
                
                    chart_df = pd.DataFrame({
                        "Value": counts.index,
                        "Count": counts.values,
                        "Column": [selected_column] * len(counts)
                    })
                
                    # 🎯 disease_analysis дээрээс утгуудыг олох
                    selected_column_clean = selected_column.strip().lower()
                    disease_row = df1[df1[first_col] == selected_column_clean]

                    if not disease_row.empty:
                        for col in disease_columns_existing:
                            chart_df[col] = disease_row[col].values[0]

                        chart_df_list.append(chart_df)  # Бүх багануудын графикийг жагсаалтад нэмэх

                # Нийтлэн зурсан бүх графикуудыг нэг дор харуулах
                if chart_df_list:
                    final_df = pd.concat(chart_df_list, ignore_index=True)

                    bar = alt.Chart(final_df).mark_bar(size=30).encode(
                        x=alt.X("Column:N", title="Багана"),
                        y=alt.Y("Count:Q", title="Тоо хэмжээ", stack='zero'),
                        color=alt.Color("Value:N", title="Утга", scale=alt.Scale(domain=['0', '1'], range=['blue', 'red'])),
                        tooltip=["Value", "Count"] + disease_columns_existing
                    )
                    
                    text = alt.Chart(final_df).mark_text(
                        align="center",
                        baseline="middle",
                        dx=0,
                        dy=5,
                        color="white"
                    ).encode(
                        x=alt.X("Column:N", title="Багана"),
                        y=alt.Y("Count:Q", title="Тоо хэмжээ"),
                        detail="Value:N",
                        text=alt.Text("Count:Q")
                    )

                    chart = (bar+text).properties(
                        width=600,
                        height=400,
                        title="K өвчний ач холбогдолт багана"
                    )
        
                    # 1-р график: disease_analysis үндэслэлтэй график
                    # col5, col6 = st.columns(2)
                    with col3:
                        st.divider()
                        st.altair_chart(chart, use_container_width=True)
                else:
                    with col3:
                        st.warning("Сонгосон баганууд disease_analysis файлд таарахгүй байна.")
            else:
                with col3:
                    st.warning("Багануудыг сонгоогүй байна, багана сонгох хэсгээс сонгоно уу!")
        else:
            with col3:
                st.warning("Таарсан багана олдсонгүй.")

    with col4:
        st.markdown("Хоол боловсруулах өвчний BD_with_one_hot_diagnoses хүснэгтийн дата")

    # Excel файл
    excel_file = 'BD_with_one_hot_diagnoses.xlsx'

    # Файл шалгах
    if not os.path.exists(excel_file):
        st.error(f"'{excel_file}' файл олдсонгүй.")
    else:
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names

        all_data = []

        for sheet in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            k_columns = [col for col in df.columns if str(col).startswith("K")]

            for col in k_columns:
                if set(df[col].dropna().unique()).issubset({0, 1}):
                    counts = df[col].value_counts().to_dict()
                    all_data.append({
                        "sheet": sheet,
                        "column": col,
                        "column_id": f"{sheet} | {col}",
                        "value": "0",
                        "count": counts.get(0, 0)
                    })
                    all_data.append({
                        "sheet": sheet,
                        "column": col,
                        "column_id": f"{sheet} | {col}",
                        "value": "1",
                        "count": counts.get(1, 0)
                    })

        if all_data:
            chart_df = pd.DataFrame(all_data)

            # ✅ Multiselect: хэрэглэгч аль багануудыг харахыг сонгоно
            all_column_ids = sorted(chart_df['column_id'].unique())
            with col4:
                selected_columns = st.multiselect(
                    "📌 Баганууд сонгох (sheet | column хэлбэрээр)",
                    options=all_column_ids,
                    default=all_column_ids[:5]  # анхны 5-г default сонгоно
            )


            if selected_columns:
                filtered_df = chart_df[chart_df['column_id'].isin(selected_columns)]

                with col4:
                    st.subheader("📊 Сонгосон багануудын Stacked Bar Chart")
               
                bar2 = alt.Chart(filtered_df).mark_bar(size=25).encode(
                    x=alt.X('column_id:N', title='Sheet | Багана', sort=None),
                    y=alt.Y('count:Q', title='Тоо ширхэг', stack='zero'),
                    color=alt.Color('value:N', title='Утга', scale=alt.Scale(domain=['0','1'], range=['blue','red'])),
                    tooltip=['sheet', 'column', 'value', 'count']
                )
                
                text2 = alt.Chart(filtered_df).mark_text(
                    align="center",
                    baseline="middle",
                    dx=0,
                    dy=0,
                    color="white"
                ).encode(
                    x=alt.X("column_id:N", title="Багана"),
                    y=alt.Y("count:Q",title="Тоо хэмжээ"),
                    detail="value:N",
                    text=alt.Text("count:Q")
                )

                chart2 = (bar2+text2).properties(
                    width=600,
                    height=400,
                    title="K өвчний BD_with_one_hot_diagnoses хүснэгтийн график"
                )
              

                # 2-р график: one-hot багануудын stacked chart
                # col5, col6 = st.columns(2)
                with col4:
                    st.divider()
                    st.altair_chart(chart2, use_container_width=True)
            else:
                st.info("Эхлээд жагсаалтаас баганууд сонгоно уу.")
        else:
            st.warning("K-ээр эхэлсэн one-hot баганууд олдсонгүй.")

# show_hool_bolovsruulalt()
