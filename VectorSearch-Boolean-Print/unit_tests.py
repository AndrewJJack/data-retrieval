import unittest
import os

from create_index import *
from boolean_query import *
from print_index import *
#from vs_query import *

#test cases run with sample documents
#there must a folder called documents with correct files in same directory
class TestFunctions(unittest.TestCase):
#    def setUp(self):
#        os.system("python3 create_index.py documents")
        
    #################### create_index tests ##############################
    
    #make sure all the words were inserted
    def test_correct_insert(self):
        c = connect()
        c.execute('''SELECT count(word_id) FROM instances''')
        self.assertEqual(c.fetchall()[0][0],49)
    
    #make sure idf score are being properely calculated
    #stem appears 6 times idf = log(49/6)
    def test_correct_idf_score(self):
        c = connect()
        c.execute('''SELECT idf FROM words WHERE word = "stem"''')
        self.assertEqual(c.fetchall()[0][0], 0)
    
    #make sure tf is correct
    #1 occurence in doc 3 of stem log(1) = 1
    def test_correct_tf_score(self):
        c = connect()
        c.execute('''SELECT tf FROM tf_score WHERE word_tf = "stem" AND doc_id = 3''')
        self.assertEqual(c.fetchall()[0][0], 1)
    
    #make sure tf is correct
    #3 occurences in doc 4 of stem log(3) = 1.4771212547196624  
    def test_correct_tf_score2(self):
        c = connect()
        c.execute('''SELECT tf FROM tf_score WHERE word_tf = "stem" AND doc_id = 4''')
        self.assertEqual(c.fetchall()[0][0], 1.4771212547196624)
        
    #################### print_index tests ###############################
    
    #check to make sure it gets all words and that the words are in 
    #alphabetical order
    def test_word_list(self):
        c = connect()
        list_word = get_word_list(c)
        self.assertEqual(list_word,[('a',),('at',),('be',),('bool',),('but',),('chop',),('end',),('in',),('increas',),('index',),('invok',),('low',),('nev',),('not',),('of',),('off',),('precid',),('process',),('query',),('recal',),('retriev',),('should',),('siz',),('stem',),('system',),('the',),('tim',),('vocab',),('whil',),('word',)])
        
    #make sure all instances are retrived and that they are in order
    def test_get_instances(self):
        c = connect()
        list_instances = get_instances(c,["stem",])
        self.assertEqual(list_instances, [(1, 6), (2, 6), (3, 1), (4, 1), (4, 14), (4, 20)])
        
    def test_get_instances(self):
        c = connect()
        list_instances = get_instances(c,["bool",])
        self.assertEqual(list_instances, [(1, 3), (2, 3)])
    
    #################### boolean_query tests #############################
    
    #quick check to make sure tokenizer works
    def test_simple_tokenize(self):
        self.assertEqual(tokenize("stemming"),"stem")
        
    #make sure captials are made lowercase in tokenizer
    def test_cap_tokenize(self):
        self.assertEqual(tokenize("Recalling"),"recal")
    
    #make sure the phrases are correctly calculated
    def test_phrase_evaluation(self):
        c = connect()
        self.assertEqual(eval_phrase(c, "boolean retrieval"), [1,2])
    
    #correctly gets postings list
    def test_single_word(self):
        c = connect()
        self.assertEqual(get_postings(c, tokenize("stemming")),[1,2,3,4])
     
    #different postings list check
    def test_single_word2(self):
        c = connect()
        self.assertEqual(get_postings(c, tokenize("Boolean")), [1,2])
    
    #correctly and two lists together
    def test_and_list(self):
        self.assertEqual(and_lists([1,2,3],[3,4,5]),{3})
    
  
    ################## vs_query tests ####################################
    #check if data prints with scores
    def check_output1(self):
        #print_values(weights, index_location, k, scores):
        self.assertEqual(print_values([(0.9, 1), (0.8, 2), (0.95, 3)], index_location, 3, True), ['3(0.95)', '1(0.9)', '2(0.8)'])
        
    #check if data prints without scores
    def check_output2(self):
    #print_values(weights, index_location, k, scores):
        self.assertEqual(print_values([(0.9, 1), (0.8, 2), (0.95, 3)], index_location, 3, True), [3, 1, 2])
    
    #If query not in db, doc values should be 0. In this case the query is 1 term: yrhvkdgveyejkdchfvjf
    #get_weights(c, index_location, k, scores, terms)
    def check_0_val(self):
        c = connect()
        self.assertEqual(get_weights(c, index_location, 3, True, yrhvkdgveyejkdchfvjf),[(0.0, 1), (0.0, 2), (0.0, 3), (0.0, 4)])
    
    
    
    
if __name__ == '__main__':
    os.system("python3 create_index.py documents")
    unittest.main()
