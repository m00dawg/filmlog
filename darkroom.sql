DROP TABLE IF EXISTS Prints;
DROP TABLE IF EXISTS PaperFilters;

CREATE TABLE PaperFilters(
    filterID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name varchar(8) NOT NULL
) ENGINE='InnoDB';

INSERT INTO PaperFilters (name) VALUES ('00');
INSERT INTO PaperFilters (name) VALUES ('0');
INSERT INTO PaperFilters (name) VALUES ('1/2');
INSERT INTO PaperFilters (name) VALUES ('1');
INSERT INTO PaperFilters (name) VALUES ('1 1/2');
INSERT INTO PaperFilters (name) VALUES ('2');
INSERT INTO PaperFilters (name) VALUES ('2 1/2');
INSERT INTO PaperFilters (name) VALUES ('3');
INSERT INTO PaperFilters (name) VALUES ('3 1/2');
INSERT INTO PaperFilters (name) VALUES ('4');
INSERT INTO PaperFilters (name) VALUES ('4 1/2');
INSERT INTO PaperFilters (name) VALUES ('5');

CREATE TABLE Prints (
    printID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber tinyint(3) unsigned NOT NULL,
    filterID TINYINT UNSIGNED NOT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime TIME NOT NULL,
    printType ENUM('Enlargement', 'Contact') NOT NULL,
    width DECIMAL(3,1) NOT NULL,
    height DECIMAL(3,1) NOT NULL,
    notes TEXT DEFAULT NULL
) ENGINE='InnoDB';
