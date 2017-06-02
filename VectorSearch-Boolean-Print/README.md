

## LICENSE

[CC Zero](https://wiki.creativecommons.org/wiki/Public_domain)

All code is created with python3 and implements sqlite3

* Put the corpus directory in same directory as programs
* inverted index is created in the same directory as programs

###### create_index 

* assumes the directory with files is in the same directory as the create_index file
* to run example **create_index.py documents**
* takes roughly 2 minutes to create inverted index on 2000 test files from eclass 
* Uses nltk for  tokenization and stopwords
* need to have nltk/corpora/stopwords and nltk/models/punkt downloaded from nltk.download()
* tokens are stemmed using lancaster stemmer
* when index is created it also computes the tf and idf scores to be used with the vector space model
* the inverted index database file is created in the same directory as the create_index.py file

###### print_index
* assumes the database file is in the same directory as the print_index file
* example to run **python3 print_index.py**

###### boolean_query
* IMPORTANT: **() do not work on the command line use [] for brackets instead**
* assumes the database file is in the same directory as the boolean_query file
* run using **python3 boolean_query query**
* example **python3 boolean_query time OR [precision AND while]**

###### vs_query
* assumes the database file is in the same directory as the vs_query file
* to calculate the euclidian length the square root of the sum of the squares of all the tf values for a particular document is used
* uses a stemmer, so the values might be different
* the algorithm is roughly based off of the sample program vector_space_model.py in starter!!!
* example to run **python3 vs_query.py index_location 4 y recall**

###### testing
* **do not delete documents folder because the test files use it for testing** 
* run unit tests by running the unit_tests.py file
* example to run **python3 unit_tests.py**
* will run all the tests for all of the different files
