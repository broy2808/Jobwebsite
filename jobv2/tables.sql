DROP TABLE IF EXISTS users;

CREATE TABLE users (
    ID INTEGER primary key AUTOINCREMENT,
    username VARCHAR(20) NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    image_file VARCHAR NOT NULL DEFAULT 'default.jpg',
    UNIQUE(username,email)
);


DROP TABLE IF EXISTS userprofile;

CREATE TABLE userprofile (
    username VARCHAR(20) PRIMARY KEY,
    firstname VARCHAR(30) NOT NULL,
    lastname VARCHAR(30) NOT NULL,
    city VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    country VARCHAR(30) NOT NULL,
    zipcode INT NOT NULL,
    degreename VARCHAR(40) NOT NULL,
    studyfield VARCHAR(40) NOT NULL,
    school VARCHAR(40) NOT NULL,
    gpa REAL,
    exp1  INT NOT NULL,
    resume1 BLOB,
    skillset BLOB
);

DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    ID INTEGER primary key AUTOINCREMENT,
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    summary BLOB,
    location VARCHAR(30),
    status varchar(50) NOT NULL DEFAULT "NotApplied"
);

DROP TABLE IF EXISTS jobsapplied;
CREATE TABLE jobsapplied (
    ID INTEGER,
    username VARCHAR(20),
    status varchar(50) NOT NULL DEFAULT "NotApplied",
    primary key(ID,username)
);

DROP TABLE IF EXISTS recruiters;

CREATE TABLE recruiters (
    ID INTEGER primary key AUTOINCREMENT,
    username VARCHAR(20) NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    image_file VARCHAR NOT NULL DEFAULT 'default.jpg',
    UNIQUE(username,email)
);