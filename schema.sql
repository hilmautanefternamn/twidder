create table user(
  firstname varchar(100),
  familyname varchar(100),
  gender varchar(10),
  city varchar(50),
  country varchar(50),
  email varchar(50),
  password varchar(50),
  primary key(email)
  );

create table messages(
  toEmail varchar(50),
  fromEmail varchar(50),
  message varchar(280)
);

create table loggedin_user(
  token varchar(50),
  email varchar(50),
  primary key(token)
);
