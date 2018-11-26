#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy import create_engine
Base = declarative_base()

# Create User Table


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    print "user table is made"

# Create First Table called departments


class Departments(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'))
    user = relationship(User, cascade="save-update")
    print "Departments table is made"

    @property
    def serialize(self):
        return {
            'department_id': self.id,
            'name': self.name
        }


# Create Second Table called courses


class Courses(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    grade = Column(String(250), nullable=False)
    description = Column(String(350), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id',
                           ondelete='cascade'))
    departments = relationship(Departments,
                               backref=backref("courses",
                                               cascade="all, delete-orphan"))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship(User, cascade="save-update")
    print "Courses table is made"

    @property
    def serialize(self):
        return {
            'course_id': self.id,
            'name': self.name,
            'grade': self.grade,
            'description': self.description,
        }


engine = create_engine('sqlite:///departmentCourses.db')
Base.metadata.create_all(engine)
