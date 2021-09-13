import os, re, regex
import json
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dropout, TimeDistributed, Dense, Activation, Embedding
"""
from google.colab import drive
drive.mount('/content/gdrive/')
google_drive = '/content/gdrive/MyDrive/'
"""
google_drive = './'
model_weights_directory = google_drive+'model_weights/'
BATCH_SIZE = 15
CHORD_LENGTH = 1
EPOCHS = 75
MODEL_WEIGHTS_FILE = 'corpus.h5'
corpus_json_file = 'corpus.json'
LOG_FILE = "log.txt"
starting_word_json_file = corpus_json_file.replace(".json", '') + 'starting_words.json'
ending_word_json_file = corpus_json_file.replace(".json", '') + 'ending_words.json'
TOKEN_PATTERN = r"[\w]+" #r"[\\X+]" #r"[\w']+" #r"[\w']+|[.,!?;]" r"[^\x00-\x7F]+"
def _get_all_tamil_characters(include_space=True, include_vadamozhi=False):
    TAMIL_UNICODE_1_TA = ["க","ங","ச","ஞ","ட","ண","த","ந","ன","ப","ம","ய","ர","ற","ல","ள","ழ","வ"]
    TAMIL_UNICODE_1_SAN = ["ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ"]
    TAMIL_UNICODE_1 = TAMIL_UNICODE_1_TA+TAMIL_UNICODE_1_SAN
    TAMIL_UNICODE_2 = ["ா","ி","ீ","ூ","ு","ெ","ே","ை","ொ","ோ","ௌ","்"]
    UYIRGAL = ["அ","ஆ","இ","ஈ","உ","ஊ","எ","ஏ","ஐ","ஒ","ஓ","ஔ"]
    MEYGAL= [tu1+TAMIL_UNICODE_2[-1] for tu1 in TAMIL_UNICODE_1 ]
    all_tamil_chars = []
    if include_space:
        all_tamil_chars = [' ']
    T_U_1 = TAMIL_UNICODE_1_TA
    if include_vadamozhi:
        T_U_1 += TAMIL_UNICODE_1_SAN 
    all_tamil_chars += UYIRGAL+['ஃ']+T_U_1+ [t1+t2 for t1 in T_U_1 for t2 in TAMIL_UNICODE_2]
    return all_tamil_chars

def set_parameters(batch_size=None, number_of_epochs=None,model_weights_folder= None,
                   corpus_file=None, model_weights_file=None, token_pattern=None,
                   starting_word_file=None, ending_word_file=None,log_file=None):
    """
    Set parameters of deep learning method:
    @param batch_size: Batch size for training. Default=16
    @param number_of_epochs: Default 90
    @param model_weights_folder: Default: "model_weights/"
    @param corpus_file: File containing dictionary of unique tokens. Default:"corpus.json"
    @param starting_word_file: File containing dictionary of starting tokens. Default:"starting_words.json"
    @param ending_word_file: File containing dictionary of ending tokens. Default:"ending_words.json"
    @param model_weights_file: File containing trained weights. Default:"<raagam_name>_corpus.h5"
    @param log_file: File containing loss and accuracy at end of each epoch. Default:"log.txt"
    @param token_pattern: default regex pattern for collecting tokens/words from corpus file. Default: r"[\w']+|[.,!?;]" 
    """
    global BATCH_SIZE, EPOCHS, model_weights_directory, corpus_json_file, MODEL_WEIGHTS_FILE, TOKEN_PATTERN, starting_word_json_file, ending_word_json_file
    if token_pattern:
        TOKEN_PATTERN = token_pattern
        print('TOKEN_PATTERN set to:',TOKEN_PATTERN)
    if batch_size:
        BATCH_SIZE = batch_size
        print('BATCH_SIZE set to:',BATCH_SIZE)
    if number_of_epochs:
        EPOCHS = number_of_epochs
        print('EPOCHS set to:',EPOCHS)
    if model_weights_folder:
        model_weights_directory = model_weights_folder
        print('model_weights_directory set to:',model_weights_directory)
    if corpus_file:
        corpus_json_file = corpus_file
        print('corpus_json_file set to:',corpus_json_file)
    if starting_word_file:
        starting_word_json_file = starting_word_file
        print('starting_word_json_file set to:',starting_word_json_file)
    if ending_word_file:
        ending_word_json_file = ending_word_file
        print('ending_word_json_file set to:',ending_word_json_file)
    if model_weights_file:
        MODEL_WEIGHTS_FILE = model_weights_file
        print('MODEL_WEIGHTS_FILE set to:',MODEL_WEIGHTS_FILE)
    if log_file:
        LOG_FILE = log_file
        print('LOG FILE set to:',LOG_FILE)
def are_deeplearning_parameters_defined():
    parameters_are_set = (CHORD_LENGTH >0 ) and (BATCH_SIZE>0) and (EPOCHS>0) and (corpus_json_file != '') and (MODEL_WEIGHTS_FILE != '') and (TOKEN_PATTERN != '')
    print("parameters_are_set to:",parameters_are_set)
    return parameters_are_set
def _read_batches(all_chars, unique_chars):
    length = all_chars.shape[0]
    batch_chars = int(length / BATCH_SIZE) #155222/16 = 9701
    
    for start in range(0, batch_chars - CHORD_LENGTH, CHORD_LENGTH):  #(0, 9637, 64)  #it denotes number of batches. It runs everytime when
        #new batch is created. We have a total of 151 batches.
        X = np.zeros((BATCH_SIZE, CHORD_LENGTH))    #(16, 64)
        Y = np.zeros((BATCH_SIZE, CHORD_LENGTH, unique_chars))   #(16, 64, 87)
        for batch_index in range(0, BATCH_SIZE):  #it denotes each row in a batch.  
            for i in range(0, CHORD_LENGTH):  #it denotes each column in a batch. Each column represents each token means 
                #each time-step token in a sequence.
                X[batch_index, i] = all_chars[batch_index * batch_chars + start + i]
                Y[batch_index, i, all_chars[batch_index * batch_chars + start + i + 1]] = 1 #here we have added '1' because the
                #correct label will be the next token in the sequence. So, the next token will be denoted by
                #all_chars[batch_index * batch_chars + start + i] + 1. 
        yield X, Y
def _get_model(batch_size, sequence_length, unique_chars):
    model = Sequential()
    
    model.add(Embedding(input_dim = unique_chars, output_dim = 512, batch_input_shape = (batch_size, sequence_length), name = "embd_1")) 
    
    model.add(LSTM(256, return_sequences = True, stateful = True, name = "lstm_first"))
    model.add(Dropout(0.2, name = "drp_1"))
    
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(TimeDistributed(Dense(unique_chars)))
    model.add(Activation("softmax"))
    
    #model.load_weights("model_weights/Weights_80.h5", by_name = True)
    
    return model
def _train_the_model(data, epoch_max):
    global MODEL_WEIGHTS_FILE, corpus_json_file
    char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(data))))}
    print("Number of unique tokens in our whole tunes database = {}".format(len(char_to_index))) #87
    with open(os.path.join(model_weights_directory, corpus_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
        
    index_to_char = {i: ch for (ch, i) in char_to_index.items()}
    unique_chars = len(char_to_index)
    
    model = _get_model(BATCH_SIZE, CHORD_LENGTH, unique_chars)
    model.summary()
    model.compile(loss = "categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])
    
    all_tokens = np.asarray([char_to_index[c] for c in data], dtype = np.int32)
    print("Total number of tokens = "+str(all_tokens.shape[0])) #155222
    
    epoch_number, loss, accuracy = [], [], []
    
    for epoch in range(epoch_max+1):
        print("Epoch {}/{}".format(epoch+1, epoch_max))
        final_epoch_loss, final_epoch_accuracy = 0, 0
        epoch_number.append(epoch+1)
        
        for i, (x, y) in enumerate(_read_batches(all_tokens, unique_chars)):
            final_epoch_loss, final_epoch_accuracy = model.train_on_batch(x, y) #check documentation of train_on_batch here: https://keras.io/models/sequential/
            print("Batch: {}, Loss: {}, Accuracy: {}".format(i+1, final_epoch_loss, final_epoch_accuracy))
            #here, above we are reading the batches one-by-one and train our model on each batch one-by-one.
        loss.append(final_epoch_loss)
        accuracy.append(final_epoch_accuracy)
        
    if not os.path.exists(model_weights_directory):
        os.makedirs(model_weights_directory)
    model.save_weights(os.path.join(model_weights_directory, MODEL_WEIGHTS_FILE))
    print('Saved Weights at epoch {} to file {}'.format(epoch+1, MODEL_WEIGHTS_FILE))
    
    #creating dataframe and record all the losses and accuracies at each epoch
    log_frame = pd.DataFrame(columns = ["Epoch", "Loss", "Accuracy"])
    log_frame["Epoch"] = epoch_number
    log_frame["Loss"] = loss
    log_frame["Accuracy"] = accuracy
    log_frame.to_csv(LOG_FILE, index = False)
    
def _make_model(unique_chars):
    model = Sequential()
    
    model.add(Embedding(input_dim = unique_chars, output_dim = 512, batch_input_shape = (1, 1))) 
  
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, stateful = True)) 
    #remember, that here we haven't given return_sequences = True because here we will give only one token to generate the
    #sequence. In the end, we just have to get one output which is equivalent to getting output at the last time-stamp. So, here
    #in last layer there is no need of giving return sequences = True.
    model.add(Dropout(0.2))
    
    model.add((Dense(unique_chars)))
    model.add(Activation("softmax"))
    
    return model
def _generate_sequence(starting_token, ending_token, seq_length):
    global MODEL_WEIGHTS_FILE, corpus_json_file,starting_word_json_file, ending_word_json_file
    print('_generate_sequence','corpus_json_file',corpus_json_file,'MODEL_WEIGHTS_FILE',MODEL_WEIGHTS_FILE)
    with open(os.path.join(model_weights_directory, corpus_json_file),encoding='utf-8') as f:
        char_to_index = json.load(f)
    index_to_char = {i:ch for ch, i in char_to_index.items()}
    unique_chars = len(index_to_char)
    if starting_token == None or starting_token.trim() == '':
        with open(os.path.join(model_weights_directory,starting_word_json_file),mode='r',encoding='utf-8') as f:
            starting_words = json.load(f)
        starting_token = np.random.choice(list(starting_words))
        print("Starting Token: ", starting_token)
    if ending_token == None or ending_token.trim() == '':
        with open(os.path.join(model_weights_directory,ending_word_json_file),mode='r',encoding='utf-8') as f:
            ending_words = json.load(f)
        ending_token = np.random.choice(list(ending_words))
        print("Ending Token: ", ending_token)
    initial_index = char_to_index[starting_token]
    ending_index = char_to_index[ending_token]
    
    model = _make_model(unique_chars)
    model_file = model_weights_directory + MODEL_WEIGHTS_FILE
    print("Reading model weights from file:"+model_file)
    model.load_weights(model_file)
     
    sequence_index = [initial_index]
    excluded_tokens = ['.', '?']
    for _ in range(seq_length-2):
        batch = np.zeros((1, 1))
        batch[0, 0] = sequence_index[-1]
        
        predicted_probs = model.predict_on_batch(batch).ravel()
        sample = np.random.choice(range(unique_chars), size = 1, p = predicted_probs)
        sequence_index.append(sample[0])
    sequence_index.append(ending_index)
    seq = [index_to_char[c] for c in sequence_index]
    return seq 
def _get_tokens_from_file(file, _TOKEN_PATTERN):
    token_array =[]
    with open(file,"r",encoding='utf-8') as file_object:
        line = file_object.readline()
        while line:
            tokens = regex.findall(_TOKEN_PATTERN, line)
            #tokens = line.split()
            token_array += tokens
            line = file_object.readline()
    file_object.close()
    return token_array
def _create_corpus_files(data_files,corpus_file=None, starting_word_file=None, ending_word_file=None,end_token_boundary=7):
    global MODEL_WEIGHTS_FILE, corpus_json_file,starting_word_json_file, ending_word_json_file
    if corpus_file:
        set_parameters(corpus_file=corpus_file)
    if starting_word_file:
        set_parameters(starting_word_file=starting_word_file)
    if ending_word_file:
        set_parameters(ending_word_file=ending_word_file)

    print(model_weights_directory, corpus_json_file, starting_word_json_file, ending_word_json_file)
    end_token_boundary = end_token_boundary
    starting_words = []
    ending_words = []
    data =[]
    for data_file in data_files:
        if not os.path.exists(data_file):
            Exception("Data file:",data_file," does not exist")
        if end_token_boundary is None:
            f= open(data_file,"r",encoding='utf-8')
            file_contents = f.read()
            import string
            file_contents = file_contents.translate(str.maketrans('', '', string.punctuation))
            file_contents = file_contents.replace("‘", '')
            file_contents = file_contents.replace("’", '')
            file_contents = file_contents.replace("“", '')
            file_contents = file_contents.replace("”", '')
            file_contents = regex.sub("\d+",'',file_contents)
            line_data= file_contents.split("\n\n")
            data += [item for item in file_contents.split() if item != '']
            f.close()
            starting_words += [item.split()[0] for item in line_data if item != '']
            ending_words += [item.split()[-1] for item in line_data if item != '']
            #print(starting_words, ending_words,len(data))
        else:
            data += _get_tokens_from_file (data_file, TOKEN_PATTERN)
            starting_words += data[0::end_token_boundary]
            ending_words = +data[end_token_boundary-1::end_token_boundary]
        print(data_file,len(starting_words),len(ending_words),len(data),len(set(data)))
    data = sorted(list(set(data)),key=lambda x: (x[0] == "", x[0]))
    char_to_index = {ch: i for (i, ch) in enumerate(data)}
    #char_to_index = {ch: i for (i, ch) in enumerate(list(set(data)))}
    print("Number of unique tokens in corpus data = {}".format(len(char_to_index)),corpus_json_file) #87
    with open(os.path.join(model_weights_directory,corpus_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    starting_words = sorted(list(set(starting_words)),key=lambda x: (x[0] == "", x[0]))
    char_to_index = {ch: i for (i, ch) in enumerate(starting_words)}
    #char_to_index = {ch: i for (i, ch) in enumerate(list(set(starting_words)))}
    print(list(char_to_index.items())[:5])
    print("Number of unique starting words in corpus data = {}".format(len(char_to_index)),starting_word_json_file) #87
    with open(os.path.join(model_weights_directory,starting_word_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    ending_words = sorted(list(set(ending_words)),key=lambda x: (x[0] == "", x[0]))
    char_to_index = {ch: i for (i, ch) in enumerate(ending_words)}
    #char_to_index = {ch: i for (i, ch) in enumerate(list(set(ending_words)))}
    print(list(char_to_index.items())[:5])
    print("Number of unique ending words in corpus data = {}".format(len(char_to_index)),ending_word_json_file) #87
    with open(os.path.join(model_weights_directory,ending_word_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    return data,starting_words,ending_words
def _create_corpus_files_old(data_files,corpus_file=None, starting_word_file=None, ending_word_file=None,end_token_boundary=7):
    global MODEL_WEIGHTS_FILE, corpus_json_file,starting_word_json_file, ending_word_json_file
    if corpus_file:
        set_parameters(corpus_file=corpus_file)
    if starting_word_file:
        set_parameters(starting_word_file=starting_word_file)
    if ending_word_file:
        set_parameters(ending_word_file=ending_word_file)

    print(model_weights_directory, corpus_json_file, starting_word_json_file, ending_word_json_file)
    end_token_boundary = end_token_boundary
    starting_words = []
    ending_words = []
    data =[]
    for data_file in data_files:
        if not os.path.exists(data_file):
            Exception("Data file:",data_file," does not exist")
        if end_token_boundary is None:
            with open(data_file,"r",encoding='utf-8') as f:
                line = f.readline()
                start_index = 0
                end_index = -1
                while line:
                    #print(line)
                    temp_list = line.split()
                    token_count = len(temp_list)
                    if line == "\n" or token_count == 0:
                        print('end of poem reached',start_index,end_index)
                        starting_words.append(data[start_index])
                        ending_words.append(data[end_index])
                        end_index -= 1
                        print(data_file,start_index,data[start_index],end_index,data[end_index])
                        start_index = end_index + 1
                        end_index = start_index
                    else:
                        print("inside the poem",start_index,end_index)
                        end_index += token_count
                        data += temp_list
                    print(line,token_count,start_index,data[start_index],end_index,data[end_index])
                    line = f.readline()
            end_index -= 1
            starting_words.append(data[start_index])
            ending_words.append(data[end_index])
            f.close()
        else:
            data += _get_tokens_from_file (data_file, TOKEN_PATTERN)
            starting_words += data[0::end_token_boundary]
            ending_words += data[end_token_boundary-1::end_token_boundary]
        print(data_file,len(starting_words),len(ending_words),len(data),len(set(data)))
    
    #char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(data)),key=lambda x: (x[0] == "", x[0])))}
    char_to_index = {ch: i for (i, ch) in enumerate(list(set(data)))}
    print("Number of unique tokens in corpus data = {}".format(len(char_to_index)),corpus_json_file) #87
    with open(os.path.join(model_weights_directory,corpus_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    #char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(starting_words)),key=lambda x: (x[0] == "", x[0])))}
    char_to_index = {ch: i for (i, ch) in enumerate(list(set(starting_words)))}
    print(list(char_to_index.items())[:5])
    print("Number of unique starting words in corpus data = {}".format(len(char_to_index)),starting_word_json_file) #87
    with open(os.path.join(model_weights_directory,starting_word_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    #char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(ending_words)),key=lambda x: (x[0] == "", x[0])))}
    char_to_index = {ch: i for (i, ch) in enumerate(list(set(ending_words)))}
    print(list(char_to_index.items())[:5])
    print("Number of unique ending words in corpus data = {}".format(len(char_to_index)),ending_word_json_file) #87
    with open(os.path.join(model_weights_directory,ending_word_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
                
def generate_tokens_from_corpus(corpus_files:list,starting_token:str=None, ending_token:str=None, length:int=32, 
                                save_to_file=None,perform_training=False, tokens_per_sentence=4):
    """
    Generate token sequence of defined length from corpus text files
    @param corpus_files: List of corpus file paths that contain sequence of tokens
    @param starting_token: Starting token. Default=None
    @param ending_token: Ending token. Default=None
    @param length: desired length of tokens to be generated. 
            Note: Not always exact number of tokens may be generated
    @param save_to_file: File name to which generated tokens are to be written. Default=None
    @param perform_training: True/False. Default = False. 
        If True, training weights are generated even if model weight file is found  
    """
    global MODEL_WEIGHTS_FILE,corpus_json_file
    print('generate_tokens_from_corpus','corpus_json_file',corpus_json_file,'MODEL_WEIGHTS_FILE',MODEL_WEIGHTS_FILE)
    print("Batch Size = {} Width = {} Epochs = {}".format(BATCH_SIZE,CHORD_LENGTH,EPOCHS))
    model_file = model_weights_directory + MODEL_WEIGHTS_FILE
    if not os.path.isfile(model_file) or perform_training:
        data = []
        for corpus_file in corpus_files:
            data += _get_tokens_from_file (corpus_file, TOKEN_PATTERN)
        _train_the_model(data, EPOCHS)
    tokens = _generate_sequence(starting_token, ending_token, length)
    result = ''
    for i in range(0, len(tokens), tokens_per_sentence):
        result += ' '.join(tokens[i:i+tokens_per_sentence]) + "\n"
    if save_to_file:
        with open(save_to_file,"w",encoding="utf-8") as f:
            f.write(result)
    return result

if __name__ == "__main__":
    """
    data_files = ['agananuru','purananuru','ainkurunuru','kalithokai', 'kurunthokai', 'natrinai', 'pathitrupathu', 'pattinapaalai', 
              'mullaipaattu', 'nedunalvaadai', 'kurinjipaattu','malaipadukadaam','maduraikaanji','porunaraatrupadai',
              'perumpaanaatrupadai', 'sirupaanaatrupadai', 'thirumurugaatrupadai', 'ainthinaiezhupathu', 'ainthinaiaimpathu',
              'kaarnaarpathu','thinaimozhiaimpathu','kainnilai','thinaimaalainootraimbathu']#, 'thirukkural' ]
    #data_files = ['delme','delme2','delme3']
    data_files = ["./sangam_tamil_poems/" + d + "_poems.txt" for d in data_files]
    set_parameters(corpus_file='sangam_corpus.json', model_weights_file='sangam_corpus.h5',
                       starting_word_file='sangam_starting_words.json', ending_word_file='sangam_ending_words.json')
    #_create_corpus_files_old(data_files,end_token_boundary=None)
    #_,_,_=_create_corpus_files(data_files,end_token_boundary=None)
    exit()
    """
    """
    f = open(data_files[0],"r",encoding='utf-8')
    data = f.read().split("\n\n")
    starting_words = [item.split()[0] for item in data if item != '']
    ending_words = [item.split()[-1] for item in data if item != '']
    print(starting_words)
    print(ending_words)
    """
    #"""
    data_files = ['agananuru','purananuru','ainkurunuru','kalithokai', 'kurunthokai', 'natrinai', 'pathitrupathu', 'pattinapaalai', 
                  'mullaipaattu', 'nedunalvaadai', 'kurinjipaattu','malaipadukadaam','maduraikaanji','porunaraatrupadai',
                  'perumpaanaatrupadai', 'sirupaanaatrupadai', 'thirumurugaatrupadai', 'ainthinaiezhupathu', 'ainthinaiaimpathu',
                  'kaarnaarpathu','thinaimozhiaimpathu','kainnilai','thinaimaalainootraimbathu']#, 'thirukkural' ]
    poem = "kurunthokai_poems" # 'thirukural1'# 
    perform_training = False
    tokens_per_sentence = 5
    poem_token_count = 13 * tokens_per_sentence # 7 for Kural  76 for sangam aga,/puram
    data_files = [poem+'.txt']
    data_files = ["./sangam_tamil_poems/"+data_file for data_file in data_files]
    set_parameters(corpus_file=poem+'_corpus.json', model_weights_file=poem+'_corpus.h5', starting_word_file=poem+'_starting_words.json', 
                   ending_word_file=poem+'_ending_words.json')
    _,_,_=_create_corpus_files(data_files,end_token_boundary=None)
    result = generate_tokens_from_corpus(corpus_files=data_files, 
                    length=poem_token_count, save_to_file=poem+'_corpus.h5',perform_training=perform_training,
                    tokens_per_sentence=tokens_per_sentence)
    print(result)
    """
    #"""
    """ Get First and Last words of kural and save in json file
    data = _get_tokens_from_file ('thirukural1.txt', TOKEN_PATTERN)
    starting_words = data[0::7]
    ending_words = data[6::7]
    char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(starting_words))))}
    print(list(char_to_index.items())[:5])
    print("Number of unique starting words in our whole kural database = {}".format(len(char_to_index))) #87
    with open(os.path.join(model_weights_directory, 'kural_starting_words.json'), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(ending_words))))}
    print(list(char_to_index.items())[:5])
    print("Number of unique ending words in our whole kural database = {}".format(len(char_to_index))) #87
    with open(os.path.join(model_weights_directory, 'kural_ending_words.json'), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    """
    """
    data = _get_tokens_from_file ('thirukural1.txt', TOKEN_PATTERN)
    char_to_index = {ch: i for (i, ch) in enumerate(sorted(list(set(data))))}
    print("Number of unique tokens in our whole tunes database = {}".format(len(char_to_index))) #87
    with open(os.path.join(model_weights_directory, corpus_json_file), mode = "w",encoding='utf-8') as f:
        json.dump(char_to_index, f)
    exit()
    """
    pass
