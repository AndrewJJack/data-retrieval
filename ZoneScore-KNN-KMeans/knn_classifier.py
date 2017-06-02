import sys
import sqlite3
import nltk
import os
import math
from collections import Counter

word_list = []
tup_list = []
num_docs = 0
doc_vectors = []
final_vectors = []

def tokenizer(terms):
    punctuation = [",",".",";","(",")","#","!","$","%","&","'","''","'s","—","–","[","]","{","}","|-","|", "\n"]
    st = nltk.stem.LancasterStemmer()
    words = nltk.word_tokenize(terms)

    words = [x for x in words if x not in punctuation]
    return words

def print_values(weights, k, c):
    k = int(k)
    weights.sort()
    list1 = []
    printlist = []
    #getting a list with all the k relevent genres
    for tup in weights:
        list1.append(tup[1])
    for i in range(0,k):
        printlist.append(list1.pop())

    genrelist = []
    #Getting the class for each element in printlist
    for i in printlist:
        c.execute('''SELECT class FROM instances WHERE doc_id = {}'''.format(str(i)))
        classval = c.fetchone()
        genrelist.append(classval[0])
    #http://stackoverflow.com/questions/3594514/how-to-find-most-common-elements-of-a-list
    #This code gets the most common word that is in the list, which is what the genre should be classified as
    most_common_words= [word for word, word_count in Counter(genrelist).most_common(1)]
    genre = most_common_words[0]

    print(genre)

def get_vector_length(c):
    #adds up the squares of all the tf values per document and then takes the squareroot to get the final normalized size.
    c.execute('''SELECT MAX(doc_id) from instances''')
    global num_docs
    num_docs = c.fetchone()
    num_docs = num_docs[0]
    for doc_id in range(1,num_docs+1):
        c.execute('''SELECT tf FROM tf_score
                    WHERE doc_id = {}'''.format(doc_id))
        #getting list of term frequencies for doc
        tflist = c.fetchall()
        global doc_vectors
        docid_tf = (doc_id,tflist)
        doc_vectors.append(docid_tf)

    for tup in doc_vectors:
        current_sum = 0
        #summing up all the squares of the tfs
        for tf in tup[1]:
            val = tf[0] * tf[0]
            current_sum += val
        #Taking the square root of the sum, and storing in a list as a tuple with docid followed by the length
        global final_vectors
        sqrtval = math.sqrt(current_sum)
        newtup = (tup[0],sqrtval)
        final_vectors.append(newtup)
        current_sum = 0
    return



def get_weights(c, k, terms):
#calculate the tf-idf weigths and store in the instances table
    scores = {}
    global num_docs

    for term in terms:
        #calculating w_t_q
        try:
            c.execute('''SELECT df FROM words
                 WHERE word = "{}"'''.format(str(term)))
        except:
            c.execute('''SELECT df FROM words
                 WHERE word = '{}' '''.format(str(term)))
        df = c.fetchone()
        wtq = 0
        if df is None:
            df = 1
            w_t_q = 0
        else:
            df = df[0]
            w_t_q = math.log(num_docs / df)

        for doc in range(1,num_docs+1):
            try:
                c.execute('''SELECT word, idf, tf, doc_id
                        FROM words, tf_score
                        WHERE word = "{}" AND doc_id = {} AND word = word_tf'''.format(str(term),doc))
            except:
                c.execute('''SELECT word, idf, tf, doc_id
                        FROM words, tf_score
                        WHERE word = '{}' AND doc_id = {} AND word = word_tf'''.format(str(term),doc))

            #storing info in a tuple
            tup = c.fetchone()
            #if the term isnt in the doc so the tf is 0.
            #if it doesnt return a tuple, the term isnt there so tf-idf is set to 0
            if tup is None:
                tf_idf = 0
            #multiplying idf and tf together to get tf-idf
            else:
                idf = tup[1]
                tf = tup[2]
                tf_idf = idf * tf

            if doc in scores:
                scores[doc] += tf_idf * w_t_q
            else:
                scores[doc] = tf_idf * w_t_q
    answer = []

    for doc in scores:
        answer.append((scores[doc]/final_vectors[doc-1][1], doc)) #/ by length
    return answer

def connect():
    #starts connection with inverted index
    try:
        conn = sqlite3.connect("labeled_index.db")
        c = conn.cursor()
    except:
        print("Connection failed")
        exit()
    return c
 
def main():

    try:
        #open database
        try:
            index_directory = sys.argv[1]
        except:
            print("No index directory given")
            exit()
        try:
            file_list = os.listdir(index_directory)
        except Exception as e:
            print("Index directory doesn't exsist")
            exit()

        os.chdir(index_directory)
        conn = sqlite3.connect("labeled_index.db")
        c = conn.cursor()

        #get k
        k = sys.argv[2]
        #scores = True

        #open file
        #opening directory
        try:
            doc_name = sys.argv[3]
        except:
            print("No document directory given")
            exit()
        #try to open the file
        try:
            working_file = open(str(doc_name), 'r')
        except Exception as e:
            print(e)
            print("File doesn't exsist")
            exit()

        #read document
        try:
            file_contents = working_file.read()
            working_file.close()
            terms = tokenizer(file_contents)
        except Exception as e:
            print(e)
            print("File not readable")

        #Getting euclidian vector distance for each doc and storing values in a list called final_vectors
        get_vector_length(c)
        #getting the answer
        weights = get_weights(c, k, terms)
        #printing the answers
        print_values(weights, k, c)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        #print("Invalid input")
        exit()

if __name__ == '__main__':
    main()
