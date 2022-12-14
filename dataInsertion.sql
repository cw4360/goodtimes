use goodtime_db;

-- populating media table to have starter data

insert into media(title, releaseYear, type)
values ('Pride & Prejudice', 2005, 'movie');

insert into media(title, releaseYear, type)
values ('A Sun', 2019, 'movie');

insert into media(title, releaseYear, type)
values ('Hades', 2018, 'game');

insert into media(title, releaseYear, type)
values ('Chicory: A Colorful Tale', 2021, 'game');

insert into media(title, releaseYear, type)
values ('Cloud Atlas', 2004, 'book');

insert into media(title, releaseYear, type)
values ('The Lightning Thief', 2005, 'book');

insert into media(title, releaseYear, type)
values ('The Sandman', 2022, 'tv');

insert into media(title, releaseYear, type)
values ('Squid Game', 2021, 'tv');

insert into media(title, releaseYear, type)
values ('Animal Farm', 2022, 'music');

insert into media(title, releaseYear, type)
values ('Dream Girl Evil', 2022, 'music');


-- populating user table with example users

insert into user(name, username, password)
values ('Rik Sampson', 'es1', '123');

insert into user(name, username, password)
values ('Audrey Liang', 'al118', '123');

insert into user(name, username, password)
values ('Catherine Wang', 'cw4', '123');

--populating creator table with directors from wmdb
insert into creator(pID, name)
select nm, name from wmdb.person where nm >20;

--populating media table with movies from the wmdb
insert into media(mediaID, title, releaseYear, pID)
select tt, title, `release`, director from wmdb.movie where director!=0 and tt!=1454468;
update media set type = 'movie' where mediaID > 40;
