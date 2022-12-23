# CS304 Final Project: GoodTimes
# Team: Audrey, Catherine, Rik

import cs304dbi as dbi

def do_search(conn, query, kind, mood, genre, audience):
    """ Given a query, search type, and potential filters by mood, genre, and audience, 
        returns a list of dictionaries representing all users or media that match this query."""
    curs = dbi.dict_cursor(conn)
    if kind == "username": 
        curs.execute('''select * from user where username like %s or name like %s''', 
        ["%"+query+"%", "%"+query+"%"])
    elif kind == "media" and mood == "" and genre == "" and audience == "": 
        curs.execute('''select * from media inner join creator on media.pID=creator.pID where title like %s''', 
        ["%"+query+"%"])
    elif kind == "media" and mood != "" and genre == "" and audience == "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and moodTag=%s''', 
        ["%"+query+"%", mood])
    elif kind == "media" and mood == "" and genre != "" and audience == "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and genreTag=%s''', 
        ["%"+query+"%", genre])
    elif kind == "media" and mood == "" and genre == "" and audience != "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and audienceTag=%s''', 
        ["%"+query+"%", audience])
    elif kind == "media" and mood != "" and genre != "" and audience == "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and moodTag=%s and genreTag=%s''', 
        ["%"+query+"%", mood, genre])
    elif kind == "media" and mood != "" and genre == "" and audience != "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and moodTag=%s and audienceTag=%s''', 
        ["%"+query+"%", mood, audience])
    elif kind == "media" and mood == "" and genre != "" and audience != "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
        where title like %s and genreTag=%s and audienceTag=%s''', 
        ["%"+query+"%", genre, audience])
    elif kind == "media" and mood != "" and genre != "" and audience != "":
        curs.execute('''select * from media inner join creator on (media.pID=creator.pID) inner join mediaInCollections 
        on (media.mediaID=mediaInCollections.mediaID) 
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

def insertCreator(conn, creator_name):
   '''Given creator name, inserts into database'''
   curs = dbi.dict_cursor(conn)
   curs.execute('''insert into creator(name)
                values (%s)''', 
                [creator_name])
   conn.commit()
   curs.execute('select last_insert_id()')
   return curs.fetchone()

def getAllUsers(conn):
    '''Returns a list of dictionaries containing the uid, name, and username of all users'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from user')
    return curs.fetchall()

def getAllMediaAndCreator(conn):
    '''Returns a list of dictionaries containing the  mediaID, title, releaseYear, type, pID,
        and name of all media associated with a creator'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select mediaID, title, releaseYear, type, media.pID, name 
                    from media left join creator on media.pID = creator.pID
                    order by title''')
    return curs.fetchall()

def insertCollection(conn, result, uID):
    '''Given a collection name and current uID, inserts a new collection in the collections table and
        returns an integer of the collectionID of the newly created collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('insert into collections(name, uID) values (%s, %s)', 
        [result['collectionName'], uID])
    conn.commit()
    curs.execute('select last_insert_id()')
    return curs.fetchone()

def getCollectionName(conn, cID):
    '''Given a collectionID, returns the name of that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name from collections where collectionID=%s', 
        [cID])
    return curs.fetchone()['name']

def getCreator(conn, pID): # may be deleted later
    '''Given a personID, returns the name of that creator'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name from creator where pID=%s',
        [pID])
    return curs.fetchone()

def get_media(conn, mediaID):
    '''Given a mediaID, returns the mediaID, title, releaseYear, type for that particular media'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from media where mediaID=%s;''',
        [mediaID])
    return curs.fetchone()

def updateName(conn, uid, name):
    '''Given a user's uid and their new desired name, updates the user's name'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''update user set name=%s where uid=%s''',
        [name, uid])
    conn.commit()

def getUserInfo(conn, username):
    '''Given a user's username, returns the user's name, username, and uid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, username, uid from user where username = %s;',
        [username])
    return curs.fetchone()

def getAllCollectionsByUserName(conn, username):
    '''Given a user's username, returns a list of dictionaries representing 
        all collections (collectionID, name, uID) made by that user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select collections.name as name, collectionID 
        from collections inner join user using (uid) 
        where username = %s;''',
        [username])
    return curs.fetchall()

def getAllCollections(conn, uID): #uID no longer hard coded
    '''Given a user's uID, returns a list of dictionaries representing
        all collections (collectionID, name, uID) made by that user'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from collections where uID = %s;',
        [uID])
    return curs.fetchall()

def getAllCreators(conn):
    '''returns a list of dictionaries representing all pID, 
        name from the creator table, sorted alphabetically'''
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from creator order by name;')
    return curs.fetchall()

def getMediaInCollection(conn, cID):
    '''Given a collectionID, returns a list of dictionaries representing
         all the media located within that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select title, mediaID, rating, review, moodTag, genreTag, audienceTag from media inner join mediaInCollections 
        using (mediaID) where collectionID = %s;''',
        [cID])
    return curs.fetchall()

def getMediaCreatorInCollection(conn, cID):
    '''Given a collectionID, returns a list of dictionaries representing
         all media with a creator in that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select media.mediaID, title, releaseYear, type, rating, review, moodTag, genreTag, audienceTag, name, media.pID
                from mediaInCollections join media on mediaInCollections.mediaID = media.mediaID
                left join creator on creator.pID = media.pID
                where collectionID = %s;''', [cID])
    return curs.fetchall()

def deleteCollection(conn, result):
    '''Given a collectionID, deletes that collection (available from user page)'''
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from collections where collectionID=%s',
        [result['collectionID']])
    conn.commit()

def deleteMediaFromCollection(conn, cID, result):
    '''Given a collectionID and mediaID, deletes that media from that collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('delete from mediaInCollections where collectionID=%s and mediaID=%s',
        [cID, result['mediaID']])
    conn.commit()

def updateMediaFromCollection(conn, cID, result):
    '''Given a collectionID and result, updates the media from the collection'''
    # replace any values to None if they are any empty string
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
    '''Given collectionID and all form data about media, inserts that media into the collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into mediaInCollections(mediaID, collectionID, rating, review, moodTag, genreTag, audienceTag)
        values (%s, %s, %s, %s, %s, %s, %s)''',
        [mediaID, cID, rating, review, moodTag, genreTag, audienceTag])
    conn.commit()

def getRatedMedia(conn, mediaID):
    """Given the mediaID, returns a list of dictionaries representing
        all rated media, ratings, reviews, tags"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from mediaInCollections where mediaID=%s''', [mediaID])
    return curs.fetchall()

def isUsersCollection(conn, uid, cID):
    '''Given a user's ID and a collection ID, returns a boolean value of 
    whether the collection belongs to the user.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from collections where uID=%s and collectionID=%s''', 
        [uid, cID])
    result = curs.fetchone()
    return result != None # returns True if collection belongs to user, otherwise False

def isMediaInCollection(conn, mediaID, cID):
    '''Given a mediaID and a collectionID, returns a boolean value of whether 
    the media is in the collection'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select title, mediaID, rating, review, moodTag, genreTag, audienceTag 
        from media inner join mediaInCollections 
        using (mediaID) where mediaID = %s and collectionID = %s;''',
        [mediaID, cID])
    result = curs.fetchone()
    return result != None
