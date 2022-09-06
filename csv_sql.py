# code inspired from post by George Pearse at https://medium.com/mlearning-ai/how-to-start-learning-sql-with-streamlit-d3edad7494cd
from operator import index
import sqlite3
import streamlit as st
import pandas as pd
import os



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.write(e)

    return conn


def create_database():
    st.markdown("# Create Database")

    st.write("""A database in SQLite is just a file on same server. 
    By convention their names always end in .db""")


    db_filename = st.text_input("DB Filename")
    create_db = st.button('Create Database')

    if create_db:
        if db_filename.endswith('.db'):
            conn = create_connection(db_filename)
            st.write(conn) # success message?
        else: 
            st.write('DB filename must end with .db, please retry.')


def upload_data():
    st.markdown("# Upload Data")
    # https://discuss.streamlit.io/t/uploading-csv-and-excel-files/10866/2
    sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = st.selectbox('DB Filename', sqlite_dbs)
    table_name = st.text_input('Table Name to Insert')
    conn = create_connection(db_filename)
    uploaded_file = st.file_uploader('Choose a file')
    if uploaded_file is not None:
        #read csv
        try:
            df = pd.read_csv(uploaded_file,index_col=0)
            if ValueError:
                st.write('Table already exists! Do you want to replace or choose another name?')
                table_replace = st.button('Replace table')
                table_rename = st.button('Choose another name')
                if table_rename:
                    df.to_sql(name=table_name, con=conn, if_exists='fail')
                    st.write('Data uploaded successfully. These are the first 5 rows.')
                    st.dataframe(df.head(5))
                elif table_replace:
                    df.to_sql(name=table_name, con=conn, if_exists='replace')
                    st.write('Data uploaded successfully. These are the first 5 rows.')
                    st.dataframe(df.head(5))                   

        except Exception as e:
            st.write(e)

def view_table():
    st.markdown("# View Table(s)")
    sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = st.selectbox('DB Filename', sqlite_dbs)
    conn = create_connection(db_filename)
    table_name = st.selectbox('Table(s) in database', pd.read_sql("select name from sqlite_master where type='table'",con=conn))
    if table_name is None:
        st.write('No table(s) in database')
    else:
        dataframe = pd.read_sql_query("select * from " + table_name, con=conn)
        st.write('These are the first 5 rows of the',table_name,'table.')
        st.dataframe(dataframe.head())
        download_df = dataframe.to_csv().encode('utf-8')
        st.download_button(
        label="Download "+table_name+" table as CSV",
        data=download_df,
        file_name=table_name+'.csv',
        mime='text/csv',
        )
    st.sidebar.markdown("# View Table(s)")

def run_query():
    st.markdown("# Run Query")
    sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = st.selectbox('DB Filename', sqlite_dbs)

    query = st.text_area("SQL Query", height=100)
    conn = create_connection(db_filename)

    submitted = st.button('Run Query')

    if submitted:
        try:
            query = conn.execute(query)
            cols = [column[0] for column in query.description]
            results_df= pd.DataFrame.from_records(
                data = query.fetchall(), 
                columns = cols
            )
            st.dataframe(results_df)
        except Exception as e:
            st.write(e)
    st.sidebar.markdown("# Run Query")

    # https://discuss.streamlit.io/t/save-user-input-into-a-dataframe-and-access-later/2527/2
    @st.cache(allow_output_mutation=True) 
    #@st.experimental_memo # clear persisted dataframe
    def get_query():
        return []

    save_query = st.button("Save Query")
    if save_query:
        if query == "":
            st.write("Cannot save empty query")
        else:
            get_query().append({"Database":db_filename,"Query":query})

    view_query = st.button("View Saved Queries")
    if view_query:
        dataframe = pd.DataFrame(get_query()).drop_duplicates(["Query"])
        st.table(dataframe)

page_names_to_funcs = {
    "Create Database": create_database,
    "Upload Data": upload_data,
    "View Table(s)": view_table,
    "Run Query": run_query,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
