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
    poem_number = 13
    config_keywords = config["key_words"]
    for poem in sangam_tamil.POEM_TYPES:
        user_input = poem + " " + str(poem_number)
        expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
        for value in config_keywords[poem]:
            user_input = value + " " + str(poem_number)
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = poem+"-"+user_input
            print("Testing "+test_name+" ...")
            unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
def sangam_thirukural_tests():
    search_types = {"contains":"தாள்சேர்ந்தார்க்","ends_with":"குறிப்பு.", "begins_with":"கண்ணொடு"}
    poem = "திருக்குறள்"
    config_keywords = config["key_words"][poem]
    for poem_value in config_keywords:
        for search_type in search_types.keys():
            search_word = search_types[search_type]
            for search_value in config["key_words"][search_type]:
                user_input = poem_value + " " +search_value + " "+ search_word
                expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
                actual_result = sangam_class.respond_to_bot_user_input(user_input)
                test_name = poem+"-"+user_input
                print("Testing "+test_name+" ...")
                unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
                ## Reverse the key value
                user_input = poem_value + " "+ search_word + " " +search_value 
                expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
                actual_result = sangam_class.respond_to_bot_user_input(user_input)
                test_name = poem+"-"+user_input
                print("Testing "+test_name+" ...")
                unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
            # Get tests
            search_keys = ["get 12", "get 12, 5", "kural 1234"]
            for search_key in search_keys:
                user_input = poem_value + " " +search_key
                expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
                actual_result = sangam_class.respond_to_bot_user_input(user_input)
                test_name = poem+"-"+user_input
                print("Testing "+test_name+" ...")
                unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
def sangam_poet_count_tests():
    config_key = 'poet_count'
    config_keywords = config["key_words"][config_key]
    for poem in sangam_tamil.POEM_TYPES:
        for value in config_keywords:
            user_input = poem + " " + str(value)
            expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = config_key+"-"+user_input
            print("Testing "+test_name+" ...")
            unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
def sangam_poet_poems_tests():
    config_key = 'poet_poems'
    config_keywords = config["key_words"][config_key]
    for poem in sangam_tamil.POEM_TYPES:
        for value in config_keywords:
            user_input = poem + " " + str(value)
            expected_result = sangam_class._respond_to_bot_user_input_old(user_input)
            actual_result = sangam_class.respond_to_bot_user_input(user_input)
            test_name = config_key+"-"+user_input
            print("Testing "+test_name+" ...")
            unit_test(test_name,expected_result,actual_result, assert_test=False,show_output=False)
def sangam_start_end_words():
    data_files = ['test_1','test_2','test_3']
    data_files = ["./sangam_tamil_poems/" + d + "_poems.txt" for d in data_files]
    cdeeplearn.set_parameters(corpus_file='sangam_corpus.json', model_weights_file='sangam_corpus.h5',
           starting_word_file='sangam_starting_words.json', ending_word_file='sangam_ending_words.json')
    _,starting_words,ending_words = cdeeplearn._create_corpus_files(data_files,end_token_boundary=None)
    expected_result = ['மல்லர்க்','உவவுமதி','மண்','கண்ணி','இருங்கழி','கோழ்','அணி','வண்டு','மின்னும்']
    unit_test("Starting-Unique-Words",set(expected_result),set(starting_words), assert_test=False,show_output=False)
    expected_result = ['வன்மையானே','கொண்டன்றே','ஞான்றே','தோள்','அருந்தவத்தோற்கே','இறந்தோரே','கார்','போன்றே']
    unit_test("Ending-Unique-Words",set(expected_result),set(ending_words), assert_test=False,show_output=False)
           
def run_all_unit_tests():
    sangam_poem_tests()
    sangam_poet_count_tests()
    sangam_poet_poems_tests()
    sangam_thirukural_tests()
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
    