import streamlit as st
from openai import OpenAI
import os
import time


# streamlit apps run in an environment where the code is run 
def delete_history(client):
    with open(os.path.join("assistants", "assistants.txt"), "r") as file:
        assistants = file.readlines()
    assistants = [assistant.strip() for assistant in assistants]

    with open(os.path.join("threads", "threads.txt"), "r") as file:
        threads = file.readlines()
    threads = [thread.strip() for thread in threads]

    success = st.success("Deleting history...")
    with success:
        for assistant in assistants:
            try:
                client.beta.assistants.delete(assistant)
            except Exception as e:
                print(f"error on assistant {assistant}: {e}")
        
        for thread in threads:
            try:
                client.beta.threads.delete(thread)
            except Exception as e:
                print(f"error on thread {thread}: {e}")

    with open(os.path.join("assistants", "assistants.txt"), "w") as file:
        file.write("")
    with open(os.path.join("threads", "threads.txt"), "w") as file:
        file.write("")

    time.sleep(0.2)
    success.empty()


openai_api_key = st.secrets["OPENAI_API_KEY"]
if not openai_api_key:
    st.info("Please add your OpenAI API key in the environment", icon="🗝️")
else:
    # SETUP STREAMLIT APP
    st.title("💬 Lu'au Planner Chatbot")

    # create an OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # input files if they do not exist
    remote_files = client.files.list().data
    remote_filenames = [remote_file.filename for remote_file in remote_files]

    if "Club + Lūʻau Manual.pdf" not in remote_filenames:
        with open(os.path.join("files", "Club + Lūʻau Manual.pdf"), "rb") as file:
            client.files.create(file=file, purpose="assistants")
    if "Lu'au Todo List 24-25.pdf" not in remote_filenames:
        with open(os.path.join("files", "Lu'au Todo List 24-25.pdf"), "rb") as file:
            client.files.create(file=file, purpose="assistants")

    # create files as attachments
    remote_file_ids = [remote_file.id for remote_file in remote_files if remote_file.filename in ["Club + Lūʻau Manual.pdf", "Lu'au Todo List 24-25.pdf"]]
    attachments = [{"file_id": r_id, "tools": [{"type": "file_search"}]} for r_id in remote_file_ids]

    # check if the assistant already exists and use it
    with open(os.path.join("assistants", "assistants.txt"), "r") as file:
        assistants = file.readlines()
    assistants = [assistant.strip() for assistant in assistants]

    if assistants:
        assistant_id = assistants[0].strip()
        assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
    else:
        assistant = client.beta.assistants.create(
            name="Lu'au Assistant",
            description="Andrew's chatbot that can answer questions about how to plan Concordia University Irvine's Lu'au.",
            instructions="You are a helpful assistant that can answer questions about how to plan Concordia University Irvine's Lu'au.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )
        with open(os.path.join("assistants", "assistants.txt"), "a") as file:
            file.write(f"{assistant.id}\n")

    # check if existing thread exist and use it
    with open(os.path.join("threads", "threads.txt"), "r") as file:
        threads = file.readlines()
    threads = [thread.strip() for thread in threads]
    if threads:
        thread_id = threads[0].strip()
        thread = client.beta.threads.retrieve(thread_id=thread_id)
    else:
        thread = client.beta.threads.create()
        with open(os.path.join("threads", "threads.txt"), "a") as file:
            file.write(f"{thread.id}\n")

    # STREAMLIT DISPLAY

    with st.sidebar:
        with open(os.path.join("assistants", "assistants.txt"), "r") as file:
            assistants = file.readlines()
        assistants = [assistant.strip() for assistant in assistants]
        with open(os.path.join("threads", "threads.txt"), "r") as file:
            threads = file.readlines()
        threads = [thread.strip() for thread in threads]

        st.button(
            "Delete Conversation History",
            on_click=lambda: delete_history(client),
        )

    # Display the existing chat messages via `st.chat_message`.
    for message in client.beta.threads.messages.list(thread_id=thread.id, order="asc"):
        if message.role == "user":
            with st.chat_message("user"):
                st.markdown(message.content[0].text.value)
        elif message.role == "assistant":
            with st.chat_message("assistant"):
                for content_block in message.content:
                    if content_block.type == "text":
                        st.markdown(content_block.text.value)

    # interact with user prompts
    if prompt := st.chat_input("How can I help you today?"):

        # add user prompt to messages and display
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
            attachments=attachments,
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # call openai and stream response and store the result
        run = client.beta.threads.runs.create(
            assistant_id=assistant.id,
            thread_id=thread.id,
        )

        with st.spinner("Assistant is typing..."):
            while run.status != "completed":
                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id,
                )

        # get the latest message from the assistant and display it
        messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc")
        latest = next(message for message in messages if message.role == "assistant")
        with st.chat_message("assistant"):
            for content_block in latest.content:
                if content_block.type == "text":
                    st.markdown(content_block.text.value)