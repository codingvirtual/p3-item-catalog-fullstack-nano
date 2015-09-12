## Full-Stack Nanodegree: Project 3 - Catalog App


#### CONTENTS ####

-A- Project Details
        Application Overview
        Requirements
-B- Prerequisites
-C- Project Files
-D- Installation/Use
-E- Customizing the Application
-F- Known Issues


#### -A- PROJECT DETAILS ####

Application Overview
####################

This application is a Python-based web application that offers a simplistic
catalog driven by a Postgres database on the backend. The application allows
anyone to see the categories and items in the database. Additionally, if
the user logs in using a Google Plus login, they can also modify the data
in the database such as adding, editing, and deleting categories in the database
as well as adding, editing, and deleting items within each category.

The application as provided comes with a small set of data already included
in the catalog.db database file. In actual use, you would want to delete this
file and build your own initial data file. See the section on Installation/Use
for more details on this.


Requirements
###########################

The following project requirements are defined by the Udacity project rubric
that was provided for the project.

Specifications (minimum required functionality)
1.  Page does implement an JSON endpoint with all required content.
2.  Page does read category and item information from a database.
3.  Page does include a form allowing users to add new items and correctly 
    processes submitted forms.
4   Page does include a function to edit/update a current record in the database 
    table and correctly processes submitted forms.
5.  Page does include a function to delete a current record.
6.  Page does implement a third-party authentication & authorization service; 
    and create, delete and update operations do consider authorization status 
    prior to execution.
7.  Code is ready for personal review and neatly formatted.
8.  Comments are present and effectively explain longer code procedures.
9.  A README file is included detailing all steps required to successfully 
    run the application.
    

#### -B- PREREQUISITES ####
In order to run this application on your machine, there are a number of
prerequisites that must be met:
a)  You must have the Postgres database system installed on your machine
b)  You must have Python 2.x to run the code. It was developed on 2.7, but
    may or may not work on other versions.
c)  You must have the Flask microframework installed including the Jinja2
    templating engine (which is included by default).
    See http://flask.pocoo.org for more details on Flask and Jinja.
d)  You must have the SQLAlchemy extension for Flask installed on your machine.
e)  For the site to render correctly, you must have an active Internet connection
    as the site makes heavy use of the Bootstrap framework and loads it
    dynamically via content delivery networks rather than prepackaging it.
    You will also need the Internet connection to be able to log in
f)  If you want to log in, you will also need a Google account to sign in with.
    Only your id and name are extracted from Google - no other data is used.


#### -C- PROJECT FILES ####

Within the project files you will find the following:
a)  At the top level of the project you will find this README.md file as well
    as the run.py file (the main file used to launch the application) and a
    config.py file that contains a handful of configuration settings.
b)  The catalog_main directory is a Python package containing the core of the
    application and sub-packages containing various components of functionality.
    The app itself is defined in the __init__.py file.
c)  The mod_catalog package contains the core code for the logic of the app
    (within controllers.py) as well as the models.py file that contains the
    object models for the Category and CategoryItem objects in the database.
    This allows object-relational mapping between the database and Python
    objects.
d)  The mod_db subdirectory contains the database schema (database_setup.py)
    and a file that can be used to populate the database with an initial load
    of data (populate_db.py).
e)  The static subdirectory contains static files, in this case only a css
    subdirectory and the styles.css file for site styling.
f)  The templates subdirectory is used by the Jinja2 templating system and
    the app to render the site's pages properly. Within the catalog subdirectory,
    there are templates for major function point in the application and each 
    template is heavily commented to explain its use. The base.html template is 
    the core page template that all the others inherit from and contains the 
    main HTML code that doesn't change from page to page.
    Loose within the templates subdirectory is also the 404.html file which
    is displayed when the user attempts to reach a page that doesn't exist.
    Feel free to customize this file to suit your requirements for "page not
    found" errors.
    
    
#### -D- INSTALLATION/USE ####

To INSTALL this application, follow these steps:
a)  First, make sure your machine meets all of the prerequisites described above.
    If you are missing necessary libraries or elements, it is up to you to
    seek them out, install them, and validate their proper use. It is beyond
    the scope of this document to try to explain all of that.
b)  Download the project to your computer into an appropriate directory. That
    can mean different things on different platforms, so interpretation is
    up to you. You can use git clone to pull down the entire project or use
    Github's app or "Download ZIP" options to pull it down.
c)  CRITICAL: you will need to create a developer account with Google and
    then create a project to associate with this project. The reason for this
    is that a "client secret" is needed to enable the Google+ authentication
    to work and you get that by creating a project. See the relevant docs
    at Google's developer pages and the Google Developer Console to get that
    set up. Once set up, you will need to download the client_secrets.json
    file and save it to your machine ONE LEVEL UP from the project root (said
    another way, it must be 2 levels up from run.py).
    The file containing the secret must be named client_secrets.json or the 
    app will not find it to load it.

    
To RUN this application, follow the above installation steps and then:
a)  Once you have the project installed, go to a command line and "cd" into
    the directory containing the project root, then cd into the "catalog"
    directory (which is the project root itself).
b)  Now just type this followed by the return key to launch the application.
    python run.py
c)  Once launched, point your browser to http://localhost:8000 to see the
    application and use the various pages in the app.
    

    
#### -E- CUSTOMIZING THE APP ####

The principle customizations that one would consider making to the app would
involve the initial populating of the database with categories and items so
that when the app was first launched, there is at least one category and
one item in the database.

To reset the database to empty and populate it with your own initial set of
data, you must perform the following steps:

a)  Delete the catalog.db file that came with the project. It's located inside
    the catalog_main package, then inside the mod_db subdirectory.
b)  In that same subdirectory, you will find a file named populate_db.py
    Open this file into your favorite text editor and make the appropriate
    changes to what is already there. The comments at the top explain how
    you can change it and there is a clear indicator of where your modifications
    should go. The existing code that created the catalog.db file is there and
    well-commented so you can easily modify what's there and copy/paste more
    iterations as needed. If you have the Python skill, you could also adapt
    it further to read the info from some other sort of file, but that's well
    beyond the scope of this document and is an exercise for you to undertake
    on your own.
        
        
#### -F- KNOWN ISSUES ####

The app has very minimal error checking and catches only basic errors and 
problems. As such, it should not be considered a secure app and more should
be done to improve the overall security of the app, specifically around the
way that buttons are shown (using only CSS to "hide" them).

If you delete a category, the system is presently set up to automatically
delete all the child items of that category. That may NOT be the behavior
you desire. If you wish to change the code to handle this differently, you
will need to change the models.py file in mod_catalog:

Replace this line:
category = relationship(Category, backref=backref("items", cascade="all"))

With this:
category = relationship(Category)  
   
and then make the appropriate additional code modifications in controllers.py
within the catDelete() function.

Finally, I made some attempt to split the app up into logical packages but have 
not had much success getting it to work, hence the current state. More could be 
done to improve the code structure and separation of concerns.


