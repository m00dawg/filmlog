DROP TABLE IF EXISTS Prints;
DROP TABLE IF EXISTS Papers;
DROP TABLE IF EXISTS PaperFilters;
DROP TABLE IF EXISTS PaperBrands;

CREATE TABLE PaperBrands(
    paperBrandID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name varchar(32) NOT NULL,
    UNIQUE name_iq (name)
) ENGINE='InnoDB';

INSERT INTO PaperBrands (name) VALUES ('Ilford');

CREATE TABLE Papers(
    paperID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    paperBrandID TINYINT UNSIGNED NOT NULL,
    type ENUM('Resin Coated', 'Fibre Base', 'Cotton Rag'),
    grade ENUM('Multi', 'Fixed'),
    surface ENUM('Glossy', 'Pearl', 'Satin', 'Semi-Matt', 'Matt'),
    tone ENUM('Cool', 'Neutral', 'Warm'),
    name varchar(64),
    KEY paperBrandID_fk (paperBrandID),
    CONSTRAINT papers_paperBrandID FOREIGN KEY (paperBrandID) REFERENCES PaperBrands (paperBrandID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

INSERT INTO Papers (paperBrandID, type, grade, surface, tone, name)
VALUES (1, 'Resin Coated', 'Multi', 'Satin', 'Neutral', 'MULTIGRADE IV RC DELUXE Satin');

CREATE TABLE PaperFilters(
    paperFilterID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
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
INSERT INTO PaperFilters (name) VALUES ('Split-Grade');

CREATE TABLE Prints (
    printID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber tinyint(3) unsigned NOT NULL,
    paperID TINYINT UNSIGNED NOT NULL,
    paperFilterID TINYINT UNSIGNED NOT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime TIME NOT NULL,
    printType ENUM('Enlargement', 'Contact') NOT NULL,
    size ENUM('4x5', '5x7', '8x10'),
    notes TEXT DEFAULT NULL,
    KEY paperID_fk (paperID),
    KEY paperFilterID_fk (paperFilterID),
    KEY film_exposure_idx (filmID, exposureNumber),
    CONSTRAINT prints_paperID FOREIGN KEY (paperID) REFERENCES Papers (paperID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_paperFilterID FOREIGN KEY (paperFilterID) REFERENCES PaperFilters (paperFilterID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_film_exposure FOREIGN KEY (filmID, exposureNumber) REFERENCES Exposures (filmID, exposureNumber)
) ENGINE='InnoDB';
