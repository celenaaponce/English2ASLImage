import requests
from pywsd import lesk 
from nltk.corpus import wordnet
import pandas as pd
from wordfreq import word_frequency
from bs4 import BeautifulSoup
import string
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()

def get_lesk(sentence, words):
    synsets = {}
    for word in words:
      word = word.lower()
      if word not in synsets.keys():
          synsets[word] = lesk.simple_lesk(sentence, word)
      else:
          test_word = lesk.simple_lesk(sentence, word)
          if test_word != synsets[word]:
              print('duplicate word diff meaning')
    return synsets
    
def get_asl(word, synsets):
  video_links = find_words_asl(word, synsets)
  return video_links

def english_root_and_synonyms(synsets, word):
      _, pos, _ = synsets[word].name().split('.')
      root = wnl.lemmatize(word, pos=pos)
      lstsyn = find_synonyms(word, synsets)
      return root, lstsyn

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
        video_urls = []
        video = get_single_video(website)
        video_urls.append(video)
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
        if len(possible_urls) > 1:
          break
    if possible_urls != []:
        return True, possible_urls
    else:
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
