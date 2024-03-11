import search_frontend
from inverted_index_gcp import *
import math
import re
from nltk.corpus import stopwords
from collections import defaultdict
import heapq

english_stopwords = frozenset(stopwords.words('english'))
RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)
corpus_stopwords = ['references', 'category', 'also', 'may', 'known', 'including', 'made', 'count', 'since', 'would',
                    'many', 'new', 'however', 'links', 'external', 'see', 'thumb', 'who', 'what', 'when', 'is', 'the',
                    'of', 'did']
all_stopwords = english_stopwords.union(corpus_stopwords)

inverted_title = InvertedIndex()
inverted_body = InvertedIndex()
index_body = inverted_body.read_index('postings_gcp', 'index_body', 'bucket_207547183_body')
index_title = inverted_title.read_index('postings_gcp', 'index_title', 'bucket_207547183_title')


def tokenize(text):
    """
    This function aims in tokenize a text into a list of tokens. Moreover, it filter stopwords.
    Parameters:
    -----------
    text: string , represting the text to tokenize.
    Returns:
    -----------
    list of tokens (e.g., list of tokens).
    """
    tokens = [token.group() for token in RE_WORD.finditer(text.lower())]
    tokens_no_stop = [token for token in tokens if token not in all_stopwords]
    return tokens_no_stop


def BM25_score_and_idf(index_read, query, str_index, weight):
    k1 = 1.5
    b = 0.75
    scores = defaultdict(float)

    sum_of_len_index = sum(index_read.doc_len.values())
    avg_doc_length = sum_of_len_index / len(index_read.doc_len)

    for term in query:
        if str_index == 'body':
            post_lst = index_body.read_a_posting_list('.', term, 'bucket_207547183_body')
        else:
            post_lst = index_title.read_a_posting_list('.', term, 'bucket_207547183_title')

        x = len(index_read.doc_len) - index_read.df[term] + 0.5
        y = index_read.df[term] + 0.5
        idf_body = math.log((x / y) + 1)

        for doc_id, tf in post_lst:
            mone = (k1 + 1) * tf
            B = 1 - b + b * (index_read.doc_len[doc_id] / avg_doc_length)
            machene = k1 * B + tf

            bm25_score = idf_body * (mone / machene)
            scores[doc_id] += bm25_score * weight

    return scores


def search_second(dict_search, pagerank_scores):
    # Combine BM25 and PageRank scores
    combined_scores = defaultdict(float)
    for doc_id, bm25_score in dict_search.items():
        pagerank_score = pagerank_scores.get(int(doc_id), 0.0)
        combined_scores[doc_id] = 0.6 * bm25_score + 0.4 * math.log(pagerank_score)
    return combined_scores


def search_third(query, index_body, index_title, pagerank_dict, doc_title_dict):
    # final search
    tokens = tokenize(query)
    body_top = {}
    title_top = {}
    if len(tokens) <= 1:
        title_top = BM25_score_and_idf(index_title, tokens, 'title', 1)
    elif 1 < len(tokens) <= 3:
        body_top = BM25_score_and_idf(index_body, tokens, 'body', 0.4)
        title_top = BM25_score_and_idf(index_title, tokens, 'title', 0.6)
    elif len(tokens) >= 4:
        body_top = BM25_score_and_idf(index_body, tokens, 'body', 1)
    body_top.update(title_top)
    combined_scores = search_second(body_top, pagerank_dict)  # return combined pagerank and BM25 (title+body)
    top = get_top_n(combined_scores)  # sort and return top 100 docs
    merged_list = merge_dicts(top, doc_title_dict)
    return merged_list


def merge_dicts(doc_score_dict, doc_title_dict):
    # merge doc_id with title (no need to show score)
    merged_list = [(str(doc_id), doc_title_dict.get(doc_id, "Unknown Title")) for doc_id in doc_score_dict]
    return merged_list


def get_top_n(dirug):
    # Use heapq.nlargest to directly get the top N items
    top_n_list = heapq.nlargest(100, dirug.items(), key=lambda item: item[1])
    # Create a dictionary from the top 100 list
    top_n_dict = {key: value for key, value in top_n_list}
    return top_n_dict
