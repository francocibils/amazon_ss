import pandas as pd
import streamlit as st
from io import BytesIO

st.title('Skoon - Save & Subscribe')
st.header('File upload')
st.markdown('Upload txt/csv file that you downloaded from Amazon Sellercentral. This will return an Excel file where each row represents a date and the corresponding amount of Save & Subscribe orders for Skoon in that day.')

file = st.file_uploader('Upload Amazon Sellercentral file', type = ['csv', 'txt'])

if file is not None:
    df = pd.read_csv(file, sep = '\t')

    st.success('File uploaded succesfully.')

if st.button('Process file'):

    # Pre-process
    df['purchase-date'] = pd.to_datetime(df['purchase-date'], format = 'mixed').dt.date
    min_date = df['purchase-date'].min().strftime('%Y-%m-%d')
    max_date = df['purchase-date'].max().strftime('%Y-%m-%d')

    # Masks
    mask_1 = df['promotion-ids'].str.contains('subscribe', case = False, na = False)
    mask_2 = df['product-name'].str.contains('skoon', case = False, na = False)
    mask_3 = df['sku'].str.contains('skn', case = False, na = False)

    ss_df = df[mask_1 & (mask_2 | mask_3)]

    # Process
    ss_df_daily = pd.DataFrame(ss_df.groupby(ss_df['purchase-date']).size())

    df = pd.DataFrame(index = pd.date_range(start = min_date, end = max_date))
    df = pd.merge(df, ss_df_daily, left_index = True, right_index = True, how = 'left')
    df = df.fillna(0)
    df.columns = ['S&S - Orders']
    df['S&S - Orders'] = df['S&S - Orders'].astype(int)

    st.header('Processed data')
    st.success('File processed succesfully.')

    output = BytesIO()
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        df.to_excel(writer, sheet_name = 'Skoon - S&S orders')
        writer.close()

    # Rewind the buffer
    output.seek(0)

    # Create a download button
    st.download_button(
        label = "Download Excel file",
        data = output,
        file_name = "Amazon - S&S orders.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
