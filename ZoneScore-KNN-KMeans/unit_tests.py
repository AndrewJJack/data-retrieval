import unittest
import os

from knn_classifier import *
from k_means_clusterer import *
from zone_scorer import *
from zone_scorer import tokenize as zone_scorer_tokenize
from knn_classifier import tokenizer as knn_classifier_tokenizer
from knn_classifier import get_weights as knn_classifier_get_weights
from knn_classifier import get_vector_length as knn_classifier_get_vector_length

class TestFunctions(unittest.TestCase):

    ################### knn_classifier #######################
    def test_punctuation_tests(self):
        #making sure our tokenizer is getting rid of punctuation, and 'apostrophe s'
        term = "$hello mak's!"
        tokenized = knn_classifier_tokenizer(term)
        self.assertEqual(tokenized, ['hello', 'mak'])

    def test_weight_check(self):
        #make sure that this term isnt in any txt files
        c = for_testing()
        knn_classifier_get_vector_length(c)
        weights = knn_classifier_get_weights(c, 1, "alsdfkja;lsdkjf;alskjd")
        self.assertEqual(weights, [(0.0, 1), (0.0, 2), (0.0, 3), (0.0, 4), (0.0, 5), (0.0, 6), (0.0, 7)])

    def test_compare_docs(self):
        c = for_testing()
        get_vector_length(c)
        doc1 = 1
        doc2 = 2
        similarity = compare_doc(doc1, doc2, c)
        self.assertEqual(similarity, 0.8211596545039014)

    ################### k_means clusterer ####################
    
    #test to make sure it correctly gets all docs from corpus
    def test_get_docs(self):
        c = for_testing()
        doc_list = get_docs(c)
        self.assertEqual(doc_list, [2, 1, 6, 5, 7, 3, 4, 0]
)
     
    #test to make sure it correctly gets one group (should return all docs)
    def test_get_grouping(self):
        c = for_testing()
        doc_list = get_docs(c)
        get_vector_length(c)
        group_return = get_groups(doc_list, [3],c)
        self.assertEqual(group_return, {3: [2, 1, 6, 5, 7, 3, 4, 0]}
)
    
    #test to make sure it correctly gets multiple groups
    def test_get_multiple_groups(self):
        c = for_testing()
        doc_list = get_docs(c)
        get_vector_length(c)
        group_return = get_groups(doc_list, [3,4],c)
        self.assertEqual(group_return, {3: [2, 1, 6, 5, 3], 4: [4, 6, 7]})


    ################### zone_scorer ##########################
    def test_unique_title_body(self):
        #This test is to make sure that it gives different scores to q terms that are only in the title or the body
        score = zoneScore(0.6, ['hello'], ['cat', 'dog'], ['hello'])
        #since dog and cat are in the title and g = 0.6, they should be 0.6 and hello is in the body so it should be 0.4
        self.assertEqual(score, {'dog': 0.6, 'cat': 0.6, 'hello': 0.4})

    def test_title_and_body(self):
        #This test makes sure that if it is in the title and body its score is 1
        score = zoneScore(0.6, ['hello'], ['cat', 'dog', 'hello'], ['hello'])
        self.assertEqual(score, {'dog': 0.6, 'cat': 0.6, 'hello': 1.0})

    def test_tokenizer_test(self):
        term = zone_scorer_tokenize("mans")
        self.assertEqual(term, "man")




if __name__ == '__main__':
    unittest.main()
