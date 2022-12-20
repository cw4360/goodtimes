import cs304dbi as dbi

def do_search(conn, query, kind, mood, genre, audience):
    """does a search on the media depending on the typed query, kind of search (media or user), as well as any mood, genre, or audience tags"""
    curs = dbi.dict_cursor(conn)
    if kind == "username": 
        curs.execute('''select * from user where username like %s or name like %s''', 
        ["%"+query+"%", "%"+query+"%"])
    elif kind == "media" and mood == "" and genre == "" and audience == "": 
        curs.execute('''select * from media where title like %s''', 
        ["%"+query+"%"])
    elif kind == "media" and mood != "" and genre == "" and audience == "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and moodTag=%s''', 
        ["%"+query+"%", mood])
    elif kind == "media" and mood == "" and genre != "" and audience == "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and genreTag=%s''', 
        ["%"+query+"%", genre])
    elif kind == "media" and mood == "" and genre == "" and audience != "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and audienceTag=%s''', 
        ["%"+query+"%", audience])
    elif kind == "media" and mood != "" and genre != "" and audience == "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and moodTag=%s and genreTag=%s''', 
        ["%"+query+"%", mood, genre])
    elif kind == "media" and mood != "" and genre == "" and audience != "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and moodTag=%s and audienceTag=%s''', 
        ["%"+query+"%", mood, audience])
    elif kind == "media" and mood == "" and genre != "" and audience != "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and genreTag=%s and audienceTag=%s''', 
        ["%"+query+"%", genre, audience])
    elif kind == "media" and mood != "" and genre != "" and audience != "":
        curs.execute('''select * from media inner join mediaInCollections on media.mediaID=mediaInCollections.mediaID 
        where title like %s and moodTag=%s and genreTag=%s and audienceTag=%s''', 
        ["%"+query+"%", mood, genre, audience])
        #select the mediaID rows from mediaInCollectiosn that corresponds to mood, genre and audience
        #but we want the media from the media table give mediaID, only appear once
    return curs.fetchall()

def insert_media(conn, media_title, media_release, media_type, media_pID):
   '''Given media data, inserts media into database'''
   curs = dbi.dict_cursor(conn)
   curs.execute('''insert into media(title,releaseYear,type, pID)
                values (%s, %s, %s, %s)''', 
                [media_title, media_release, media_type, media_pID])
   conn.commit()

def getAllUsers(conn):
    '''returns uid, name, and username of all users'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from user')
    return curs.fetchall()

def getAllMedia(conn):
    '''returns mediaID, title, releaseYear, type, pID of all media'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from media')
    return curs.fetchall()

def getAllMediaAndCreator(conn):
    '''returns mediaID< title, releaseYear, type, pID, and name of all media associated with a creator'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select mediaID, title, releaseYear, type, media.pID, name from media inner join creator on media.pID = creator.pID')
    return curs.fetchall()

# inserts data for new collection into collections table and returns new ID
def insertCollection(conn, result, uID):
    '''given collection name and current uID, creates a new collection in the collections table and
    returns the collectionID of the newly created collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('insert into collections(name, uID) values (%s, %s)', 
        [result['collectionName'], uID])
    conn.commit()
    curs.execute('select last_insert_id()')
    return curs.fetchone()

# returns last_insert_id()
# def getLatestId(conn):
#     curs = dbi.dict_cursor(conn)
#     curs.execute('select last_insert_id()')
#     return curs.fetchone()

def getCollectionName(conn, cID):
    '''given a collectionID, returns the name of that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name from collections where collectionID=%s', 
        [cID])
    return curs.fetchone()['name']

def getMediaTitle(conn, mediaID):
    '''given a mediaID, returns the title of that media'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select title from media where mediaID=%s',
        [mediaID])
    return curs.fetchone()

def getCreator(conn, pID): # may be deleted later
    '''given a personID, returns the name of that creator'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name from creator where pID=%s',
        [pID])
    return curs.fetchone()

def get_media(conn, mediaID):
    '''given a mediaID, returns the mediaID, title, releaseYear, type, and pID for that particular media'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from media where mediaID=%s;''',
        [mediaID])
    return curs.fetchall()


def getAllCollections(conn, uID): #uID no longer hard coded
    '''given a uID, returns all collections (collectionID, name, uID) made by that user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from collections where uID = %s;',
        [uID])
    return curs.fetchall()

def getAllCreators(conn):
    '''returns all pID, name from the creator table, sorted alphabetically'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from creator order by name;')
    return curs.fetchall()

def getMediaInCollection(conn, cID):
    '''given a collectionID, returns all the media located within that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select title, mediaID, rating, review, moodTag, genreTag, audienceTag from media inner join mediaInCollections 
        using (mediaID) where collectionID = %s;''',
        [cID])
    return curs.fetchall()

def getMediaCreatorInCollection(conn, cID):
    '''given a collectionID, returns all media with a creator in that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select title, releaseYear, type, media.mediaID, rating, review, moodTag, genreTag, audienceTag, name, media.pID
                from mediaInCollections join media on mediaInCollections.mediaID = media.mediaID
                join creator on creator.pID = media.pID
                where collectionID = %s;''', [cID])
    return curs.fetchall();

def deleteCollection(conn, result):
    '''given a collectionID, deletes that collection (available from user page)'''
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from collections where collectionID=%s',
        [result['collectionID']])
    conn.commit()

def deleteMediaFromCollection(conn, cID, result):
    '''given a collectionID and mediaID, deletes that media from that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from mediaInCollections where collectionID=%s and mediaID=%s',
        [cID, result['mediaID']])
    conn.commit()

def updateMediaFromCollection(conn, cID, result):
    '''given a collectionID and result, updates the media from the collection'''
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

def insertInCollection (conn, mediaID, cID, rating, review, moodTag, genreTag, audienceTag):
    '''given collectionID and all form data about media, inserts that media into the collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into mediaInCollections(mediaID, collectionID, rating, review, moodTag, genreTag, audienceTag)
        values (%s, %s, %s, %s, %s, %s, %s)''',
        [mediaID, cID, rating, review, moodTag, genreTag, audienceTag])
    conn.commit()

def getRatedMedia(conn, mediaID):
    """get all rated media, ratings, reviews, tags given mediaID"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from mediaInCollections where mediaID=%s''', [mediaID])
    return curs.fetchall()
