"""
Models for Products

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Product(db.Model):
    """
    Class that represents a product
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    sku = db.Column(db.String(14))
    available = db.Column(db.Boolean())
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    size = db.Column(db.String(4))
    color = db.Column(db.String(10))
    category = db.Column(db.String(63))
    description = db.Column(db.String(250))
    #lastUpdated = db.Column(db.String(10))#

    def __repr__(self):
        return "<Product %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a product to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a product from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a product into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "available": self.available,
            "price": self.price,
            "stock": self.stock,
            "size": self.size,
            "color": self.color,
            "category": self.category,
            "description": self.description#, Tabling for this sprint
            #"lastUpdated": self.lastUpdated#
        }

    def deserialize(self, data):
        """
        Deserializes a product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.sku = data["sku"]
            self.available = data["available"]
            self.price = data["price"]
            self.stock = data["stock"]
            self.size = data["size"]
            self.color = data["color"]
            self.category = data["category"]
            self.description = data["description"]
            #self.lastUpdated = data["lastUpdated"]# Tabling for this sprint

        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            )
        except TypeError:
            raise DataValidationError(
                "Invalid Product: body of request contained" "bad or no data"
            )
        return self

    def restock(self, quant):
        """ Restocks a product in the database """
        self.stock = quant
        self.available = True
        logger.info("Restocked {0}. There are now {1} available".format(self.name, self.stock))

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the products in the database """
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a product by its ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a product by its id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all products with the given name

        Args:
            name (string): the name of the products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category):
        """ Returns all products with the given category

        Args:
            name (string): the category of the products you want to match
        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        cls.query.delete()
