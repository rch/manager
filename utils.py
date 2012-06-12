from uuid import uuid4
"""
Base36 Encoder/Decoder
by Mike Crute (mcrute@gmail.com) on August 26, 2008
This code has been placed in the public domain.

This is just a simple module to do base36 encoding and decoding. Theoretically
you could use this for any base < 2 <= 36 && base != 32 but I only really need 
to have base36 so its an exercise for the reader to implement other base 
conversions.

This won't work for base32 at least not if you want your output to work with other
base32 decoders because RFC4648 skips 0 and 1 (2-7A-Z) and this module doesn't
account for that. Bah...

The only reason I wrote this is because the other implementations of base
conversion relied upon hard coded lists of characters and that really 
bothered me, plus didn't quite give me the flexibility I was looking for.
"""

def uuid36(str_in=None, base_from=10, base_to=36):
    """Convert a number to/from a base less than or equal to 36.
    Converts a string or number to or from a base without using static
    lookup tables.
    """
    # init if needed
    if str_in is None:
        str_in = str(uuid4().int)

    # Some ASCII Codes
    ASCII = { "0": 48, "9": 57, "A": 65, "Z": 90 }
    #
    # There are 8 characters between 9 and A
    from_digits = [chr(x) for x in range(ASCII["0"], ASCII["9"] + 8 + base_from) 
                            if (x >= ASCII["0"] and x <= ASCII["9"]) or 
                               (x >= ASCII["A"] and x <= ASCII["Z"])][:base_from]
    #                          
    to_digits = [chr(x) for x in range(ASCII["0"], ASCII["9"] + 8 + base_to) 
                            if (x >= ASCII["0"] and x <= ASCII["9"]) or 
                               (x >= ASCII["A"] and x <= ASCII["Z"])][:base_to]
    #
    x = long(0)
    for digit in str(str_in).upper():
        x = x * len(from_digits) + from_digits.index(digit)
    #
    result = ""
    # This is going to assemble our number in reverse order
    # so we'll have to fix it before we return it
    while x > 0:
        result += to_digits[x % len(to_digits)]
        x /= len(to_digits)
    #    
    return result[::-1]
