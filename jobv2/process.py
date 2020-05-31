import csv
import json
import os, sys
from flask import Flask
import json
import pandas as pd
import numpy as np
import re
import nltk
import gensim
from nltk.tokenize import word_tokenize, sent_tokenize
import time


app = Flask(__name__)
app.config["DEBUG"] = True


jobs = pd.read_csv("monster_com-job_sample.csv")
jobs = (jobs.drop(["job_board", "has_expired","date_added", "country", "country_code", "job_type","page_url","salary","sector","uniq_id"],
      axis='columns'))
jobs=jobs[jobs['location'].apply(lambda x: len(x)<20)]
jobs=jobs.dropna()
jobs=jobs.iloc[:10000]
p = re.compile(r'[^\w\s,.#:]+')
jobs['job_description'] = [p.sub('', x) for x in jobs['job_description'].tolist()]

def get_data():
    data=jobs.to_dict('records')
    return data


def preprocess_jobs(file1):
       file_docs=[]
       for val in file1:
             file_docs.append(val[0])

       #Tokenize words and create dictionary

       gen_docs = [[w.lower() for w in word_tokenize(text)]
            for text in file_docs]

       dictionary = gensim.corpora.Dictionary(gen_docs)
       dictionary.save('workdir/dictionary.index')
      #  with open('data.txt', 'w') as outfile:
      #         json.dump(dict(dictionary), outfile)

       #Create a bag of words
       corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]


       #TFIDF
       tf_idf = gensim.models.TfidfModel(corpus)
       tf_idf.save('workdir/tf_idf.index')

       #Creating similarity measure object
       sims = gensim.similarities.Similarity('workdir/',tf_idf[corpus],
                                        num_features=len(dictionary))
       print(sims)

       sims.save('workdir/jobs.index')


def compareresumejob(file1,file2_docs):
       sims = gensim.similarities.Similarity.load('workdir/jobs.index')

       dictionary=gensim.corpora.Dictionary.load('workdir/dictionary.index')

       tf_idf = gensim.models.TfidfModel.load('workdir/tf_idf.index')

       #Create Query Document

       query_doc = [w.lower() for w in word_tokenize(file2_docs)]
       query_doc_bow = dictionary.doc2bow(query_doc)


       query_doc_tf_idf = tf_idf[query_doc_bow]
       print('Comparing Result:', sims[query_doc_tf_idf])
       final=[]
       index=1

       for val in sims[query_doc_tf_idf]:
             if val>0.1:
                  final.append(int(index))
             index+=1

       print(len(final),len(sims[query_doc_tf_idf]))
       return final

###########################################
