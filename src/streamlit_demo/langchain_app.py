import base64
import os
from io import BytesIO

import dotenv
import streamlit as st
from PIL import Image

from langchain_core.messages import HumanMessage

dotenv.load_dotenv()


def image_to_base64(image):
    """Convert PIL Image to base64 encoded string"""
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')


def format_input(input_message):
    """Format the input message for the LLM"""
    content = []

    if input_message.get("content"):
        content.append({
            "type": "text",
            "text": input_message["content"],
        })

    if input_message.get("images"):
        image_b64 = image_to_base64(input_message["images"])
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
        })

    return [HumanMessage(content=content)]


# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="AFI Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "OPEN_AI_API_KEY" not in st.session_state:
    st.session_state.OPEN_AI_API_KEY = os.environ["OPENAI_API_KEY"]
if "process_images" not in st.session_state:
    st.session_state.process_images = False


# Create a sidebar
with st.sidebar:
    # Model selection
    st.header("Settings")
    selected_model = st.selectbox(
        "Choose model:",
        ["gemma3:4b", "deepseek-r1:7b", "gpt-4o-mini"],
    )
    if selected_model == "gemma3:4b":
        st.session_state.process_images = True
    else:
        st.session_state.process_images = False

    # OpenAI API Key
    if selected_model == "gpt-4o-mini":
        os.environ["OPENAI_API_KEY"] = st.text_input(
            "OpenAI API Key",
            st.session_state.OPEN_AI_API_KEY,
            type="password",
        )


# Display the app title
st.title("AFI DEMO")

# Load model
if selected_model == "gpt-4o-mini":
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model=selected_model, api_key=st.session_state.OPEN_AI_API_KEY)
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model=selected_model)

# Define the chain
chain = format_input | llm

# Create a chat interface
prompt = st.chat_input(
    accept_file=st.session_state.process_images,
    file_type=["jpg", "jpeg", "png"],
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        if message.get("file"):
            st.image(message["file"])

# Process the user input and display the response
message = {}
if prompt and isinstance(prompt, str):  # st.session_state.process_images == False
    message["text"] = prompt
    with st.chat_message("user"):
        st.markdown(message["text"])
    st.session_state.messages.append({"role": "user"} | message)

    with st.chat_message("assistant", avatar="🔮"):
        response = st.write_stream(chain.stream({"content": message["text"]}))
    st.session_state.messages.append({"role": "assistant", "text": response})

elif prompt and prompt.text:  # st.session_state.process_images == True
    if prompt.text:               
        message["text"] = prompt.text
    if prompt.get("files"):
        message["file"] = Image.open(prompt["files"][0])
    with st.chat_message("user"):
        st.markdown(prompt.text)
        if "file" in message:
            st.image(message["file"])
    st.session_state.messages.append({"role": "user"} | message)

    with st.chat_message("assistant", avatar="🔮"):
        response = st.write_stream(chain.stream({"content": message.get("text"), "images": message.get("file")}))
    st.session_state.messages.append({"role": "assistant", "text": response})
