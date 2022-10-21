from sqlalchemy import create_engine, Column, String, UnicodeText, distinct, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from config import DB_URI


def start() -> scoped_session:
    engine = create_engine(DB_URI)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


try:
    BASE = declarative_base()
    SESSION = start()
except AttributeError as e:
    print(
        "DB_URI is not configured. Features depending on the database might have issues."
    )
    print(str(e))


class Gvar(BASE):
    __tablename__ = "gvar"
    variable = Column(String, primary_key=True, nullable=False)
    value = Column(UnicodeText, primary_key=True, nullable=False)

    def __init__(self, variable, value):
        self.variable = str(variable)
        self.value = value


Gvar.__table__.create(checkfirst=True)


def gvarstat(variable):
    try:
        return SESSION.query(Gvar).filter(Gvar.variable == str(variable)).first().value
    except BaseException:
        return None
    finally:
        SESSION.close()


def addgvar(variable, value):
    if SESSION.query(Gvar).filter(Gvar.variable == str(variable)).one_or_none():
        delgvar(variable)
    adder = Gvar(str(variable), value)
    SESSION.add(adder)
    SESSION.commit()


def delgvar(variable):
    rem = (
        SESSION.query(Gvar)
        .filter(Gvar.variable == str(variable))
        .delete(synchronize_session="fetch")
    )
    if rem:
        SESSION.commit()
