# Puts MODTRAN inputs into format required for tape5 file

def A(text, n):
    '''
    Re-formats the string 'text' to an n-length string, right-justified
    '''
    if type(text) != str:
        raise TypeError("Argument " + str(text) + " must be a string")
    L = len(text)
    if L > n:
        raise ValueError("Cannot re-format argument '" + text + "' to " + str(n) + "-length string")
    else:
        return ' ' * (n - L) + text


def I(integer, n):
    '''
    Re-formats an integer to an n-length string, right justified
    '''
    if type(integer) != int:
        raise TypeError("Argument " + str(integer) + " must be an integer")
    L = len(str(integer))
    if L > n:
        raise ValueError("Cannot re-format argument '" + str(integer) + "' to " + str(n) + "-length string")
    else:
        return ' ' * (n - L) + str(integer)


def F(number, n, d):
    '''
    Re-formats a number (integer or float) to an n-length string with d decimal places, right-justified
    '''
    if (type(number) != float and type(number) != int):
        raise TypeError("Argument " + str(number) + " must be a float or integer")
    num, dec = str(number).split('.')
    if len(dec) > d:  # truncate
        print("WARNING: truncating " + str(number) + " to " + str(d) + " decimal places")
    elif len(dec) < d:  # add trailing zeros
        dec += '0' * (d - len(dec))
    number_truncated = num + '.' + dec[:d]
    L = len(number_truncated)
    if L > n:
        raise ValueError("Cannot re-format argument '" + str(number) + "' to " + str(n) + "-length string " +\
                          "with " + str(d) + " decimal places")
    else:
        return ' ' * (n - L) + number_truncated