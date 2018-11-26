from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Departments, Courses, Base, User

engine = create_engine('sqlite:///departmentCourses.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
User1 = User(name="Islam Saied",
             email="islam.saied@must.edu.eg",
             picture='https://source.unsplash.com/random/150x150')
session.add(User1)
session.commit()
department1 = Departments(user_id=1, name="Computer Science")
session.add(department1)
session.commit()

department2 = Departments(user_id=1, name="Information Science")
session.add(department2)
session.commit()

department3 = Departments(user_id=1, name="Information Technology")
session.add(department3)
session.commit()

course1 = Courses(user_id=1, name="Introduction To Computer Programming",
                  grade="150 marks",
                  description="Introduction to computer application "
                  "and structured programming,"
                  " problem solving, simple data types,"
                  " control statements, "
                  "towards the complete program,"
                  " more control statements,"
                  " sub range type definition, arrays, "
                  "functions and procedures. ",
                  departments=department1)
session.add(course1)
session.commit()

course2 = Courses(user_id=1, name="Structured Programming", grade="150 marks",
                  description="Basic concepts for reading"
                  " and writing complex structured programs."
                  " Modularity,basic and complex"
                  " data types, procedures and functions,"
                  " control structures and basic data"
                  " structure (arrays, records,"
                  " lists and pointers.", departments=department1)
session.add(course2)
session.commit()

course3 = Courses(user_id=1, name="Data Structures", grade="150 marks",
                  description="Data types, simple data type,"
                  " compound data type, arrays,"
                  " strings, and abstract data type (ADT)."
                  " Abstract data definition,"
                  " implementation and application. Structures,"
                  " self referential structures."
                  " Dynamically allocated storage.",
                  departments=department1)
session.add(course3)
session.commit()

course4 = Courses(user_id=1, name="Introduction to Database",
                  grade="150 marks",
                  description="Database concepts: characteristics"
                  " of database approach, "
                  " database architecture, data models,"
                  " schemas, and instances, "
                  "DBMS architecture and data independence, "
                  "database language and interfaces. ",
                  departments=department2)
session.add(course4)
session.commit()

course5 = Courses(user_id=1, name="Object-Oriented Analysis & Design",
                  grade="150 marks",
                  description="Fundamental concepts"
                  " of Object Orientation,"
                  " Definition of key OO concepts"
                  "(An in-depth coverage of "
                  "the various OO concepts such as Classes,"
                  " Objects, Associations,"
                  " Aggregation, Inheritance, Polymorphism, Encapsulation,"
                  " Delegation, etc).",
                  departments=department2)
session.add(course5)
session.commit()

course6 = Courses(user_id=1, name="Management of Information Systems",
                  grade="150 marks",
                  description="Introduction to Computer Based"
                  " Information System (CBIS):"
                  " Types of CBIS; Relationship between CBIS models."
                  " Management concepts related to CBIS:"
                  " The nature of management;"
                  " the role of CBIS in management;"
                  " the impact of CBIS on management.",
                  departments=department2)
session.add(course6)
session.commit()

course7 = Courses(user_id=1, name="Data Communication and Networking",
                  grade="100 marks",
                  description="Communication model,"
                  " OSI and TCP/IP protocol architecture, Data transmission,"
                  " Data encoding and modulation, Data link control,"
                  " Wide area networks,"
                  " Circuit and packet switching, ATM,"
                  " Congestion control, Local area networks,"
                  " LAN.", departments=department3)
session.add(course7)
session.commit()

course8 = Courses(user_id=1, name="Computer Networks II",
                  grade="100 marks",
                  description="Computer Networks "
                  "and the Internet, network structure, protocol stack,"
                  " Application Layer, HTTP, FTP, SMTP, DNS,"
                  " socket programming,"
                  " content distribution, Network Layer and Routing,"
                  " Routing principles,"
                  " IP, IPv6", departments=department3)
session.add(course8)
session.commit()

course9 = Courses(user_id=1, name="Internet Technologies", grade="100 marks",
                  description="Programmer-oriented survey"
                  " of the authoring, distributing,"
                  " and browsing technologies. The role,"
                  " use, and implementation"
                  " of current Internet tools. TCP/IP; namespace,"
                  " connections, and protocols.", departments=department3)
session.add(course9)
session.commit()
