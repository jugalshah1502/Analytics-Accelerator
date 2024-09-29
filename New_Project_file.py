import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io 
from io import BytesIO
import logging 

logging.getLogger().setLevel(logging.ERROR)

# Check if a page key exists in session state; if not, create it
if 'page' not in st.session_state:
    st.session_state.page = 'upload'

# Function to show the upload page
def show_upload_page():
    st.markdown("<h1 style='text-align: center; font-size: 36px; color: #bec1bd;'>Analytics Accelerator</h1>", unsafe_allow_html=True)
    st.markdown("""
        <style>
            .upload-text {
                font-size: 20px;
                color: #bec1bd;
                font-weight: bold;
                margin: 20px 0;
            }
            .file-uploader {
                margin-bottom: 30px;
                border: 2px dashed #4CAF50;
                padding: 10px;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='upload-text'>Upload your inventory file</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an Inventory file", type=["xlsx"], key="inventory", label_visibility="collapsed")
    st.markdown("<div class='upload-text'>Upload your sales file</div>", unsafe_allow_html=True)
    sales_uploaded_file = st.file_uploader("Choose a Sales file", type=["xlsx"], key="sales", label_visibility="collapsed")
    st.markdown("<div class='upload-text'>Upload your Base Price File</div>", unsafe_allow_html=True)
    base_price_uploaded_file = st.file_uploader("Choose a Base Price file", type=["xlsx"], key="base_price", label_visibility="collapsed")

    col1, col2, col3 = st.columns([1,1,1], gap="small")

    with col1: 
        if st.button("Inventory Report", key="next"):
            if uploaded_file and sales_uploaded_file and base_price_uploaded_file:
                # Set the session state to navigate to the results page
                st.session_state.page = 'inventory_report'
                # Store the uploaded files in session state for later use
                st.session_state.uploaded_file = uploaded_file
                st.session_state.sales_uploaded_file = sales_uploaded_file
                st.session_state.base_price_uploaded_file = base_price_uploaded_file
            else:
                st.error("Please upload all required files before proceeding.")

    with col2:
        if st.button("P/L Report"):
            if uploaded_file and sales_uploaded_file and base_price_uploaded_file:
                st.session_state.page = 'pl_report'
                st.session_state.uploaded_file = uploaded_file
                st.session_state.sales_uploaded_file = sales_uploaded_file
                st.session_state.base_price_uploaded_file = base_price_uploaded_file
            else:
                st.error("Please upload all required files before proceeding.")

    with col3:
        if st.button("P/L Analytics"):
            if uploaded_file and sales_uploaded_file and base_price_uploaded_file:
                st.session_state.page = 'pl_analytics'
                st.session_state.uploaded_file = uploaded_file
                st.session_state.sales_uploaded_file = sales_uploaded_file
                st.session_state.base_price_uploaded_file = base_price_uploaded_file
            else:
                st.error("Please upload all required files before proceeding.")

# Function to show the results page
def inventory_report_page():
    # Read the uploaded files
    df1 = pd.read_excel(st.session_state.sales_uploaded_file, sheet_name=None)
    df2 = pd.read_excel(st.session_state.uploaded_file)
    df3 = pd.read_excel(st.session_state.base_price_uploaded_file, sheet_name=None)

    # Process the inventory report
    df2.drop(columns=['DayWise Id', 'Coupon Id', 'Dep Time', 'Arr Date', 'Arr Time', 
                      'Starting Price', 'Total Fare', 'PNR', 'Series Owner'], axis=1, inplace=True)
    df2['Flight Number'] = df2['Flight Number'].str.replace('QP-', '', regex=False)
    df2['Sector'] = df2['Sector'].str.replace('-', '', regex=False)
    df2.rename(columns={'Current Seat': 'Unsold Seats', 'Total Seat': 'Total Seats'}, inplace=True)

    # Adding new columns
    df2['Sold Seats'] = df2['Total Seats'] - df2['Unsold Seats']
    df2['MAT_Ratio'] = df2['Sold Seats'] / df2['Total Seats'] * 100
    df2['Release Ratio'] = df2['Unsold Seats'] / df2['Total Seats'] * 100

    # Display the processed DataFrame
    st.markdown("<h2 style='text-align: center;'>Processed Inventory Report</h2>", unsafe_allow_html=True)
    st.dataframe(df2)

    st.markdown("<h2 style='text-align: center;'>Inventory Report by Sector</h2>", unsafe_allow_html=True)
    new_df = df2.groupby('Sector').agg({
        'Total Seats': 'sum', 
        'Sold Seats': 'sum', 
        'Unsold Seats': 'sum', 
        'MAT_Ratio': 'mean', 
        'Release Ratio': 'mean'
    }).reset_index()
    st.dataframe(new_df, use_container_width=True)

    # Defining the grouped_df
    st.markdown("<h2 style='text-align: center;'>Inventory Analytics</h2>", unsafe_allow_html=True)
    grouped_df = df2.groupby('Sector').agg({'MAT_Ratio': 'mean', 'Release Ratio': 'mean'}).reset_index()

    # Create gauge charts for MAT Ratio and Release Ratio
    for sector in grouped_df['Sector']:
        mat_ratio = grouped_df.loc[grouped_df['Sector'] == sector, 'MAT_Ratio'].values[0]
        release_ratio = grouped_df.loc[grouped_df['Sector'] == sector, 'Release Ratio'].values[0]

        # Create the gauge chart for MAT Ratio
        fig_mat = go.Figure(go.Indicator(
            mode="gauge+number",
            value=mat_ratio,
            title={'text': f"MAT Ratio for {sector}", 'font': {'color': "silver"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 50], 'color': "crimson"},
                    {'range': [50, 100], 'color': "lightgreen"},
                ],
            }
        ))

        # Create the gauge chart for Release Ratio
        fig_release = go.Figure(go.Indicator(
            mode="gauge+number",
            value=release_ratio,
            title={'text': f"Release Ratio for {sector}", 'font': {'color': "silver"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 50], 'color': "crimson"},
                    {'range': [50, 100], 'color': "lightgreen"},
                ],
            }
        ))

        # Display the gauge charts
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_mat, use_container_width=True)
        with col2:
            st.plotly_chart(fig_release, use_container_width=True)

    if st.button("Home"):
        st.session_state.page = 'upload'
        st.rerun()

def show_pl_report_page():
    st.markdown("<h2 style='text-align: center;'>Profit and Loss Report</h2>", unsafe_allow_html=True)
        # Check if the files are uploaded
    if 'sales_uploaded_file' not in st.session_state or 'uploaded_file' not in st.session_state or 'base_price_uploaded_file' not in st.session_state:
        st.error("Please upload all required files.")
        st.stop()  # Safely stop execution if files are missing
    # Cache the loading of Excel files
    @st.cache_data
    def load_excel(file):
        return pd.read_excel(file, sheet_name=None)
    # Load the uploaded files
    sales_file = st.session_state.sales_uploaded_file
    base_price_file = st.session_state.base_price_uploaded_file
    # Load all sheets from the Sales report and base price with caching
    try:
        df1 = load_excel(sales_file)
    except Exception as e:
        st.error(f"Error loading Sales report: {e}")
        st.stop()
    try:
        df3 = load_excel(base_price_file)
    except Exception as e:
        st.error(f"Error loading Base Price file: {e}")
        st.stop()
    # Sidebar for date selection
    st.sidebar.header("Select Date Range")
    start_date = pd.to_datetime(st.sidebar.date_input("Start Date", key='start_date'))
    end_date = pd.to_datetime(st.sidebar.date_input("End Date", key='end_date'))
    if start_date > end_date:
        st.error("Start Date must be before or equal to End Date.")
        st.stop()
    # Cache the data filtering for 'infant' and 'child' types
    @st.cache_data
    def filter_infant_child(df_dict):
        for sheet_name, df in df_dict.items():
            if 'Type' in df.columns:
                df_dict[sheet_name] = df[~df['Type'].isin(['infant', 'child'])]
        return df_dict
    df1 = filter_infant_child(df1)
    # Cache dropping irrelevant columns
    irrelevant_columns = ['SL NO', 'Title', 'First Name', 'Last Name', 'Booking Status', 'Carrier', 'Type',
                          'DepTime', 'PNR', 'DOB', 'DMinusDays', 'Name Updated', 'Name Updated By', 
                          'Name Updated On']
    @st.cache_data
    def drop_irrelevant_columns(df_dict):
        for sheet_name, df in df_dict.items():
            existing_columns = [col for col in irrelevant_columns if col in df.columns]
            if existing_columns:
                df.drop(columns=existing_columns, inplace=True)
        return df_dict
    df1 = drop_irrelevant_columns(df1)
    # Cache sorting of the data by 'TravelDate'
    @st.cache_data
    def sort_by_travel_date(df_dict):
        for sheet_name, df in df_dict.items():
            if 'TravelDate' in df.columns:
                df_dict[sheet_name] = df.sort_values(by='TravelDate')
        return df_dict
    df1 = sort_by_travel_date(df1)
    # Cache formatting of the 'Sector' column
    @st.cache_data
    def format_sector(df_dict):
        for sheet_name, df in df_dict.items():
            if 'Sector' in df.columns:
                df['Sector'] = df['Sector'].str.replace('-', '', regex=False).str.replace(' ', '', regex=False)
        return df_dict
    df1 = format_sector(df1)
    # Cache saving of the modified sales report to a new Excel file in-memory
    @st.cache_data
    def save_modified_sales(df_dict):
        modified_sales = BytesIO()
        with pd.ExcelWriter(modified_sales, engine='openpyxl') as writer:
            for sheet_name, df in df_dict.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        modified_sales.seek(0)  # Reset the buffer to the beginning
        return modified_sales
    modified_sales = save_modified_sales(df1)
    # Reload the modified Sales report
    try:
        new_df1 = pd.read_excel(modified_sales, sheet_name=None)
    except Exception as e:
        st.error(f"Error loading modified Sales report: {e}")
        st.stop()
    # Create an empty list to hold the results
    temporary_data = []
    # Cache filtering based on date range and profit/loss calculation
    @st.cache_data
    def calculate_profit_loss(new_df1, df3, start_date, end_date):
        temporary_data = []
        for sheet_name, df in new_df1.items():
            if 'TravelDate' in df.columns:
                filtered_df = df[(df['TravelDate'] >= start_date) & (df['TravelDate'] <= end_date)]
                for _, row in filtered_df.iterrows():
                    sector = row['Sector']
                    flight_number = row['FlightNumber']
                    amount = row['Amount']
                    date = row['TravelDate']
                    for base_sheet_name, base_df in df3.items():
                        date_range = base_sheet_name.split('_')
                        if len(date_range) != 2:
                            continue
                        try:
                            sheet_start_date = pd.to_datetime(date_range[0])
                            sheet_end_date = pd.to_datetime(date_range[1])
                        except:
                            continue
                        if (sheet_start_date <= end_date) and (sheet_end_date >= start_date):
                            base_row = base_df[base_df['Sector'] == sector]
                            base = base_row['Base'].values[0] if not base_row.empty else None
                            profit_loss = amount - base if base is not None else None
                            temporary_data.append({
                                'Sector': sector,
                                'Date': date,
                                'FlightNumber': flight_number,
                                'Amount': amount,
                                'Base': base,
                                'Profit/Loss': profit_loss
                            })
                            break
        return pd.DataFrame(temporary_data)
    temporary_df = calculate_profit_loss(new_df1, df3, start_date, end_date)
    # Remove rows with NaN in 'Profit/Loss' column
    temporary_df = temporary_df.dropna(subset=['Profit/Loss'])
    # Display the temporary DataFrame
    st.write("Profit and Loss Data:")
    st.dataframe(temporary_df)
    # Group by sector for aggregated Profit/Loss
    new_df2 = temporary_df.groupby('Sector').agg({'Profit/Loss': 'sum', 'Base': 'sum', 'Amount': 'sum'}).reset_index()
    st.write("Profit and Loss Data by Sector:")
    st.dataframe(new_df2, use_container_width=True)
    
    if st.button("Home"):
        st.session_state.page = 'upload'

def show_pl_analytics_page():
    
    # Check if the files are uploaded
    if 'sales_uploaded_file' not in st.session_state or 'uploaded_file' not in st.session_state or 'base_price_uploaded_file' not in st.session_state:
        st.error("Please upload all required files.")
        st.stop()  # Safely stop execution if files are missing
    # Cache the loading of Excel files
    @st.cache_data
    def load_excel(file):
        return pd.read_excel(file, sheet_name=None)
    # Load the uploaded files
    sales_file = st.session_state.sales_uploaded_file
    base_price_file = st.session_state.base_price_uploaded_file
    # Load all sheets from the Sales report and base price with caching
    try:
        df1 = load_excel(sales_file)
    except Exception as e:
        st.error(f"Error loading Sales report: {e}")
        st.stop()
    try:
        df3 = load_excel(base_price_file)
    except Exception as e:
        st.error(f"Error loading Base Price file: {e}")
        st.stop()
    # Sidebar for date selection
    st.sidebar.header("Select Date Range")
    start_date = pd.to_datetime(st.sidebar.date_input("Start Date", key='start_date'))
    end_date = pd.to_datetime(st.sidebar.date_input("End Date", key='end_date'))
    if start_date > end_date:
        st.error("Start Date must be before or equal to End Date.")
        st.stop()
    # Cache the data filtering for 'infant' and 'child' types
    @st.cache_data
    def filter_infant_child(df_dict):
        for sheet_name, df in df_dict.items():
            if 'Type' in df.columns:
                df_dict[sheet_name] = df[~df['Type'].isin(['infant', 'child'])]
        return df_dict
    df1 = filter_infant_child(df1)
    # Cache dropping irrelevant columns
    irrelevant_columns = ['SL NO', 'Title', 'First Name', 'Last Name', 'Booking Status', 'Carrier', 'Type',
                          'DepTime', 'PNR', 'DOB', 'DMinusDays', 'Name Updated', 'Name Updated By', 
                          'Name Updated On']
    @st.cache_data
    def drop_irrelevant_columns(df_dict):
        for sheet_name, df in df_dict.items():
            existing_columns = [col for col in irrelevant_columns if col in df.columns]
            if existing_columns:
                df.drop(columns=existing_columns, inplace=True)
        return df_dict
    df1 = drop_irrelevant_columns(df1)
    # Cache sorting of the data by 'TravelDate'
    @st.cache_data
    def sort_by_travel_date(df_dict):
        for sheet_name, df in df_dict.items():
            if 'TravelDate' in df.columns:
                df_dict[sheet_name] = df.sort_values(by='TravelDate')
        return df_dict
    df1 = sort_by_travel_date(df1)
    # Cache formatting of the 'Sector' column
    @st.cache_data
    def format_sector(df_dict):
        for sheet_name, df in df_dict.items():
            if 'Sector' in df.columns:
                df['Sector'] = df['Sector'].str.replace('-', '', regex=False).str.replace(' ', '', regex=False)
        return df_dict
    df1 = format_sector(df1)
    # Cache saving of the modified sales report to a new Excel file in-memory
    @st.cache_data
    def save_modified_sales(df_dict):
        modified_sales = BytesIO()
        with pd.ExcelWriter(modified_sales, engine='openpyxl') as writer:
            for sheet_name, df in df_dict.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        modified_sales.seek(0)  # Reset the buffer to the beginning
        return modified_sales
    modified_sales = save_modified_sales(df1)
    # Reload the modified Sales report
    try:
        new_df1 = pd.read_excel(modified_sales, sheet_name=None)
    except Exception as e:
        st.error(f"Error loading modified Sales report: {e}")
        st.stop()
    # Create an empty list to hold the results
    temporary_data = []
    # Cache filtering based on date range and profit/loss calculation
    @st.cache_data
    def calculate_profit_loss(new_df1, df3, start_date, end_date):
        temporary_data = []
        for sheet_name, df in new_df1.items():
            if 'TravelDate' in df.columns:
                filtered_df = df[(df['TravelDate'] >= start_date) & (df['TravelDate'] <= end_date)]
                for _, row in filtered_df.iterrows():
                    sector = row['Sector']
                    flight_number = row['FlightNumber']
                    amount = row['Amount']
                    date = row['TravelDate']
                    for base_sheet_name, base_df in df3.items():
                        date_range = base_sheet_name.split('_')
                        if len(date_range) != 2:
                            continue
                        try:
                            sheet_start_date = pd.to_datetime(date_range[0])
                            sheet_end_date = pd.to_datetime(date_range[1])
                        except:
                            continue
                        if (sheet_start_date <= end_date) and (sheet_end_date >= start_date):
                            base_row = base_df[base_df['Sector'] == sector]
                            base = base_row['Base'].values[0] if not base_row.empty else None
                            profit_loss = amount - base if base is not None else None
                            temporary_data.append({
                                'Sector': sector,
                                'Date': date,
                                'FlightNumber': flight_number,
                                'Amount': amount,
                                'Base': base,
                                'Profit/Loss': profit_loss
                            })
                            break
        return pd.DataFrame(temporary_data)
    
    temporary_df = calculate_profit_loss(new_df1, df3, start_date, end_date)
    # Remove rows with NaN in 'Profit/Loss' column

    new_df2 = temporary_df.groupby('Sector').agg({'Profit/Loss': 'sum', 'Base': 'sum', 'Amount': 'sum'}).reset_index()
       
    st.markdown("<h2 style='text-align: center;'>KPIs</h2>", unsafe_allow_html=True)
    # To add space between the KPIs title and actual figures
    st.write(" ")
    st.write(" ") 
    
    
    total_sales = new_df2['Amount'].sum()
    total_profit = new_df2['Profit/Loss'].sum()
    average_profit = total_profit / len(new_df2)
    num_flights = len(temporary_df['FlightNumber'].unique())
    num_sectors = len(temporary_df['Sector'].unique())

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.metric("Total Sales", f"₹{total_sales:,.2f}")
    with col2:
        st.metric("Total Profit", f"₹{total_profit:,.2f}")

    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.metric("Average Profit/Loss", f"₹{average_profit:,.2f}")
    with col4:
        st.metric("Number of Flights", num_flights)

    col5, col6 = st.columns(2, gap="large")
    with col5:
        st.metric("Number of Sectors", num_sectors)
    with col6:
        st.empty() 
    
    st.markdown("<h2 style='text-align: center;'>Sector Performance Analytics</h2>", unsafe_allow_html=True)
    top_sectors = new_df2.sort_values(by='Profit/Loss', ascending=False).head(5)
    
    fig = px.pie(top_sectors, values='Profit/Loss', names='Sector', title='Top 5 Performing Sectors')
    st.plotly_chart(fig, use_container_width=True)
    

    bottom_sectors = new_df2.sort_values(by='Profit/Loss', ascending=True).head(5)

   # Bar chart showing both negative (loss) and positive (profit)
    fig = px.bar(bottom_sectors, x='Sector', y='Profit/Loss', title='Bottom 5 Performing Sectors')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.bar(new_df2, x='Sector', y='Profit/Loss',title='Profit/Loss by Sector')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(temporary_df, x= 'Date', y='Profit/Loss', color='Sector', title='Profit/Loss trend across sectors')
    st.plotly_chart(fig, use_container_width=True)
    
    
    
    if st.button("Home"):
        st.session_state.page = 'upload'


# Run the app
def render_page():
  if st.session_state.page == 'upload':
    show_upload_page()
  elif st.session_state.page == 'inventory_report':
    inventory_report_page()
  elif st.session_state.page == 'pl_report':
    show_pl_report_page()
  elif st.session_state.page == 'pl_analytics':
    show_pl_analytics_page()
  else:
    st.error("Invalid page")

def main():
    render_page()

if __name__ == "__main__":
    main()

