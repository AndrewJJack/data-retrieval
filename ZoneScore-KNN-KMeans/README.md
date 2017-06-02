

## LICENSE

[CC Zero](https://wiki.creativecommons.org/wiki/Public_domain)

All code is created with python3

#### Zone Scoring
###### Create zone index
* **run with command** python3 create_zone_index.py [document dir path] [index dir path]
* **example** python3 create_zone_index.py /home/jordan/Documents/Git/zone_data /home/jordan/Documents/Git/zone_data

created a db file called zone_index.db in the index directory

###### Zone Scorer
* **run with command** python3 zone_scorer.py [index dir] [k] [g] [q]
* **example** python3 zone_scorer.py /home/jordan/Documents/Git/zone_data 5 .4 ["professor has" AND logan]

Queries use square brackets "[" instead of round brackets "("
Couldn't get the multiple line queries to work so query must be on one line

#trimming 'AND' and 'OR' terms. trimming code built on from http://stackoverflow.com/questions/2793324/is-there-a-simple-way-to-delete-a-list-element-by-value

    q = [x for x in q if x != 'AND']
    q = [x for x in q if x != 'OR']

#### Document Classification
###### Create Labeled Index
* **run with command** python3 create_labeled_index.py [document dir path] [index dir path]
* **example** python3 create_labeled_index.py /home/ajack/Documents/Git/class_data /home/jordan/Documents/Git/class_data

creates a file called labeled_index.db in the index directory

###### KNN Classifier
* **run with command** python3 knn_classifier.py [index dir path] [k] [document path]
* **example** python3 create_labeled_index.py /home/ajack/Documents/Git/class_data 20 /home/jordan/Documents/Git/class_data/0.txt

returns the classification of the document

#http://stackoverflow.com/questions/3594514/how-to-find-most-common-elements-of-a-list
#This code gets the most common word that is in the list, which is what the genre should be classified as
#It was built on from the following link
most_common_words= [word for word, word_count in Counter(genrelist).most_common(1)[]]


#### Document Clustering
###### Create Index
* **run with command** python3 create_index.py [document dir path] [index dir path]
* **example** python3 create_index.py /home/ajack/Documents/Git/cluster_data /home/jordan/Documents/Git/cluster_data
Creates index called inverted_index.db

###### K Means Clusterer
* **run with command** python3 k_means_clusterer.py [index dir path] [k] [optional seeds]
* **example** python3 create_index.py /home/ajack/Documents/Git/cluster_data 5 1 2 3 4 5

returns clusters on seperate lines
takes about 30 seconds to a minute to finish with 40 documents

###Running Test Cases
* **run with command** python3 unit_tests.py
Dont remove test_index.db
