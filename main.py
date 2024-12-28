import streamlit as st
import pandas as pd
import os

# Constants
UPLOAD_DIRECTORY = "uploaded_files"
FILE_NAME = "uploaded_file.xlsx"
PASSCODE = "securepass123"  # Hardcoded password

# Create the upload directory if not exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Function to handle file upload
def handle_file_upload(uploaded_file):
    file_path = os.path.join(UPLOAD_DIRECTORY, FILE_NAME)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Function to load the Excel file
@st.cache_resource
def load_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        df['ACCT_ID'] = df['ACCT_ID'].astype(str).str.strip()
        df['SERIAL_NBR'] = df['SERIAL_NBR'].astype(str).str.strip()
        df_acc = df.set_index(['ACCT_ID'])
        df_sno = df.set_index(['SERIAL_NBR'])
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
    return df_acc, df_sno

# Streamlit App
# Set page configuration for responsive design
st.set_page_config(page_title="Get Account Details", layout="wide")

st.title("Get Meter Details")

# Sidebar for optional file upload
with st.sidebar:
    st.header("Upload a New File (Admin)")
    input_passcode = st.text_input("Enter the password to upload the file:", type="password")
    if input_passcode:
        if input_passcode == PASSCODE:
            st.success("Passcode is correct!")

            # File Upload
            uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
            if uploaded_file is not None:
                file_path = handle_file_upload(uploaded_file)
                st.cache_resource.clear()
                st.success(f"File uploaded successfully! Replaced existing file at {file_path}.")
        else:
            st.error("Incorrect passcode!")

# File Processing Section
file_path = os.path.join(UPLOAD_DIRECTORY, FILE_NAME)
if os.path.exists(file_path):
    df_acc, df_sno = load_excel_file(file_path)
    if df_acc is not None:        
        # Input Fields for Filtering
        acct_id = st.text_input("Enter value for Account ID:").strip()
        st.text("OR")
        serial_nbr = st.text_input("Enter value for SERIAL Number:").strip()

        # Ensure at least one input is provided
        if st.button("Submit"):
            with st.spinner(f"Searching for Acc Id:{acct_id}, S. No:{serial_nbr}"):
                # st.text(f"Searching for Acc Id:{acct_id}, S. No:{serial_nbr}")
                if acct_id:
                    try:
                        filtered_df = df_acc.loc[acct_id]
                        st.write(f"Account Detail For: Acc Id: {acct_id}, S. No: {serial_nbr}")
                        st.dataframe(filtered_df.T, width=1500, height=500)  # Display as vertical table
                    except KeyError as e:
                        st.warning(f"No matching rows found. Error: {e}")
                elif serial_nbr:
                    try:
                        filtered_df = df_sno.loc[serial_nbr]
                        st.write(f"Account Detail: Acc Id:{acct_id}, S. No:{serial_nbr}")
                        st.dataframe(filtered_df.T, width=1500, height=500)  # Display as vertical table
                    except KeyError as e:
                        st.warning(f"No matching rows found. Error: {e}")
                else:
                    st.error("Please provide at least one value: ACCT_ID or SERIAL_NBR.")
else:
    st.warning("No file uploaded yet.")