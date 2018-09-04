# Line Server

## How the line server operates
This line server works by utilizing a LRU cache to store whole file or parts of
(if the entire file will not fit in memory) in order to serve the lines
effectively. This was chosen to allow for files that are too large to fit into
memory to be served without making a separate copy or chunking them manually
while still having very little overhead for files that will fit entirely into
memory.

The cache is set up to have similarly sized blocks based on memory usage
not by line count. This prevents a few very long or very short lines from
causing wasted space in the cache. The cache is loaded by memory-mapping the
source file and creating an index that keeps track of where in the file
(memory location) each line starts and ends.

### Main Risks
There is still a risk if there is a line that is too large to fit into a block,
but would fit into memory by itself. This is not addressed in this version of
the line server but can be ameliorated by destroying the cache, loading the
relevant line, then rebuilding the cache as needed.

## System Performance
Server correctness was confirmed by generating a file (using utilities/file_gen.py)
that outputs lines that correspond to the SHA256 hash value of the line number.
This allows for random reads that can easily be confirmed (rather than having
an identical file stored in memory).

The system performance was tested using Locust (locust.io) in order to simulate
1000s of users at a single time.

### File Size
The system performs well with several different sized

### User Count


## Documentation and Libraries Used
The main libraries and corresponding documentation used were:
Flask - web Server
Pytest - testing
MMap - supports memory-mapped files
LRU-dict - a LRU cache library implemented in C


## Time Spent and Future Improvements
I spend a couple of hours (unsure of the exact time) developing the line server.
I have had experience using the testing tools before which helped (also why the
server is implemented in Python).

The main future improvements for the single-node performance would be utilizing a "proper"
web-server (versus Flask), as well as simply adding more RAM (ie increase the
available cache size) to the machine that is running the server as that is the
main performance bottleneck. This could be a combination of Gunicorn, and Nginx
or something similar. Another improvement could be an optimization mode which
would determine (based on average use-cases) the block size and number of blocks
for the cache. The first version is simply "reasonable" numbers for both of
those values. For example, if locality is shown to be in high use (ie queries
for lines 1-10000 in a row) then fewer but larger blocks would probably be beneficial.
On the other hand, if there are a large number of diverse random reads, then a
more but smaller blocks might be better.

If the demand was high enough to warrant a larger change, a multi-node setup
could be developed. This could involve a load-balancer, and several workers
with multiple copies of the data between them.


## Code critiques
