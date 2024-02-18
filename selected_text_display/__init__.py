import nltk
if 'nltk_data' not in nltk.data.path:
  nltk.data.path.append('nltk_data')

import streamlit as st
import streamlit.components.v1 as components
from nltk.stem import WordNetLemmatizer
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import numpy as np
import easyocr
import os
import backend

st.set_page_config(layout="wide")
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_selected_text_display = components.declare_component("selected_text_display", path=build_dir)

def selected_text_display(txt, key=None):
    return _selected_text_display(txt=txt, key=key)

if 'img' not in st.session_state:
    st.session_state.img = False

if 'screen_size' not in st.session_state:
    st.session_state.screen_size = None

if 'words' not in st.session_state:
    st.session_state['words'] = []    

if "txt" not in st.session_state:
    st.session_state.txt = ""
import traceback
import os
import requests
import json
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, jsonify
app = Flask(__name__)

load_dotenv()

@app.route('/')
def index():
	'Show the index page'
	return render_template('index.html')

@app.route('/options')
def options():
	'Show the options page'
	return render_template('options.html')

@app.route('/GetTokenAndSubdomain', methods=['GET'])
def getTokenAndSubdomain():
	'Get the access token'
	if request.method == 'GET':
		try:
			headers = { 'content-type': 'application/x-www-form-urlencoded' }
			data = {
				'client_id': str(os.environ.get('CLIENT_ID')),
				'client_secret': str(os.environ.get('CLIENT_SECRET')),
				'resource': 'https://cognitiveservices.azure.com/',
				'grant_type': 'client_credentials'
			}

			resp = requests.post('https://login.windows.net/' + str(os.environ.get('TENANT_ID')) + '/oauth2/token', data=data, headers=headers)
			jsonResp = resp.json()
			
			if ('access_token' not in jsonResp):
				print(jsonResp)
				raise Exception('AAD Authentication error')

			token = jsonResp['access_token']
			subdomain = str(os.environ.get('SUBDOMAIN'))

			return jsonify(token = token, subdomain = subdomain)
		except Exception as e:
			message = 'Unable to acquire Azure AD token. Check the debugger for more information.'
			print(message, e)
			return jsonify(error = message)
def main():  
    screen_width = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')

    if screen_width != None:
      if screen_width < 400:
        on_phone()
      else:
        col1, col2 = st.columns([2,1])
        with st.container():
          with col1:
              st.title("English to ASL")
              st.subheader("Put in your paragraph here: ")
              on = st.toggle('Choose here to use picture')
              if not on:
                  st.session_state.txt = st.text_area("Input")
              else:
                  image_file = st.file_uploader("Upload Image",type=['jpg','png','jpeg','JPG'])
          
                  if image_file is not None:
                      img = Image.open(image_file)
                      img = np.array(img)
                      
                      st.subheader('Image you Uploaded...')
                      st.image(image_file,width=450)
                      if st.session_state.img == False:
                          with st.spinner('Extracting Text from given Image'):
                              eng_reader = easyocr.Reader(['en'])
                              detected_text = eng_reader.readtext(img)
                          st.session_state.txt = display_text(detected_text)
                          st.session_state.img = True
          with col2:
              st.image('./video-recording_V1-min.gif')
        with st.container():
          with col1:
              st.divider()
              st.subheader("Choose your words to translate here by highlighting the word and clicking 'Select Text'")
          with col2:
              st.divider()
              st.image('./video-recording_V2-min.gif')
        with col1:
            selected_text = selected_text_display(st.session_state.txt)
            
            if selected_text not in st.session_state.words and selected_text not in [None, '', ' ']:
                st.session_state.words.append(selected_text)
        container_dict = {}
        left_column_dict = {}
        right_column_dict = {}
        translate = st.button("Translate to ASL")
        ChangeButtonColour("Translate to ASL", "#000000", "#B3C7F7")
        if translate:
            synsets, words = backend.get_lesk(st.session_state.txt, st.session_state.words)
            if words != st.session_state.words:
                st.session_state.words = words
            for word in st.session_state.words:
                container_dict[word] = st.container()
                left_column_dict[word], right_column_dict[word] = st.columns([2,1])
            for word in st.session_state.words:
                root, lstsyn, asl_synonyms = backend.english_root_and_synonyms(synsets, word)
                video_links = backend.get_asl(word, synsets, root)
                if video_links != []:
                    with container_dict[word]:
                        with left_column_dict[word]:
                            st.divider()
                            st.subheader(word)
                            for video in video_links:
                                st.video(video)
                        with right_column_dict[word]:
                            try:
                              if root != '':
                                st.divider()
                                st.subheader("Root: ")
                                st.write(root)
                              if lstsyn != []:
                                st.subheader("This English word can also mean: ")
                                for syn in lstsyn:
                                    st.write(syn)
                              if asl_synonyms != []:
                                st.subheader("This ASL sign can also mean: ")
                                for syn in asl_synonyms:
                                  syn = syn.split(',')
                                  for item in syn:
                                      st.write(item.strip('[]'))
                            except Exception as e:
                              st.write("")
                else:
                    st.write(word)
                    root, lstsyn, asl_synonyms = backend.english_root_and_synonyms(synsets, word)
                    st.write(root, lstsyn, asl_synonyms)
                    for syn in lstsyn:
                        synsets[syn] = synsets[word]
                        video_links = backend.get_asl(syn, synsets, root)
                        if video_links != []:
                            st.write(syn)
                            break
                    for video in video_links:
                        st.video(video)
    
        restart = st.button("Restart")
        ChangeButtonColour("Restart", "#000000", "#F194B8")
        if restart:
            st.session_state.words = []
            st.session_state.img = False
            st.session_state.txt = ""
            streamlit_js_eval(js_expressions="parent.window.location.reload()")

def on_phone():
          st.title("English to ASL")
          st.subheader("Put in your paragraph here: ")
          on = st.toggle('Choose here to use picture')
          if not on:
              st.session_state.txt = st.text_area("Input")
          else:
              image_file = st.file_uploader("Upload Image",type=['jpg','png','jpeg','JPG'])
      
              if image_file is not None:
                  img = Image.open(image_file)
                  img = np.array(img)
                  
                  st.subheader('Image you Uploaded...')
                  st.image(image_file,width=450)
                  if st.session_state.img == False:
                      with st.spinner('Extracting Text from given Image'):
                          eng_reader = easyocr.Reader(['en'])
                          detected_text = eng_reader.readtext(img)
                      st.session_state.txt = display_text(detected_text)
                      st.session_state.img = True
          st.divider()
          st.subheader("Choose your words to translate here by highlighting the word and clicking 'Select Text'")
          selected_text = selected_text_display(st.session_state.txt)
          
          if selected_text not in st.session_state.words and selected_text not in [None, '', ' ']:
              st.session_state.words.append(selected_text)
          container_dict = {}

          if st.button("Translate to ASL"):
      
              for word in st.session_state.words:
                  container_dict[word] = st.container()
  
              for word in st.session_state.words:
                  video_links = backend.find_words_asl(word, synsets)
                  if video_links != []:
                      with container_dict[word]:
                              st.subheader(word)
                              for video in video_links:
                                  st.video(video)
                  else:
                      lstsyn = backend.find_synonyms(word, syns)
                      for syn in lstsyn:
                          video_links = backend.find_words_asl(syn)
                          if video_links != []:
                              st.write(syn)
                              break
                      for video in video_links:
                          st.video(video)
      
      
          if st.button("Restart"):
              st.session_state.words = []
              st.session_state.img = False
              st.session_state.txt = ""
              streamlit_js_eval(js_expressions="parent.window.location.reload()")
          
def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}';
                    elements[i].style.width = '33%';
                    elements[i].style.padding = '15px';
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)
  
if __name__ == "__main__":
    main()
