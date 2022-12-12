import cs304dbi as dbi

def do_search(conn, query, kind, mood, genre, audience):
    curs = dbi.dict_cursor(conn)
    if kind == "username": 
        curs.execute('select * from user where username like %s or name like %s', 
        ["%"+query+"%", "%"+query+"%"])
    elif kind == "media" and mood == "" and genre == "" and audience == "": 
        curs.execute('select * from media where title like %s', 
        ["%"+query+"%"])
    elif kind == "media" and mood != "" and genre == "" and audience == "":
        curs.execute('select * from media inner join mediaInCollections on media.mediaID==mediaInCollections.mediaID where title like %s and mood==%s', 
        ["%"+query+"%", "%"+mood+"%"])
    else:
        curs.execute('select * from media where title like %s', 
        ["%"+query+"%"])
        #select the mediaID rows from mediaInCollectiosn that corresponds to mood, genre and audience
        #but we want the media from the media table give mediaID, only appear once
    return curs.fetchall()

def insert_media(conn, media_title, media_release, media_type):
   '''Given media data, inserts media into database'''
   curs = dbi.dict_cursor(conn)
   curs.execute('''insert into media(title,releaseYear,type)
                values (%s, %s, %s)''', 
                [media_title, media_release, media_type])
   conn.commit()

# gets all users in the database
def getAllUsers(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from user')
    return curs.fetchall()

# gets all media in the database
def getAllMedia(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from media')
    return curs.fetchall()

# inserts data for new collection into collections table and returns new ID
def insertCollection(conn, result):
    curs = dbi.dict_cursor(conn)
    # the uID situation is temporary rn, will be updated once users can create accounts
    curs.execute('insert into collections(name, uID) values (%s, %s)', 
        [result['collectionName'], result['userID']])
    conn.commit()
    curs.execute('select last_insert_id()')
    return curs.fetchone()

# returns last_insert_id()
# def getLatestId(conn):
#     curs = dbi.dict_cursor(conn)
#     curs.execute('select last_insert_id()')
#     return curs.fetchone()

def getMediaTitle(conn, mediaID):
    curs = dbi.dict_cursor(conn)
    curs.execute('select title from media where mediaID=%s',
        [mediaID])
    return curs.fetchone()

def get_media(conn, mediaID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from media where mediaID=%s''',
        {mediaID})
    return curs.fetchall()

# gets all collections of user, given their uID (uID temp hard coded)
def getAllCollections(conn, tempUID):
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from collections where uID = %s;',
        [tempUID])
    return curs.fetchall()

#gets all the media within a specified collection
def getMediaInCollection(conn, cID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from media inner join mediaInCollections 
        using (mediaID) where collectionID = %s''',
        [cID])
    return curs.fetchall()

# deletes a collection, currently only available on user page (uID temp hard coded)
def deleteCollection(conn, result):
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from collections where collectionID=%s',
        [result['collectionID']])
    conn.commit()

# deletes a media from a collection, available on collection detail page
def deleteMediaFromCollection(conn, cID, result):
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from mediaInCollections where collectionID=%s and mediaID=%s',
        [cID, result['mediaID']])
    conn.commit()

# updates a media from a collection, available on collection detail page
def updateMediaFromCollection(conn, cID, result):
    # is there a more succinct way to change these values to None?
    resultA = {}
    for kind in ['rating', 'review', 'mood', 'genre', 'audience']:
        if result[kind] == '':
            resultA[kind] = None
        else: resultA[kind] = result[kind]

    curs = dbi.dict_cursor(conn)
    curs.execute('''update mediaInCollections set rating=%s, review=%s, moodTag=%s, 
        genreTag=%s, audienceTag=%s where collectionID=%s and mediaID=%s''',
        [resultA['rating'], resultA['review'], resultA['mood'], resultA['genre'], 
         resultA['audience'], cID, result['mediaID']])
    conn.commit()

# inserts media into collection
def insertInCollection (conn, mediaID, cID, rating, review, moodTag, genreTag, audienceTag):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into mediaInCollections(mediaID, collectionID, rating, review, moodTag, genreTag, audienceTag)
        values (%s, %s, %s, %s, %s, %s, %s)''',
        [mediaID, cID, rating, review, moodTag, genreTag, audienceTag])
    conn.commit()
