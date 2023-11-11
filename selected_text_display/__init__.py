import nltk
nltk.data.path.append('nltk_data')

import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from wordfreq import word_frequency
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import numpy as np
import easyocr
from pywsd import disambiguate
from pywsd import lesk
import re



wnl = WordNetLemmatizer()
st.set_page_config(layout="wide")
_selected_text_display = components.declare_component("selected_text_display",
                                                          url="http://localhost:3001",)

def selected_text_display(txt, key=None):
    return _selected_text_display(txt=txt, key=key)

if 'img' not in st.session_state:
    st.session_state.img = False

if 'words' not in st.session_state:
    st.session_state['words'] = []    

if "txt" not in st.session_state:
    st.session_state.txt = ""
def main():
    m = st.markdown("""<style> div.stButton > button:first-child {
  background-color: #4e83e0; /* Background color */
  color: #ffffff; /* Text color */
  padding: 10px 20px; /* Padding */
  border: none; /* No border */
  border-radius: 4px; /* Rounded corners */
  cursor: pointer; /* Cursor on hover */
  font-weight: bold; /* Bold text */
  font-size: 20px; /* Font size */
  margin-top: 10px;
  margin-bottom: 10px;
    height:2.em;width:50%;
}
</style>""", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
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
        st.image('/Users/celenap/selected_text_display/video-recording_V1.gif')
    with col1:
        st.divider()
        st.subheader("Choose your words to translate here by highlighting the word and clicking 'Select Text'")
    with col2:
        st.image('/Users/celenap/selected_text_display/video-recording_V1.gif')
    with col1:
        selected_text = selected_text_display(st.session_state.txt)
        
        if selected_text not in st.session_state.words and selected_text not in [None, '', ' ']:
            st.session_state.words.append(selected_text)
    container_dict = {}
    left_column_dict = {}
    right_column_dict = {}

    if st.button("Translate to ASL"):
        syns = disambiguate(st.session_state.txt)
        result_dict = dict(syns)

        for word in st.session_state.words:
            container_dict[word] = st.container()
            left_column_dict[word], right_column_dict[word] = st.columns([2,1])
        for word in st.session_state.words:
            video_links = find_words_asl(word)
            if video_links != []:
                with container_dict[word]:
                    with left_column_dict[word]:
                        st.subheader(word)
                        for video in video_links:
                            st.video(video)
                    with right_column_dict[word]:
                        st.subheader("Root: ")
                        _, pos, _ = result_dict[word].name().split('.')
                        st.write(wnl.lemmatize(word, pos=pos))
                        st.subheader("This English word can also mean: ")
                        lstsyn = find_synonyms(word, syns)
                        for syn in lstsyn:
                            st.write(syn)
            else:
                lstsyn = find_synonyms(word, syns)
                for syn in lstsyn:
                    video_links = find_words_asl(syn)
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

        
def find_words_asl(word):
    word = word.lower()
    found_ss, video_urls = find_word(f"https://www.signingsavvy.com/search/{word}", word)
    if not found_ss:
        found_sa, video_urls = find_word(f"https://www.signasl.org/sign/{word}", word)
    if found_ss or found_sa:
        return video_urls
    else:
        return []

def find_synonyms(word, syn):
    synonyms = []
    for sent_word in syn:
        if sent_word[0] == word and sent_word[1] is not None:
            synset = sent_word[1]
            name = synset.name()
            for i in wordnet.synset(name).lemmas():
                if word_frequency(i.name(), 'en') > .0000001 and i.name() != word:
                    synonyms.append(i.name())
    return synonyms



def find_word(website, word):
    r = requests.get(website)
    soup = BeautifulSoup(r.content, 'html.parser')
    video_tags = soup.findAll('video')
    possible_urls = []
    for tag in video_tags:
        video_url = tag.find("source")['src']
        possible_urls.append(video_url)
        return True, possible_urls
    else:
        if 'signingsavvy' in website:
            tag_starts_with = f'sign/{word}'
            a_tags = soup.find_all('a', {'href': re.compile(f'^{re.escape(tag_starts_with)}')})
            if len(a_tags) != 0:
                found, possible_urls = duplicate_words(a_tags)
                return found, possible_urls
        return False, ""
    
def duplicate_words(a_tags):
    possible_urls= []
    for tag in a_tags:
        r = requests.get('https://www.signingsavvy.com/' + tag.get('href'))
        soup = BeautifulSoup(r.content, 'html.parser')
        video_tags = soup.findAll('video')
        for tag in video_tags:
            video_url = tag.find("source")['src']
            possible_urls.append(video_url)
    return True, possible_urls


def display_text(bounds):
    text = []
    for x in bounds:
        t = x[1]
        text.append(t)
    text = ' '.join(text)
    return text 

if __name__ == "__main__":
    main()
