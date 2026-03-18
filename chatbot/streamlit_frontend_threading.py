import streamlit as st
from lang_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()


if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []


if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = {}

add_thread(st.session_state['thread_id'])


# ---------------------------sidebar ui ---------------

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversation')


for thread_id in st.session_state['chat_threads'][::-1]:

    chat_name = st.session_state['chat_names'].get(thread_id, f"Chat {str(thread_id)[:5]}")

    if st.sidebar.button(chat_name, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []

        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# st.sidebar.text(st.session_state['thread_id'])


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')


if user_input:

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    if st.session_state['thread_id'] not in st.session_state['chat_names']:
        # Creates a name from the first 25 characters
        st.session_state['chat_names'][st.session_state['thread_id']] = user_input[:25] + "..."

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}    

    with st.chat_message('assistant'):
       ai_message = st.write_stream(
            message_chunk.content for message_chunk, metatdata in chatbot.stream(
                {'messages': [HumanMessage(content = user_input)]},
                config = CONFIG,
                stream_mode = 'messages'
           )
       )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})