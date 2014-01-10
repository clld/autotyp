from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import IdNameDescriptionMixin, Language, Value


class Stock(Base, IdNameDescriptionMixin):
    pass


class Continent(Base, IdNameDescriptionMixin):
    pass


class Area(Base, IdNameDescriptionMixin):
    continent_pk = Column(Integer, ForeignKey('continent.pk'))
    continent = relationship(Continent, backref='areas')


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.ILanguage)
class Languoid(Language, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    area_pk = Column(Integer, ForeignKey('area.pk'))
    area = relationship(Area, backref='languages')
    stock_pk = Column(Integer, ForeignKey('stock.pk'))
    stock = relationship(Stock, backref='languages')
