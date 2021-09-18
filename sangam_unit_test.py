# -*- coding: utf-8 -*-
test_input_folder = 'test_input/'
sangam_tamil = __import__("sangam_tamil")
cdeeplearn = __import__("cdeeplearn")
sangam_class = sangam_tamil.SangamPoems()
config = sangam_tamil.config
GREEN_CHECK = u'\u2714  '
RED_CROSS = u'\u274C  '
GEQ = u' \u2265 '
STATUS_CHECK = lambda rc : GREEN_CHECK if rc else RED_CROSS

def unit_test(test_name,expected,actual, assert_test=False,show_output=True):
    unit_test.counter +=1
    status = 'Passed'
    if (expected != actual):
        status = 'Failed'
        unit_test.failed += 1
        unit_test.failed_tests += str(unit_test.counter) +';'
    if show_output:
        print('Test#:',unit_test.counter,'Test:',STATUS_CHECK(expected == actual)+test_name, \
              "\tExpected Result:",expected, \
              '\tActual Result :',actual, \
               '\tStatus:',status
              )
    else:
        print('Test#:',unit_test.counter,'Test:',STATUS_CHECK(expected == actual)+test_name, \
               '\tStatus:',status
              )
    if assert_test:
         assert(status)

def unit_test_actual_contains_expected(test_name,expected,actual, assert_test=False,show_output=True):
    unit_test.counter +=1
    status = 'Passed'
    if (not expected in actual):
        status = 'Failed'
        unit_test.failed += 1
        unit_test.failed_tests += str(unit_test.counter) +';'
    if show_output:
        print('Test#:',unit_test.counter,'Test:',STATUS_CHECK(expected in actual)+test_name, \
              "\tExpected Result:",expected, \
              '\tActual Result :',actual, \
               '\tStatus:',status
              )
    else:
        print('Test#:',unit_test.counter,'Test:',STATUS_CHECK(expected in actual)+test_name, \
               '\tStatus:',status
              )
    if assert_test:
         assert(status)

def class_method_unit_test(class_name, init_value, function_name, expected_result, *args):
    obj = eval(class_name)(init_value)
    test_name = str(class_name) +'-' + function_name + ' ' + init_value +' args: '+' '.join(map(str, args))
    actual_result = getattr(obj,function_name)(*args)
    unit_test(test_name,expected_result,actual_result)

def class_attribute_unit_test(class_name, init_value, attribute_name, expected_result):
    obj = eval(class_name)(init_value)
    test_name = str(class_name) +'-' + attribute_name + ' ' + init_value
    actual_result = getattr(obj,attribute_name)
    unit_test(test_name,expected_result,actual_result)

def sangam_poem_tests():
    show_output = False
    poem_number = 13
    config_keywords = config["key_words"]
    POEM_DICT = {"அகநானூறு":"தென்னவன்", "புறநானூறு":"களிற்று", "ஐங்குறுநூறு":"அடைகரை", "கலித்தொகை":"சுவைத்துத்", "குறுந்தொகை":"கழீஇய", "நற்றிணை":"பெருந்தோளோயே", "பதிற்றுப்பத்து":"யாக்கை", "பட்டினப்பாலை":"புணரியோடு", 
              "முல்லைப்பாட்டு":"பதைப்பன்ன", "நெடுநல்வாடை":"நுண்ணிதின்","குறிஞ்சிப்பாட்டு":"மொய்ம்பு","மலைபடுகடாம்":"பயம்புமார்", "மதுரைக்காஞ்சி":"உறைதும்","பொருநராற்றுப்படை":"கிளந்தனம்",
              "பெரும்பாணாற்றுப்படை":"மறம்பூண்", "சிறுபாணாற்றுப்படை":"கடம்பின்","திருமுருகாற்றுப்படை":"மஞ்ஞை","ஐந்திணை எழுபது":"முயங்கினேன்","ஐந்திணை ஐம்பது":"மயங்கல்","கார் நாற்பது":"வனப்பின்",
              "திணைமொழி ஐம்பது":"மலர்ந்தன","கைந்நிலை":"செலவுரைப்பக்","திணைமாலை நூற்றைம்பது":"ஆயுங்கால்"}#,"திருக்குறள்"]
    for poem in POEM_DICT.keys():
        user_input = poem + " " + str(poem_number)
        expected_result = POEM_DICT[poem]
        for value in config_keywords[poem]:
            user_input = value + " " + str(poem_number)
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = poem+"-"+user_input
            print("Test: "+test_name+" ...")
            unit_test_actual_contains_expected(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)
def sangam_thirukural_keywords_tests():
    show_output = False
    search_types = {"contains":"தாள்சேர்ந்தார்க்","ends_with":"குறிப்பு.", "begins_with":"கண்ணொடு"}
    poem = "திருக்குறள்"
    config_keywords = config["key_words"][poem]
    for poem_value in config_keywords:
        for search_type in search_types.keys():
            search_word = search_types[search_type]
            for search_value in config["key_words"][search_type]:
                user_input = poem_value + " " +search_value + " "+ search_word
                expected_result = search_word
                actual_result = sangam_class.respond_to_bot_user_input(user_input)
                test_name = poem+"-"+user_input
                print("Test: "+test_name+" ...")
                unit_test_actual_contains_expected(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)
                ## Reverse the key value
                user_input = poem_value + " "+ search_word + " " +search_value 
                expected_result = search_word
                actual_result = sangam_class.respond_to_bot_user_input(user_input)
                test_name = poem+"-"+user_input
                print("Test: "+test_name+" ...")
                unit_test_actual_contains_expected(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)
def sangam_thirukural_get_tests():
    show_output = False
    search_types = {
        "get":"சீரற்ற தேர்வு  (random choice)",
        "get 12":"அறத்துப்பால்", 
        "get 12,3":"நடுவிகந்தாம்", 
        "get 1234":"அதிகார எண் 133 க்குள் இருக்க வேண்டும்",
        "kural 1234":"பைந்தொடி"
    }
    poem = "திருக்குறள்"
    config_keywords = config["key_words"][poem]
    for poem_value in config_keywords:
        for search_key in search_types.keys():
            search_value = search_types[search_key]
            user_input = poem_value + " " +search_key
            expected_result = search_value
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = poem+"-"+user_input
            print("Test: "+test_name+" ...")
            unit_test_actual_contains_expected(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)
def sangam_poet_count_tests():
    show_output = False
    config_key = 'poet_count'
    config_keywords = config["key_words"]
    POEM_DICT = {"அகநானூறு":174, "புறநானூறு":160, "ஐங்குறுநூறு":5, "கலித்தொகை":6, "குறுந்தொகை":216, "நற்றிணை":200, "பதிற்றுப்பத்து":9, "பட்டினப்பாலை":1, 
              "முல்லைப்பாட்டு":1, "நெடுநல்வாடை":1,"குறிஞ்சிப்பாட்டு":1,"மலைபடுகடாம்":1, "மதுரைக்காஞ்சி":1,"பொருநராற்றுப்படை":1,
              "பெரும்பாணாற்றுப்படை":1, "சிறுபாணாற்றுப்படை":1,"திருமுருகாற்றுப்படை":1,"ஐந்திணை எழுபது":1,"ஐந்திணை ஐம்பது":1,"கார் நாற்பது":1,
              "திணைமொழி ஐம்பது":1,"கைந்நிலை":1,"திணைமாலை நூற்றைம்பது":1}#,"திருக்குறள்"]
    for poem in POEM_DICT.keys():
        expected_result = poem + " எழுதிய புலவர்கள் எண்ணிக்கை:  "+str(POEM_DICT[poem])
        for value in config_keywords[config_key]:
            user_input = poem + " " + str(value)
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = poem+"-"+user_input
            print("Test: "+test_name+" ...")
            unit_test_actual_contains_expected(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)
def sangam_poet_poems_tests():
    show_output = False
    config_key = 'poet_poems'
    config_keywords = config["key_words"]
    POEM_DICT = {"அகநானூறு":["பரணர்",34], "புறநானூறு":["ஔவையார்",33], "ஐங்குறுநூறு":["அம்மூவனார்",100], "கலித்தொகை":["பாலை பாடிய பெருங்கடுங்கோ",35], "குறுந்தொகை":["அள்ளூர் நன்முல்லையார்",9], "நற்றிணை":["உலோச்சனார்",20], "பதிற்றுப்பத்து":["அரிசில்கிழார்",12], "பட்டினப்பாலை":["உருத்திரங்கண்ணனார்",40], 
              "முல்லைப்பாட்டு":["காவிரிப்பூம்பட்டினத்துப் பொன்வணிகனார்",18], "நெடுநல்வாடை":["கணக்காயனார்",27],"குறிஞ்சிப்பாட்டு":["கபிலர்",28],"மலைபடுகடாம்":["பெருங்கெளசிகனார்",44], "மதுரைக்காஞ்சி":["மாங்குடி மருதனார்",63],"பொருநராற்றுப்படை":["முடத்தாமக் கண்ணியார்",20],
              "பெரும்பாணாற்றுப்படை":["கடியலூர் உருத்திரங் கண்ணனார்",41], "சிறுபாணாற்றுப்படை":["நத்தத்தனார்",50],"திருமுருகாற்றுப்படை":["நக்கீரர்",30],"ஐந்திணை எழுபது":["மூவாதியார்",70],"ஐந்திணை ஐம்பது":["மாறன் பொறையனார்",50],"கார் நாற்பது":["மதுரைக் கண்ணங்கூத்தனார்",40],
              "திணைமொழி ஐம்பது":["கண்ணன்சேந்தனார்",50],"கைந்நிலை":["புல்லங்காடனார்",60],"திணைமாலை நூற்றைம்பது":["கணிமேதாவியார்",153]
              }#,"திருக்குறள்"]
    for poem in POEM_DICT.keys():
        poet_name = str(POEM_DICT[poem][0])
        expected_result = str(POEM_DICT[poem][1])
        for value in config_keywords[config_key]:
            user_input = poem + " " + value + " "+poet_name
            actual_result = str(sangam_class.respond_to_bot_user_input(user_input).count(poet_name))
            test_name = poem+"-"+user_input
            print("Test: "+test_name+" ...")
            unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=show_output)    
def sangam_start_end_words():
    show_output = False
    data_files = ['test_1','test_2','test_3']
    data_files = ["./sangam_tamil_poems/" + d + "_poems.txt" for d in data_files]
    cdeeplearn.set_parameters(corpus_file='sangam_corpus.json', model_weights_file='sangam_corpus.h5',
           starting_word_file='sangam_starting_words.json', ending_word_file='sangam_ending_words.json')
    _,starting_words,ending_words = cdeeplearn._create_corpus_files(data_files,end_token_boundary=None)
    expected_result = ['மல்லர்க்','உவவுமதி','மண்','கண்ணி','இருங்கழி','கோழ்','அணி','வண்டு','மின்னும்']
    unit_test("Starting-Unique-Words",set(expected_result),set(starting_words), assert_test=False,show_output=show_output)
    expected_result = ['வன்மையானே','கொண்டன்றே','ஞான்றே','தோள்','அருந்தவத்தோற்கே','இறந்தோரே','கார்','போன்றே']
    unit_test("Ending-Unique-Words",set(expected_result),set(ending_words), assert_test=False,show_output=show_output)
           
def run_all_unit_tests():
    sangam_poem_tests()
    sangam_poet_count_tests()
    sangam_poet_poems_tests()
    sangam_thirukural_keywords_tests()
    sangam_thirukural_get_tests()
    sangam_start_end_words()
    pass
def run_specific_tests():
    pass
if __name__ == '__main__':
    unit_test.counter = 0
    unit_test.failed=0
    unit_test.failed_tests = ''
    #run_specific_tests()
    run_all_unit_tests()
      
    if unit_test.failed > 0:
        print(str(unit_test.failed)+ ' out of ' + str(unit_test.counter) + " tests Failed. Test id's of failed tests:",unit_test.failed_tests)
    else:
        print('All (' + str(unit_test.counter)+') unit tests passed.')
    exit()
    