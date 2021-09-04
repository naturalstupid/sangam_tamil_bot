import os
import string
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from operator import itemgetter
from collections import Counter
import random
from tkinter import ttk 
from tkinter import *
import regex
import json
cdeeplearn = __import__("cdeeplearn")

bot_config_file = "./ChatBot.json"
config = {}
with open(bot_config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
"""  Message Patterns """
_RE_DICT = {
    'contains': regex.compile(r"^\s?contains\s?(?P<contains>[\p{L}*+|\p{L}\p{M}*+].*)\s?.*", regex.IGNORECASE),
    'ends_with': regex.compile(r"^\s?ends\s?(with)?\s?(?P<ends_with>[\p{L}*+|\p{L}\p{M}*+].*)\s?.*", regex.IGNORECASE),
    'ends_with_1': regex.compile(r"^\s?(?P<ends_with>[\p{L}*+|\p{L}\p{M}*+])\s?[என]?\s?முடியும்.*", regex.IGNORECASE),
    'starts_with': regex.compile(r"^\s?(starts|begins)\s?(with)?\s?(?P<starts_with>[\p{L}*+|\p{L}\p{M}*+].*)\s?.*", regex.IGNORECASE),
    'starts_with_1': regex.compile(r"^\s?(?P<starts_with>[\p{L}*+|\p{L}\p{M}*+])\s?[எனத்]?\s?தொடங்கும்.*", regex.IGNORECASE),
    'get':regex.compile(r"^\s?get\s?(?P<Chapter>\d+)?\s?,?\s?(?P<Verse>\d+)?\s?.*", regex.IGNORECASE),
    'Kural':regex.compile(r"^\s?குறள்|Kural\s?(?P<Kural>\d+)?.*", regex.IGNORECASE),
    'Help':regex.compile(r"^\s?Help|உதவி\s?.*", regex.IGNORECASE),
    'Quit':regex.compile(r"^\s?Quit|Thanks|Bye|நன்றி\s?.*", regex.IGNORECASE),
    'Greet':regex.compile(r"^\s?Welcome|Greet|Hello|வணக்கம்|வாழ்த்து|நல்வரவு\s?.*", regex.IGNORECASE),
    'New':regex.compile(r"^\s?New|Generate|Create|புதிய|வாழ்த்து|உருவாக்கு\s?.*", regex.IGNORECASE),
    }
END_OF_KURAL = "."
flatten_list = lambda list: [item for sublist in list for item in sublist]
def frequency_of_occurrence(words, specific_words=None):
    """
    Returns a list of (instance, count) sorted in total order and then from most to least common
    Along with the count/frequency of each of those words as a tuple
    If specific_words list is present then SUM of frequencies of specific_words is returned 
    """
    freq = sorted(sorted(Counter(words).items(), key=itemgetter(0)), key=itemgetter(1), reverse=True)
    if not specific_words or specific_words==None:
        return freq
    else:
        frequencies = 0
        for (inst, count) in freq:
            if inst in specific_words:
                frequencies += count        
        return float(frequencies)
        
def has_required_percentage_of_occurrence(words, specific_words=None,required_percent_of_occurrence=0.99):
    actual_percent_of_occurrence = percentage_of_occurrence(words, specific_words=specific_words)
    percent_check = actual_percent_of_occurrence >= required_percent_of_occurrence
    return [percent_check, actual_percent_of_occurrence]

def percentage_of_occurrence(words, specific_words=None):
    """
    Returns a list of (instance, count) sorted in total order and then from most to least common
    Along with the percent of each of those words as a tuple
    If specific_words list is present then SUM of percentages of specific_words is returned 
    """
    frequencies = frequency_of_occurrence(words) # Dont add specific_word as argument here float error happens
    perc = [(instance, count / len(words)) for instance, count in frequencies]
    if not specific_words or specific_words==None:
        return perc
    else:
        percentages = 0
        for (inst, per) in perc:
            if inst in specific_words:
                percentages += per        
        return percentages
class Thirukural:
    chapter_max = 133
    verse_max = 10
    kural_max = 1330
    CHAPTER_NAME=0
    SECTION_NAME=1
    VERSE=2
    TRANSLATION=3
    EXPLANATION=4
    CHAPTER_INDEX=5
    SECTION_INDEX=6
    VERSE_INDEX=7
    KURAL_INDEX=8
    ERROR_CHAPTER_MSG = 'அதிகார எண் 133 க்குள் இருக்க வேண்டும்.'
    ERROR_VERSE_MSG = 'அதிகார குறள் வரிசை எண் 10 க்குள் இருக்க வேண்டும்.'
    ERROR_KURAL_MSG = 'குறள்  எண் 1330 க்குள் இருக்க வேண்டும்.'
    RANDOM_KURAL_MSG = 'சீரற்ற தேர்வு  (random choice):\n' 
    def __init__(self,data_file=None):
        """
            Column-0: Chapter Name, Col-1: Section Name, Col-2: Verse, Col-3: Translation, Col-4: Explanation
            Col-5: Chapter Index, Col-6: Section/Adhikaaram Index, Col-7: Verse Index, Col-8: Kural Index 
        """
        if os.path.exists(data_file):
            self.data_file = data_file
        else:
            Exception("data file:"+data_file+" not found.")
        df=pd.read_csv(data_file,header=None,encoding='utf-8')
        self.df = df
    def _format_output(self, kural_id_list, random_kural=False):
        result =[]
        df = self.df
        for kural_id in kural_id_list:
            pd_series = df.loc[ (df[Thirukural.KURAL_INDEX]==kural_id)]
            chapter = ' '.join(pd_series[Thirukural.CHAPTER_NAME].values)
            adhikaram = ' '.join((pd_series[Thirukural.SECTION_NAME].values) + 
                                 str(pd_series[Thirukural.SECTION_INDEX].values)+" Kural:"+
                                 str(pd_series[Thirukural.KURAL_INDEX].values))
            verse_series = pd_series[Thirukural.VERSE].values
            verse = ' '.join(verse_series)
            verse1 = verse.replace('\t\t\t','\n').replace('\t',' ')
            if config["show_columns"]['show_meaning'].lower()=="true":
                meaning = ' '.join((pd_series[Thirukural.EXPLANATION].values))
                result.append(chapter+"\t"+adhikaram+"\n"+verse1+"\n"+meaning+"\n")
            else:
                result.append(chapter+"\t"+adhikaram+"\n"+verse1+"\n")
        random_kural_msg = ""
        if (random_kural):
            random_kural_msg = Thirukural.RANDOM_KURAL_MSG
        return random_kural_msg+'\n'.join(result)
    def get_statistics(self):
        df = self.df
        dfv = df[Thirukural.VERSE].str.translate(str.maketrans('', '', string.punctuation)).replace('\t',' ')
        kural_words = flatten_list([item.split() for item in dfv])
        print('Number of words in thirukuraL',len(kural_words))
        freq_words = frequency_of_occurrence(kural_words)
        print('Number of unique words in thirukuraL',len(freq_words))
        print('Top 10 words\n',freq_words[:10])        
    def contains(self, word):
        df = self.df
        temp_str = df.loc[df[Thirukural.VERSE].str.contains(word)][Thirukural.KURAL_INDEX]
        return self._format_output(temp_str)
    def endswith(self, word):
        if not word.endswith(END_OF_KURAL):
            word += END_OF_KURAL
        df = self.df
        end_char = '\t'
        if not word.endswith(end_char):
            word += end_char
        temp_str = df[df[Thirukural.VERSE].str.endswith(word)][Thirukural.KURAL_INDEX]
        return self._format_output(temp_str)
    def startswith(self, word):
        df = self.df
        end_char = '\t'
        if not word.endswith(end_char):
            word += end_char
        temp_str = df[df[Thirukural.VERSE].str.startswith(word)][Thirukural.KURAL_INDEX]
        return self._format_output(temp_str)
    def get(self, chapter_number=None,verse_number=None, kural_number=None):
        df = self.df
        temp_str = []
        random_kural = False
        if chapter_number is not None:
            if chapter_number > Thirukural.chapter_max:
                return Thirukural.ERROR_CHAPTER_MSG
            if verse_number is not None:
                if verse_number > Thirukural.verse_max:
                    return Thirukural.ERROR_VERSE_MSG
                temp_str = df.loc[ (df[Thirukural.SECTION_INDEX]==chapter_number) & (df[Thirukural.VERSE_INDEX]==verse_number)][Thirukural.KURAL_INDEX]
            else:
                temp_str = df.loc[df[Thirukural.SECTION_INDEX]==chapter_number][Thirukural.KURAL_INDEX]
        else:
            if kural_number is not None:
                if kural_number > Thirukural.kural_max:
                    return Thirukural.ERROR_KURAL_MSG
            else:
                kural_number = random.randint(1, Thirukural.kural_max)
                random_kural = True
            temp_str = df.loc[ (df[Thirukural.KURAL_INDEX]==kural_number) ][Thirukural.KURAL_INDEX]
        return self._format_output(temp_str,random_kural=random_kural)        
    def random(self):
        df = self.df
        kural_number = random.randint(1,Thirukural.kural_max)
        temp_str = df.loc[ (df[Thirukural.KURAL_INDEX]==kural_number)  ][Thirukural.KURAL_INDEX]
        return self._format_output(temp_str)
    def respond_to_bot_user_input(self, bot_user_input):
        key, match = self._parse_line(bot_user_input)
        response = ""
        if key == "contains":
            word = match.group("contains")
            response = self.contains(word)
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
        elif key == "ends_with" or key == "ends_with_1":
            word = match.group("ends_with")
            response = self.endswith(word)
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
        elif key == "starts_with" or key == "starts_with_1":
            word = match.group("starts_with")
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
            response = self.startswith(word)
        elif key == "get":
            if match.group("Chapter")==None:
                response = self.get()
                if not response:
                    return bot_user_input + config["SEARCH_FAIL_MSG"]
                return response
            else:
                chapter_number = int(match.group("Chapter"))
            verse_number = None
            if match.group("Verse")==None:
                response = self.get(chapter_number)
                if not response:
                    return bot_user_input + config["SEARCH_FAIL_MSG"]
            else:
                verse_number = int(match.group("Verse"))
                response = self.get(chapter_number, verse_number)
                if not response:
                    return bot_user_input + config["SEARCH_FAIL_MSG"]
        elif key == "Kural":
            if match.group("Kural") is None:
                kural_number = None
            else:
                kural_number = int(match.group("Kural"))
            response = self.get(kural_number=kural_number)     
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
        elif key == "New":
            response = cdeeplearn.generate_tokens_from_corpus(corpus_files=['thirukural1.txt'], 
                    length=7, save_to_file='kural_model.h5',perform_training=False)
        elif key == "Help":
            response = config["HELP_MSG"]
        elif key == "Greet":
            response = config["GREET_MSG"]
        elif key == "Quit":
            response = config["QUIT_MSG"]
        else:
            response = config['FALLBACK_MSG']
        return response
    def _parse_line(self, line):
        for key, rx in _RE_DICT.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None
if __name__ == "__main__":
    """ Main script """
