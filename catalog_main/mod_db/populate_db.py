# Simple program that can pre-populate the database with a few categories
# and items. This file should only be used for testing purposes.
# You can customize this file by changing the content below starting at
# the section divider labeled "BEGIN CUSTOMIZATION HERE" using the provided
# code as a guide for how to construct categories and items.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, CategoryItem

engine = create_engine('sqlite:///catalog_main/mod_db/catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#################################################
#                                               #
#       BEGIN CUSTOMIZATIONS HERE               #
#                                               #
#################################################

# create a category
category1 = Category(name="Snowboarding")

# add it to the database
session.add(category1)

# create an item "under" the above category
item1 = CategoryItem(title="Goggles", description="Some Goggles", category=category1)

# add it to the database
session.add(item1)

# create a second category
category2 = Category(name="Soccer")

# add it to the database
session.add(category2)

# create a second item "under" the 2nd category just above
item2 = CategoryItem(title="Ball", description="A Soccer Ball", category=category2)

# add it to the database
session.add(item2)

#################################################
#                                               #
#       STOP CUSTOMIZATIONS HERE                #
#                                               #
#################################################

session.commit()

# print a success message to the console so the invoker knows it finished
print "database populated!"