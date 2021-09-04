import regex
import pandas as pd
import json
# 
bot_config_file = "./ChatBot.json"
config = {}
with open(bot_config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
data_ext = ".csv"
data_folder = ""
headers = []
headers_to_display = []
headers = ["poem_type", "poet_name", "poem", "translation","notes", "meaning", "poem_id", "poet_name_e",]
headers_to_display = ['poem_type', "poet_name", 'poem',"translation","notes", "meaning"]
data_folder = "./sangam_tamil_csv/"
data_files = ['agananuru','purananuru','ainkurunuru','kalithokai', 'kurunthokai', 'natrinai', 'pathitrupathu', 'pattinapaalai', 
              'mullaipaattu', 'nedunalvaadai', 'kurinjipaattu','malaipadukadaam','maduraikaanji','porunaraatrupadai',
              'perumpaanaatrupadai', 'sirupaanaatrupadai', 'thirumurugaatrupadai' ]
POEM_TYPES = ['அகநானூறு ', 'புறநானூறு', 'ஐங்குறுநூறு ', 'கலித்தொகை', 'குறுந்தொகை', 'நற்றிணை', 'பதிற்றுப்பத்து', 'பட்டினப்பாலை', 
              'முல்லைப்பாட்டு', 'நெடுநல்வாடை','குறிஞ்சிப்பாட்டு','மலைபடுகடாம்', 'மதுரைக்காஞ்சி','பொருநராற்றுப்படை',
              'பெரும்பாணாற்றுப்படை', 'சிறுபாணாற்றுப்படை','திருமுருகாற்றுப்படை']
class SangamPoems():
    POEM_TYPE = 0
    POET_NAME = 1
    POEM = 2
    TRANSLATION = 3
    NOTES = 5
    MEANING = 4
    POEM_ID = 6
    POET_NAME_ENGLISH = 7
    RANDOM_POEM_MSG = 'சீரற்ற தேர்வு  (random choice):\n'
    def __init__(self):
        self.df = self.get_poem_data()
    def _format_output(self, matching_row_indices, random_poem=False):
        print(input)
        result =[]
        df = self.df
        for row_id in matching_row_indices:
            row_id = int(row_id)
            pd_series = df.loc[df.index[row_id]]
            #print('row id',row_id,pd_series)
            for col in headers_to_display:
                #print('column',col,pd_series[col])
                col_str = pd_series[col]
                result.append(col_str)
        random_poem_msg = ""
        if (random_poem):
            random_poem_msg = SangamPoems.RANDOM_POEM_MSG
        return random_poem_msg+'\n'.join(result)
    def get_poem_data(self):
        df = pd.DataFrame()
        for data_file in data_files:
            print('reading csv',data_folder+data_file+data_ext)
            dfs = pd.read_csv(data_folder+data_file+data_ext,encoding='utf-8',na_filter=False)
            dfs = dfs.replace({'poem' : {"<br>":'\n'}})
            dfs = dfs.replace({"poet_name":{"பாடியவர்:":""}})
            poem_type = data_file.replace(data_ext,"")
            dfs['poem_type']=poem_type
            df = df.append(dfs,ignore_index=True)
        return df
    def respond_to_bot_user_input(self, bot_user_input):
        print('user_input',bot_user_input)
        pd.set_option('display.max_colwidth',1000)
        inputs = self._get_key_words(bot_user_input)
        if len(inputs)==0:
            return config['FALLBACK_MSG']
        poem_type = ''
        key = ''
        value = ''
        response = []
        verse_index = -1
        poem_type = inputs[0]
        if len(inputs)>1:
            if str(inputs[1]).isnumeric():
                verse_index = int(inputs[1])
            else:
                key = inputs[1]
                value = ''
                if len(inputs)>2:
                    value = inputs[2]
        else:
            key = inputs[0]
        if key =='contains':
            response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.contains(value))].tolist()#.to_string(index=False)
            print(poem_type,'key == contains',value,response)
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
            return self._format_output(response)
        elif key =='begins_with':
            response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.startswith(value))].tolist()#.to_string(index=False)
            print(poem_type,'key == begins_with',value,response)
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
            return self._format_output(response)
        elif key =='ends_with':
            response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem'].str.endswith(value))].tolist()#.to_string(index=False)
            print(poem_type,'key == ends_with',value,response)
            if not response:
                return bot_user_input + config["SEARCH_FAIL_MSG"]
            return self._format_output(response)
        if verse_index != -1:
            poem_id_min, poem_id_max = self._get_poem_min_max(poem_type)
            print(poem_type,poem_id_min, verse_index, poem_id_max)
            if verse_index < poem_id_min or verse_index > poem_id_max:
                response = "(" + str(int(poem_id_min)) + " - "+ str(int(poem_id_max)) + ") "+config["NUMBER_LIMIT_MSG"]
                return response
            response = self.df.index[ (self.df['poem_type']==poem_type) & (self.df['poem_id']==verse_index)].tolist()#.to_string(index=False)
            return self._format_output(response)
        elif key.lower() == "help":
            response = config["HELP_MSG"]
        elif key.lower() == "greet":
            response = config["GREET_MSG"]
        elif key.lower() == "quit":
            response = config["QUIT_MSG"]
        else:
            response = config['FALLBACK_MSG']
        return response
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
                    user_message = user_message.replace(value,"")
                    break
        [key_words.append(int(s)) for s in user_message.split() if s.isdigit()]
        if key_words and not str(key_words[-1]).isdigit() and user_message != '':
            key_words.append(user_message.strip())
        print(key_words)
        return key_words
    def _get_poem_min_max(self, poem_type):
        poem_id_min = self.df.loc[self.df['poem_type']==poem_type]['poem_id'].min()
        poem_id_max = self.df.loc[self.df['poem_type']==poem_type]['poem_id'].max()
        return poem_id_min, poem_id_max
        
        
if __name__ == "__main__":
    #user_message = "agananuru contains பணைத்தோள்"
    #user_message = "kalitogai உடைய மதுகையால்"
    #user_message = "kalitogai கொண்ட மதுகையால்"
    #user_message = "agananuru contains வண்டு"
    #user_message = "kalitogai ends with மதுகையால்"
    #user_message = "kalitogai செலவு. என்று முடியும்"
    #user_message = "kalitogai மதுகையால் என முடியும்"
    #user_message = "kalitogai மதுகையால் எனத் தொடங்கும்"
    #user_message = "kalitogai மதுகையால் என தொடங்கும்"
    #user_message = "pathitrupathu 91"
    user_message = "சிறுபாணாற்றுப்படை  33"
    #user_message = "greetings"
    #user_message = "Greet!"
    #user_message = "welcome!"
    #user_message = "How are You?"
    #user_message = "Help"
    #user_message = "Bye"
    #user_message = "Get Lost"    
    sp = SangamPoems()
    #result = sp._get_key_words(user_message)
    #print(result)
    poem = sp.respond_to_bot_user_input(user_message)
    print('poem',poem)
