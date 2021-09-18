import random
import requests
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import wikipedia as wk
import regex
import pandas as pd
import json
import os
cdeeplearn = __import__("cdeeplearn")
thirukkural = __import__("thirukkural")
tamil_utils = __import__("tamil_utils")

WIKI_DEFAULT_LANG = 'ta'
GOOGLE_SENTENCE_COUNT = 10
WIKI_SENTENCE_COUNT = 10

" Flatten a list of lists "
flatten_list = lambda list: [item for sublist in list for item in sublist]
bot_config_file = "./ChatBot.json"
config = {}
with open(bot_config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
sangam_nigandu_file = config['sangam_dictionary_file']    
data_ext = ".csv"
headers = []
columns_to_display = []
headers = ["poem_type", "poet_name", "poem", "translation","notes", "meaning", "poem_id", "poet_name_e","title","title_e"]
columns_to_display= []
config["show_columns"]['show_poem']="True"
_config_show = config["show_columns"]
for col in headers:
    key = 'show_'+col
    if _config_show[key].lower()=="true":
        columns_to_display.append(col)
data_folder = "./sangam_tamil_csv/"
poem_folder = "./sangam_tamil_poems/"
data_files = ['agananuru','purananuru','ainkurunuru','kalithokai', 'kurunthokai', 'natrinai', 'pathitrupathu', 'pattinapaalai', 
              'mullaipaattu', 'nedunalvaadai', 'kurinjipaattu','malaipadukadaam','maduraikaanji','porunaraatrupadai',
              'perumpaanaatrupadai', 'sirupaanaatrupadai', 'thirumurugaatrupadai', 'ainthinaiezhupathu', 'ainthinaiaimpathu',
              'kaarnaarpathu','thinaimozhiaimpathu','kainnilai','thinaimaalainootraimbathu']#, 'thirukkural' ]
POEM_TYPES = ['அகநானூறு', 'புறநானூறு', 'ஐங்குறுநூறு', 'கலித்தொகை', 'குறுந்தொகை', 'நற்றிணை', 'பதிற்றுப்பத்து', 'பட்டினப்பாலை', 
              'முல்லைப்பாட்டு', 'நெடுநல்வாடை','குறிஞ்சிப்பாட்டு','மலைபடுகடாம்', 'மதுரைக்காஞ்சி','பொருநராற்றுப்படை',
              'பெரும்பாணாற்றுப்படை', 'சிறுபாணாற்றுப்படை','திருமுருகாற்றுப்படை','ஐந்திணை எழுபது','ஐந்திணை ஐம்பது','கார் நாற்பது',
              'திணைமொழி ஐம்பது','கைந்நிலை','திணைமாலை நூற்றைம்பது']#,'திருக்குறள்']
def get_wikipedia_response(input,lang=WIKI_DEFAULT_LANG):
    wiki = ''
    if lang != WIKI_DEFAULT_LANG:
        wk.set_lang(lang)
    topic = input #reg_ex.group(1)
    wiki = wk.summary(topic, sentences = WIKI_SENTENCE_COUNT)
    return wiki
def get_google_search_response(query, index=0,sentence_count=GOOGLE_SENTENCE_COUNT):
    result = ''
    #print('google searching',query)
    try:
        search_result_list = list(search(query, tld="com", num=10, stop=3, pause=1))
        page = requests.get(search_result_list[index])
        tree = html.fromstring(page.content)
        soup = BeautifulSoup(page.content, features="lxml")
        article_text = ''
        article = soup.findAll('p')
        for element in article:
            article_text += '\n' + ''.join(element.findAll(text = True))
        article_text = article_text.replace('\n', '')
        sentences = article_text.split('.')[:sentence_count]
        sentences = '.'.join(sentences)
        #print(len(sentences),sentences)
        #chars_without_whitespace = sentences.translate(
        #    { ord(c): None for c in string.whitespace }
        #)
#        print(chars_without_whitespace)
        if len(sentences) > 0:
            result = sentences
        else:
            result = config["FALLBACK_MSG"]
        return result
    except:
        if len(result) == 0: result = fallback
        return result


class SangamPoems():
    POEM_TYPE = 0
    POET_NAME = 1
    POEM = 2
    TRANSLATION = 3
    NOTES = 5
    MEANING = 4
    POEM_ID = 6
    POET_NAME_ENGLISH = 7
    RANDOM_POEM_MSG = 'சீரற்ற தேர்வு  (random choice):<br>'
    def __init__(self):
        self.df = self.get_poem_data()
        self.nigandu = self._get_nigandu_from_file()
        print("There are {} words in sangam nigandu".format(len(self.nigandu)))
        self.tk = thirukkural.Thirukural(data_folder+'thirukkural.csv')
    def get_meaning(self, text):
        meaning = dict()
        for word in text.split():
            try:
                word_matching_dict = dict(filter(lambda item: word in item[0].split(), self.nigandu.items()))
                word_matching_dict = [{item:word_matching_dict[item]} for item in sorted(word_matching_dict, key=lambda k: len(k.split()), reverse=False)][0]
                meaning.update(word_matching_dict)
            except:
                continue
        return meaning
    def _get_nigandu_from_file(self,dictionary_file=sangam_nigandu_file):
        nigandu = dict()
        if not os.path.exists(dictionary_file):
            print('Creating and writing nigandu to',dictionary_file)
            nigandu = self._collect_nigandu()
            f = open(dictionary_file,"w",encoding='utf-8')
            for key in nigandu.keys():
                if key.strip() == '':
                    continue
                word = key.strip()
                meaning = ','.join(nigandu[key])
                f.write(word+"="+meaning+"\n")
            f.close()
            return nigandu
        print('Collecting nigandu from',dictionary_file)
        f = open(dictionary_file,"r",encoding='utf-8')
        for line in f:
            if line.strip() == '':
                continue
            word, meaning = line.split("=",1)
            word = word.strip()
            meaning = meaning.strip()
            if word == '' or meaning =='':
                continue
            if word in nigandu.keys():
                if meaning not in nigandu[word]:
                    #print('adding>'+meaning+'<to',nigandu_dict[word])
                    nigandu[word].append(meaning)
            else:
                nigandu[word]=list()
                nigandu[word].append(meaning)
        f.close()
        return nigandu                
    def _collect_nigandu(self):
        meanings = flatten_list(self.df['meaning'].str.split(","))
        nigandu_dict = dict()
        for word_pair in meanings:
            word = ''
            meaning = ''
            if "–" in word_pair:
                #print('word_pair',word_pair)
                word, meaning = word_pair.split("–",1)
                word = word.strip()
                meaning = meaning.strip()
                #print('word=',word,'meaning=',meaning)
            else:
                #print('"–" not in word_pair',word_pair)
                continue
            if word == '' or meaning =='':
                continue
            if word in nigandu_dict.keys():
                if meaning not in nigandu_dict[word]:
                    #print('adding>'+meaning+'<to',nigandu_dict[word])
                    nigandu_dict[word].append(meaning)
            else:
                nigandu_dict[word]=list()
                nigandu_dict[word].append(meaning)
        return nigandu_dict
    def _format_output(self, matching_row_indices, random_poem=False):
        result =[]
        df = self.df
        for row_id in matching_row_indices:
            row_id = int(row_id)
            pd_series = df.loc[df.index[row_id]]
            for col in columns_to_display:
                col_str = pd_series[col]
                result.append(col_str)
        random_poem_msg = ""
        if (random_poem):
            random_poem_msg = SangamPoems.RANDOM_POEM_MSG
        return random_poem_msg+'<br>'.join(result)
    def get_poem_data(self):
        df = pd.DataFrame()
        for index, data_file in enumerate(data_files):
            print('reading csv',data_folder+data_file+data_ext)
            dfs = pd.read_csv(data_folder+data_file+data_ext,encoding='utf-8',na_filter=False)
            dfs = dfs.replace({'poem' : {"\n":"<br>"}})
            dfs['poem'] = dfs['poem'].apply(tamil_utils._remove_punctuation_numbers)
            dfs = dfs.replace({"poet_name":{"பாடியவர்:":""}})
            dfs['poet_name'] = dfs['poet_name'].str.strip()
            dfs['poet_name_e'] = dfs['poet_name_e'].str.strip()
            #poem_type = data_file.replace(data_ext,"")
            poem_type = POEM_TYPES[index]
            dfs['poem_type']=poem_type
            df = df.append(dfs,ignore_index=True)
        return df
    def _help(self):
        return config["HELP_MSG"]
    def _greet(self):
        return config["GREET_MSG"]
    def _quit(self):
        return config["QUIT_MSG"]
    def _get_poem_line_word_count(self, poem_type):
        poems = [poem for poem in self.df.loc[self.df['poem_type']==poem_type]['poem'].tolist()]
        lines = flatten_list([poem.split("\n") for poem in poems])
        line_count = random.choice([len(poem.split("\n")) for poem in poems])
        word_count = sorted([len(line.split()) for line in lines if line.strip() != ''])
        minimum_word_count = word_count[0]
        maximum_word_count = word_count[-1]
        #print('line_count,minimum_word_count,maximum_word_count',line_count,minimum_word_count,maximum_word_count)
        return line_count,minimum_word_count,maximum_word_count
    def _deep_learn(self,poem_type,bot_user_input,value,include_meaning=False,minimum_words_per_sentence=4):
        poem = data_files[POEM_TYPES.index(poem_type)]
        #print('calling sangam tamil _deep_learn()',poem_type,poem)
        sentence_count, word_count_min, word_count_max = self._get_poem_line_word_count(poem_type)
        words_per_sentence = random.randrange(max(word_count_min,minimum_words_per_sentence),word_count_max)
        poem_word_count = sentence_count * words_per_sentence # 7 for Kural  76 for sangam aga,/puram
        #print('sentence count',sentence_count,'words per sentence',words_per_sentence)
        response = config["SEARCH_FAIL_MSG"]
        corpus_file=poem+'_poems_corpus.json'
        model_weights_file=poem+'_poems_corpus.h5'
        starting_word_file=poem+'_poems_starting_words.json'
        ending_word_file=poem+'_poems_ending_words.json'
        model_weights_folder = "./model_weights/"
        files_not_found = [model_weights_folder+file for file in [corpus_file,model_weights_file,starting_word_file,ending_word_file] if not os.path.exists(model_weights_folder+file) ]
        if len(files_not_found)>0:
            print("Following files needed for deep learning are missing:",files_not_found)
            return response
        if os.path.exists(model_weights_folder+corpus_file) and os.path.exists(model_weights_folder+model_weights_file) and \
                os.path.exists(model_weights_folder+starting_word_file) and os.path.exists(model_weights_folder+ending_word_file):
            cdeeplearn.set_parameters(corpus_file=corpus_file, model_weights_file=model_weights_file, 
                starting_word_file=starting_word_file,ending_word_file=ending_word_file)
            response = cdeeplearn.generate_tokens_from_corpus(corpus_files=[poem_folder+poem+"_poems.txt"], 
                    length=poem_word_count,perform_training=False,tokens_per_sentence=words_per_sentence)
            response = tamil_utils._cleanup_generated_poem(response)
            if include_meaning:
                meaning = self.get_meaning(response)
                for key,value in meaning.items():
                    response += "\n" + key+"="+''.join(value)
        return response
    def _contains(self,poem_type,bot_user_input,value):
        response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.contains(value))].tolist()#.to_string(index=False)
        #print(poem_type,'key == contains',value,response)
        if not response:
            return get_google_search_response(bot_user_input,value)
            #return bot_user_input + config["SEARCH_FAIL_MSG"]
        return self._format_output(response)
    def _begins_with(self,poem_type,bot_user_input,value):
        #print('_begins with',poem_type,bot_user_input,value)
        response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.startswith(value))].tolist()#.to_string(index=False)
        #print(poem_type,'key == begins_with',value,response)
        if not response:
            return get_google_search_response(bot_user_input)
            #return bot_user_input + config["SEARCH_FAIL_MSG"]
        return self._format_output(response)
    def _ends_with(self,poem_type,bot_user_input,value):
        response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.endswith(value))].tolist()#.to_string(index=False)
        #print(poem_type,'key == ends_with',value,response)
        if not response:
            return get_google_search_response(bot_user_input)
            #return bot_user_input + config["SEARCH_FAIL_MSG"]
        return self._format_output(response)
    def _poet_count(self,poem_type,bot_user_input):
        response = self.list_of_poets(poem_type)
        #print(poem_type,'key == ends_with',value,response)
        if not response:
            return get_google_search_response(bot_user_input)
        return response
    def _poet_poems(self,poem_type,bot_user_input,value):
        #print('_poet_poems value',value)
        response = self.list_poems_by_poet(poem_type, value)
        #print(poem_type,'key == ends_with',value,response)
        if not response:
            return get_google_search_response(bot_user_input)
        return response
    def _get_meaning(self,bot_user_input):
        inputs = self._get_key_words(bot_user_input)
        if len(inputs)>1:
            try:
                meaning = self.get_meaning(inputs[1])
                response = ''
                for key,value in meaning.items():
                    response += key+"="+''.join(value) +"\n"
                return response
            except:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
    def _get_poem_from_poem_id(self,poem_type,verse_index):
        poem_id_min, poem_id_max = self._get_poem_min_max(poem_type)
        #print(poem_type,poem_id_min, verse_index, poem_id_max)
        if verse_index < int(poem_id_min) or verse_index > int(poem_id_max):
            response = "(" + str(int(poem_id_min)) + " - "+ str(int(poem_id_max)) + ") "+config["NUMBER_LIMIT_MSG"]
            return response
        response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem_id']==verse_index)].tolist()#.to_string(index=False)
        return self._format_output(response)
        
    def _split_user_input(self,bot_user_input):
        inputs = self._get_key_words(bot_user_input)
        if len(inputs)==0:
            response = get_google_search_response(bot_user_input)
            if len(response)>0:
                return response
            else:
                return config['FALLBACK_MSG']
        poem_type = ''
        key = ''
        value = ''
        response = []
        verse_index = -1
        poem_type = inputs[0]
        if poem_type in POEM_TYPES and len(inputs)>1:
            if str(inputs[1]).isnumeric():
                verse_index = int(inputs[1])
            else:
                key = inputs[1]
                value = ''
                if len(inputs)>2:
                    value = ' '.join(inputs[2:])
        else:
            key = inputs[0]
        return poem_type,key,value,verse_index
    def respond_to_bot_user_input(self, bot_user_input):
        #print('user_input',bot_user_input)
        pd.set_option('display.max_colwidth',1000)
        if bot_user_input.split()[0] in config['key_words']["திருக்குறள்"]:
            response = self.tk.respond_to_bot_user_input(' '.join(bot_user_input.split()[1:]))
            return response
        try:
            poem_type,key,value,verse_index = self._split_user_input(bot_user_input)
        except:
            return config["FALLBACK_MSG"]
        #print('poem_type',poem_type,'key',key,'value',value,'verse_index',verse_index)
        if verse_index != -1:
            return self._get_poem_from_poem_id(poem_type, verse_index)
        action_dict={"greet":(self._greet,[],{}),
                     "help":(self._help,[],{}),
                     "quit":(self._quit,[],{}),
                     "contains":(self._contains,[poem_type,bot_user_input,value],{}),
                     "begins_with":(self._begins_with,[poem_type,bot_user_input,value],{}),
                     "ends_with":(self._ends_with,[poem_type,bot_user_input,value],{}),
                     "new":(self._deep_learn,[poem_type,bot_user_input,value],{"include_meaning":False}),
                     "poet_count" : (self._poet_count,[poem_type,bot_user_input],{}),
                     "poet_poems" : (self._poet_poems,[poem_type,bot_user_input,value],{}),
                     "meaning" : (self._get_meaning,[bot_user_input],{}),
                     "introduce": (self._introduce_bot,[bot_user_input],{})
                    }
        if key in action_dict.keys() or poem_type in action_dict.keys():
            function, args, kwargs = action_dict[key]
            return function(*args,**kwargs)
        else:
            return config['FALLBACK_MSG']
    def _introduce_bot(self, user_message):
        return "எனது பெயர் " + config["BOT_NAME"]        
    def _get_key_words(self, user_message):
        user_message = user_message.lower()
        user_words = user_message.split()
        key_words = []
        dict_keys = config["key_words"]
        for key in dict_keys:
            for value in map(str.lower, dict_keys[key]):
                #print(value,"==",user_message)
                if value in user_message:
                    key_words.append(key)
                    # Remove the word from user_message
                    """TODO remove words that contain value """
                    #user_message = '  '.join(filter(lambda x: value not in x, user_message.split()))
                    #print("removing ",value,"from user input",user_message)
                    user_message = user_message.replace(value,"")
                    break
        [key_words.append(int(s)) for s in user_message.split() if s.isdigit()]
        if key_words and not str(key_words[-1]).isdigit() and user_message != '':
            key_words.append(user_message.strip())
        #print(key_words)
        return key_words
    def _get_poem_min_max(self, poem_type):
        if not poem_type in POEM_TYPES:
            return config["INVALID_POEM_TYPE_MSG"]
        poem_id_min = self.df.loc[self.df['poem_type']==poem_type]['poem_id'].min()
        poem_id_max = self.df.loc[self.df['poem_type']==poem_type]['poem_id'].max()
        return poem_id_min, poem_id_max
    def list_poems_by_poet(self,poem_type,poet_name):
        poem_type = poem_type.strip()
        poet_name = poet_name.strip()
        if not poem_type in POEM_TYPES:
            return config["INVALID_POEM_TYPE_MSG"]
        #print('list_poems_by_poet',poem_type,poet_name)
        poems_by_poet = self.df.index[(self.df['poem_type']==poem_type) & 
                        (self.df['poet_name'].str.contains(poet_name)) | 
                        (self.df['poet_name_e'].str.contains(poet_name,flags=regex.IGNORECASE, regex=True))].tolist()
        #print('poems_by_poet',poems_by_poet)
        return self._format_output(poems_by_poet)
    def _create_corpus_data(self):
        poem_files = [data_folder.replace("csv","poems")+ p + "_poems.txt" for p in data_files]
        cdeeplearn._create_corpus_files(poem_files,corpus_file='sangam_corpus.json',starting_word_file='sangam_starting_words.json',
                       ending_word_file='sangam_ending_words.json',end_token_boundary=None)
    def _train_corpus_data(self):
        poem_files = [data_folder.replace("csv","poems")+ p + "_poems.txt" for p in data_files]
        perform_training = False
        poem_token_count = 94 # 7 for Kural  76 for sangam aga,/puram
        tokens_per_sentence = 4
        cdeeplearn.set_parameters(corpus_file='sangam_corpus.json', model_weights_file='sangam_corpus.h5',
                       starting_word_file='sangam_starting_words.json', ending_word_file='sangam_ending_words.json',
                       batch_size=15, number_of_epochs=90)
        result = cdeeplearn.generate_tokens_from_corpus(corpus_files=poem_files, 
                        length=poem_token_count, save_to_file='sangam_corpus.h5',perform_training=perform_training,
                        tokens_per_sentence=5)
        return result
    def list_of_poets(self, poem_type):
        #print('List of poets')
        if poem_type in POEM_TYPES:
            #print('getting list of poets',poem_type)
            poet_list = self.df.loc[self.df['poem_type']==poem_type,['poet_name','poem_id']]
            poet_list1 = poet_list.groupby('poet_name')['poem_id'].nunique().reset_index(name='# of Poems').sort_values('# of Poems',ascending=False)
            result1 = "{} எழுதிய புலவர்கள் எண்ணிக்கை:  {}".format(poem_type,len(poet_list1))
            poet_list = poet_list1.values.tolist()
            result = '\n'.join([poet+" எழுதிய பாடல்கள்:"+str(count) for poet,count in poet_list])
            return result1 + "\n" + result
        else:
            return config["INVALID_POEM_TYPE_MSG"]
if __name__ == "__main__":
    #user_message = "help 12"
    #user_message = "kalitogai உடைய மதுகையால்"
    #user_message = "kalitogai கொண்ட மதுகையால்"
    #user_message = "agananuru contains வண்டு"
    #user_message = "kalitogai ends with மதுகையால்"
    #user_message = "kalitogai செலவு. என்று முடியும்"
    #user_message = "kalitogai மதுகையால் என முடியும்"
    #user_message = "kalitogai மதுகையால் எனத் தொடங்கும்"
    #user_message = "kalitogai மதுகையால் என தொடங்கும்"
    #user_message = "meaning of அடுநை"
    #user_message = "thirumurugatrupadai 12"
    #user_message = "greetings"
    #user_message = "Greet!"
    #user_message = "welcome!"
    #user_message = "How are You?"
    #user_message = "Help"
    #user_message = "Bye"
    #user_message = "thirukural contains   தாள்சேர்ந்தார்க்   "
    #user_message = 'திணை மாலை நூற்று ஐம்பது list of poets'
    #user_message = "thirukural contains தாள்சேர்ந்தார்க்"
    #user_message = "திருக்குறள்  new"
    #user_message = "திருக்குறள் ends with பாற்று."
    #user_message = "thirukural starts with இருள்சேர்"
    #user_message="pathitrupathu 91"
    user_message="thirukural contains தாள்சேர்ந்தார்க்"
    user_message="thirukural தாள்சேர்ந்தார்க்  contains "
    user_message="thirukural கொண்ட  தாள்சேர்ந்தார்க் "
    user_message="thirukural தாள்சேர்ந்தார்க்  கொண்ட  "
    #user_message="thirukural உடைய  தாள்சேர்ந்தார்க் "
    #user_message="thirukural தாள்சேர்ந்தார்க்  உடைய  "
    #user_message="thirukural ends with குறிப்பு."
    #user_message="thirukural ends குறிப்பு."
    #user_message="thirukural ends with குறிப்பு."
    #user_message="thirukural ends குறிப்பு."
    #user_message="thirukural குறிப்பு என முடியும் "
    #user_message="thirukural குறிப்பு. முடியும் "
    #user_message="thirukural செறாஅச்  தொடங்கும்"
    #user_message="thirukural begins செறாஅச் "
    #user_message="thirukural starts with செறாஅச் "
    #user_message="create a new agananuru song" 
    #user_message = "thirukural     தாள்சேர்ந்தார்க்        contains "
    #user_message = "thirukural kural 1234"
    user_message = "thirukural get 13,4"
    user_message = "what is your name?"
    sp = SangamPoems()
    response = sp.respond_to_bot_user_input(user_message)
    print(user_message,"\n",response)
    exit()
    #exit()
    for poem in POEM_TYPES:
        user_message = poem +' poet_count'
        response = sp.respond_to_bot_user_input(user_message)
        print(poem, ' poet_count \n',response+"\n\n")
    exit()
    """
    meaning = sp.get_meaning("இலாட்டியேன்")
    response = ''
    for key,value in meaning.items():
        response += key+"="+''.join(value) +"\n"
    print("meaning of: இலாட்டியேன்=",response)
    exit()
    """
    #print(sp.list_of_poets('திணை மாலை நூற்று ஐம்பது'))
    #exit()
    #user_message = "உண்துறைம் மன்ற"
    bot_response = sp.respond_to_bot_user_input(user_message)
    print('bot_response',bot_response)
    exit()
    #"""    
    sp._create_corpus_data()
    exit()
    #"""
    """
    import random
    word, meaning = random.choice(list(sp.nigandu.items()))
    print(word,"=", ''.join(meaning),len(sp.nigandu))
    exit()
    """
    """
    #text = "நனந்தலை உலகம் வளைஇ நேமியொடு\nவலம்புரி பொறித்த மா தாங்கு தடக்கை\nநீர் செல நிமிர்ந்த மாஅல் போல\nபாடு இமிழ் பனிக்கடல் பருகி வலன் ஏர்பு\nகோடு கொண்டு எழுந்த கொடுஞ் செலவு எழிலி\nபெரும் பெயல் பொழிந்த சிறு புன்மாலை \n"
    meaning = sp.get_meaning(text,True)
    for key,value in meaning.items():
        print(key+"="+''.join(value))
    """
    #result = sp._get_key_words(user_message)
    #print(result)
    #poem = sp.respond_to_bot_user_input(user_message)
    #print('poem',poem)
