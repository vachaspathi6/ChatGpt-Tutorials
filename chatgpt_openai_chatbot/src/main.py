import os
import json
import streamlit as st
import openai
import time

# Load default API key from config file
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
DEFAULT_OPENAI_API_KEY = config_data["OPENAI_API_KEY"]

# Configuring streamlit page settings
st.set_page_config(
    page_title="GPT-4.o OpenAI Chat Assistant",
    page_icon="🤖",
    layout="centered"
)

# Initialize chat session in streamlit if not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "How can I help you?"}]

# Sidebar for API key input
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API key: ", type="password", key="api_key", value=DEFAULT_OPENAI_API_KEY)

# Streamlit page title
st.title("💬 OpenAI ChatBot")
st.caption("🚀 A streamlit chatbot fueled by the ingenious prowess of OpenAI's GPT-4.0")
# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user's message
user_prompt = st.chat_input("Ask GPT-4o...")

if user_prompt:
    if api_key:
        # Set the provided API key
        openai.api_key = api_key

        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # Send user's message to GPT-4o and get a response
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                *st.session_state.chat_history
            ]
        )
        end_time = time.time()

        assistant_response = response.choices[0].message["content"]
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Calculate evaluation metrics
        latency = end_time - start_time
        input_tokens = len(user_prompt.split())
        output_tokens = len(assistant_response.split())
        throughput = output_tokens / latency

        # Display GPT-4o's response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Display metrics in the sidebar
        st.sidebar.subheader("Evaluation Metrics")
        st.sidebar.write(f"- **Throughput:** {throughput:.6f} tokens/second")
        st.sidebar.write(f"- **Latency:** {latency:.6f} seconds")
        st.sidebar.write(f"- **Input Tokens:** {input_tokens}")
        st.sidebar.write(f"- **Output Tokens:** {output_tokens}")
    else:
        st.sidebar.error("Please enter your OpenAI API key to proceed.")
