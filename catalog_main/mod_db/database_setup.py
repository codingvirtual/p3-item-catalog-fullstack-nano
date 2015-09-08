# sqlalchemy imports to handle ORM mapping
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# configure the base object for the various db classes to inherit from
Base = declarative_base()

# Define a class that encapsulates the data for a single category in the
# system.
class Category(Base):
    # The category item contains only a unique id and a category name
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }

# Define a class that encapsulates the data for a single item in the catalog
class CategoryItem(Base):
    # an item in the catalog consists of a unique id, a title, and the id
    # of the category the item "belongs" to.
    __tablename__ = 'categoryitems'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('categories.id'))
    # create the relationship between category and item (one category to
    # many items; one item to only category)
    category = relationship(Category)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'category_id': self.category_id
        }
