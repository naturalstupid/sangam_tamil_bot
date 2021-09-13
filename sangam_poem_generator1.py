import pandas as pd
sangam_csv_folder =  "./sangam_tamil_csv/"
df = pd.read_csv(sangam_csv_folder+"sangam_poems.csv")
df= df.sample(frac=1).reset_index(drop=True)

#Data Preparation
# Importing the libraries
import tensorflow as tf
import numpy as np
import os
import time
import json
import tensorflowjs as tfjs
import nltk
from nltk.util import ngrams
#nltk.download('punkt')
def word_collection(song_lyric, ngram_pair=(1,)):
    words = []
    for sentence in song_lyric.split("\n"):
        tokens = nltk.word_tokenize(sentence) #[ t for t in sentence.strip().split() if len(t)!=0]
        if 1 in ngram_pair:
            words.extend(tokens)
        if 2 in ngram_pair:
            bigrams = [ " ".join(bigram) for bigram in ngrams(tokens, 2)]
            words.extend(bigrams)
    return words
WORDS_COLLECTION = []
for poem in df.poem.tolist():
    words = word_collection(poem,(1,2))
    WORDS_COLLECTION.extend(words)
print("Total words with Unigram & Bigram: ",len(WORDS_COLLECTION))
#Model Creation and Evaluation
def generate_text(model, char2idx, idx2char, start_string, temperature=1.0, num_generate = 500):
  # Evaluation step (generating text using the learned model)

  # Converting our start string to numbers (vectorizing)
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store our results
  text_generated = []

  # Low temperatures results in more predictable text.
  # Higher temperatures results in more surprising text.
  # Experiment to find the best setting.
  temperature = temperature

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
      predictions = model(input_eval)
      # remove the batch dimension
      predictions = tf.squeeze(predictions, 0)
      # using a categorical distribution to predict the character returned by the model
      predictions = predictions / temperature 
      cat_dist_predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
      # We pass the predicted character as the next input to the model
      # along with the previous hidden state
      input_eval = tf.expand_dims([cat_dist_predicted_id], 0)
      character_generated = idx2char[cat_dist_predicted_id]
      text_generated.append(character_generated)
      
  return (start_string + ''.join(text_generated))
def get_score(generated_text, ngram_value, words_collection):
    total_matched_words = 0
    unmatched_words= []
    gen_words = word_collection(generated_text, ngram_value)
    for word in gen_words:
        if word in words_collection:
            total_matched_words+=1
        else:
            unmatched_words.append(word)    
    score = round(total_matched_words/len(gen_words),3)
    return score, unmatched_words

def evaluate_single_song(generated_text, words_collection =WORDS_COLLECTION):
    uni_score, uni_unmatched_words = get_score(generated_text, (1,), words_collection)
    bi_score, bi_unmatched_words = get_score(generated_text, (2,), words_collection)
    unmatched_words = uni_unmatched_words + bi_unmatched_words
    return uni_score,bi_score, unmatched_words

def evaluate_model(model, model_name, char2idx, idx2char, debug=False):
    diveristy_values = [i for i in np.arange(0.1, 1, 0.1)]
    uni_score_col = []
    bi_score_col = []
    generated_texts_col = []
    unmatched_words_col = []
    for diversity in diveristy_values:
        generated_text = generate_text(model, char2idx, idx2char, "யாரோ", diversity)
        uni_score, bi_score, unmatched_words = evaluate_single_song(generated_text)
        uni_score_col.append(uni_score)
        bi_score_col.append(bi_score)
        generated_texts_col.append(generated_text)
        unmatched_words_col.append(unmatched_words)
        if debug:
            print("Model "+model_name+" - Diversity "+str(diversity)+" - Uni score "+str(uni_score)+" - Bi score "+str(bi_score))
    return pd.DataFrame(
        {
            model_name+"_uni_score":uni_score_col, 
            model_name+"_bi_score":bi_score_col,
            model_name+"_generated_lyric":generated_texts_col,
            model_name+"_unmatched_words":unmatched_words_col
         }
         )
def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim,
                              batch_input_shape=[batch_size, None]),
    tf.keras.layers.LSTM(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.LSTM(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.Dense(vocab_size)
  ])
  return model
def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)
def create_model(model_name, df, path_to_save_model, callbacks, build_model_func, checkpoint_dir, EPOCHS=30):
    print("Creating Model: ", model_name)
    print("-------------------------------")
    # Concatenating the strings
    text = " ".join([ song.strip() for song in df.poem])
    print("Total songs combined : {}".format(len(df.poem)))
    print()
    print ('Length of text: {} characters'.format(len(text)))
    print("Sample Text: ")
    print()
    print(text[:250])
    print()
    vocab = sorted(set(text))
    print ('{} unique characters'.format(len(vocab)))

    # Creating a mapping from unique characters to indices
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)

    text_as_int = np.array([char2idx[c] for c in text])

    # The maximum length sentence we want for a single input in characters
    seq_length = 100
    examples_per_epoch = len(text)//(seq_length+1)

    # Create training examples / targets
    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
    
    sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

    def split_input_target(chunk):
        input_text = chunk[:-1]
        target_text = chunk[1:]
        return input_text, target_text

    dataset = sequences.map(split_input_target)
    print()
    for input_example, target_example in  dataset.take(5):
        print ('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
        print ('Target data:', repr(''.join(idx2char[target_example.numpy()])))
    print()
    # Batch size
    BATCH_SIZE = 64

    # Buffer size to shuffle the dataset
    # (TF data is designed to work with possibly infinite sequences,
    # so it doesn't attempt to shuffle the entire sequence in memory. Instead,
    # it maintains a buffer in which it shuffles elements).
    BUFFER_SIZE = 10000

    dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
    #print(dataset)

    # Length of the vocabulary in chars
    vocab_size = len(vocab)

    # The embedding dimension
    embedding_dim = 256

    # Number of RNN units
    rnn_units = 1024
    saved_model_file = "./modelweights/"+model_name+"_spg.hd5"
    if os.path.exists(saved_model_file):
        model = build_model_func(vocab_size, embedding_dim, rnn_units, BATCH_SIZE)
        model.load_weights(saved_model_file)
        test_model = model
        return model, test_model, char2idx, idx2char
    model = build_model_func(vocab_size, embedding_dim, rnn_units, BATCH_SIZE)
    if os.path.exists(checkpoint_dir):
        print('loading saved weights from',checkpoint_dir)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model.compile(optimizer='adam', loss=loss)
    
    for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)
        print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")    
    
    history = model.fit(dataset, epochs=EPOCHS, callbacks=callbacks)
    
    #char2idx_str = json.dumps(char2idx)
    
    #tfjs.converters.save_keras_model(model, path_to_save_model)
    
    #with open(path_to_save_model+"char_idx_converter.js","w",encoding='utf-8') as f:
    #    f.write("var char2idx ="+ str(char2idx)+"; \n var idx2char = "+str(idx2char.tolist()))
    
    tf.train.latest_checkpoint(checkpoint_dir)
    test_model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
    test_model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    test_model.build(tf.TensorShape([1, None]))
    
    return model, test_model, char2idx, idx2char
def get_callbacks(checkpoint_dir):
    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")

    checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True,
    save_best_only=True,
    monitor='loss'
    )
    return [checkpoint_callback]
def create_model_for(model_name, data_df):
    path_to_store = "./model_weights/"+model_name+'/'
    checkpoint_dir = "./model_weights/"+model_name+'/training_checkpoints/'
    model, test_model, char2idx, idx2char = create_model(
        model_name, 
        data_df, 
        path_to_store, 
        get_callbacks(checkpoint_dir),
        build_model,
        checkpoint_dir)
    results_df = evaluate_model(test_model, model_name, char2idx, idx2char, debug=True)
    #results_df.to_csv(path_to_store+"result.csv")
    print("Saving model weights in",saved_model_file)
    test_model.model.save_weights(saved_model_file)
    return results_df
results_agananuru = create_model_for("agananuru_poems", df[df.poem_type.str.contains("அகநானூறு")])
print(results_agananuru)
exit()
results_all_songs = create_model_for("all_sangam_poems", df)
print(results_all_songs)
