from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from support.database_setup import Base, Category, CategoryItem

engine = create_engine('sqlite:///catalog.db')
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


category1 = Category(name="Snowboarding")

session.add(category1)
session.commit()

item1 = CategoryItem(title="Goggles", description="Some Goggles", category=category1)

session.add(item1)
session.commit()


category2 = Category(name="Soccer")

session.add(category2)
session.commit()

item2 = CategoryItem(title="Ball", description="A Soccer Ball", category=category2)

session.add(item2)
session.commit()

print "database populated!"