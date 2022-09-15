import datetime
import uuid
from dataclasses import dataclass


@dataclass(order=True)
class _UUIDMixin:
    id: uuid.UUID


@dataclass(order=True)
class _TimeStampedValidator:
    created_at: str
    updated_at: str

    def __post_init__(self):
        if type(self.created_at) == datetime.datetime:
            self.created_at = self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            self.created_at = datetime.datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S.%f %z')

            self.updated_at = self.updated_at.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            self.updated_at = datetime.datetime.strptime(self.updated_at, '%Y-%m-%d %H:%M:%S.%f %z')
        else:
            self.created_at += ':00'
            self.updated_at += ':00'
            self.created_at = datetime.datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S.%f%z')
            self.updated_at = datetime.datetime.strptime(self.updated_at, '%Y-%m-%d %H:%M:%S.%f%z')


@dataclass(order=True)
class _CreatedAtValidator:
    created_at: str

    def __post_init__(self):
        if type(self.created_at) == datetime.datetime:
            self.created_at = self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            self.created_at = datetime.datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S.%f %z')
        else:
            self.created_at += ':00'
            self.created_at = datetime.datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S.%f%z')




@dataclass(order=True)
class Filmwork(_UUIDMixin, _TimeStampedValidator):
    title: str
    description: str
    creation_date: str
    file_path: str
    rating: float
    type: str


@dataclass(order=True)
class Genre(_UUIDMixin, _TimeStampedValidator):
    name: str
    description: str


@dataclass(order=True)
class Person(_UUIDMixin, _TimeStampedValidator):
    full_name: str


@dataclass(order=True)
class GenreFilmwork(_UUIDMixin, _CreatedAtValidator):
    film_work_id: str
    genre_id: str


@dataclass(order=True)
class PersonFilmwork(_UUIDMixin, _CreatedAtValidator):
    film_work_id: str
    person_id: str
    role: str


TABLE_MAPPING = {
    'film_work': Filmwork,
    'genre': Genre,
    'genre_film_work': GenreFilmwork,
    'person': Person,
    'person_film_work': PersonFilmwork
}
