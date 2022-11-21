'''
CS304: GoodTimes Final Project
Team: Audrey Liang, Rik Sampson, Catherine Wang
Fall 2022
'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import queries

app.secret_key = 'your secret here' # replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return "Welcome to GoodTimes!"
    
@app.route('/search/', methods = ['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    else:
        conn = dbi.connect()
        query = request.form['query']
        kind = request.form['kind']

        # do search and store search results
        search_results = queries.do_search(conn, query, kind)
        return render_template("search_results.html", 
                query=query, kind=kind, search_results=search_results, length=len(search_results))

@app.route('/createCollection/', methods = ["GET", "POST"])
def createCollection():
    conn = dbi.connect()

    if request.method == "POST":
        print ("post method")
        print (request.form['collectionName'])
        print (request.form['userID'])
        # start of code to be put in other py file
        # this would take in conn, result of the form, and uID
        # rn this is a temp uID, will be updated once user can create an account
        curs = dbi.dict_cursor(conn)
        curs.execute('''insert into collections(name, uID) 
        values (%s, %s);''',
            (
            request.form['collectionName'], 
            request.form['userID']
            # result['collectionName'], result['userID']
            )
        )
        conn.commit()
        # end of code to be put in other py file?
        curs.execute('select last_insert_id()')
        newID = curs.fetchone()

        return redirect(url_for('testCollectionPage', cID=newID['last_insert_id()']))
        #return redirect(url_for('testUserPage'))

    else:
        print ("get method")
        return render_template('createCollectionForm.html')

    #return render_template('createCollectionForm.html')

@app.route('/testCollectionPage/<cID>', methods = ["GET", "POST"])
def testCollectionPage(cID):
    conn = dbi.connect()

    if request.method == "POST":
        print ('post method')
        if request.form['submit'] == 'back to user page':

            # code to be put in other py file
            curs = dbi.dict_cursor(conn)
            collectionID = request.form['collectionID']
            curs.execute('''delete from mediaInCollections where collectionID=%s and mediaID=%s;''',
                (collectionID, mediaID)
            )
            conn.commit()
            # end of code to be put in other py file

            return redirect(url_for('testUserPage'))

        if request.form['submit'] == 'delete media':
            return redirect(url_for('testUserPage'))

        return render_template('testCollectionPage.html', collectionID = cID)
    else:
        print ('get method')
        return render_template('testCollectionPage.html', collectionID = cID)

@app.route('/testUserPage/', methods = ["GET", "POST"])
def testUserPage():
    conn = dbi.connect()

    # start of code to be put in other py file
    tempUID = 1 #hard coded for now
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from collections where uID = %s;''',
        (tempUID)
    )
    collections = curs.fetchall()
    # end of code to be put in other py file

    if request.method == "POST":

        if request.form['submit'] == 'create collection':
            return redirect(url_for('createCollection'))

        if request.form['submit'] == 'delete':
            #curs = dbi.dict_cursor(conn)
            collectionID = request.form['collectionID']
            curs.execute('''delete from collections where collectionID=%s;''',
                (collectionID)
            )
            conn.commit()

            # this updates collections so the page rerenders correctly
            curs.execute('''select * from collections where uID = %s;''',
                (tempUID)
            )
            collections = curs.fetchall()

        # hypothetical code for deleting media from a collection
        if request.form['submit'] == 'delete media':
            #curs = dbi.dict_cursor(conn)                
            collectionID = request.form['collectionID']
            curs.execute('''delete from collections where collectionID=%s;''',
                (collectionID)
            )
            conn.commit()

            # this updates collections so the page rerenders correctly
            curs.execute('''select * from collections where uID = %s;''',
                (tempUID)
            )
            collections = curs.fetchall()

        return render_template('testUserPage.html', collections = collections)

    else:
        return render_template('testUserPage.html', collections = collections)

    #return render_template('testUserPage.html', collections = collections)

@app.before_first_request
def init_db():
    db_to_use = 'goodtime_db' # use team database
    dbi.conf(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
