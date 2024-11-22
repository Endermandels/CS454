# Running

In order to run the main file, three steps must be completed first:
    Build Adjacency Dict
    Build Adjacency Matrix
    Calculate PageRank Scores

## Build Adjacency Dict

    python3 build_adj_matrix.py -d

## Build Adjacency Matrix

    python3 build_adj_matrix.py -m

## Calculate PageRank Scores

    python3 page_rank.py

## Run Main

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
Results are ranked using PageRank.

To exit the program, send the interrupt signal (Ctrl+C on Windows/Linux; Cmd+. on Mac).

# Returned Results

Each returned result contains the following: URL, Score
By default, Whoosh stops on words such as 'a', 'the', 'and', etc.