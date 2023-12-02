import nltk
if 'nltk_data' not in nltk.data.path:
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
import os
import pandas as pd

wnl = WordNetLemmatizer()
st.set_page_config(layout="wide")
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_selected_text_display = components.declare_component("selected_text_display", path=build_dir)

def selected_text_display(txt, key=None):
    return _selected_text_display(txt=txt, key=key)

if 'img' not in st.session_state:
    st.session_state.img = False

if 'words' not in st.session_state:
    st.session_state['words'] = []    

if "txt" not in st.session_state:
    st.session_state.txt = ""
def main():
    screen_width = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
    # st.write(f"Screen width is {streamlit_js_eval(js_expressions='screen.width', key = 'SCR')}")
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
    if screen_width < 400:
      on_phone()
    else:
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
          st.image('./video-recording_V1.gif')
      with col1:
          st.divider()
          st.subheader("Choose your words to translate here by highlighting the word and clicking 'Select Text'")
      with col2:
          st.image('./video-recording_V1.gif')
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
              video_links = find_words_asl(word, syns)
              if video_links != []:
                  with container_dict[word]:
                      with left_column_dict[word]:
                          st.subheader(word)
                          for video in video_links:
                              st.video(video)
                      with right_column_dict[word]:
                          try:
                            _, pos, _ = result_dict[word].name().split('.')
                            root = wnl.lemmatize(word, pos=pos)
                            if root != '':
                              st.subheader("Root: ")
                              st.write(root)
                            lstsyn = find_synonyms(word, syns)
                            st.write(lstsyn)
                            if lstsyn != []:
                              st.subheader("This English word can also mean: ")
                              for syn in lstsyn:
                                  st.write(syn)
                          except:
                            st.write("")
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
          synsets = {}
          if st.button("Translate to ASL"):
              for word in st.session_state.words:
                  word = word.lower()
                  if word not in synsets.keys():
                      synsets[word] = lesk.simple_lesk(sentence, word)
      
              for word in st.session_state.words:
                  container_dict[word] = st.container()
  
              for word in st.session_state.words:
                  video_links = find_words_asl(word, synsets)
                  if video_links != []:
                      with container_dict[word]:
                              st.subheader(word)
                              for video in video_links:
                                  st.video(video)
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
          
def find_words_asl(word, synsets):
    word = word.lower()
    found_ss, video_urls = find_word_ss(f"https://www.signingsavvy.com/search/{word}", word, synsets)
    if not found_ss:
        found_sa, video_urls = find_word(f"https://www.signasl.org/sign/{word}", word)
    if found_ss or found_sa:
        return video_urls
    else:
        return []

def find_synonyms(word, syn):
    synonyms = []
    if syn[word]:
        name = syn[word].name()
        for i in wordnet.synset(name).lemmas():
            lemma_name = i.name().replace('_', " ")
            if word_frequency(lemma_name, 'en') > .0000001 and lemma_name != word:
                synonyms.append(lemma_name)
    return synonyms

def find_word_ss(website, word, synsets):
    url = 'https://raw.githubusercontent.com/celenaaponce/English2ASLImage/main/selected_text_display/signing_savvy_words.csv'
    result = pd.read_csv(url, index_col=0)
    r = requests.get(website)
    soup = BeautifulSoup(r.content, 'html.parser')
    header_tag = soup.find('div', class_ = 'signing_header')
    if header_tag == None:
        video_urls = get_multiple_meanings(soup, synsets, result, word)
        if video_urls == []:
            found = False
        else:
            found = True
        return found, video_urls
    lists = header_tag.find_all('li')
    if len(lists) == 2:
        video_urls = get_single_video(website)
    elif len(lists) > 2:
        video_urls = get_multiple_videos(lists, website)
    return True, video_urls
  
def get_multiple_meanings(soup, synsets, result, word):
    video_urls = []
    results = soup.find('div', class_ = 'search_results')
    if results == None:
        return []
    meanings = results.find_all('li')
    
    asl_translation = None
    if synsets[word]:
        english = synsets[word]
        
        asl = result.loc[result['word'] == word]
        asl_translation = match_synset(asl, english)
        video_urls = asl_translation
        
        if asl_translation == None:
            asl_translation = match_synonyms(asl, english)
            video_urls = asl_translation
            
    if asl_translation == None:
        video_urls = []
        prefix = 'https://www.signingsavvy.com/'
        for meaning in meanings:
            suffix = meaning.find('a')['href']
            website = prefix + suffix
            if len(video_urls) < 2:
                video_urls.append(get_single_video(website))
    return video_urls

def match_synset(asl, english):
    asl_translation = None
    prefix = 'https://www.signingsavvy.com/'
    for index, row in asl.iterrows():
        if type(row['synset']) != float:
            if row['synset'] == str(english):
                asl_translation = row['link'].to_list()
                website = prefix + asl_translation
                asl_translation = get_single_video(website)
    return asl_translation
  
def match_synonyms(asl, english):
    asl_translation = None
    prefix = 'https://www.signingsavvy.com/'
    synonyms = [x.name() for x in english.lemmas()]
    for index, row in asl.iterrows():
        asl_lst = row['synonyms'].strip('][').split(', ')
        asl_syn_lst = []
        for i in asl_lst:
            splt = i.split('(')
            asl_syn_lst.append(splt[0].lower().translate(str.maketrans('', '', string.punctuation)))
        if any(x in synonyms for x in asl_syn_lst):
            asl_translation = row['link']
            website = prefix + asl_translation
            asl_translation = get_single_video(website)
    return asl_translation  
def get_single_video(website):
    r = requests.get(website)
    soup = BeautifulSoup(r.content, 'html.parser')
    video_tag = soup.find('video')
    video_url = video_tag.find("source")['src']
    return video_url

def get_multiple_videos(lists, website):
    video_urls = []
    video_urls.append(get_single_video(website))
    #first one accounted for above, last one is finger spelling
    prefix = 'https://www.signingsavvy.com/'
    for item in lists[1:-1]:
        suffix = item.find('a')['href']
        website = prefix + suffix
        if len(video_urls) < 2:
            video_urls.append(get_single_video(website))
        else:
            break
    return video_urls
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
