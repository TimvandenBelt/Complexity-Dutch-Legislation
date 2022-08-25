
# Paving A Path To Simplify Legislation Using AI
#### An empirical complexity analysis of the Dutch legislation

A master's thesis IT-Law at the University of Groningen

### Abstract
As we all are deemed to know the law, a simple and understandable law can be helpful.
However, to make law, more specifically, legislation, more simple and understandable, we must first determine the complexity of legislation. This paper adopts the methodology set out by Katz & Bommarito to define the complexity of the legislation.
They defined three features that increase the knowledge acquisition costs in a theoretical process of deciding to comply or not comply with a legal obligation.
These features are structure, interdependence and language. Each of these features consists of benchmarks, and each benchmark consists of measures, signifying the complexity of the feature. We used these benchmarks and measures along with our additions. Using their methodology, we successfully determined the complexity of the Dutch legislation. We added a Flesch reading ease score to improve the accuracy of determining the complexity of language. After that, we evaluated the usefulness of some measures by calculating the correlation between measures and the legislation's size. As a result, we suggest omitting some measures in future work, as we believe that measures growing along with the size of legislation are less practical for legislators to use in improving the quality of legislation. Based on these findings, we also adjusted the ranking composites set out by Katz & Bommarito. Lastly, we made some suggestions for future work to improve the process of determining the complexity and to assist the legislator better.

### Code base
The code is written in Python. For best compatability, a Docker environment is available.
All neccesary Python packages can be found in /src/requirements.txt
The code has only been tested with Python 3.9.

`main_extract.py` is the starting point as it extracts data from the research data (legislation).
`main_stats.py` and `main_rank.py` calculate statistics and ranks based on the procured data.
To draw a graph, use one of the `main_draw_*.py` files.

Some customizable variables are located in `variables.py`, although they are specific for the Dutch legislation.
`draw.py`, `calculations.py` and `extract.py` contain functions less suitable to have directly in the main files.  More should be in those files rather then in the main files, but that is a thing for the future.

Most of the logic resides in `Legal_node.py` and `Legislation.py`. They deal with extracting information from legislation and procuring/calculating the required results per legislation.