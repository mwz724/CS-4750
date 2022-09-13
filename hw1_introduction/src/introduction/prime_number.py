def is_prime_number(n):
    assert(isinstance(n, int), "Did you cast to int in Q1.2?")
    """Return whether given integer is a prime_number.

    >>> is_prime_number(9)
    False
    >>> is_prime_number(2011)
    True

    """
    # BEGIN QUESTION 1.1s
    
    if n == 0 or n == 1 or n < 0: # special cases: 0, 1, negative #s
    	return False
  
    	
    for i in range(2, n): # [2, n), if there's a factor other than 1 and n
        if n%i == 0:
            return False;
           
    return True; # code will only reach here if no divisors
    
    # END QUESTION 1.1
