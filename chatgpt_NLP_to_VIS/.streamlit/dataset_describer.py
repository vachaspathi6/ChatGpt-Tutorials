import os
import openai
import streamlit as st
import pandas as pd
import re
import uuid

def read_csv_to_string(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        content = file.read()
    return content

def extract_string_between_triple_backticks(text):
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    sanitized_matches = []
    for match in matches:
        # Remove the leading "python" keyword if it exists
        sanitized_match = match.lstrip('python').strip()
        sanitized_matches.append(sanitized_match)
    return sanitized_matches

def save_to_py_file(strings, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for string in strings:
            file.write(string)
            file.write('\n')

#@st.cache_data
def load_data(uploaded_file, file_name):
    dataframe_version = pd.read_csv(uploaded_file, encoding='utf-8', delimiter=csv_delimiter)
    dataframe_version.to_csv('datasets/' + file_name + '.csv')
    string_version = read_csv_to_string('datasets/' + file_name + '.csv')
    return dataframe_version, string_version

max_token = 3000
summ_temprature = 0.5

# Upload a CSV file to the datasets folder using st.file_uploader
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a CSV file from your computer", accept_multiple_files=False)
    csv_delimiter = st.radio("Choose delimiter", (';', ','))

if uploaded_file is not None:
    unique_filename = str(uuid.uuid4())

    df, st_version = load_data(uploaded_file, unique_filename)
    st.dataframe(df.head(5))

    # Set up OpenAI API key
    openai.api_key = st.secrets['open_ai_key']['OPENAI_API_KEY']

    with st.form(key='my_form'):
        plot_description = st.text_area("Describe the plot you want to see.")
        submit_button = st.form_submit_button(label='Submit')

    if plot_description:
        response_dataset_description = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": st.secrets['chatgpt_queries']['datadescribe_query1'] +
                                             st_version[0:200] + "\n" +
                                             st.secrets['chatgpt_queries']['datadescribe_query2']}
            ],
            max_tokens=max_token,
            temperature=summ_temprature,
        )

        response_dataset_summary = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": st.secrets['chatgpt_queries']['datadescribe_query1'] +
                                             st_version[0:200] + "\n" +
                                             plot_description + "\n" +
                                             st.secrets['chatgpt_queries']['datadescribe_query3'] +
                                             st.secrets['chatgpt_queries']['datadescribe_query4'] +
                                             st.secrets['chatgpt_queries']['datadescribe_query5'] +
                                             st.secrets['chatgpt_queries']['datadescribe_query6'] +
                                             f'datasets/{unique_filename}.csv' +
                                             st.secrets['chatgpt_queries']['datadescribe_query7']}
            ],
            max_tokens=max_token,
            temperature=summ_temprature,
        )

        with st.sidebar:
            st.write(response_dataset_description.choices[0].message.content)

        created_code = extract_string_between_triple_backticks(response_dataset_summary.choices[0].message.content)
        save_to_py_file(created_code, 'plotter.py')

        # Print the content of plotter.py for inspection
        with open("plotter.py", "r") as f:
            plotter_code = f.read()
            st.text(plotter_code)  # Display the code in the Streamlit app for debugging

        # Execute the code safely
        try:
            exec_globals = {}
            exec(plotter_code, exec_globals)
        except Exception as e:
            st.error(f"An error occurred while executing the plotter code: {e}")

        os.remove('datasets/' + unique_filename + '.csv')
