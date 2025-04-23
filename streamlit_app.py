import streamlit as st
from openai import OpenAI
import signal
import atexit

st.title("💬 Shakespearian Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-4o-mini model to generate responses. "
)

openai_api_key = st.secrets["OPENAI_API_KEY"]
if not openai_api_key:
    st.info("Please add your OpenAI API key in the environment", icon="🗝️")
else:
    # create an OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # create vectorstore for files
    vectorstore = client.vector_stores.create(name="vector-store")

    file_paths = []
    file_streams = []
    
    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vectorstore_id=vectorstore.id,
    )

    # create assistant  with this tool
    assistant = client.beta.assistants.create(
        name="Shakespeare Assistant",
        description="A chatbot that can answer questions about computer science.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        tool_resources=[{"type": "file_search", "vectorstore_id": vectorstore.id}],
    )

    thread = client.beta.threads.create()

    # Display the existing chat messages via `st.chat_message`.
    for message in client.beta.threads.messages.list(thread_id=thread.id):
        print(message)
        with st.chat_message(message.role):
            st.markdown(message.content)

    # interact with user prompts
    if prompt := st.chat_input("How can I help you today?"):

        # Store and display the current prompt.
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        # call openai and stream response and store the result
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        with st.chat_message("assistant"):
            st.markdown(run["content"])