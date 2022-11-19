import cs304dbi as dbi

def do_search(conn, query, kind):
    curs = dbi.dict_cursor(conn)
    if kind == "username": 
        curs.execute('select * from user where username like %s or name like %s', 
        ["%"+query+"%", "%"+query+"%"])
    else: 
        curs.execute('select * from media where title like %s', 
        ["%"+query+"%"])
    return curs.fetchall()