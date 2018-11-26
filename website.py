# /usr/bin/python2.7
from flask import Flask, render_template, \
    request, redirect, url_for, flash, session, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Departments, Courses, Base, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
CLIENT_ID = json.loads(open('/var/www/My-Website-/client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "DepartmentsCourses"

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/My-Website-/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade '
                                            'the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/'
           'tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's"
                                            " user ID doesn't "
                                            "match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID "
                                            "does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                            ' already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius:' \
              ' 150px;-webkit-border-radius: ' \
              '150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/' \
          'oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token '
                                            'for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/departments/<int:department_id>/menu/JSON/')
def DepartmentMenuJSON(department_id):
    department = session.query(Departments).filter_by(id=department_id).one()
    items = session.query(Courses).filter_by(
        department_id=department_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# ADD JSON ENDPOINT HERE
@app.route('/departments/JSON')
def departmentsJSON():
    departments = session.query(Departments).all()
    return jsonify(departments=[r.serialize for r in departments])


# Task 1: Create routes for restaurants
@app.route('/')
@app.route('/departments')
def showDepartments():
    departments = session.query(Departments).order_by(asc(Departments.name))
    if 'username' not in login_session:
        return render_template("publicDepartments.html",
                               departments=departments)
    else:
        return render_template('departments.html',
                               departments=departments)


@app.route('/department/new', methods=['GET', 'POST'])
def newDepartment():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newDepartment = Departments(name=request.form['name'],
                                    user_id=login_session['user_id'])
        session.add(newDepartment)
        flash('New Department %s Successfully Created' % newDepartment.name)
        session.commit()
        return redirect(url_for('showDepartments'))
    else:
        return render_template('newDepartment.html')


@app.route('/department/<int:department_id>/edit/', methods=['POST', 'GET'])
def editDepartment(department_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedDepartment = \
        session.query(Departments).filter_by(id=department_id).one()
    if editedDepartment.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized to edit this department." \
               " Please create " \
               "your own department in order to edit.');}" \
               "</script><body onload='myFunction()'> "
    if request.method == 'POST':
        if request.form['name']:
            editedDepartment.name = request.form['name']
            flash('Department Successfully Edited %s' % editedDepartment.name)
            return redirect(url_for('showDepartments'))
    else:
        return render_template('editDepartment.html',
                               department=editedDepartment)


@app.route('/department/<int:department_id>/delete/', methods=['POST', 'GET'])
def deleteDepartment(department_id):
    departmentToDelete = session.query(Departments).filter_by(
        id=department_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if departmentToDelete.user_id != login_session['user_id']:
        return "<script>" \
               "function myFunction(){" \
               "alert('You aren't allowed to perform this action" \
               " please login to create , delete and update your own " \
              "}" \
               "<body onload='myFunction()'></script>"
    if request.method == 'POST':
        session.delete(departmentToDelete)
        session.commit()
        flash("Department has been deleted")
        return redirect(url_for('showDepartments'))
    else:
        return render_template('deleteDepartment.html',
                               department=departmentToDelete)


@app.route('/department/<int:department_id>/')
@app.route('/department/<int:department_id>/menu')
def showCourses(department_id):
    department = session.query(Departments).filter_by(id=department_id).one()
    creator = getUserInfo(department.user_id)
    items = session.query(Courses).filter_by(
        department_id=department_id).all()
    if 'username' not in login_session \
            or creator.id != login_session['user_id']:
        return render_template('publicCourses.html',
                               items=items,
                               department=department,
                               creator=creator)
    else:
        return render_template('courses.html', items=items,
                               department=department,
                               creator=creator)


@app.route('/department/<int:department_id>'
           '/course/new/', methods=['POST', 'GET'])
def newCourseItem(department_id):
    if 'username' not in login_session:
        return redirect('/login')
    department = session.query(Departments).filter_by(id=department_id).one()
    if login_session['user_id'] != department.user_id:
        return "<script>function myFunction() " \
               "{alert('You are not authorized to " \
               "add course items to this department. " \
               "Please create your own department " \
               "in order to add items.');}</script><body " \
               "onload='myFunction()'> "
    if request.method == 'POST':
        newItem = Courses(name=request.form['name'],
                          grade=request.form['grade'],
                          description=request.form['description'],
                          department_id=department_id,
                          user_id=department.user.id)
        session.add(newItem)
        session.commit()
        flash("New Course Item Created")
        return redirect(url_for('showCourses',
                                department_id=department_id))
    else:
        return render_template('newCourseItem.html',
                               department_id=department_id)


@app.route('/department/<int:department_id>/'
           '<int:course_id>/edit/', methods=['POST', 'GET'])
def editCourseItem(department_id, course_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Courses).filter_by(id=course_id).one()
    department = session.query(Departments).filter_by(id=department_id).one()
    if login_session['user_id'] != department.user_id:
        return "<script>function myFunction() " \
           "Please create your own department " \
               "in order to edit items.');}</script>" \
               "<body onload='myFunction()'> "
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['grade']:
            editedItem.grade = request.form['grade']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Course Item Successfully Edited')
        return redirect(url_for('showCourses', department_id=department_id))
    else:
        return render_template('editCourseItem.html',
                               department_id=department_id,
                               course_id=course_id,
                               item=editedItem)


@app.route('/department/<int:department_id>/'
           '<int:course_id>/delete/', methods=['POST', 'GET'])
def deleteCourseItem(department_id, course_id):
    if 'username' not in login_session:
        return redirect('/login')
    department = session.query(Departments).filter_by(id=department_id).one()
    itemToDelete = session.query(Courses).filter_by(id=course_id).one()
    if login_session['user_id'] != department.user_id:
        return "<script>function myFunction() " \
               "{alert('You are not authorized" \
               " to delete course items to this department. " \
               "Please create your own department" \
               " in order to delete items.');}</script>" \
               "<body onload='myFunction()'> "
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Course Item Successfully Deleted')
        return redirect(url_for('showCourses', department_id=department_id))
    else:
        return render_template('deleteCourseItem.html', item=itemToDelete)


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("you have logged out")
        return redirect(url_for('showDepartments'))
    else:
        flash("You have to login first")
        return url_for('showDepartments')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
