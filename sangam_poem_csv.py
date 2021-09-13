import string
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
sangam_poem_csv_file = sangam_csv_folder+"sangam_poems.csv"
sangam_poems_combined = []
csv_separator = ","
for i, sangam_poem in enumerate(data_files):
    csv_file = sangam_csv_folder+sangam_poem+".csv" # agananuru
    print("reading poems from",csv_file)
    df = pd.read_csv(csv_file,encoding='utf-8',sep=csv_separator,header=0,usecols=['poem'],index_col=None)
    df['poem_type'] = POEM_TYPES[i]
    df['poem'] = df['poem'].str.translate(str.maketrans('', '', string.punctuation))
    df['poem'] = df['poem'].str.replace("‘", '')
    df['poem'] = df['poem'].str.replace("’", '')
    df['poem'] = df['poem'].str.replace("“", '')
    df['poem'] = df['poem'].str.replace("”", '')
    df['poem'] = df['poem'].replace("\d+","",regex=True)
    sangam_poems_combined.append(df)
print("Combining all sangam poems into a single database")
sangam_df = pd.concat(sangam_poems_combined,axis=0,ignore_index=True)
print("Writing sangam poems into",sangam_poem_csv_file)
sangam_df.to_csv(sangam_poem_csv_file,encoding='utf-8',sep=csv_separator, index=False, columns=["poem_type", "poem"])