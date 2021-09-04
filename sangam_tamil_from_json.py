import regex
import pandas as pd
import json
headers = ['poem_type','poem','verse']
csv_file = "agananuru.csv"
json_folder = "./sangam_tamil_json/"
json_files = ['aganaanuru.json','puranaanuru.json','aingurunuru.json','divyaprabandam.json','kalittokai.json', 'kuruntokai.json', 'natrinai.json', 'sivavaakkiyam.json', 'tirukkoovaiyar.json', 'tirumantiram.json', 'tiruvarutpaa.json']#, 'thirukkural.json']
POEM_TYPES = ['அகநானூறு ', 'புறநானூறு', 'ஐங்குறுநூறு', 'திவ்யபிரபந்தம்', 'கலித்தொகை', 'குறுந்தொகை', 'நற்றிணை', 'சிவவாக்கியம்', 'திருக்கோவையார்', 'திருமந்திரம்', 'திருவருட்பா']
class SangamPoems():
    def __init__(self):
        self.df = self.get_poem_data()
        #self.df = self.df.drop(['meaning', 'paraphrase', 'translation'])
    def get_poem_data(self):
        df = pd.DataFrame()
        #import glob
        #json_files = list(glob.glob(json_folder+"/*.json")) 
        for json_file in json_files:
            print('reading json',json_folder+json_file)
            dfs = pd.read_json(json_folder+json_file,encoding='utf-8')
            # change <br> to "\n"
            dfs.replace({'poem' : {"<br>":"\n"}})
            poem_type = json_file.replace(".json","")
            dfs['poem_type']=poem_type
            df = df.append(dfs,ignore_index=True)
        return df
    def respond_to_bot_user_input(self, bot_user_input):
        pd.set_option('display.max_colwidth',1000)
        inputs = bot_user_input.split()
        poem_type = ''
        key = ''
        response = ''
        verse_index = -1
        poem_type = inputs[0]
        if inputs[1].isnumeric():
            verse_index = int(inputs[1])
        else:
            key = inputs[1]
        if key != '':
            response = self.df.loc[ (self.df['poem_type']==poem_type) & (self.df['poem'].str(key))]['poem'].to_string(index=False)
        elif verse_index != -1:
            response = self.df.loc[ (self.df['poem_type']==poem_type) & (self.df['verse']==verse_index)]['poem'].to_string(index=False)
        response = response.replace("<br>", "\n")
        response = response.replace("<br/>", "\n")
        response = response.replace("<br />", "\n")
        print(poem_type,key,verse_index)
        return response
if __name__ == "__main__":
    sp = SangamPoems()
    poem = sp.respond_to_bot_user_input("aganaanuru 12")
    #poem = sp.respond_to_bot_user_input('puranaanuru 23')
    #poem = sp.respond_to_bot_user_input('aingurunuru 23')
    #poem = sp.respond_to_bot_user_input('divyaprabandam 23') """ Not Working """
    #poem = sp.respond_to_bot_user_input('kalittokai 23')
    #poem = sp.respond_to_bot_user_input('kuruntokai 23')
    #poem = sp.respond_to_bot_user_input('natrinai 23')
    #poem = sp.respond_to_bot_user_input('sivavaakkiyam 23') """ Not Working """
    #poem = sp.respond_to_bot_user_input('tirukkoovaiyar 23')
    #poem = sp.respond_to_bot_user_input('tirumantiram 23') """ Not Working """
    #poem = sp.respond_to_bot_user_input('tiruvarutpaa 23')
    print(poem)
    exit()
