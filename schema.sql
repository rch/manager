drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  resid string not null unique,
  title string not null unique,
  text string not null
);

drop table if exists attachments;
create table attachments (
  id integer primary key autoincrement,
  resid string not null,
  title string not null,
  filename string not null,
  foreign key(resid) references entries(resid)
);
