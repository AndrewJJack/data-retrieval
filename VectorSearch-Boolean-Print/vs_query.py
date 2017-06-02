import sys
import sqlite3
import nltk
import os
import math

word_list = []
tup_list = []
num_docs = 0
doc_vectors = []
final_vectors = []

def tokenizer(terms):
    newlist = []
    for term in terms:
        st = nltk.stem.LancasterStemmer()
        stemmed_word = st.stem(term)
        newlist.append(stemmed_word)
    return newlist
        
def print_values(weights, index_location, k, scores):
    k = int(k)
    weights.sort()
    list1 = []
    printlist = []
    #if score == n than dont print the scores
    if not scores:
        for tup in weights:
            list1.append(tup[1])
        for i in range(0,k):
            printlist.append(list1.pop())
        print(printlist)
    #otherwise print the scores
    else:
        for i in range(0,k):
            value = weights.pop()
            string1 = str(str(value[1])+'('+str(value[0])+')')
            printlist.append(string1)
        print(printlist)
            

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

    

def get_weights(c, index_location, k, scores, terms):
#calculate the tf-idf weigths and store in the instances table 
    scores = {}
    global num_docs

    for term in terms:
        #calculating w_t_q
        c.execute('''SELECT df FROM words
                 WHERE word = {}'''.format(str("'"+term+"'")))
        df = c.fetchone()
        wtq = 0
        if df is None:
            df = 0
            w_t_q = 0
        else:
            df = df[0]
            w_t_q = math.log(num_docs / df)
        
        for doc in range(1,num_docs+1):
            c.execute('''SELECT word, idf, tf, doc_id 
                        FROM words, tf_score
                        WHERE word = {} AND doc_id = {} AND word = word_tf'''.format(str("'"+term+"'"),doc))
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
        conn = sqlite3.connect("inverted_index.db")
        c = conn.cursor()   
    except:
        print("Connection failed")
        exit()
    return c
    
def main():
    #try:
        #creating connection to db
    c = connect()
    num_args = len(sys.argv)
    #print(num_args)
    index_location = sys.argv[1]
    k = sys.argv[2]
    scores = True
    if sys.argv[3] == 'n':
        scores = False
    #getting query terms
    terms = []
    terms = sys.argv[4:num_args]
    terms = tokenizer(terms)
    #Getting euclidian vector distance for each doc and storing values in a list called final_vectors
    get_vector_length(c)
    #getting the answer
    weights = get_weights(c, index_location, k, scores, terms)
    #printing the answers
    print_values(weights, index_location, k, scores)
    #except:
        #print("Invalid input")
        #exit()
	
	
if __name__ == '__main__':
    main()