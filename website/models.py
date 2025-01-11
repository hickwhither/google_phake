import sqlalchemy
from types import FunctionType
from website import db
# from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON
from sqlalchemy.ext.mutable import *

import time

class Hyperlinks(db.Model):
    url: Mapped[str] = mapped_column(primary_key=True)
    last_crawl: Mapped[int] = mapped_column(default=0)
    icon: Mapped[str] = mapped_column(default='')
    title: Mapped[str] = mapped_column(default='')
    description: Mapped[str] = mapped_column(default='')
    rate: Mapped[int] = mapped_column(default=1000)
    words: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=[])

class Word(db.Model):
    word: Mapped[str] = mapped_column(primary_key=True)
    urls: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=[])
