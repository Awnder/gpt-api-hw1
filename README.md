# 💬 Shakespearian Chatbot

A chatbot that talks in old english reminiscent of Shakespeare, using GPT-4o-mini.  

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-n6rjsvu07ek.streamlit.app/)

### How to run it on your own machine

1. Clone the repository and install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Add secrets
   - add `.streamlit/secrets.toml` folder and file to the cloned project
   - then add your OpenAI API Key in `secrets.toml`:
   ```
   OPENAI_API_KEY = "<open_api_key_here>"
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
