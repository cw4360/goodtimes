from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import queries
import bcrypt

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
    return render_template("home.html")

@app.route('/join/', methods=['POST'])
def join():
    username = request.form.get('username')
    passwd1 = request.form.get('password1')
    passwd2 = request.form.get('password2')
    if passwd1 != passwd2:
        flash('Passwords do not match')
        return redirect(url_for('index'))
    hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
    stored = hashed.decode('utf-8')
    print(passwd1, type(passwd1), hashed, stored)
    conn = dbi.connect()
    curs.dbi.cursor(conn)
    try:
        curs.execute('''insert into user(uid,username,hashed)
            values(null,%s,%s)''', [username, stored])
        conn.commit()
    except Exception as err:
        flash('The username is taken: {}'.format(repr(err)))
        return redirect(url_for('index'))
    curs.execute('select last_insert_id()')
    row = curs.fetchone()
    uid = row[0]
    flash('FYI, you were issued UID {}'.format(uid))
    session['username'] = username
    session['uid'] = uid
    session['logged_in'] = True
    session['visits'] = 1
    return redirect(url_for('user', username=username))

@app.route('/login/', methods=['POST'])
def login():
    username = request.form.get('username')
    passwd = request.form.get('password')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select uid,hashed from user
                    where username = %s''', [username])
    row = curs.fetchone()
    ### Catherine: Left off here. Finish adding code from CS304: Logins
    
@app.route('/search/', methods = ['GET', 'POST'])
def search():
    conn = dbi.connect()
    if request.method == 'GET':
        all_users = queries.getAllUsers(conn)
        all_media = queries.getAllMedia(conn)
        return render_template('search.html', 
            all_users=all_users, all_media=all_media)
    else:
        query = request.form['query']
        kind = request.form['kind']

        # do search and store search results
        search_results = queries.do_search(conn, query, kind)

        if len(search_results) == 0:
            return redirect(url_for('insert'))
        else:
            return render_template("search_results.html", 
                query=query, kind=kind, search_results=search_results, length=len(search_results))

@app.route('/insert/', methods=["GET", "POST"])
def insert():
    #renders the insert media form if media doesn't exist
    if request.method == "GET":
        return render_template('insert.html')
    else:
        conn = dbi.connect()
        media_title = request.form['media_title']
        media_release = request.form['media_release']
        media_type = request.form['media_type']

         # detect incomplete form
        if media_title == "" or media_release == "" or media_type == "":
            return render_template('insert.html', msg="Form is not complete, fill in missing info")

        # if media id doesn't exist
        else:
            # insert the media
            queries.insert_media(conn, media_title, media_release, media_type)
            flash('Media successfully inserted!')
            return render_template('insert.html', media_title=media_title, media_release=media_release, media_type=media_type)

@app.route('/createCollection/', methods = ["GET", "POST"])
def createCollection():
    conn = dbi.connect()
    formInput = request.form

    if request.method == "GET":
        return render_template('createCollectionForm.html')

    else:
        newID = queries.insertCollection(conn, formInput)
        # newID = queries.getLatestId(conn)
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

        if request.form['submit'] == 'view':
            toView = request.form
            print (toView)
            return redirect(url_for('collectionPage', cID = toView['collectionID']))

        if request.form['submit'] == 'delete': #may need to update value to be more specific
            toDelete = request.form
            queries.deleteCollection(conn, toDelete)
            # this updates collections so the page rerenders correctly
            collections = queries.getAllCollections(conn, tempUID)

        return render_template('userPage.html', collections = collections)

    else:
        return render_template('userPage.html', collections = collections)


@app.route('/media_details/<int:mediaID>', methods = ["GET", "POST"])
def media_info(mediaID):
    conn = dbi.connect()
    media_info = queries.get_media(conn, mediaID)
    if request.method == "POST":
        if request.form['submit'] == 'add media':
                mediaID = request.form['media-add']
                cID = request.form['collection-add']
                rating = request.form['rating']
                review = request.form['review']
                moodTag = request.form['mood']
                genreTag = request.form['genre']
                audienceTag = request.form['audience']
                queries.insertInCollection(conn, mediaID, cID, rating, review, moodTag, genreTag, audienceTag)
                # updating the media in the collection
                #mediaCollection = queries.getMediaInCollection(conn, cID)
                return render_template('mediaPage.html', media= media_info)
        else:
            return render_template('mediaPage.html',  
                media= media_info, 
                )

    else:
        return render_template('mediaPage.html',  
                media= media_info, 
                )
                          
@app.route('/update/<cID>', methods=['GET', 'POST'])
def update(cID):
    # thinking of adding the update form for a media to a separate page
    pass

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
