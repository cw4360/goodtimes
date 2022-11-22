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
    #return "Welcome to GoodTimes!"
    return render_template("base.html")
    
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
    formInput = request.form

    if request.method == "GET":
        return render_template('createCollectionForm.html')

    else:
        queries.insertCollection(conn, formInput)
        newID = queries.getLatestId(conn)
        # redirects to collection detail page, will be updated with correct url_for()
        return redirect(url_for('collectionPage', cID=newID['last_insert_id()']))


@app.route('/collection/<cID>', methods = ["GET", "POST"])
def collectionPage(cID): # collection detail page, includes all media in that collection
    conn = dbi.connect()
    mediaCollection = queries.getMediaInCollection(conn, cID)

    if request.method == "POST":
    
        if request.form['submit'] == 'back to user page':
            return redirect(url_for('userPage'))

        if request.form['submit'] == 'delete media':
            toDelete = request.form
            print (toDelete)
            queries.deleteMediaFromCollection(conn, cID, toDelete)
            # updating the media in the collection
            mediaCollection = queries.getMediaInCollection(conn, cID)

        return render_template('collectionPage.html', collectionID = cID, mediaInCollection = mediaCollection)
    else:
        return render_template('collectionPage.html', collectionID = cID, mediaInCollection = mediaCollection)

# will add uid to the end of url
@app.route('/user/', methods = ["GET", "POST"])
def userPage():
    conn = dbi.connect()
    tempUID = 1
    collections = queries.getAllCollections(conn, tempUID)

    if request.method == "POST":

        if request.form['submit'] == 'create collection':
            return redirect(url_for('createCollection'))

        if request.form['submit'] == 'delete': #may need to update value to be more specific
            toDelete = request.form
            queries.deleteCollection(conn, toDelete)
            # this updates collections so the page rerenders correctly
            collections = queries.getAllCollections(conn, tempUID)

        return render_template('userPage.html', collections = collections)

    else:
        return render_template('userPage.html', collections = collections)

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
