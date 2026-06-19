## Problem Statement

### Description
Given Random Numbers are [-1, 0, 1, 2, 3] and Probabilities are [0.01, 0.3, 
0.58, 0.1, 0.01] if we call nextNum() 100 times, we may get the following 
results. As the results are random, these particular results are unlikely.

```text
-1: 1 times
0: 22 times
1: 57 times
2: 20 times
3: 0 times
```

### Requirements

 - Write a random number generator that returns numbers based on the 
   probabilities provided.
 - Implement the method nextNum() and a minimal but effective set of unit tests.
 - Implement in the language of your choice, Python is preferred, but Java and 
   other languages are completely fine.
 - Make sure your code is exemplary, as if it was going to be shipped as part 
   of a production system.

You may use random.random() which returns a pseudo random number between 0 
and 1. 

```python
import random

class RandomGen(object):
  
  # Values that may be returned by next_num()
  _random_nums = []
  
  # Probability of the occurrence of random_nums
  _probabilities = []
  
def next_num(self):
    """
    Returns one of the randomNums. When this method is called multiple
    times over a long period, it should return the numbers roughly with
    the initialized probabilities.
    """
    pass 

```