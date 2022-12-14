# CS304 Final Project: GoodTimes
# Team: Audrey, Catherine, Rik

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import bcrypt
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
    """ Renders GoodTimes' home page, which includes functionality
    to create an account or log into their user account."""
    return render_template("home.html", title="GoodTimes")

@app.route('/join/', methods=['GET', 'POST'])
def join():
    """ Given a name, username, and a confirmed password, adds new user to
    GoodTimes user table in database. Then logs user in. Requires user
    to supply a name, username, password, and confirmed password. """
    if request.method == 'GET':
        # redirect user to index instead of using this endpoint
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        passwd1 = request.form.get('password1')
        passwd2 = request.form.get('password2')
        if passwd1 != passwd2:
            flash('Passwords do not match')
            return redirect(url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        stored = hashed.decode('utf-8')
        print("password:", passwd1, type(passwd1), hashed, stored)
        conn = dbi.connect()
        curs = dbi.cursor(conn)
        try:
            curs.execute('''insert into user(uid,name,username,hashed)
                values(null,%s,%s,%s)''', [name, username, stored])
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

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """ Given the username and password of an existing GoodTimes user, 
    logs the user into their account and renders their user page.
    Requires user to to supply their username and password. """
    if request.method == 'GET':
        # redirect user to index instead of using this endpoint
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        passwd = request.form.get('password')
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''select uid,hashed from user
                        where username = %s''', [username])
        row = curs.fetchone()
        if row is None:
            # same response as wrong password, so no information
            # about what went wrong
            flash('Login incorrect. Try again or create account')
            return redirect(url_for('index'))
        stored = row['hashed']
        print('database has stored: {} {}'.format(stored,type(stored)))
        print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                                stored.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
        if hashed2_str == stored:
            print('Password matches!')
            flash('Successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            session['logged_in'] = True
            session['visits'] = 1
            print('session:', session)
            return redirect( url_for('user', username=username) )
        else:
            flash('Login incorrect. Try again or join')
            return redirect( url_for('index'))

@app.route('/logout/')
def logout():
    """ Logs user out of GoodTimes."""
    if 'username' in session:
        username = session['username']
        session.pop('username')
        session.pop('uid')
        session.pop('logged_in')
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index'))

@app.route('/user/<username>', methods = ["GET", "POST"])
def user(username):
    """ Given a user's unique username, renders their user page with
    all their collections displayed and options to manage their 
    collections."""
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index'))
    else:
        print("session:", session)
        conn = dbi.connect()
        uid = session['uid'] ## get current user's UID
        # get given user's name, username, and uid
        userInfo = queries.getUserInfo(conn, username) 
        collections = queries.getAllCollectionsByUserName(conn, username)

        if uid != userInfo['uid']: # if user is viewing another user's profile
            return render_template('userPage.html', title="My Profile", 
                isUser=False, userInfo=userInfo, collections=collections)
        else: # if user is viewing their own profile, and has access to manage profile and collections
            if request.method == "POST":
                if request.form['submit'] == 'update name':
                    queries.updateName(conn, uid, request.form['name'])
                    # this updates userInfo so the page rerenders correctly
                    userInfo = queries.getUserInfo(conn, username)

                if request.form['submit'] == 'create collection':
                    return redirect(url_for('createCollection'))

                if request.form['submit'] == 'view':
                    toView = request.form
                    print(toView)
                    return redirect(url_for('collectionPage', cID = toView['collectionID']))

                if request.form['submit'] == 'delete': 
                    toDelete = request.form
                    queries.deleteCollection(conn, toDelete)
                    # this updates collections so the page rerenders correctly
                    collections = queries.getAllCollections(conn, uid)

                return render_template('userPage.html', title="My Profile", 
                    isUser=True, userInfo=userInfo, collections=collections)
            else:
                return render_template('userPage.html', title="My Profile", 
                    isUser=True, userInfo=userInfo, collections=collections)

@app.route('/createCollection/', methods = ["GET", "POST"])
def createCollection():
    """ Renders a page to create a new collection for the user. """
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index'))
    else:
        conn = dbi.connect()
        formInput = request.form
        if request.method == "GET":
            return render_template('createCollectionForm.html', title="Create Collection")
        else:
            newID = queries.insertCollection(conn, formInput, session['uid'])
            # redirects to collection detail page, will be updated with correct url_for()
            return redirect(url_for('collectionPage', title="View Collection", cID=newID['last_insert_id()']))

@app.route('/collection/<cID>', methods = ["GET", "POST"])
def collectionPage(cID): 
    """ Renders the collection detail page, includes all media in that collection. """
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index', title="GoodTimes",))
    else:
        conn = dbi.connect()
        uid = session['uid'] # get current user's UID
        collectionName = queries.getCollectionName(conn, cID)
        mediaCollection = queries.getMediaCreatorInCollection(conn, cID)

        if not queries.isUsersCollection(conn, uid, cID): # checks if collection belongs to user
            return render_template('collectionPage.html', title="View Collection", isUser=False,
                collectionID = cID, collectionName=collectionName, mediaInCollection = mediaCollection)
        else:
            if request.method == "GET":
                return render_template('collectionPage.html', title="View Collection", isUser=True,
                    collectionID = cID, collectionName=collectionName, mediaInCollection = mediaCollection)
            if request.method == "POST":
                if request.form['submit'] == 'back to user page':
                    return redirect(url_for('user', title="My Profile", username=session['username']))
                # redirects user to explore page
                if request.form['submit'] == 'add media':
                    # toAdd = request.form
                    return redirect(url_for('search', title="Explore",))
                #deletes media from the given collection
                if request.form['submit'] == 'delete media':
                    toDelete = request.form
                    queries.deleteMediaFromCollection(conn, cID, toDelete)
                #updates the media in the collection
                if request.form['submit'] == 'update media':
                    toUpdate = request.form
                    print(toUpdate)
                    queries.updateMediaFromCollection(conn, cID, toUpdate)
                # retrieve updated mediaCollection after deleting or updating
                mediaCollection = queries.getMediaCreatorInCollection(conn, cID)
                return render_template('collectionPage.html', title="View Collection", isUser=True,
                    collectionID = cID, collectionName=collectionName, mediaInCollection = mediaCollection)
                
@app.route('/search/', methods = ['GET', 'POST'])
def search():
    """ On the search page, users will initially see a list of all 
    GoodTime users and all media. If no results found, renders a 
    page to insert a new media to the database. Otherwise, displays
    the search results as a list."""
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index', title="GoodTimes",))
    else:
        conn = dbi.connect()
        print("session:", session)
        if request.method == 'GET':
            all_users = queries.getAllUsers(conn)
            all_media = queries.getAllMediaAndCreator(conn)
            return render_template('search.html', title="Explore",
                all_users=all_users, all_media=all_media)
        if request.method == 'POST':
            # gets responses from the form
            query = request.form['query']
            kind = request.form['kind']
            mood = request.form['mood']
            genre = request.form['genre']
            audience = request.form['audience']
            # do search and store search results
            search_results = queries.do_search(conn, query, kind, mood, genre, audience)
            #if searched media does not exist
            if len(search_results) == 0 and kind== "media" and mood=="" and genre=="" and audience=="":
                return redirect(url_for('insert'))
            #if media does not match filter options
            elif kind== "media" and len(search_results) == 0:
                flash("No media matches these filter options")
                return render_template("search_results.html", title="Search Results",
                    query=query, kind=kind, mood=mood, genre=genre, audience=audience,
                    search_results=search_results, length=len(search_results))
            #if user does not match search options
            elif kind == "username" and len(search_results) == 0:
                flash("No such user exists in the system")
                return render_template("search_results.html", title="Search Results",
                    query=query, kind=kind, mood=mood, genre=genre, audience=audience,
                    search_results=search_results, length=len(search_results))
            #display results of search if exists
            else:
                return render_template("search_results.html", title="Search Results",
                    query=query, kind=kind, mood=mood, genre=genre, audience=audience,
                    search_results=search_results, length=len(search_results))

@app.route('/insert/', methods=["GET", "POST"])
def insert():
    """ Renders form for inserting new media into the database of all media. """
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index', title="GoodTimes",))
    else:
        conn = dbi.connect()
        creators = queries.getAllCreators(conn)
        if request.method == "GET":
            return render_template('insert.html', title="Insert New Media", allCreators=creators)
        if request.method == 'POST':
            if request.form['submit'] == 'Add New Creator':
                #insert a new creator
                print(request.form)
                creatorName = request.form['inputAdd']
                #return a new pID
                newPID = queries.insertCreator(conn, creatorName)
                creators = queries.getAllCreators(conn) #update list of creators
                flash("Creator successfully inserted! Search again in the media creator dropdown.")
                return render_template('insert.html', title="Insert New Media", allCreators=creators)
            if request.form['submit'] == 'Insert Media':
                media_title = request.form['media_title']
                media_release = request.form['media_release']
                media_type = request.form['media_type']
                media_pID = request.form['media_creator']
                # detect incomplete form
                if media_title == "" or media_release == "" or media_type == "" or media_pID =="":
                    return render_template('insert.html', title="Insert New Media", 
                    msg="Form is not complete, fill in missing info", allCreators=creators)
                # if media id doesn't exist
                else:
                    # if no media creator was selected, change value to NULL
                    if media_pID == 'N/A':
                        media_pID = None
                    # insert the media
                    queries.insert_media(conn, media_title, media_release, media_type, media_pID)
                    flash('Media successfully inserted!')
                    return render_template('insert.html', title="Insert New Media", 
                        media_title=media_title, media_release=media_release, 
                        media_type=media_type, allCreators=creators)
            
@app.route('/media_details/<mediaID>', methods = ["GET", "POST"])
def media_info(mediaID):
    """ Renders the movie detail page to include a description (e.g. release year and creator
        and the ratings previously made for that movie."""
    if 'username' not in session:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('index', title="GoodTimes"))
    else:
        conn = dbi.connect()
        media_info = queries.get_media(conn, mediaID)
        pID = media_info['pID']
        creator_info = queries.getCreator(conn, pID)
        uid = session.get('uid')
        collections = queries.getAllCollections(conn, uid)
        rated = queries.getRatedMedia(conn, mediaID)
        if request.method == "POST":
            if request.form['submit'] == 'add media':
                cID = request.form['addMedia']
                exists = queries.isMediaInCollection(conn, mediaID, cID)
                rating = request.form['rating']
                review = request.form['review']
                moodTag = request.form['mood']
                genreTag = request.form['genre']
                audienceTag = request.form['audience']
                if not exists:
                    queries.insertInCollection(conn, mediaID, cID, rating, review, moodTag, genreTag, audienceTag)
                    # updating the media in the collection
                    mediaCollection = queries.getMediaInCollection(conn, cID)
                    flash("Media successfully inserted into collection!")
                    return redirect(url_for('collectionPage',  title="View Collection", cID= cID)) 
                else:
                    flash("The media you tried to insert is already in the specified collection!")
                    return redirect(url_for('collectionPage',  title="View Collection", cID= cID))
        else:
            return render_template('mediaPage.html', title="Media Detail Page",
                    media_info= media_info, mediaID=mediaID, 
                    uid=uid, collections=collections, rated=rated, creator_info=creator_info)

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
