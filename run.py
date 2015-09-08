__author__ = 'Greg'

# Entry point for this application.
# Import the main app code
from catalog_main import app

# run the code on port 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)