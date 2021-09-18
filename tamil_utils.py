# -*- coding: utf-8 -*-
import regex
_UYIRGAL = ["அ","ஆ","இ","ஈ","உ","ஊ","எ","ஏ","ஐ","ஒ","ஓ","ஔ"]
_MEYGAL=("க்","ங்","ச்","ஞ்","ட்","ண்","த்","ந்","ன்","ப்","ம்","ய்","ர்","ற்","ல்","ள்","ழ்","வ்","ஜ்","ஷ்","ஸ்","ஹ்","க்ஷ்","ஃ","்",)
_VALLINAM = ("க","கா","கி","கீ","கூ","கு","கெ","கே","கை","கொ","கோ","கௌ","ச","சா","சி","சீ","சூ","சு","செ","சே","சை","சொ","சோ","சௌ","ட","டா","டி","டீ","டூ","டு","டெ","டே","டை","டொ","டோ","டௌ","த","தா","தி","தீ","தூ","து","தெ","தே","தை","தொ","தோ","தௌ","ப","பா","பி","பீ","பூ","பு","பெ","பே","பை","பொ","போ","பௌ","ற","றா","றி","றீ","றூ","று","றெ","றே","றை","றொ","றோ","றௌ", "க்","ச்", "ட்", "த்", "ப்", "ற்", )
_TAMIL_UNICODE_1_TA = ["க","ங","ச","ஞ","ட","ண","த","ந","ன","ப","ம","ய","ர","ற","ல","ள","ழ","வ",]
_TAMIL_UNICODE_1_SAN = ["ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ",]
_TAMIL_UNICODE_1 = _TAMIL_UNICODE_1_TA+_TAMIL_UNICODE_1_SAN
_TAMIL_UNICODE_2 = ["ா","ி","ீ","ூ","ு","ெ","ே","ை","ொ","ோ","ௌ","்",]
def _is_uyir_ezhuthu(tamil_char):
    return _list_has_element(_UYIRGAL, tamil_char)
def _is_mey_ezhuthu(tamil_char):
    return _list_has_element(_MEYGAL, tamil_char)
def _is_vallinam(tamil_char):
    return _list_has_element(_VALLINAM, tamil_char)
def _get_last_morpheme(word):
    if word.strip()=='':
        return '' 
    last_char = word[-1]
    if last_char == "்":
        last_char = _MEYGAL[_TAMIL_UNICODE_1.index(word[-2])]
    if _is_uyir_ezhuthu(last_char) or _is_mey_ezhuthu(last_char):
        return last_char
    index = _get_index(_TAMIL_UNICODE_2,last_char)
    if (index == -1):
        return "அ"
    index = _get_index(_TAMIL_UNICODE_2,last_char)
    if index != -1:
        return _UYIRGAL[index+1]
    return last_char

def _get_first_morpheme(word):
    if word.strip()=='':
        return '' 
    first_char = word[0]
    if _is_uyir_ezhuthu(first_char) or _is_mey_ezhuthu(first_char):
        return first_char
    index = _get_index(_TAMIL_UNICODE_1,first_char)
    if (index != -1 ):
        return _MEYGAL[index]
    index = _get_index(_YIYAIBU_ENDING_LETTERS,first_char)
    if index != -1:
        return _UYIRGAL[index+1]
    return first_char

def _get_index(list, element):
    index = -1
    try:
        index = list.index(element)
    except:
        index = -1
    return index
def _list_has_element(list,element):
    try:
        return element in list
    except:
        return False
def _get_unicode_characters(word):
    if (' ' in word):
        return regex.findall('\p{L}\p{M}*|\p{Z}*',word)
    else:
        return regex.findall('\p{L}\p{M}*',word)
def _remove_punctuation_numbers(text):
    import string
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.replace("‘", '')
    text = text.replace("’", '')
    text = text.replace("“", '')
    text = text.replace("”", '')
    text = text.replace("–",'')
    text = text.replace("…",'')
    text = regex.sub("\d+",'',text)
    return text
def _cleanup_generated_poem(text):
    #print(text)
    new_text = ''
    lines = text.split("\n")
    text_words = [[ word for word in line.split()] for line in lines if line.strip()!='']
    #print('last word of the poem',text_words[-1][-1])
    for l,line in enumerate(lines):
        line_words = line.split()
        for w,word2 in enumerate(line_words):
            if l==0 and w==0:
                continue
            if w==0:
                word1 = text_words[l-1][-1]
            else:
                word1 = text_words[l][w-1]
            last_char = _get_last_morpheme(word1)
            first_char = _get_first_morpheme(word2)
            corrected_word1 = word1
            if (_is_vallinam(last_char) and _is_mey_ezhuthu(last_char) and 
                first_char != last_char ):
                corrected_word1 = ''.join(_get_unicode_characters(word1)[:-1])                    
            #print(word1,last_char,first_char,word2,'corrected word1',corrected_word1)
            new_text += corrected_word1 + " "
            if w==0:
                new_text+="\n"
    new_text += " " + text_words[-1][-1]
    return new_text
