__author__ = 'Greg'

import os
import random
import string

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits)
    for x in xrange(32))