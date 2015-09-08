__author__ = 'Greg'

import random
import string
import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# # Enable protection against *Cross-site Request Forgery (CSRF)*
# CSRF_ENABLED = True
#
# # Use a secure, unique and absolutely secret key for
# # signing the data.
# CSRF_SESSION_KEY = "secret"
#
# # Secret key for signing cookies
# SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                      for x in xrange(32))
#
# CSRF_SESSION_KEY = "secret"