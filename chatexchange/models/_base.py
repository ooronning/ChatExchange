import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()
Base._chatExchangeClient = None

