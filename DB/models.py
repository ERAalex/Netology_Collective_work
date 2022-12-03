import sqlalchemy as sqa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    mode = relationship('User_session', backref='users')
    name = sqa.Column(sqa.String, nullable=False)
    last_name = sqa.Column(sqa.String, nullable=False)
    vk_id = sqa.Column(sqa.Text, nullable=False)
    age = sqa.Column(sqa.Integer, nullable=True)
    relations = sqa.Column(sqa.String, nullable=True)
    b_day = sqa.Column(sqa.Text, nullable=True)
    city = sqa.Column(sqa.String, nullable=True)
    language = sqa.Column(sqa.Text, nullable=True)
    activities = sqa.Column(sqa.Text, nullable=True)
    interests = sqa.Column(sqa.Text, nullable=True)
    movies = sqa.Column(sqa.Text, nullable=True)
    books = sqa.Column(sqa.Text, nullable=True)
    games = sqa.Column(sqa.Text, nullable=True)
    music = sqa.Column(sqa.Text, nullable=True)
    gender = sqa.Column(sqa.Text, nullable=True)

    users_selected = relationship('UsersSelected', backref='users')
    banned = relationship('Banned', backref='users')
    deleted_selected = relationship('DeletedSelected', backref='users')
    mode = relationship('User_session', backref='users')


class Selected(Base):
    __tablename__ = 'selected'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    name = sqa.Column(sqa.String, nullable=False)
    last_name = sqa.Column(sqa.String, nullable=False)
    vk_id = sqa.Column(sqa.Text, nullable=False)
    age = sqa.Column(sqa.Integer, nullable=True)
    relations = sqa.Column(sqa.String, nullable=True)
    b_day = sqa.Column(sqa.Text, nullable=True)
    city = sqa.Column(sqa.String, nullable=True)
    language = sqa.Column(sqa.Text, nullable=True)
    activities = sqa.Column(sqa.Text, nullable=True)
    interests = sqa.Column(sqa.Text, nullable=True)
    movies = sqa.Column(sqa.Text, nullable=True)
    books = sqa.Column(sqa.Text, nullable=True)
    games = sqa.Column(sqa.Text, nullable=True)
    music = sqa.Column(sqa.Text, nullable=True)
    gender = sqa.Column(sqa.Text, nullable=True)

    photo = relationship('Photos', backref='selected')
    users_selected = relationship('UsersSelected', backref='selected')
    deleted = relationship('DeletedSelected', backref='selected')


class Photos(Base):
    __tablename__ = 'photos'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    photo_id = sqa.Column(sqa.Text, nullable=False)
    id_selected = sqa.Column(sqa.Integer, sqa.ForeignKey("selected.id"), nullable=False)


class UsersSelected(Base):
    __tablename__ = 'users_selected'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    id_user = sqa.Column(sqa.Integer, sqa.ForeignKey('users.id'), nullable=False)
    id_selected = sqa.Column(sqa.Integer, sqa.ForeignKey('selected.id'), nullable=False)


class Banned(Base):
    __tablename__ = 'banned'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    id_user = sqa.Column(sqa.Integer, sqa.ForeignKey('users.id'), nullable=False)
    banned_vk_id = sqa.Column(sqa.Text, nullable=False)


class DeletedSelected(Base):
    __tablename__ = 'selected_deleted'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    id_user = sqa.Column(sqa.Integer, sqa.ForeignKey('users.id'), nullable=False)
    id_selected = sqa.Column(sqa.Integer, sqa.ForeignKey('selected.id'), nullable=False)


class User_session(Base):
    __tablename__ = 'user_session'

    id = sqa.Column(sqa.Integer, primary_key=True, unique=True)
    id_user = sqa.Column(sqa.Integer, sqa.ForeignKey('users.id'), nullable=False)
    mode_name = sqa.Column(sqa.String, nullable=True)
    city_find = sqa.Column(sqa.String, nullable=True)
    age_find = sqa.Column(sqa.Integer, nullable=True)
    ids_found = sqa.Column(sqa.Text, nullable=True)
    step = sqa.Column(sqa.Integer, nullable=True)
    

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)