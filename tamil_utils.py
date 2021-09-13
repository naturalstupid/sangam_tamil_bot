# -*- coding: utf-8 -*-
import grammar
import string
from itertools import islice
from operator import itemgetter
from collections import Counter
from enum import IntEnum
_TREAT_AAYDHAM_AS_KURIL = False
_TREAT_KUTRIYALIGARAM_AS_OTRU = False    
"""  _CHARACTER_TYPES keys should match is_xxx functions of grammar.Ezhuthu  """
_CHARACTER_TYPES = {'kuril':"குறில்கள்",'nedil':"நெடில்கள்",'uyir_ezhuthu':"உயிர் எழுத்துக்கள்",'mey_ezhuthu':"மெய்யெழுத்துக்கள்",
                    'uyir_mey_ezhuthu':"உயிர்மெய் எழுத்துக்கள்",'vada_ezhuthu':"வட எழுத்துக்கள்", 'vallinam':"வல்லின எழுத்துக்கள்",
                    'yidaiyinam':"இடையின எழுத்துக்கள்",'mellinam':"மெல்லின எழுத்துக்கள்",'aaydham':"ஆய்த எழுத்து",'aikaaram':"ஐகாரம்",
                    'aukaaram':"ஒளகாரம்",'kutriyalugaram':"குற்றியலுகரம்",'kutriyaligaram':"குற்றியலிகரம்",'magarakurukkam':"மகரகுருக்கம்",
                    "uyiralabedai" : "உயிரளபெடை" , "otralabedai" : "ஒற்றளபெடை" }    
AYDHAM = ('ஃ')
UYIRGAL = ["அ","ஆ","இ","ஈ","உ","ஊ","எ","ஏ","ஐ","ஒ","ஓ","ஔ"]
MEYGAL=("க்","ங்","ச்","ஞ்","ட்","ண்","த்","ந்","ன்","ப்","ம்","ய்","ர்","ற்","ல்","ள்","ழ்","வ்","ஜ்","ஷ்","ஸ்","ஹ்","க்ஷ்","ஃ","்",)
AIKAARAM = ("ஐ","கை","ஙை","சை","ஞை","டை","ணை","தை","நை","னை","பை","மை","யை","ரை","றை","லை","ளை","ழை",
            "வை","ஜை","ஷை","ஸை","ஹை","க்ஷை","ை",)
AUKAARAM = ("ஔ","கௌ","ஙௌ","சௌ","ஞௌ","டௌ","ணௌ","தௌ","நௌ","னௌ","பௌ",
    "மௌ","யௌ","ரௌ","றௌ","லௌ","ளௌ","ழௌ","வௌ","ஜௌ","ஷௌ","ஸௌ","ஹௌ","க்ஷௌ","ௌ",)
KURILGAL = ("அ","இ","உ","எ","ஐ","ஒ",  "க","கி","கு","கெ","கை","கொ",
            "ங","ஙி","ஙு","ஙெ","ஙை","ஙொ","ச","சி","சு","செ","சை","சொ","ஞ","ஞி","ஞு","ஞெ","ஞை","ஞொ",
            "ட","டி","டு","டெ","டை","டொ","ண","ணி","ணு","ணெ","ணை","ணொ","த","தி","து","தெ","தை","தொ",
            "ந","நி","நு","நெ","நை","நொ","ன","னி","னு","னெ","னை","னொ","ப","பி","பு","பெ","பை","பொ",
            "ம","மி","மு","மெ","மை","மொ","ய","யி","யு","யெ","யை","யொ","ர","ரி","ரு","ரெ","ரை","ரொ",
            "ற","றி","று","றெ","றை","றொ","ல","லி","லு","லெ","லை","லொ","ள","ளி","ளு","ளெ","ளை","ளொ",
            "ழ","ழி","ழு","ழெ","ழை","ழொ","வ","வி","வு","வெ","வை","வொ","ஜ","ஜி","ஜூ","ஜெ","ஜை","ஜொ",
            "ஷ","ஷி","ஷூ","ஷெ","ஷை","ஷொ", "ஸ","ஸி","ஸூ","ஸெ","ஸை","ஸொ","ஹ","ஹி","ஹூ","ஹெ","ஹை","ஹொ",
            "க்ஷ","க்ஷி","க்ஷூ","க்ஷெ","க்ஷை","க்ஷை","க்ஷொ","ி","ு","ெ","ை","ொ",AUKAARAM,)
NEDILGAL = ("ஆ","ஈ","ஊ","ஏ","ஓ","கா","கீ","கூ","கே","கோ","ஙா","ஙீ","ஙூ","ஙே","ஙோ",
            "சா","சீ","சூ","சே","சோ","ஞா","ஞீ","ஞூ","ஞே","ஞோ","டா","டீ","டூ","டே","டோ","ணா","ணீ","ணூ","ணே","ணோ",
            "தா","தீ","தூ","தே","தோ","நா","நீ","நூ","நே","நோ","னா","னீ","னூ","னே","னோ","பா","பீ","பூ","பே","போ",
            "மா","மீ","மூ","மே","மோ","யா","யீ","யூ","யே","யோ","ரா","ரீ","ரூ","ரே","ரோ","றா","றீ","றூ","றே","றோ",
            "லா","லீ","லூ","லே","லோ","ளா","ளீ","ளூ","ளே","ளோ","ழா","ழீ","ழூ","ழே","ழோ","வா","வீ","வூ","வே","வோ",
            "ஜா","ஜீ","ஜு","ஜே","ஜோ","ஷா","ஷீ","ஷு","ஷே","ஷோ","ஸா","ஸீ","ஸு","ஸே","ஸோ",
            "ஹா","ஹீ","ஹு","ஹே","ஹோ","க்ஷா","க்ஷீ","க்ஷு","க்ஷே","க்ஷோ","ா","ீ","ூ","ே","ோ",)
KUTRIYALUGARAM = ("கு","சு","டு","து","பு","று")
KUTRIYALIGARAM = ("கி","சி","டி","தி","பி","றி","மி",'னி')
VALLINAM = ("க","கா","கி","கீ","கூ","கு","கெ","கே","கை","கொ","கோ","கௌ","ச","சா","சி","சீ","சூ","சு","செ","சே","சை","சொ","சோ","சௌ","ட","டா","டி","டீ","டூ","டு","டெ","டே","டை","டொ","டோ","டௌ","த","தா","தி","தீ","தூ","து","தெ","தே","தை","தொ","தோ","தௌ","ப","பா","பி","பீ","பூ","பு","பெ","பே","பை","பொ","போ","பௌ","ற","றா","றி","றீ","றூ","று","றெ","றே","றை","றொ","றோ","றௌ", "க்","ச்", "ட்", "த்", "ப்", "ற்", )
ZERO_DURATION_SANDHA_OTRUGAL = ("ய்","ர்","ல்","ள்","ழ்","வ்","ண்","ன்",)#"ம்",)
MELLINAM = ("ங","ஙா","ஙி","ஙீ","ஙூ","ஙு","ஙெ","ஙே","ஙை","ஙொ","ஙோ","ஙௌ","ஞ","ஞா","ஞி","ஞீ","ஞூ","ஞு","ஞெ","ஞே","ஞை","ஞொ","ஞோ","ஞௌ","ண","ணா","ணி","ணீ","ணூ","ணு","ணெ","ணே","ணை","ணொ","ணோ","ணௌ","ந","நா","நி","நீ","நூ","நு","நெ","நே","நை","நொ","நோ","நௌ","ம","மா","மி","மீ","மூ","மு","மெ","மே","மை","மொ","மோ","மௌ","ன","னா","னி","னீ","னூ","னு","னெ","னே","னை","னொ","னோ","னௌ","ங்", "ஞ்", "ண்", "ந்", "ன்", "ம்",)
YIDAIYINAM = ("ய","யா","யி","யீ","யூ","யு","யெ","யே","யை","யொ","யோ","யௌ","ர","ரா","ரி","ரீ","ரூ","ரு","ரெ","ரே","ரை","ரொ","ரோ","ரௌ","ல","லா","லி","லீ","லூ","லு","லெ","லே","லை","லொ","லோ","லௌ","வ","வா","வி","வீ","வூ","வு","வெ","வே","வை","வொ","வோ","வௌ","ழ","ழா","ழி","ழீ","ழூ","ழு","ழெ","ழே","ழை","ழொ","ழோ","ழௌ","ள","ளா","ளி","ளீ","ளூ","ளு","ளெ","ளே","ளை","ளொ","ளோ","ளௌ","ய்", "ர்", "ல்", "ள்", "ழ்", "வ்",)
"""
VARUKKA_EDHUGAI = ("அ","இ","உ","எ","ஒ","ஐ","க","கி","கு","கெ","கொ","கை","ங","ஙி","ஙு","ஙெ","ஙொ","ஙை",
    "ச","சி","சு","செ","சொ","சை","ஞ","ஞி","ஞு","ஞெ","ஞொ","ஞை","ட","டி","டு","டெ","டொ","டை","ண","ணி","ணு","ணெ","ணொ","ணை",
    "த","தி","து","தெ","தொ","தை","ந","நி","நு","நெ","நொ","நை","ன","னி","னு","னெ","னொ","னை","ப","பி","பு","பெ","பொ","பை",
    "ம","மி","மு","மெ","மொ","மை","ய","யி","யு","யெ","யொ","யை", "ர","ரி","ரு","ரெ","ரொ","ரை","ற","றி","று","றெ","றொ","றை",
    "ல","லி","லு","லெ","லொ","லை","ள","ளி","ளு","ளெ","ளொ","ளை","ழ","ழி","ழு","ழெ","ழொ","ழை",
    "வ","வி","வு","வெ","வொ","வை","ஜ","ஜி","ஜூ","ஜெ","ஜை","ஜொ","ஷ","ஷி","ஷூ","ஷெ","ஷை","ஷொ",
    "ஸ","ஸி","ஸூ","ஸெ","ஸை","ஸொ","ஹ","ஹி","ஹூ","ஹெ","ஹை","ஹொ","க்ஷ","க்ஷி","க்ஷூ","க்ஷெ","க்ஷை","க்ஷொ",
    "ி","ு","ெ","ொ","ை",)
"""
VALLINA_THODAI = ("க", "ச", "ட", "த", "ப", "ற", "கா", "சா", "டா", "தா", "பா", "றா", 
    "கி", "சி", "டி", "தி", "பி", "றி", "கீ", "சீ", "டீ", "தீ", "பீ", "றீ", "கு", "சு", "டு", "து", "பு", "று", "கூ", "சூ", "டூ", "தூ", "பூ", "றூ", 
    "கெ", "செ", "டெ", "தெ", "பெ", "றெ", "கே", "சே", "டே", "தே", "பே", "றே", "கை","சை", "டை", "தை", "பை", "றை", "கொ", "சொ", "டொ", "தொ", "பொ","றொ",  
    "கோ", "சோ", "டோ", "தோ", "போ", "றோ", "கௌ", "சௌ", "டௌ", "தௌ", "பௌ", "றௌ", "க்","ச்", "ட்", "த்", "ப்", "ற்", )
YAGARA_VARISAI = ("ய","யா","யி","யீ","யு","யூ","யெ","யே","யை","யொ","யோ","யௌ",)
VAGARA_VARISAI = {"வ","வா","வி","வீ","வு","வூ","வெ","வே","வை","வொ","வோ","வௌ",}
YIDAIYINA_THODAI = ("ய", "ர", "ல", "ள", "ழ", "வ", "யா", "ரா", "லா", "ளா", "ழா", "வா", "யி", "ரி", "லி", "ளி", "ழி", "வி", 
    "யீ", "ரீ", "லீ", "ளீ", "ழீ", "வீ", "யு", "ரு", "லு", "ளு", "ழு", "வு", "யூ", "ரூ", "லூ", "ளூ", "ழூ", "வூ", "யெ", "ரெ", "லெ", "ளெ", "ழெ", "வெ", 
    "யே", "ரே", "லே", "ளே", "ழே", "வே", "யை", "ரை", "லை", "ளை", "ழை", "வை", "யொ", "ரொ", "லொ", "ளொ", "ழொ", "வொ", 
    "யோ", "ரோ", "லோ", "ளோ", "ழோ", "வோ", "யௌ", "ரௌ", "லௌ", "ளௌ", "ழௌ", "வௌ", "ய்", "ர்", "ல்", "ள்", "ழ்", "வ்", )
MELLINA_THODAI = ("ங", "ஞ", "ண", "ந", "ன", "ம", "ஙா", "ஞா", "ணா", "நா", "னா", "மா", 
    "ஙி", "ஞி", "ணி", "நி", "னி", "மி", "ஙீ", "ஞீ", "ணீ", "நீ", "னீ", "மீ", "ஙூ", "ஞூ", "ணூ", "நூ", "னூ", "மூ", "ஙு", "ஞு", "ணு", "நு", "னு", "மு", 
    "ஙெ", "ஞெ", "ணெ", "நெ", "னெ", "மெ", "ஙே", "ஞே", "ணே", "நே", "னே", "மே", "ஙை", "ஞை", "ணை", "நை", "னை", "மை", 
    "ஙொ", "ஞொ", "ணொ", "நொ", "னொ", "மொ", "ஙோ", "ஞோ", "ணோ", "நோ", "னோ", "மோ", "ஙௌ", "ஞௌ", "ணௌ", "நௌ", "னௌ", "மௌ",  
    "ங்", "ஞ்", "ண்", "ந்", "ன்", "ம்", )
TAMIL_UNICODE_1_TA = ["க","ங","ச","ஞ","ட","ண","த","ந","ன","ப","ம","ய","ர","ற","ல","ள","ழ","வ",]
TAMIL_UNICODE_1_SAN = ["ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ",]
TAMIL_UNICODE_1 = TAMIL_UNICODE_1_TA+TAMIL_UNICODE_1_SAN
TAMIL_UNICODE_2 = ["ா","ி","ீ","ூ","ு","ெ","ே","ை","ொ","ோ","ௌ","்",]
VADA_EZHUTHUKKAL= ("ஜ","ஜா","ஜி","ஜீ","ஜூ","ஜு","ஜெ","ஜே","ஜை","ஜொ","ஜோ","ஜௌ","ஜ்","ஷ","ஷா","ஷி","ஷீ","ஷூ","ஷு","ஷெ","ஷே","ஷை","ஷொ","ஷோ","ஷௌ","ஷ்","ஸ","ஸா","ஸி","ஸீ","ஸூ","ஸு","ஸெ","ஸே","ஸை","ஸொ","ஸோ","ஸௌ","ஸ்","ஹ","ஹா","ஹி","ஹீ","ஹூ","ஹு","ஹெ","ஹே","ஹை","ஹொ","ஹோ","ஹௌ","ஹ்","க்ஷ","க்ஷா","க்ஷி","க்ஷீ","க்ஷூ","க்ஷு","க்ஷெ","க்ஷே","க்ஷை","க்ஷொ","க்ஷோ","க்ஷௌ","க்ஷ்",)
MONAI_THODAI_1= ("அ", "ஆ", "ஐ", "ஔ","க","கா","கை","கௌ","ங","ஙா","ஙை","ஙௌ","ச",
    "சா","சை","சௌ","ஞ","ஞா","ஞை","ஞௌ","ட","டா","டை","டௌ","ண","ணா","ணை","ணௌ","த","தா","தை","தௌ",
    "ந","நா","நை","நௌ","ன","னா","னை","னௌ","ப","பா","பை","பௌ","ம","மா","மை","மௌ","ய","யா","யை","யௌ",
    "ர","ரா","ரை","ரௌ","ற","றா","றை","றௌ","ல","லா","லை","லௌ","ள","ளா","ளை","ளௌ","ழ","ழா","ழை","ழௌ",
    "வ","வா","வை","வௌ","ஜ","ஜா","ஜை","ஜௌ","ஷ","ஷா","ஷை","ஷௌ","ஸ","ஸா","ஸை","ஸௌ",
    "ஹ","ஹா","ஹை","ஹௌ","க்ஷ","க்ஷா","க்ஷை","க்ஷௌ",)
MONAI_THODAI_2= ("இ", "ஈ", "எ", "ஏ","கி","கீ","கெ","கே","ஙி","ஙீ","ஙெ","ஙே","சி","சீ","செ","சே","ஞி",
    "ஞீ","ஞெ","ஞே","டி","டீ","டெ","டே","ணி","ணீ","ணெ","ணே","தி","தீ","தெ","தே","நி","நீ","நெ","நே","னி","னீ","னெ","னே",
    "பி","பீ","பெ","பே","மி","மீ","மெ","மே","யி","யீ","யெ","யே","ரி","ரீ","ரெ","ரே","றி","றீ","றெ","றே","லி","லீ","லெ","லே",
    "ளி","ளீ","ளெ","ளே","ழி","ழீ","ழெ","ழே","வி","வீ","வெ","வே","ஜி","ஜீ","ஜெ","ஜே","ஷி","ஷீ","ஷெ","ஷே",
    "ஸி","ஸீ","ஸெ","ஸே","ஹி","ஹீ","ஹெ","ஹே","க்ஷி","க்ஷீ","க்ஷெ","க்ஷே",)
MONAI_THODAI_3= ("உ", "ஊ", "ஒ", "ஓ","கு","கூ","கொ","கோ","ஙு","ஙூ","ஙொ","ஙோ","சு","சூ","சொ","சோ","ஞு",
    "ஞூ","ஞொ","ஞோ","டு","டூ","டொ","டோ","ணு","ணூ","ணொ","ணோ","து","தூ","தொ","தோ","நு","நூ","நொ","நோ",
    "னு","னூ","னொ","னோ","பு","பூ","பொ","போ","மு","மூ","மொ","மோ","யு","யூ","யொ","யோ","ரு","ரூ","ரொ","ரோ","று","றூ","றொ","றோ",
    "லு","லூ","லொ","லோ","ளு","ளூ","ளொ","ளோ","ழு","ழூ","ழொ","ழோ","வு","வூ","வொ","வோ","ஜூ","ஜு","ஜொ","ஜோ",
    "ஷூ","ஷு","ஷொ","ஷோ","ஸூ","ஸு","ஸொ","ஸோ","ஹூ","ஹு","ஹொ","ஹோ","க்ஷூ","க்ஷு","க்ஷொ","க்ஷோ",)
MONAI_THODAI_4 = ("ச","சா","சை","சௌ","த","தா","தை","தௌ","ஞ","ஞா","ஞை","ஞௌ","ந","நா","நை","நௌ","ம","மா","மை","மௌ","வ","வா","வை","வௌ")
MONAI_THODAI_5 = ("சி","சீ","செ","சே","தி","தீ","தெ","தே","ஞி","ஞீ","ஞெ","ஞே","நி","நீ","நெ","நே",
    "மி","மீ","மெ","மே","வி","வீ","வெ","வே")
MONAI_THODAI_6= ("சு","சூ","சொ","சோ","து","தூ","தொ","தோ","ஞு","ஞூ","ஞொ","ஞோ","நு","நூ","நொ","நோ", "மு","மூ","மொ","மோ","வு","வூ","வொ","வோ")
SIRAPPU_KURIYEEDUGAL =("","ா","ி","ீ","ு","ூ","ெ","ே","ை","ொ","ோ","ௌ","்",)
YIYAIBU_ENDING_LETTERS =("ா","ி","ீ","ு","ூ","ெ","ே","ை","ொ","ோ","ௌ")
VENPA_ALLOWED_SEERS = ("தேமா", "புளிமா", "கூவிளம்", "கருவிளம்", "தேமாங்காய்", "புளிமாங்காய்", "கூவிளங்காய்", "கருவிளங்காய்", "காசு","மலர்","நாள்","பிறப்பு",)
VENPA_ALLOWED_THALAI = ('வெண்சீர் வெண்டளை', 'இயற்சீர் வெண்டளை')
VENPA_EETRU_SEERS = ("காசு","மலர்","நாள்","பிறப்பு",)
ASIRIYAPPA_ALLOWED_SEERS = ("தேமா", "புளிமா", "கூவிளம்", "கருவிளம்",)
ASIRIYAPPA_DISALLOWED_SEERS = ("கருவிளங்கனி","கூவிளங்கனி", )
ASIRIYAPPA_EETRUCHEER_LETTERS = ("ே","ோ","ீ","ை","ாய்",)
NILAIMANDILA_EETRUCHEER_LETTERS= ("னீ","னே","னை","னோ","ம்",)
KALIPPA_EETRUCHEER_LETTERS= ("ே",)
KALIPPA_ALLOWED_SEERS = ("தேமாங்காய்", "புளிமாங்காய்","கூவிளங்காய்", "கருவிளங்காய்",)
KALIPPA_DISALLOWED_SEERS = ("தேமா","புளிமா","கருவிளங்கனி","கூவிளங்கனி", )
VANJPA_ALLOWED_SEERS= ("தேமாங்காய்", "புளிமாங்காய்","கூவிளங்காய்", "கருவிளங்காய்","கருவிளங்கனி","கூவிளங்கனி",)
VANJPA_THANISOL_ALLOWED_SEERS = ("தேமா","புளிமா","கூவிளம்", "கருவிளம்", )
SANDHA_SEERGAL = ("மா", "விளம்", "காய்", "கனி", "பூ", "ணிழல்", 'நிழல்', 'நேர்','நிரை')
UYIR_MEY_LETTERS= ("க","கா","கி","கீ","கூ","கு","கெ","கே","கை","கொ","கோ","கௌ", "ங","ஙா","ஙி","ஙீ","ஙூ","ஙு","ஙெ","ஙே","ஙை","ஙொ","ஙோ","ஙௌ",
    "ச","சா","சி","சீ","சூ","சு","செ","சே","சை","சொ","சோ","சௌ", "ஞ","ஞா","ஞி","ஞீ","ஞூ","ஞு","ஞெ","ஞே","ஞை","ஞொ","ஞோ","ஞௌ",
    "ட","டா","டி","டீ","டூ","டு","டெ","டே","டை","டொ","டோ","டௌ", "ண","ணா","ணி","ணீ","ணூ","ணு","ணெ","ணே","ணை","ணொ","ணோ","ணௌ",
    "த","தா","தி","தீ","தூ","து","தெ","தே","தை","தொ","தோ","தௌ", "ந","நா","நி","நீ","நூ","நு","நெ","நே","நை","நொ","நோ","நௌ",
    "ன","னா","னி","னீ","னூ","னு","னெ","னே","னை","னொ","னோ","னௌ", "ப","பா","பி","பீ","பூ","பு","பெ","பே","பை","பொ","போ","பௌ",
    "ம","மா","மி","மீ","மூ","மு","மெ","மே","மை","மொ","மோ","மௌ", "ய","யா","யி","யீ","யூ","யு","யெ","யே","யை","யொ","யோ","யௌ",
    "ர","ரா","ரி","ரீ","ரூ","ரு","ரெ","ரே","ரை","ரொ","ரோ","ரௌ", "ற","றா","றி","றீ","றூ","று","றெ","றே","றை","றொ","றோ","றௌ",
    "ல","லா","லி","லீ","லூ","லு","லெ","லே","லை","லொ","லோ","லௌ", "ள","ளா","ளி","ளீ","ளூ","ளு","ளெ","ளே","ளை","ளொ","ளோ","ளௌ",
    "ழ","ழா","ழி","ழீ","ழூ","ழு","ழெ","ழே","ழை","ழொ","ழோ","ழௌ","வ","வா","வி","வீ","வூ","வு","வெ","வே","வை","வொ","வோ","வௌ",
    "ஜ","ஜா","ஜி","ஜீ","ஜூ","ஜு","ஜெ","ஜே","ஜை","ஜொ","ஜோ","ஜௌ","ஷ","ஷா","ஷி","ஷீ","ஷூ","ஷு","ஷெ","ஷே","ஷை","ஷொ","ஷோ","ஷௌ",
    "ஸ","ஸா","ஸி","ஸீ","ஸூ","ஸு","ஸெ","ஸே","ஸை","ஸொ","ஸோ","ஸௌ","ஹ","ஹா","ஹி","ஹீ","ஹூ","ஹு","ஹெ","ஹே","ஹை","ஹொ","ஹோ","ஹௌ",
    "க்ஷ","க்ஷா","க்ஷி","க்ஷீ","க்ஷூ","க்ஷு","க்ஷெ","க்ஷே","க்ஷை","க்ஷொ","க்ஷோ","க்ஷௌ",)

SANDHAPAA_DICT = [
{'K': 'ன',  'N': 'னா', "O" : "த்"},
{'KK': 'தன',  'NK': 'தான',  'KN': 'னனா', 'NN': 'தானா', 
},
{'NOV': 'தாந்த',  'KOK': 'தன்ன',  'KKO': 'தனன்',  'NOK': 'தான',   'KON': 'தன்னா', 'NKO': 'தான',  'KNO': 'தனா',  'NON': 'தானா', 
},
{ 'KOKO': 'தன்ன', 'NOOK': 'தாந்த',  'NOKO': 'தான',  'KONO': 'தன்னா',  'NONO': 'தானா',  
}, 
{ 'KOOKO': 'தந்த', 'NOOKO': 'தாந்த',  'NOONO': 'தாந்தா',  'KOONO': 'தந்தா', 
},
]

VANNAPAA_DICT = [
{'UK': 'ன', 'VK': 'ன', 'YK': 'ன', 'MK': 'ன', 'UN': 'னா', 'VN': 'னா', 'YN': 'னா', 'MN': 'னா',},
{'UKUK': 'தன', 'UKVK': 'தன', 'UKYK': 'தன', 'UKMK': 'தன', 'VKUK': 'தன', 'VKVK': 'தன', 'VKYK': 'தன', 'VKMK': 'தன', 'YKUK': 'தன', 'YKVK': 'தன', 'YKYK': 'தன', 'YKMK': 'தன', 'MKUK': 'தன', 'MKVK': 'தன', 'MKYK': 'தன', 'MKMK': 'தன', 
 'UNUK': 'தான', 'UNVK': 'தான', 'UNYK': 'தான', 'UNMK': 'தான', 'VNUK': 'தான', 'VNVK': 'தான', 'VNYK': 'தான', 'VNMK': 'தான', 'YNUK': 'தான', 'YNVK': 'தான', 'YNYK': 'தான', 'YNMK': 'தான', 'MNUK': 'தான', 'MNVK': 'தான', 'MNYK': 'தான', 'MNMK': 'தான', 
'UKUN': 'தனா', 'UKVN': 'தனா', 'UKYN': 'தனா', 'UKMN': 'தனா', 'VKUN': 'தனா', 'VKVN': 'தனா', 'VKYN': 'தனா', 'VKMN': 'தனா', 'YKUN': 'தனா', 'YKVN': 'தனா', 'YKYN': 'தனா', 'YKMN': 'தனா', 'MKUN': 'தனா', 'MKVN': 'தனா', 'MKYN': 'தனா', 'MKMN': 'தனா', 
'UNUN': 'தானா', 'UNVN': 'தானா', 'UNYN': 'தானா', 'UNMN': 'தானா', 'VNUN': 'தானா', 'VNVN': 'தானா', 'VNYN': 'தானா', 'VNMN': 'தானா', 'YNUN': 'தானா', 'YNVN': 'தானா', 'YNYN': 'தானா', 'YNMN': 'தானா', 'MNUN': 'தானா', 'MNVN': 'தானா', 'MNYN': 'தானா', 'MNMN': 'தானா',
},
{'UKVOVK': 'தத்த', 'VKVOVK': 'தத்த', 'YKVOVK': 'தத்த', 'MKVOVK': 'தத்த', 'UNVOVK': 'தாத்த', 'VNVOVK': 'தாத்த', 'YNVOVK': 'தாத்த', 'MNVOVK': 'தாத்த', 'UKMOVK': 'தந்த', 'VKMOVK': 'தந்த', 'YKMOVK': 'தந்த', 'MKMOVK': 'தந்த', 'UNMOVK': 'தாந்த', 'VNMOVK': 'தாந்த', 'YNMOVK': 'தாந்த', 'MNMOVK': 'தாந்த', 
'UKMOYK': 'தன்ன', 'UKMOMK': 'தன்ன', 'VKMOYK': 'தன்ன', 'VKMOMK': 'தன்ன', 'YKMOYK': 'தன்ன', 'YKMOMK': 'தன்ன', 'MKMOYK': 'தன்ன', 'MKMOMK': 'தன்ன', 
'UKYOVK': 'தய்ய', 'UKYOYK': 'தய்ய', 'VKYOVK': 'தய்ய', 'VKYOYK': 'தய்ய', 'YKYOVK': 'தய்ய', 'YKYOYK': 'தய்ய', 'MKYOVK': 'தய்ய', 'MKYOYK': 'தய்ய', 
'UKUKYO': 'தன', 'UKVKYO': 'தன', 'UKYKYO': 'தன', 'UKMKYO': 'தன', 'VKUKYO': 'தன', 'VKVKYO': 'தன', 'VKYKYO': 'தன', 'VKMKYO': 'தன', 'YKUKYO': 'தன', 'YKVKYO': 'தன', 'YKYKYO': 'தன', 'YKMKYO': 'தன', 'MKUKYO': 'தன', 'MKVKYO': 'தன', 'MKYKYO': 'தன', 'MKMKYO': 'தன', 'UKUKMO': 'தன', 'UKVKMO': 'தன', 'UKYKMO': 'தன', 'UKMKMO': 'தன', 'VKUKMO': 'தன', 'VKVKMO': 'தன', 'VKYKMO': 'தன', 'VKMKMO': 'தன', 'YKUKMO': 'தன', 'YKVKMO': 'தன', 'YKYKMO': 'தன', 'YKMKMO': 'தன', 'MKUKMO': 'தன', 'MKVKMO': 'தன', 'MKYKMO': 'தன', 'MKMKMO': 'தன', 
'UNMOYK': 'தான', 'VNMOYK': 'தான', 'YNMOYK': 'தான', 'MNMOYK': 'தான', 'UNMOMK': 'தான', 'VNMOMK': 'தான', 'YNMOMK': 'தான', 'MNMOMK': 'தான', 'UNYOUK': 'தான', 'UNYOVK': 'தான', 'UNYOYK': 'தான', 'UNYOMK': 'தான', 'VNYOUK': 'தான', 'VNYOVK': 'தான', 'VNYOYK': 'தான', 'VNYOMK': 'தான', 'YNYOUK': 'தான', 'YNYOVK': 'தான', 'YNYOYK': 'தான', 'YNYOMK': 'தான', 'MNYOUK': 'தான', 'MNYOVK': 'தான', 'MNYOYK': 'தான', 'MNYOMK': 'தான', 'UNUKYO': 'தான', 'UNVKYO': 'தான', 'UNYKYO': 'தான', 'UNMKYO': 'தான', 'VNUKYO': 'தான', 'VNVKYO': 'தான', 'VNYKYO': 'தான', 'VNMKYO': 'தான', 'YNUKYO': 'தான', 'YNVKYO': 'தான', 'YNYKYO': 'தான', 'YNMKYO': 'தான', 'MNUKYO': 'தான', 'MNVKYO': 'தான', 'MNYKYO': 'தான', 'MNMKYO': 'தான', 'UNUKMO': 'தான', 'UNVKMO': 'தான', 'UNYKMO': 'தான', 'UNMKMO': 'தான', 'VNUKMO': 'தான', 'VNVKMO': 'தான', 'VNYKMO': 'தான', 'VNMKMO': 'தான', 'YNUKMO': 'தான', 'YNVKMO': 'தான', 'YNYKMO': 'தான', 'YNMKMO': 'தான', 'MNUKMO': 'தான', 'MNVKMO': 'தான', 'MNYKMO': 'தான', 'MNMKMO': 'தான', 'UKVOVN': 'தத்தா', 'VKVOVN': 'தத்தா', 'YKVOVN': 'தத்தா', 'MKVOVN': 'தத்தா', 'UNVOVN': 'தாத்தா', 'VNVOVN': 'தாத்தா', 'YNVOVN': 'தாத்தா', 'MNVOVN': 'தாத்தா', 'UKMOVN': 'தந்தா', 'VKMOVN': 'தந்தா', 'YKMOVN': 'தந்தா', 'MKMOVN': 'தந்தா', 'UNMOVN': 'தாந்தா', 'VNMOVN': 'தாந்தா', 'YNMOVN': 'தாந்தா', 'MNMOVN': 'தாந்தா', 'UKMOYN': 'தன்னா', 'UKMOMN': 'தன்னா', 'VKMOYN': 'தன்னா', 'VKMOMN': 'தன்னா', 'YKMOYN': 'தன்னா', 'YKMOMN': 'தன்னா', 'MKMOYN': 'தன்னா', 'MKMOMN': 'தன்னா', 'UKYOVN': 'தய்யா', 'UKYOYN': 'தய்யா', 'VKYOVN': 'தய்யா', 'VKYOYN': 'தய்யா', 'YKYOVN': 'தய்யா', 'YKYOYN': 'தய்யா', 'MKYOVN': 'தய்யா', 'MKYOYN': 'தய்யா', 'UKUNYO': 'தனா', 'UKVNYO': 'தனா', 'UKYNYO': 'தனா', 'UKMNYO': 'தனா', 'VKUNYO': 'தனா', 'VKVNYO': 'தனா', 'VKYNYO': 'தனா', 'VKMNYO': 'தனா', 'YKUNYO': 'தனா', 'YKVNYO': 'தனா', 'YKYNYO': 'தனா', 'YKMNYO': 'தனா', 'MKUNYO': 'தனா', 'MKVNYO': 'தனா', 'MKYNYO': 'தனா', 'MKMNYO': 'தனா', 'UKUNMO': 'தனா', 'UKVNMO': 'தனா', 'UKYNMO': 'தனா', 'UKMNMO': 'தனா', 'VKUNMO': 'தனா', 'VKVNMO': 'தனா', 'VKYNMO': 'தனா', 'VKMNMO': 'தனா', 'YKUNMO': 'தனா', 'YKVNMO': 'தனா', 'YKYNMO': 'தனா', 'YKMNMO': 'தனா', 'MKUNMO': 'தனா', 'MKVNMO': 'தனா', 'MKYNMO': 'தனா', 'MKMNMO': 'தனா', 'UNMOYN': 'தானா', 'VNMOYN': 'தானா', 'YNMOYN': 'தானா', 'MNMOYN': 'தானா', 'UNMOMN': 'தானா', 'VNMOMN': 'தானா', 'YNMOMN': 'தானா', 'MNMOMN': 'தானா', 'UNYOUN': 'தானா', 'UNYOVN': 'தானா', 'UNYOYN': 'தானா', 'UNYOMN': 'தானா', 'VNYOUN': 'தானா', 'VNYOVN': 'தானா', 'VNYOYN': 'தானா', 'VNYOMN': 'தானா', 'YNYOUN': 'தானா', 'YNYOVN': 'தானா', 'YNYOYN': 'தானா', 'YNYOMN': 'தானா', 'MNYOUN': 'தானா', 'MNYOVN': 'தானா', 'MNYOYN': 'தானா', 'MNYOMN': 'தானா', 'UNUNYO': 'தானா', 'UNVNYO': 'தானா', 'UNYNYO': 'தானா', 'UNMNYO': 'தானா', 'VNUNYO': 'தானா', 'VNVNYO': 'தானா', 'VNYNYO': 'தானா', 'VNMNYO': 'தானா', 'YNUNYO': 'தானா', 'YNVNYO': 'தானா', 'YNYNYO': 'தானா', 'YNMNYO': 'தானா', 'MNUNYO': 'தானா', 'MNVNYO': 'தானா', 'MNYNYO': 'தானா', 'MNMNYO': 'தானா', 'UNUNMO': 'தானா', 'UNVNMO': 'தானா', 'UNYNMO': 'தானா', 'UNMNMO': 'தானா', 'VNUNMO': 'தானா', 'VNVNMO': 'தானா', 'VNYNMO': 'தானா', 'VNMNMO': 'தானா', 'YNUNMO': 'தானா', 'YNVNMO': 'தானா', 'YNYNMO': 'தானா', 'YNMNMO': 'தானா', 'MNUNMO': 'தானா', 'MNVNMO': 'தானா', 'MNYNMO': 'தானா', 'MNMNMO': 'தானா',
},
{ 'UKVOVKYO': 'தத்த', 'UKVOVKMO': 'தத்த', 'UKYOVOVK': 'தத்த', 'VKVOVKYO': 'தத்த', 'VKVOVKMO': 'தத்த', 'VKYOVOVK': 'தத்த', 'YKVOVKYO': 'தத்த', 'YKVOVKMO': 'தத்த', 'YKYOVOVK': 'தத்த', 'MKVOVKYO': 'தத்த', 'MKVOVKMO': 'தத்த', 'MKYOVOVK': 'தத்த', 'UNVOVKYO': 'தாத்த', 'UNVOVKMO': 'தாத்த', 'UNYOVOVK': 'தாத்த', 'VNVOVKYO': 'தாத்த', 'VNVOVKMO': 'தாத்த', 'VNYOVOVK': 'தாத்த', 'YNVOVKYO': 'தாத்த', 'YNVOVKMO': 'தாத்த', 'YNYOVOVK': 'தாத்த', 'MNVOVKYO': 'தாத்த', 'MNVOVKMO': 'தாத்த', 'MNYOVOVK': 'தாத்த', 'UKMOVKYO': 'தந்த', 'UKMOVKMO': 'தந்த', 'UKYOMOVK': 'தந்த', 'VKMOVKYO': 'தந்த', 'VKMOVKMO': 'தந்த', 'VKYOMOVK': 'தந்த', 'YKMOVKYO': 'தந்த', 'YKMOVKMO': 'தந்த', 'YKYOMOVK': 'தந்த', 'MKMOVKYO': 'தந்த', 'MKMOVKMO': 'தந்த', 'MKYOMOVK': 'தந்த', 'UNMOVKYO': 'தாந்த', 'UNMOVKMO': 'தாந்த', 'UNYOMOVK': 'தாந்த', 'VNMOVKYO': 'தாந்த', 'VNMOVKMO': 'தாந்த', 'VNYOMOVK': 'தாந்த', 'YNMOVKYO': 'தாந்த', 'YNMOVKMO': 'தாந்த', 'YNYOMOVK': 'தாந்த', 'MNMOVKYO': 'தாந்த', 'MNMOVKMO': 'தாந்த', 'MNYOMOVK': 'தாந்த', 'UKMOYKYO': 'தன்ன', 'UKMOYKMO': 'தன்ன', 'UKMOMKYO': 'தன்ன', 'UKMOMKMO': 'தன்ன', 'VKMOYKYO': 'தன்ன', 'VKMOYKMO': 'தன்ன', 'VKMOMKYO': 'தன்ன', 'VKMOMKMO': 'தன்ன', 'YKMOYKYO': 'தன்ன', 'YKMOYKMO': 'தன்ன', 'YKMOMKYO': 'தன்ன', 'YKMOMKMO': 'தன்ன', 'MKMOYKYO': 'தன்ன', 'MKMOYKMO': 'தன்ன', 'MKMOMKYO': 'தன்ன', 'MKMOMKMO': 'தன்ன', 'UKYOVKYO': 'தய்ய', 'UKYOVKMO': 'தய்ய', 'UKYOYKYO': 'தய்ய', 'UKYOYKMO': 'தய்ய', 'VKYOVKYO': 'தய்ய', 'VKYOVKMO': 'தய்ய', 'VKYOYKYO': 'தய்ய', 'VKYOYKMO': 'தய்ய', 'YKYOVKYO': 'தய்ய', 'YKYOVKMO': 'தய்ய', 'YKYOYKYO': 'தய்ய', 'YKYOYKMO': 'தய்ய', 'MKYOVKYO': 'தய்ய', 'MKYOVKMO': 'தய்ய', 'MKYOYKYO': 'தய்ய', 'MKYOYKMO': 'தய்ய', 'UNMOYKYO': 'தான', 'VNMOYKYO': 'தான', 'YNMOYKYO': 'தான', 'MNMOYKYO': 'தான', 'UNMOYKMO': 'தான', 'VNMOYKMO': 'தான', 'YNMOYKMO': 'தான', 'MNMOYKMO': 'தான', 'UNMOMKYO': 'தான', 'VNMOMKYO': 'தான', 'YNMOMKYO': 'தான', 'MNMOMKYO': 'தான', 'UNMOMKMO': 'தான', 'VNMOMKMO': 'தான', 'YNMOMKMO': 'தான', 'MNMOMKMO': 'தான', 'UNYOUKMO': 'தான', 'UNYOVKMO': 'தான', 'UNYOYKMO': 'தான', 'UNYOMKMO': 'தான', 'VNYOUKMO': 'தான', 'VNYOVKMO': 'தான', 'VNYOYKMO': 'தான', 'VNYOMKMO': 'தான', 'YNYOUKMO': 'தான', 'YNYOVKMO': 'தான', 'YNYOYKMO': 'தான', 'YNYOMKMO': 'தான', 'MNYOUKMO': 'தான', 'MNYOVKMO': 'தான', 'MNYOYKMO': 'தான', 'MNYOMKMO': 'தான', 'UNYOUKYO': 'தான', 'UNYOVKYO': 'தான', 'UNYOYKYO': 'தான', 'UNYOMKYO': 'தான', 'VNYOUKYO': 'தான', 'VNYOVKYO': 'தான', 'VNYOYKYO': 'தான', 'VNYOMKYO': 'தான', 'YNYOUKYO': 'தான', 'YNYOVKYO': 'தான', 'YNYOYKYO': 'தான', 'YNYOMKYO': 'தான', 'MNYOUKYO': 'தான', 'MNYOVKYO': 'தான', 'MNYOYKYO': 'தான', 'MNYOMKYO': 'தான', 'UKVOVNMO': 'தத்தா', 'VKVOVNMO': 'தத்தா', 'YKVOVNMO': 'தத்தா', 'MKVOVNMO': 'தத்தா', 'UKVOVNYO': 'தத்தா', 'VKVOVNYO': 'தத்தா', 'YKVOVNYO': 'தத்தா', 'MKVOVNYO': 'தத்தா', 'UKYOVOVN': 'தத்தா', 'VKYOVOVN': 'தத்தா', 'YKYOVOVN': 'தத்தா', 'MKYOVOVN': 'தத்தா', 'UNVOVNMO': 'தாத்தா', 'VNVOVNMO': 'தாத்தா', 'YNVOVNMO': 'தாத்தா', 'MNVOVNMO': 'தாத்தா', 'UNVOVNYO': 'தாத்தா', 'VNVOVNYO': 'தாத்தா', 'YNVOVNYO': 'தாத்தா', 'MNVOVNYO': 'தாத்தா', 'UNYOVOVN': 'தாத்தா', 'VNYOVOVN': 'தாத்தா', 'YNYOVOVN': 'தாத்தா', 'MNYOVOVN': 'தாத்தா', 'UKMOVNMO': 'தந்தா', 'VKMOVNMO': 'தந்தா', 'YKMOVNMO': 'தந்தா', 'MKMOVNMO': 'தந்தா', 'UKMOVNYO': 'தந்தா', 'VKMOVNYO': 'தந்தா', 'YKMOVNYO': 'தந்தா', 'MKMOVNYO': 'தந்தா', 'UKYOMOVN': 'தந்தா', 'VKYOMOVN': 'தந்தா', 'YKYOMOVN': 'தந்தா', 'MKYOMOVN': 'தந்தா', 'UNMOVNMO': 'தாந்தா', 'VNMOVNMO': 'தாந்தா', 'YNMOVNMO': 'தாந்தா', 'MNMOVNMO': 'தாந்தா', 'UNMOVNYO': 'தாந்தா', 'VNMOVNYO': 'தாந்தா', 'YNMOVNYO': 'தாந்தா', 'MNMOVNYO': 'தாந்தா', 'UNYOMOVN': 'தாந்தா', 'VNYOMOVN': 'தாந்தா', 'YNYOMOVN': 'தாந்தா', 'MNYOMOVN': 'தாந்தா', 'UKMOYNYO': 'தன்னா', 'UKMOYNMO': 'தன்னா', 'UKMOMNYO': 'தன்னா', 'UKMOMNMO': 'தன்னா', 'VKMOYNYO': 'தன்னா', 'VKMOYNMO': 'தன்னா', 'VKMOMNYO': 'தன்னா', 'VKMOMNMO': 'தன்னா', 'YKMOYNYO': 'தன்னா', 'YKMOYNMO': 'தன்னா', 'YKMOMNYO': 'தன்னா', 'YKMOMNMO': 'தன்னா', 'MKMOYNYO': 'தன்னா', 'MKMOYNMO': 'தன்னா', 'MKMOMNYO': 'தன்னா', 'MKMOMNMO': 'தன்னா', 'UKYOVNYO': 'தய்யா', 'UKYOVNMO': 'தய்யா', 'UKYOYNYO': 'தய்யா', 'UKYOYNMO': 'தய்யா', 'VKYOVNYO': 'தய்யா', 'VKYOVNMO': 'தய்யா', 'VKYOYNYO': 'தய்யா', 'VKYOYNMO': 'தய்யா', 'YKYOVNYO': 'தய்யா', 'YKYOVNMO': 'தய்யா', 'YKYOYNYO': 'தய்யா', 'YKYOYNMO': 'தய்யா', 'MKYOVNYO': 'தய்யா', 'MKYOVNMO': 'தய்யா', 'MKYOYNYO': 'தய்யா', 'MKYOYNMO': 'தய்யா', 'UNMOYNYO': 'தானா', 'VNMOYNYO': 'தானா', 'YNMOYNYO': 'தானா', 'MNMOYNYO': 'தானா', 'UNMOYNMO': 'தானா', 'VNMOYNMO': 'தானா', 'YNMOYNMO': 'தானா', 'MNMOYNMO': 'தானா', 'UNMOMNYO': 'தானா', 'VNMOMNYO': 'தானா', 'YNMOMNYO': 'தானா', 'MNMOMNYO': 'தானா', 'UNMOMNMO': 'தானா', 'VNMOMNMO': 'தானா', 'YNMOMNMO': 'தானா', 'MNMOMNMO': 'தானா', 'UNYOUNMO': 'தானா', 'UNYOVNMO': 'தானா', 'UNYOYNMO': 'தானா', 'UNYOMNMO': 'தானா', 'VNYOUNMO': 'தானா', 'VNYOVNMO': 'தானா', 'VNYOYNMO': 'தானா', 'VNYOMNMO': 'தானா', 'YNYOUNMO': 'தானா', 'YNYOVNMO': 'தானா', 'YNYOYNMO': 'தானா', 'YNYOMNMO': 'தானா', 'MNYOUNMO': 'தானா', 'MNYOVNMO': 'தானா', 'MNYOYNMO': 'தானா', 'MNYOMNMO': 'தானா', 'UNYOUNYO': 'தானா', 'UNYOVNYO': 'தானா', 'UNYOYNYO': 'தானா', 'UNYOMNYO': 'தானா', 'VNYOUNYO': 'தானா', 'VNYOVNYO': 'தானா', 'VNYOYNYO': 'தானா', 'VNYOMNYO': 'தானா', 'YNYOUNYO': 'தானா', 'YNYOVNYO': 'தானா', 'YNYOYNYO': 'தானா', 'YNYOMNYO': 'தானா', 'MNYOUNYO': 'தானா', 'MNYOVNYO': 'தானா', 'MNYOYNYO': 'தானா', 'MNYOMNYO': 'தானா',
}, 
{'UKYOVOVKMO': 'தத்த', 'UKYOVOVKYO': 'தத்த', 'VKYOVOVKMO': 'தத்த', 'VKYOVOVKYO': 'தத்த', 'YKYOVOVKMO': 'தத்த', 'YKYOVOVKYO': 'தத்த', 'MKYOVOVKMO': 'தத்த', 'MKYOVOVKYO': 'தத்த', 'UNYOVOVKMO': 'தாத்த', 'UNYOVOVKYO': 'தாத்த', 'VNYOVOVKMO': 'தாத்த', 'VNYOVOVKYO': 'தாத்த', 'YNYOVOVKMO': 'தாத்த', 'YNYOVOVKYO': 'தாத்த', 'MNYOVOVKMO': 'தாத்த', 'MNYOVOVKYO': 'தாத்த', 'UKYOMOVKMO': 'தந்த', 'UKYOMOVKYO': 'தந்த', 'VKYOMOVKMO': 'தந்த', 'VKYOMOVKYO': 'தந்த', 'YKYOMOVKMO': 'தந்த', 'YKYOMOVKYO': 'தந்த', 'MKYOMOVKMO': 'தந்த', 'MKYOMOVKYO': 'தந்த', 'UNYOMOVKMO': 'தாந்த', 'UNYOMOVKYO': 'தாந்த', 'VNYOMOVKMO': 'தாந்த', 'VNYOMOVKYO': 'தாந்த', 'YNYOMOVKMO': 'தாந்த', 'YNYOMOVKYO': 'தாந்த', 'MNYOMOVKMO': 'தாந்த', 'MNYOMOVKYO': 'தாந்த', 'UKYOVOVNMO': 'தத்தா', 'VKYOVOVNMO': 'தத்தா', 'YKYOVOVNMO': 'தத்தா', 'MKYOVOVNMO': 'தத்தா', 'UKYOVOVNYO': 'தத்தா', 'VKYOVOVNYO': 'தத்தா', 'YKYOVOVNYO': 'தத்தா', 'MKYOVOVNYO': 'தத்தா', 'UNYOVOVNMO': 'தாத்தா', 'VNYOVOVNMO': 'தாத்தா', 'YNYOVOVNMO': 'தாத்தா', 'MNYOVOVNMO': 'தாத்தா', 'UNYOVOVNYO': 'தாத்தா', 'VNYOVOVNYO': 'தாத்தா', 'YNYOVOVNYO': 'தாத்தா', 'MNYOVOVNYO': 'தாத்தா', 'UKYOMOVNMO': 'தந்தா', 'VKYOMOVNMO': 'தந்தா', 'YKYOMOVNMO': 'தந்தா', 'MKYOMOVNMO': 'தந்தா', 'UKYOMOVNYO': 'தந்தா', 'VKYOMOVNYO': 'தந்தா', 'YKYOMOVNYO': 'தந்தா', 'MKYOMOVNYO': 'தந்தா', 'UNYOMOVNMO': 'தாந்தா', 'VNYOMOVNMO': 'தாந்தா', 'YNYOMOVNMO': 'தாந்தா', 'MNYOMOVNMO': 'தாந்தா', 'UNYOMOVNYO': 'தாந்தா', 'VNYOMOVNYO': 'தாந்தா', 'YNYOMOVNYO': 'தாந்தா', 'MNYOMOVNYO': 'தாந்தா'
},
]
SANDHA_PAA_DURATION = [{"N" : 2.0, "K" : 1.0, ' ' : 0.0, '' : 0.0},
                       {"NO" : 2.0, "KO" : 2.0},
                       {"NOO" : 2.0, "KOO" : 2.0},
                      ]
ASAI_DICT = [{'N':'நேர்', 'K':'நேர்'}, 
             {'NO':'நேர்', 'KO':'நேர்', 'KK':'நிரை', 'KN':'நிரை'}, 
             {'NOO':'நேர்', 'KOO':'நேர்', 'KNO':'நிரை', 'KKO':'நிரை'},
             {'KNOO':'நிரை', 'KKOO':'நிரை'}]
VIKARPAM_LIST = ['ஒரு விகற்ப', "இரு விகற்ப", "பல விகற்ப"]
ASAIGAL = ['நேர்','நிரை']
SEERGAL = ['தேமா',"புளிமா","கூவிளம்","கருவிளம்", "தேமாங்காய்", "தேமாங்கனி", "புளிமாங்காய்", "புளிமாங்கனி", "கருவிளங்காய்", "கருவிளங்கனி", \
           "கூவிளங்காய்", "கூவிளங்கனி", "தேமாந்தண்பூ", "தேமாந்தண்ணிழல்", "தேமாநறும்பூ", "தேமாநறுநிழல்", "புளிமாந்தண்பூ", "புளிமாந்தண்ணிழல்", "புளிமாநறும்பூ", \
                "புளிமாநறுநிழல்", "கூவிளந்தண்பூ", "கூவிளந்தண்ணிழல்", "கூவிளநறும்பூ", "கூவிளநறுநிழல்", "கருவிளந்தண்பூ", "கருவிளந்தண்ணிழல்", "கருவிளநறும்பூ", "கருவிளநறுநிழல்"
          ]
SEER_TYPES = [ {"நேர்":"நேர்", "நிரை":"நிரை"}, \
               {"நேர் நேர்":"தேமா", "நிரை நேர்":"புளிமா", "நேர் நிரை":"கூவிளம்", "நிரை நிரை":"கருவிளம்"}, \
               {"நேர் நேர் நேர்":"தேமாங்காய்", "நேர் நேர் நிரை":"தேமாங்கனி", "நிரை நேர் நேர்":"புளிமாங்காய்", "நிரை நேர் நிரை":"புளிமாங்கனி", \
                "நிரை நிரை நேர்":"கருவிளங்காய்", "நிரை நிரை நிரை":"கருவிளங்கனி", "நேர் நிரை நேர்":"கூவிளங்காய்", "நேர் நிரை நிரை":"கூவிளங்கனி"
               }, \
               {"நேர் நேர் நேர் நேர்":"தேமாந்தண்பூ", "நேர் நேர் நேர் நிரை":"தேமாந்தண்ணிழல்", "நேர் நேர் நிரை நேர்":"தேமாநறும்பூ", "நேர் நேர் நிரை நிரை":"தேமாநறுநிழல்", \
                "நிரை நேர் நேர் நேர்":"புளிமாந்தண்பூ", "நிரை நேர் நேர் நிரை":"புளிமாந்தண்ணிழல்", "நிரை நேர் நிரை நேர்":"புளிமாநறும்பூ", \
                "நிரை நேர் நிரை நிரை":"புளிமாநறுநிழல்", "நேர் நிரை நேர் நேர்":"கூவிளந்தண்பூ", "நேர் நிரை நேர் நிரை":"கூவிளந்தண்ணிழல்", \
                "நேர் நிரை நிரை நேர்":"கூவிளநறும்பூ", "நேர் நிரை நிரை நிரை":"கூவிளநறுநிழல்", "நிரை நிரை நேர் நேர்":"கருவிளந்தண்பூ", \
                "நிரை நிரை நேர் நிரை":"கருவிளந்தண்ணிழல்", "நிரை நிரை நிரை நேர்":"கருவிளநறும்பூ", "நிரை நிரை நிரை நிரை":"கருவிளநறுநிழல்"
               }
            ]
THALAI_TYPES = {"மா நேர்": "நேரொன்றிய ஆசிரியத்தளை", 
        "விளம் நிரை" : "நிரையொன்றிய ஆசிரியத்தளை",
        "விளம் நேர்" : "இயற்சீர் வெண்டளை",
        "மா நிரை" : "இயற்சீர் வெண்டளை",
        "காய் நேர்" : "வெண்சீர் வெண்டளை",
        "காய் நிரை" : "கலித்தளை",
        "கனி நிரை" : "ஒன்றிய வஞ்சித்தளை",
        "கனி நேர்" : "ஒன்றா வஞ்சித்தளை",
        "பூ நேர்" : "வெண்சீர் வெண்டளை",
        "பூ நிரை" : "கலித்தளை",
        "நிழல் நேர்" : "ஒன்றா வஞ்சித்தளை",
        "நிழல் நிரை" : "ஒன்றிய வஞ்சித்தளை",
        "ணிழல் நேர்" : "ஒன்றா வஞ்சித்தளை",
        "ணிழல் நிரை" : "ஒன்றிய வஞ்சித்தளை",
        }
THALAI_TYPES_SHORT = {"மா நேர்": "ஆசிரியத்தளை", 
        "விளம் நிரை" : "ஆசிரியத்தளை",
        "விளம் நேர்" : "வெண்டளை",
        "மா நிரை" : "வெண்டளை",
        "காய் நேர்" : "வெண்டளை",
        "காய் நிரை" : "கலித்தளை",
        "கனி நிரை" : "வஞ்சித்தளை",
        "கனி நேர்" : "வஞ்சித்தளை",
        "பூ நேர்" : "வெண்டளை",
        "பூ நிரை" : "கலித்தளை",
        "நிழல் நேர்" : "வஞ்சித்தளை",
        "நிழல் நிரை" : "வஞ்சித்தளை",
        "ணிழல் நேர்" : "வஞ்சித்தளை",
        "ணிழல் நிரை" : "வஞ்சித்தளை",
        }
OSAI_TYPES = {"நேரொன்றிய ஆசிரியத்தளை" : "ஏந்திசை அகவலோசை",
        "நிரையொன்றிய ஆசிரியத்தளை" : "தூங்கிசை அகவலோசை",
        "இயற்சீர் வெண்டளை" : "தூங்கிசைச் செப்பலோசை",
        "வெண்சீர் வெண்டளை" : "ஏந்திசைச் செப்பலோசை",
        "கலித்தளை" : "ஏந்திசைத் துள்ளலோசை",
        "ஒன்றிய வஞ்சித்தளை" : "ஏந்திசைத் தூங்கலோசை",
        "ஒன்றா வஞ்சித்தளை" : "அகவல் தூங்கலோசை",
        }
OSAI_TYPES_SHORT = {"ஆசிரியத்தளை" : "அகவலோசை",
        "வெண்டளை" : "செப்பலோசை",
        "கலித்தளை" : "துள்ளலோசை",
        "வஞ்சித்தளை" : "தூங்கலோசை",
        }
LINE_TYPES = ('','தனிச்சொல்', 'குறளடி', 'சிந்தடி', 'அளவடி', 'நெடிலடி', 'கழி நெடிலடி', 'கழி நெடிலடி', 'கழி நெடிலடி', 'இடையாகு கழி நெடிலடி', 'இடையாகு கழி நெடிலடி', 'கடையாகு கழி நெடிலடி'  )
THODAI_TYPES = ("மோனை", "எதுகை", "இயைபு")
SEER_THODAI_TYPES = {"":"", "1" : "","1-2" : "இணை", "1-3" : "பொழிப்பு", "1-4" : "ஒருஊ", "1-2-3" : "கூழை", "1-3-4" : "மேற்கதுவாய்", "1-2-4" : "கீழ்க்கதுவாய்", "1-2-3-4" : "முற்று"}
class POEM_TYPES(IntEnum):
    VENPA = 1
    ASIRIYAPA = 2
    KALIPA = 3
    VANJIPA = 4
    VENPAVINAM = 5
    ASIRIYAPAVINAM = 6
    KALIPAVINAM = 7
    VANJIPAVINAM = 8
POEM_CHECK_FUNCTIONS = { 
    POEM_TYPES.VENPA : 'check_for_venpaa', 
    POEM_TYPES.ASIRIYAPA : 'check_for_asiriyapaa',  
    POEM_TYPES.KALIPA : 'check_for_kalipaa', 
    POEM_TYPES.VANJIPA : 'check_for_vanjipaa', 
    POEM_TYPES.VENPAVINAM : 'check_for_venpaavinam', 
    POEM_TYPES.ASIRIYAPAVINAM : 'check_for_asiriyapaavinam', 
    POEM_TYPES.KALIPAVINAM : 'check_for_kalipaavinam', 
    POEM_TYPES.VANJIPAVINAM : 'check_for_vanjipaavinam' 
}
UYIRALABEDAI = ["ஆஅ", "ஆஅஅ", "ஈஇ", "ஊஉ", "ஏஎ", "ஐஇ", "ஓஒ", "ஔஉ"]
OTRALABEDAI = ["ங்ங்","ஞ்ஞ்","ண்ண்","ந்ந்","ன்ன்","ம்ம்","ய்ய்","ல்ல்","ள்ள்","ஃஃ",]

" Check if string has key"
string_has_key = lambda a, d: any(k in a for k in d)

" Flatten a list of lists "
flatten_list = lambda list: [item for sublist in list for item in sublist]
""" Generate VARUKKA EDHUGAI """
VARUKKA_EDHUGAI = list(UYIR_MEY_LETTERS)
n = 12
i = n
while i < len(VARUKKA_EDHUGAI):
    for j in range(len(MEYGAL)):
        x = MEYGAL[j]
        #print('inserting ',x,' at ', i)
        VARUKKA_EDHUGAI.insert(i,x)
        i += (n+1)

def _is_uyir_ezhuthu(tamil_char):
    return list_has_element(UYIRGAL, tamil_char)
def _is_mey_ezhuthu(tamil_char):
    return list_has_element(MEYGAL, tamil_char)
def insert_string_at_index(string, insert_string, index):
    if index == -1:
        index = len(string)-1
        if ' ' in string:
            index = len(string)-2
    if index < len(string):
        result = ''.join(string[:index])+insert_string[0]+string[index]+insert_string[1]+''.join(string[index+1:])
    else:
        result = string
    return result

def get_index(list, element):
    index = -1
    try:
        index = list.index(element)
    except:
        index = -1
    return index
    
def get_keys_containing_string(dict, string):
    return [value for key, value in dict.items() if key.lower() in string.lower()]
            
def get_last_morpheme(word):
    if word.strip()=='':
        return '' 
    last_char = word[-1]
    if last_char == "்":
        last_char = MEYGAL[TAMIL_UNICODE_1.index(word[-2])]
    if _is_uyir_ezhuthu(last_char) or _is_mey_ezhuthu(last_char):
        return last_char
    index = get_index(TAMIL_UNICODE_2,last_char)
    if (index == -1):
        return "அ"
    index = get_index(YIYAIBU_ENDING_LETTERS,last_char)
    if index != -1:
        return UYIRGAL[index+1]
    return last_char

def get_first_morpheme(word):
    if word.strip()=='':
        return '' 
    first_char = word[0]
    if _is_uyir_ezhuthu(first_char) or _is_mey_ezhuthu(first_char):
        return first_char
    index = get_index(TAMIL_UNICODE_1,first_char)
    if (index != -1 ):
        return MEYGAL[index]
    index = get_index(YIYAIBU_ENDING_LETTERS,first_char)
    if index != -1:
        return UYIRGAL[index+1]
    return first_char

def list_has_element(list,element):
    try:
        return element in list
    except:
        return False

def string_has_unicode_character(word, character):
    result = character in get_unicode_characters(word)
    return result

def get_unicode_characters(word):
    import regex
    if (' ' in word):
        return regex.findall('\p{L}\p{M}*|\p{Z}*',word)
    else:
        return regex.findall('\p{L}\p{M}*',word)
    

def get_matching_sublist(char,list,index):
    " To get a subarray of size index at matching element "
    try:
        beg = int(list.index(char)/index)*index
        end = beg + index
        return list[beg:end]
    except ValueError:
        return []
        
def __get_thodai_characters_TODO(thodai_char1, thodai_index=0):
    thodai_characters = []
    temp_list = []
    if (thodai_index == 0 or thodai_index == 1):
        """ Nedil monai/edhugai """
        temp_list = get_matching_sublist(thodai_char1,NEDILGAL,5)
        if temp_list:
            thodai_characters.append(temp_list)
        """ yina monai / edhigai """
        temp_list = get_matching_sublist(thodai_char1,flatten_list([VALLINAM, YIDAIYINAM, MELLINAM]),12)
        if temp_list:
            thodai_characters.append(temp_list)
        """ Varukka monai / edhugai """
        temp_list = get_matching_sublist(thodai_char1,VARUKKA_EDHUGAI,13)
        if temp_list:
            #print(thodai_char1,'found in monia4_5_6')
            thodai_characters.append(temp_list)
    elif (thodai_index == 1):
        temp_list = get_matching_sublist(thodai_char1,VARUKKA_EDHUGAI,13)
        if temp_list:
            #print(thodai_char1,'found in varukka edhugai')
            thodai_characters.append(temp_list)
        temp_list = get_matching_sublist(thodai_char1,flatten_list([VALLINA_THODAI, MELLINA_THODAI, YIDAIYINA_THODAI]),13)
        if temp_list:
            #print(thodai_char1,'found in yina edhugai')
            thodai_characters.append(temp_list)
    thodai_characters = flatten_list(thodai_characters)
    #print(thodai_char1,' in? ',thodai_characters, '???')
    return thodai_characters

def get_thodai_characters(thodai_char1, thodai_index=0):
    thodai_characters = []
    temp_list = []
    if (thodai_index == 0):
        temp_list = get_matching_sublist(thodai_char1,flatten_list([MONAI_THODAI_1, MONAI_THODAI_2, MONAI_THODAI_3]),4)
        if temp_list:
            #print(thodai_char1,'found in monia1_2_3')
            thodai_characters.append(temp_list)
        temp_list = get_matching_sublist(thodai_char1,flatten_list([MONAI_THODAI_4, MONAI_THODAI_5, MONAI_THODAI_6]),8)
        if temp_list:
            #print(thodai_char1,'found in monia4_5_6')
            thodai_characters.append(temp_list)
        temp_list = get_matching_sublist(thodai_char1,VARUKKA_EDHUGAI,13)
        if temp_list:
            #print(thodai_char1,'found in monia4_5_6')
            thodai_characters.append(temp_list)
    elif (thodai_index == 1):
        temp_list = get_matching_sublist(thodai_char1,VARUKKA_EDHUGAI,13)
        if temp_list:
            #print(thodai_char1,'found in varukka edhugai')
            thodai_characters.append(temp_list)
        temp_list = get_matching_sublist(thodai_char1,flatten_list([VALLINA_THODAI, MELLINA_THODAI, YIDAIYINA_THODAI]),13)
        if temp_list:
            #print(thodai_char1,'found in yina edhugai')
            thodai_characters.append(temp_list)
    thodai_characters = flatten_list(thodai_characters)
    #print(thodai_char1,' in? ',thodai_characters, '???')
    return thodai_characters

def frequency_of_occurrence(words, specific_words=None):
    """
    Returns a list of (instance, count) sorted in total order and then from most to least common
    Along with the count/frequency of each of those words as a tuple
    If specific_words list is present then SUM of frequencies of specific_words is returned 
    """
    freq = sorted(sorted(Counter(words).items(), key=itemgetter(0)), key=itemgetter(1), reverse=True)
    if not specific_words or specific_words==None:
        return freq
    else:
        frequencies = 0
        for (inst, count) in freq:
            if inst in specific_words:
                frequencies += count        
        return float(frequencies)
        
def has_required_percentage_of_occurrence(words, specific_words=None,required_percent_of_occurrence=0.99):
    actual_percent_of_occurrence = percentage_of_occurrence(words, specific_words=specific_words)
    percent_check = actual_percent_of_occurrence >= required_percent_of_occurrence
    #print(actual_percent_of_occurrence,required_percent_of_occurrence,percent_check)
    return [percent_check, actual_percent_of_occurrence]

def percentage_of_occurrence(words, specific_words=None):
    """
    Returns a list of (instance, count) sorted in total order and then from most to least common
    Along with the percent of each of those words as a tuple
    If specific_words list is present then SUM of percentages of specific_words is returned 
    """
    frequencies = frequency_of_occurrence(words) # Dont add specific_word as argument here float error happens
    #print('FREQ',frequencies)
    perc = [(instance, count / len(words)) for instance, count in frequencies]
    if not specific_words or specific_words==None:
        return perc
    else:
        percentages = 0
        for (inst, per) in perc:
            if inst in specific_words:
                percentages += per        
        return percentages

def convert_1d_list_to_2d(list_1d_arr, len_arr):
    it = iter(list_1d_arr)
    return [list(islice(it, i)) for i in len_arr]
    
def get_character_type_counts(sentence, results_in_descending_order=True, show_by_character_type_keys=True, include_zero_counts=False):
    stats = {}
    sentence = sentence.replace('\n',' ') #remove line ends
    sentence = sentence.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
    words = sentence.split()
    for word in words:
        if (word.strip() == ''):
            continue
        sol = grammar.Sol(word)
        for tc in sol.tamil_char_objects:
            for char_type in _CHARACTER_TYPES.keys():
                #fun = 'is_'+char_type
                #val = getattr(tc,'is_'+char_type)()
                if char_type in stats:
                    stats[char_type] += getattr(tc,'is_'+char_type)()
                else:
                    stats[char_type] = getattr(tc,'is_'+char_type)()
                #print(tc.text(),char_type,fun,val,stats[char_type])
    results = []
    if show_by_character_type_keys:
        for char_type in _CHARACTER_TYPES.keys():
            if include_zero_counts or stats[char_type] !=0:
                results.append([char_type,stats[char_type]])
    else:
        for char_type in _CHARACTER_TYPES.keys():
            if include_zero_counts or stats[char_type] !=0:
                results.append([_CHARACTER_TYPES.get(char_type),stats[char_type]])
        
    results = sorted(results,key=itemgetter(1),reverse=results_in_descending_order)
    return results       
def get_all_tamil_characters(include_space=True, include_vadamozhi=False):
    all_tamil_chars = []
    if include_space:
        all_tamil_chars = [' ']
    T_U_1 = TAMIL_UNICODE_1_TA
    if include_vadamozhi:
        T_U_1 += TAMIL_UNICODE_1_SAN 
    all_tamil_chars += UYIRGAL+['ஃ']+T_U_1+ [t1+t2 for t1 in T_U_1 for t2 in TAMIL_UNICODE_2]
    return all_tamil_chars

"""
@dataclass
class RuleEngine:
    id : int = 0
    topic = str =''
    description : str = ''
    is_met : bool = False
"""    
    
if __name__ == '__main__':
    print(print(get_unicode_characters('முத்து, வற்றல்,அரிதினில்')))
    exit()
    print(len(get_all_tamil_characters()))
    exit()
    """
    VANNAPAA_DICT_1 = {}
    for k,v in VANNAPAA_DICT.items():
        for v1 in v:
           VANNAPAA_DICT_1[v1] = k
    VANNAPAA_DICT_2 = dict(sorted(VANNAPAA_DICT_1.items(), key = lambda item : len(item[0])))
    print(VANNAPAA_DICT_2) 
    exit()
    """
    s = "முத்து, வற்றல், விட்டம், மொய்த்த, மெய்ச்சொல், கர்த்தன்\n"+ \
"அக்கா, முட்டாள், விட்டான், பொய்க்கோ, நெய்க்கோல், மெய்க்கோன்\n"+ \
"பாட்டு, பாட்டன், கூத்தன், வார்ப்பு, தூர்த்தன், வாழ்த்தல்\n"+ \
"தாத்தா, மூச்சால், சாத்தான், வேய்ப்பூ, மாய்த்தோர், வார்த்தோன்\n"+ \
"பந்து, உம்பர், சுண்டல், மொய்ம்பு, மொய்ம்பர், மொய்ம்பன்\n"+ \
"அந்தோ, வந்தார், தந்தேன், மொய்ம்பா, மொய்ம்போர், மொய்ம்போன்\n"+ \
"வேந்து, வேந்தர், பாங்கன், பாய்ந்து, சார்ங்கர், சார்ங்கம்\n"+ \
"சேந்தா, வாங்கார், நான்றான், நேர்ந்தோ, சார்ந்தார், மாய்ந்தான்"#வற்றல் விட்டம்"
    print(s,'\n',get_character_type_counts(s,show_by_character_type_keys=False, include_zero_counts=False))
    exit()
    s = "NOKOKNKO"
    total = sum([SANDHA_PAA_DURATION[k] for k in s])
    print(total)
    exit()
    print('first morpheme',get_first_morpheme("காய்"),'last morpheme',get_last_morpheme("காய்"))
    exit()
    print(insert_string_at_index(get_unicode_characters('தனந்தரும் கல்வி தருமொரு நாளும் தளர்வறியா'),'()',-1))
    exit()
    words = ["மா", "விளம்", "காய்", "கனி", "பூ", "மா", "விளம்", "காய்", "கனி", "பூ"]
    specific_words = ["விளம்"]
    print(frequency_of_occurrence(words))
    print(frequency_of_occurrence(words, specific_words))
    print(percentage_of_occurrence(words))
    print(percentage_of_occurrence(words, specific_words))
    exit()
    print(get_matching_sublist('சை',flatten_list([MONAI_THODAI_4, MONAI_THODAI_5, MONAI_THODAI_6]),8))
    print(get_matching_sublist('வெ',flatten_list([MONAI_THODAI_1, MONAI_THODAI_2, MONAI_THODAI_3]),4))
    exit()
    print(get_keys_containing_string(THALAI_TYPES,'தேமாந்தண்பூ நேர் நேர் நேர் நிரை' ))
    exit()
    print(get_unicode_characters('க்ஷோக்ஷௌஹோ'))
    exit()
    print('கூவிளங்கனி','ங்',string_has_unicode_character('கூவிளங்கனி','ங்'))
    print('கூவிளங்கனி',"ூ",string_has_unicode_character('கூவிளங்கனி',"ூ"))
    exit()
    sol = grammar.Sol('கூவிளங்கனி')
    exit()
    get_unicode_characters(str)
    exit()
    print(str,str[-1])
    print(str, string_has_unicode_character(str, "ூ"))
    tamil_letter = grammar.Ezhuthu('கூ')
    print(tamil_letter.text,tamil_letter.is_nedil,'is kuril',tamil_letter.is_kuril)