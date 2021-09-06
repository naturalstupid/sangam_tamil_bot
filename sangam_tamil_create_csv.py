import regex
import pandas as pd
from pandas.tests.io.parser import index_col
sangam_text_folder = "./sangam_tamil_text/"
sangam_poem_folder = "./sangam_tamil_poems/"
sangam_csv_folder =  "./sangam_tamil_csv/"
data_files = ['agananuru','purananuru','ainkurunuru','kalithokai', 'kurunthokai', 'natrinai', 'pathitrupathu', 'pattinapaalai', 
              'mullaipaattu', 'nedunalvaadai', 'kurinjipaattu','malaipadukadaam','maduraikaanji','porunaraatrupadai',
              'perumpaanaatrupadai', 'sirupaanaatrupadai', 'thirumurugaatrupadai', 'ainthinaiezhupathu', 'ainthinaiaimpathu',
              'kaarnaarpathu','thinaimozhiaimpathu','kainnilai','thinaimaalainootraimbathu']#, 'thirukkural' ]
POEM_TYPES = ['அகநானூறு', 'புறநானூறு', 'ஐங்குறுநூறு', 'கலித்தொகை', 'குறுந்தொகை', 'நற்றிணை', 'பதிற்றுப்பத்து', 'பட்டினப்பாலை', 
              'முல்லைப்பாட்டு', 'நெடுநல்வாடை','குறிஞ்சிப்பாட்டு','மலைபடுகடாம்', 'மதுரைக்காஞ்சி','பொருநராற்றுப்படை',
              'பெரும்பாணாற்றுப்படை', 'சிறுபாணாற்றுப்படை','திருமுருகாற்றுப்படை','ஐந்திணை எழுபது','ஐந்திணை ஐம்பது','கார் நாற்பது',
              'திணைமொழி ஐம்பது','கைந்நிலை','திணைமாலை நூற்றைம்பது']#,'திருக்குறள்']
EN_POEM_TYPES = ['Akanānūru','Puranānūru','Ainkurunūru','Kalithokai','Kurunthokai','Natrinai','Pathitruppathu','Pattinapaalai',
                 'Mullaipaattu','Nedunalvaadai','Kurinjippāttu','Malaipadukadaam','Maduraikaanji','Porunaratrupadai',
                 'Perumpaanatrupadai','Sirupaanaatrupadai','Thirumurugaatrupadai','Ainthinai Ezhupathu','Aithinai Aimbathu',
                 'Kaar Naarpathu','Thinaimozhi Aimpathu','Kainnilai','Thinaimaalai Nootraimbathu'
               ]
headers = ["poem_id", "poet_name", "poem", "translation","notes", "meaning", "poet_name_e",'title'] # ", thinai", "title", "thinai_e", "title_e" 

for i, sangam_poem in enumerate(data_files):
    #sangam_poem = "kainnilai" #'purananuru # "agananuru" # kalithokai # kurunthokai #natrinai #ainkurunuru #pathitrupathu
    text_file = sangam_poem+".txt"
    csv_file = sangam_csv_folder+sangam_poem+".csv" # agananuru
    ta_poem_str1=POEM_TYPES[i]
    ta_poem_str2=POEM_TYPES[i]
    en_poem_str = EN_POEM_TYPES[i]
    poem_line = {}
    agam = pd.DataFrame(poem_line)
    read_id = -1
    poem = ''
    translation = ''
    line_no = 0
    print('reading text file',text_file)
    for line in open(sangam_text_folder+text_file, encoding='utf-8'): # agananuru
        line_no += 1
        if ("," in line) and (line.startswith(ta_poem_str1) or line.startswith(ta_poem_str2)):
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
        elif line.lower().startswith("notes:") or line.lower().startswith("note:") :
            read_id = 3
            poem_line['notes'] = line[line.find(":")+1:]
            #print(temp_list)
        elif line.lower().startswith("meanings:") or line.lower().startswith("meaning:") :
            read_id = 4
            poem_line['meaning'] = line[line.find(":")+1:]
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
    print('writing csv file',csv_file)
    df.to_csv(csv_file,encoding='utf-8',sep=csv_separator, index=False, columns=headers)
    df = pd.read_csv(csv_file,encoding='utf-8',sep=csv_separator,header=0)
    print(len(df))
    poems = '\n'.join(map(str,df['poem'].values))
    import string
    poems = poems.translate(str.maketrans('', '', string.punctuation))
    poems = poems.replace("‘", '')
    poems = poems.replace("’", '')
    poems = regex.sub("\d+",'',poems)
    poem_file = sangam_poem_folder+sangam_poem+"_poems.txt"
    print('writing poem file',poem_file)
    open(poem_file,"w", encoding='utf-8').write(poems)
