import asyncio
from comfyclient import ComfyClient
from comfyflow import ComfyFlow
from io import StringIO
import json
from loguru import logger
import os 
from pathlib import Path
import requests 
import streamlit as st
from streamlit_card import card
import subprocess
import uuid

with open('workflow_api_gguf.json', 'r') as f:
   workspace_api = f.read()

with open('app.json', 'r') as f:
   app_config = json.loads(f.read())

server_port=app_config["server_port"]
listen_path=app_config["listen_path"]

st.title('Simple Comfy WebApp')

if "rows" not in st.session_state:
    st.session_state["rows"] = []

if "prompt_txt" not in st.session_state:
    st.session_state["prompt_txt"] = "Enter prompt"

rows_collection = []

def add_row():
    element_id = uuid.uuid4()
    st.toast(st.session_state.main_form)
    st.session_state["rows"].append([str(element_id),st.session_state.main_form])
    send_prompt(st.session_state.main_form, workspace_api)

def remove_row(row_id):
    i=0
    index=1
    for row in st.session_state["rows"]:
        if row[0]==row_id:
            index=i
            logger.info("marking row " + str(row_id) + " for removal")
        i = i+1
    
    st.session_state["rows"].pop(index)
    st.toast("deleting row " + str(row_id))

def reuse_prompt(row_id):
    delete_flag= st.session_state[f"del_{row_id[0]}"]
    if delete_flag:
      remove_row(row_id[0])
    else:
      st.session_state["main_form"]=row_id[1]


def generate_row(row_id):

    with st.form(key=f"hist_{row_id[0]}"):
        st.chat_message("assistant").write(row_id[1])
        delete_flag=st.checkbox(f"Mark for deletion {row_id[0]}", key=f"del_{row_id[0]}")
        st.form_submit_button("Execute", on_click=reuse_prompt, args=[row_id])

def send_prompt(prompt, workspace_api):
    comfy_client = ComfyClient(server_port)
    comfy_flow = ComfyFlow(comfy_client, workspace_api)
    json_prompt=comfy_flow.generate_json(prompt)
    logger.info(json_prompt)
    logger.info(comfy_client.queue_prompt(json_prompt))

def reload():
    st.toast("Reloaded")

if "stcomfy_sidebar" not in st.session_state:
    with st.sidebar:
     for row in st.session_state["rows"]:
       row_data = generate_row(row)
       rows_collection.append(row_data)

with st.form("stcomfy_form"):
    txt=st.text_area("Enter Prompt", key="main_form")
    st.form_submit_button('Submit prompt', on_click=add_row)

uploaded_file = st.file_uploader("Choose a workspace file")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    workspace_api = stringio.read()

## Credits to https://discuss.streamlit.io/t/how-to-update-app-elements-on-timer/7692/10
async def watch(image_pl):
    previous = None
    while True:
        images = list(Path(listen_path).glob("*"))
        if images:
            latest = max(images, key=lambda file: file.stat().st_mtime)
        else:
            image_pl.image(PLACEHOLDER_URL, use_column_width=True)
            latest = None
        if latest != previous:
            image_pl.image(str(latest), use_column_width=True)
            previous = latest
        _ = await asyncio.sleep(1)

image_pl = st.empty()
try:
    asyncio.run(watch(image_pl))
except Exception:
    pass 


