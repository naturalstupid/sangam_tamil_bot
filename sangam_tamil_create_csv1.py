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
headers = ["poem_id", "poet_name", "poem", "translation","notes", "meaning", "poet_name_e",'title', "title_e"] # ", thinai""thinai_e"
log_file_name= "sangam_tamil_csv.log"
log_file = open(log_file_name,"w")
#data_files = ['agananuru']
#POEM_TYPES = ['அகநானூறு']
#EN_POEM_TYPES = ['Akanānūru']
test_string =""# "_test"
warning_count = 0
missing_count = 0
for i, sangam_poem in enumerate(data_files):
    #sangam_poem = "kainnilai" #'purananuru # "agananuru" # kalithokai # kurunthokai #natrinai #ainkurunuru #pathitrupathu
    text_file = sangam_poem+".txt"
    csv_file = sangam_csv_folder+sangam_poem+test_string+".csv" # agananuru
    ta_poem_str1=POEM_TYPES[i]
    ta_poem_str2=POEM_TYPES[i]
    en_poem_str = EN_POEM_TYPES[i]
    poem_line = {}
    agam = pd.DataFrame(poem_line)
    read_id = -1
    poem = ''
    translation = ''
    line_no = 0
    log_file.write('reading text file:'+text_file+"\n")
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
                poem_bool['poem'] = True
                poem_bool['translation'] = True
                agam = agam.append(poem_line,ignore_index=True)
                #log_file.write("Processed poem_id:"+str(poem_id-1)+"\n")
                missing_keys = [key for key in poem_bool.keys() if not poem_bool[key]]
                if len(missing_keys)>0:
                    log_file.write("Poem_id:"+str(poem_id-1)+" is missing ["+' '.join(missing_keys)+"]\n")
                    missing_count += 1
            #log_file.write("reading tamil poem id,title line - poem_id="+str(poem_id)+"\n")
            poem_line = {}
            poem_keys =['poem_id','poem','poet_name_e','translation','notes','meaning']
            poem_bool = {}
            for key in poem_keys:
                poem_bool[key]=False
            poem = ''
            translation = ''
            poem_line['poem_id'] = poem_id
            poem_bool['poem_id'] = True
            poem_line['poet_name'] = temp_list[1]
            poem_line['title'] = ' '.join(temp_list[2:])#+"\n"
            #poem_line['thinai'] = ' '.join(temp_list[2].split()[0:2])
            #poem_line['title'] = ' '.join(temp_list[2].split()[3:])
        elif line.startswith(en_poem_str): # Puranānūru #Akanānūru
            #log_file.write("reading english poem_id,poet,thinai and title\n")
            read_id = 1
            temp_list = line.split(",")
            poem_line['poet_name_e'] = temp_list[1]
            poem_bool['poet_name_e'] = True
            poem_line['title_e'] =' '.join(temp_list[2:])#+"\n"
            #poem_line['thinai_e'] = ' '.join(temp_list[2].split()[0:2])
            #poem_line['title_e'] = ' '.join(temp_list[2].split()[3:])
            #print(temp_list)
        elif regex.search("^\s?note[s:]\s?",line,regex.IGNORECASE): #line.lower().startswith("notes:") or line.lower().startswith("note:") :
            #log_file.write("reading notes line\n")
            read_id = 3
            poem_line['notes'] = line[line.find(":")+1:].strip()
            poem_bool['notes'] = True
            #print(temp_list)
        elif regex.search("^\s?meaning[s:]\s?",line,regex.IGNORECASE): #line.lower().startswith("meanings:") or line.lower().startswith("meaning:") :
            #log_file.write("reading meanings line\n")
            read_id = 4
            poem_line['meaning'] = line[line.find(":")+1:].strip()
            poem_bool['meaning'] = True
            #print(temp_list)
        elif line.strip() != '' and  regex.search(u"^\p{L}*+|\p{L}\p{M}*+", line, flags=regex.UNICODE) and read_id == 0:
            #log_file.write("Reading tamil poem line\n")
            """ Poem lines """
            poem += line
            poem_bool['poem'] = True
        elif line.strip() != '' and  regex.search(r"^\w+", line):
            #log_file.write("reading translation line\n")
            """ translation lines  """
            translation += line
        else:
            continue
    poem_line['poem'] = poem
    poem_line['translation'] = translation
    poem_bool['poem'] = True
    poem_bool['translation'] = True
    missing_keys = [key for key in poem_bool.keys() if not poem_bool[key]]
    if len(missing_keys)>0:
        log_file.write("Poem_id:"+str(poem_id)+" is missing ["+' '.join(missing_keys)+"]\n")
    agam = agam.append(poem_line,ignore_index=True)
    df = pd.DataFrame.from_dict(agam)
    df = df.fillna('')
    #print(len(agam), len(df))
    #print(agam[399:400])
    #print((df.loc[ (df['poem_id']==400) ]['poem'].values))
    csv_separator = ","
    log_file.write('writing csv file'+csv_file+"\n")
    df.to_csv(csv_file,encoding='utf-8',sep=csv_separator, index=False, columns=headers)
    df = pd.read_csv(csv_file,encoding='utf-8',sep=csv_separator,header=0)
    log_file.write("Number of poems read:"+str(len(df))+"\n")
    poems = '\n'.join(map(str,df['poem'].values))
    import string
    log_file.write("Removing punctuation\n")
    poems = poems.translate(str.maketrans('', '', string.punctuation))
    poems = poems.replace("‘", '')
    poems = poems.replace("’", '')
    poems = regex.sub("\d+",'',poems)
    latin_pattern = "[a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F]+"
    for i,line in enumerate(poems.split("\n")):
        if line.strip() != "" and len(regex.findall(latin_pattern,line))>0:
            log_file.write("Warning:"+sangam_poem+" line#:"+str(i)+" "+line+" contains non-Tamil characters\n")
            warning_count += 1
    #poems = regex.sub(latin_pattern,'',poems)
    poem_file = sangam_poem_folder+sangam_poem+test_string+"_poems.txt"
    log_file.write('writing poem file'+poem_file+"\n")
    open(poem_file,"w", encoding='utf-8').write(poems)
log_file.close()
if warning_count > 0:
    print("There are",warning_count,"warnings. See",log_file_name,"for details.")
if missing_count > 0:
    print(missing_count,"poems are missing attributes. See",log_file_name,"for details.")
print("processing all sangam poem text files completed.")