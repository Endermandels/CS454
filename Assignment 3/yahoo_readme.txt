Dataset: anonymized_ysearch_logs_relevance_judgements-v1_0

One month of click logs from Yahoo! search along with editorial judgments.

=====================================================================
This dataset is provided as part of the Yahoo! Webscope program, to be
used for approved non-commercial research purposes by recipients who 
have signed a Data Sharing Agreement with Yahoo!. This dataset is not
to be redistributed. No personally identifying information is available
in this dataset. More information about the Yahoo! Webscope program is
available at http://research.yahoo.com

=====================================================================

Full description:

The dataset contains two parts:
 1- One month of search logs in July 2010. Each record contains an anonymized version of a user cookie, query, 10 displayed urls as well as the positions of the user clicks
 2- Relevance judgments collected in 2009 and 2010.
The two datasets are joined and the search logs contain only records for which at least 3 urls have been judged. 

=====================================================================

---- Search logs

File: search_logs-v1.txt

Each record is a search result page, whose format is as follows:
   query cookie timestamp url_1 ... url_10 nc et_1 pos_1 et_2 pos_2 ... et_nc pos_nc
where,
   - query is an anonymized version of the query
   - cookie is an anonymized version of the user cookie 
   - timestamp is the unix time of when the query was issued
   - url is an anonymized version of the url
   - nc is number of clicks during that session
   - et is the elapsed time between the click and the query timestamp
   - pos is the position of the click. It can be:
       + 1 ... 10: one of the ten ulrs
       + 0:  a click above the first url, such as: also-try, spelling suggestion, north ad, direct display, etc.
       + 11: a click below the last url, such as: next page, bottom also-try, south ad, bottom direct display, etc.
       + s: click on the search button (new query)
       + o: other click

Snippet: 
  00002efd        1deac14e        1279486689      2722a07f        24f6d649        1b2b5a1c        9ca4edf1        23045132        84c0d8b5        de33d1de        9f5855b2        477aabf6        e1468bbf        3       10      1       175     o       215     0

The search logs are joined with the relevance judgments and the data contains only the search result pages for which at least three urls are judged. Also, there is a maximum of 10,000 result pages per query. 
The data consists in the end of around 81M result pages and 67k queries.

---- Relevance judgments

The data consists of 659k editorial judgments collected in 2009 and 2010. Each of the (query, url) pair appears at least once in the logs. The number of queries is thus the same as in the search logs, 67k.

Format:
   query url judgment
where
   - query and url are anonymized in the same way as in the search logs.
   - judgment is an integer from 0 (bad) to 4 (perfect).

Snippet:
  00002efd        1b2b5a1c        1

=====================================================================

The Python script cascade.py is meant to be a simple example of how to parse the click logs. 
It computes the attractiveness of a query,url according to the cascade model.

=====================================================================

Contact and questions: Olivier Chapelle (chap@yahoo-inc.com)
