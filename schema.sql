drop table if exists Users;
drop table if exists LoginUsers;
drop table if exists Messages;

create table Users(
  email varchar(120) PRIMARY KEY NOT NULL UNIQUE,
  password varchar(120),
  first_name varchar(120),
  family_name varchar(120),
  gender varchar(12),
  city varchar(120),
  country varchar(120)
);

create table LoginUsers(
  email varchar(120),
  token varchar(120)
);

create table Messages(
  fromEmail VARCHAR(120),
  toEmail VARCHAR(120),
  message VARCHAR(360), 
  latitude VARCHAR(360),
  longitude VARCHAR(360),
  messageId INTEGER PRIMARY KEY autoincrement
);