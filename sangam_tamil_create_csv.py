import regex
import pandas as pd
from pandas.tests.io.parser import index_col
#str = "புறநானூறு 3, பாடியவர்: இரும்பிடர்த்தலையார், பாடப்பட்டோன்: பாண்டியன் கருங்கை ஒள்வாள் பெரும்பெயர் வழுதி, திணை: பாடாண், துறை: செவியறிவுறூஉ  வாழ்த்தியல்"
#match = regex.match(r"\s?புறநானுறு|புறநானூறு\s?(\d+)[,]\s?பாடியவர்[:]([\p{L}*+|\p{L}\p{M}*+].*)\s?[,]பாடப்பட்டோன்[:]([\p{L}*+|\p{L}\p{M}*+].*)\s?[-]\s?([\p{L}*+|\p{L}\p{M}*+].*)", str)
sangam_text_folder = "./sangam_tamil_text/"
sangam_poem = "sirupaanaatrupadai" #'purananuru # "agananuru" # kalithokai # kurunthokai #natrinai #ainkurunuru #pathitrupathu
text_file = sangam_poem+".txt"
csv_file = sangam_text_folder+sangam_poem+".csv" # agananuru
ta_poem_str1="சிறுபாணாற்றுப்படை" #"நற்றிணை" #"புறநானுறு" # "அகநானுறு" # கலித்தொகை # குறுந்தொகை #நற்றிணை #ஐங்குறுநூறு #பதிற்றுப்பத்து
ta_poem_str2="சிறுபாணாற்றுப்படை" #"நற்றிணை" #"புறநானூறு" # "அகநானுறு" # கலித்தொகை # குறுந்தொகை #நற்றிணை #ஐங்குறுநூறு #பதிற்றுப்பத்து
en_poem_str = "Sirupaanaatrupadai" #"Puranānūru" # "Akanānūru" # Kalithokai # Kurunthokai #Natrinai #Ainkurunūru #Pathitruppathu
_RE_DICT = {"poem_info_t": regex.compile("r^அகநானுறு|அகநானூறு\s?(?P<poem_info>.*)",regex.IGNORECASE|regex.UNICODE), 
           'poem_tamil_t': regex.compile(r"^\s?(?P<poem_tamil>[\p{L}*+|\p{L}\p{M}*+].*)\s?.*", regex.IGNORECASE|regex.UNICODE),
           "translation_e" : regex.compile(r"\s?(?P<translation>\b\w+\b)",regex.IGNORECASE), 
           "notes_e":regex.compile("r^Akanānūru\s?(?P<meaning_tamil>.*)",regex.IGNORECASE), 
          "meaning_e": regex.compile(r"^Meanings:\s+(?P<meaning_words>.*)",regex.IGNORECASE)
          }
def _parse_line(line):
    for key, rx in _RE_DICT.items():
        match = rx.search(line)
        if match:
            return key, match
    # if there are no matches
    return None, None
poem_line = {}
agam = pd.DataFrame(poem_line)
headers = ["poem_id", "poet_name", "poem", "translation","notes", "meaning", "poet_name_e",'title'] # ", thinai", "title", "thinai_e", "title_e" 
read_id = -1
poem = ''
translation = ''
line_no = 0
for line in open(sangam_text_folder+text_file, encoding='utf-8'): # agananuru
    line_no += 1
    if line.startswith(ta_poem_str1) or line.startswith(ta_poem_str2):
        read_id = 0
        """ TODO Use Regex for separating poem_id, poet, thinai and title """
        temp_list = line.split(",")
        poem_id = int(regex.search(r'(\d+)', temp_list[0]).group().strip())
        if poem_id > 1:
            poem_line['poem'] = poem
            poem_line['translation'] = translation
            agam = agam.append(poem_line,ignore_index=True)
            print("Processed poem_id",poem_id)
        poem_line = {}
        poem = ''
        translation = ''
        poem_line['poem_id'] = poem_id
        poem_line['poet_name'] = temp_list[1]
        poem_line['title'] = ' '.join(temp_list[2:])#+"\n"
        #poem_line['thinai'] = ' '.join(temp_list[2].split()[0:2])
        #poem_line['title'] = ' '.join(temp_list[2].split()[3:])
    elif line.startswith(en_poem_str): # Puranānūru #Akanānūru
        read_id = 1
        temp_list = line.split(",")
        poem_line['poet_name_e'] = temp_list[1]
        translation = ' '.join(temp_list[2:])#+"\n"
        #poem_line['thinai_e'] = ' '.join(temp_list[2].split()[0:2])
        #poem_line['title_e'] = ' '.join(temp_list[2].split()[3:])
        #print(temp_list)
    elif line.startswith("Notes:"):
        read_id = 3
        poem_line['notes'] = line[len('Notes:'):]
        #print(temp_list)
    elif line.startswith("Meanings:"):
        read_id = 4
        poem_line['meaning'] = line[len('Meanings:'):]
        #print(temp_list)
    elif line.strip() != '' and  regex.search(u"^\p{L}*+|\p{L}\p{M}*+", line, flags=regex.UNICODE) and read_id == 0:
        """ Poem lines """
        poem += line
    elif line.strip() != '' and  regex.search(r"^\w+", line):
        """ translation lines  """
        translation += line
    else:
        continue
poem_line['poem'] = poem
poem_line['translation'] = translation
agam = agam.append(poem_line,ignore_index=True)
df = pd.DataFrame.from_dict(agam)
df = df.fillna('')
print(len(agam), len(df))
#print(agam[399:400])
#print((df.loc[ (df['poem_id']==400) ]['poem'].values))
csv_separator = ","
df.to_csv(csv_file,encoding='utf-8',sep=csv_separator, index=False, columns=headers)
df = pd.read_csv(csv_file,encoding='utf-8',sep=csv_separator,header=0)
print(len(df))
poems = '\n'.join(map(str,df['poem'].values))
import string
poems = poems.translate(str.maketrans('', '', string.punctuation))
poems = poems.replace("‘", '')
poems = poems.replace("’", '')
poems = regex.sub("\d+",'',poems)
open(sangam_text_folder+sangam_poem+"_poems.txt","w", encoding='utf-8').write(poems)
exit()
