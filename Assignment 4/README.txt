# Running

To run main.py:
    python3 main.py [-r]

You may specify an optional flag, -r, which will rebuild the Whoosh index if it already exists.
Running main.py without the -r flag will only build the Whoosh index if it doesn't already exist.


# Query Session

NOTE:
    Building the index takes roughly 430 seconds on 4000 documents.

After the index has been loaded, a query session will begin.
The user can issue one of the following commands during the query session (case sensitive):
- 'CON' / 'AND': Change the query type to conjunctive (i.e. all query terms must appear in returned documents)
- 'DIS' / 'OR': Change the query type to disjunctive (i.e. either query term must appear in returned documents)
- 'LIM' <amount>: Set the limit on the number of returned results to specified amount.

All other user inputs will query the database and return the most relevant results.

To exit the program, send the interrupt signal (Ctrl+C on Windows/Linux; Cmd+. on Mac).

# Returned Results

Each returned result contains the following: title, URL, score, matched terms, and highlights.
The title and URL are the same as the stored title and URL of the HTML document.
The score is calculated using BM25, which is the default in Whoosh.
The matched terms are the query terms which appear in a given document.
Highlights show snippets of content surrounding the matched terms.