CREATE TABLE Users (
    userID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    username varchar(64) NOT NULL,
    email varchar(255) NOT NULL,
    password varbinary(128) NOT NULL,
    UNIQUE email_uq (email),
    UNIQUE username_uq (username)
) ENGINE='InnoDB';

CREATE TABLE Cameras (
    cameraID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    userID INT UNSIGNED NOT NULL,
    filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
    name varchar(64) NOT NULL,
    KEY userID_fk (userID),
    CONSTRAINT Cameras_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Lenses(
    lensID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name VARCHAR(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE CameraLenses(
    cameraID INT UNSIGNED NOT NULL,
    lensID INT UNSIGNED NOT NULL,
    PRIMARY KEY (cameraID, lensID),
    KEY lensID_fk (lensID),
    CONSTRAINT CameraLenses_cameraID FOREIGN KEY (cameraID) REFERENCES Cameras (cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT CameraLenses_lensID FOREIGN KEY (lensID) REFERENCES Lenses (lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmBrands(
    filmBrandID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    brand varchar(64) NOT NULL,
    UNIQUE brand_uq (brand)
) ENGINE='InnoDB';

CREATE TABLE FilmTypes (
    filmTypeID SMALLINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmBrandID TINYINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    iso smallint unsigned,
    kind ENUM ('Color Negative', 'Black & White Negative', 'Color Slide', 'Black & White Slide'),
    UNIQUE brand_name_iso_uq (filmBrandID, name, iso),
    KEY filmtypes_filmBrandID_fk (filmBrandID),
    CONSTRAINT filmtypes_filmBrandID FOREIGN KEY (filmBrandID) REFERENCES FilmBrands (filmBrandID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmStock(
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    filmSize ENUM('35mm 24', '35mm 36', '35mm 100\' Bulk Roll', '35mm Hand Rolled', '120', '220', '4x5', '8x10') NOT NULL,
    qty SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (filmTypeID, filmSize),
    CONSTRAINT filmstock_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Binders(
    binderID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    userID INT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    projectCount TINYINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY user_name_uq (userID, name),
    KEY userID_fk (userID),
    CONSTRAINT Binders_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Projects(
    projectID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    binderID INT UNSIGNED NOT NULL,
    filmCount SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name varchar(64) NOT NULL,
    UNIQUE KEY binder_name_uq (binderID, name),
    KEY projects_binderID_fk (binderID),
    CONSTRAINT projects_binderID_fk FOREIGN KEY (binderID) REFERENCES Binders (binderID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Films (
    filmID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,    
    projectID INT UNSIGNED NOT NULL,
    cameraID INT UNSIGNED DEFAULT NULL,
    lensID INT UNSIGNED DEFAULT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    iso SMALLINT UNSIGNED NOT NULL,
    fileDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    loaded TIMESTAMP NULL,
    unloaded TIMESTAMP NULL,
    developed TIMESTAMP NULL,
    exposures TINYINT UNSIGNED NOT NULL DEFAULT 0,
    fileNo varchar(32) NOT NULL,
    title varchar(64) NOT NULL,
    development varchar(255) DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    UNIQUE KEY (projectID, fileNo),
    UNIQUE KEY (projectID, title),
    KEY films_projectID_fk (projectID),
    KEY films_cameraID_fk (cameraID),
    KEY films_filmTypeID_fk (filmTypeID),
    KEY lensID_fk (lensID),
    CONSTRAINT Films_projectID_fk FOREIGN KEY (projectID) REFERENCES Projects (projectID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_cameraID_fk FOREIGN KEY (cameraID) REFERENCES Cameras (cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_lensID_fk FOREIGN KEY (lensID) REFERENCES Lenses (lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

-- Both Roll and Sheet
CREATE TABLE Exposures(
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    lensID INT UNSIGNED DEFAULT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    shutter SMALLINT DEFAULT NULL,
    aperture DECIMAL(4,1) UNSIGNED DEFAULT NULL,
    flash ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    metering ENUM('Incident', 'Reflective') DEFAULT NULL,
    stability ENUM('Handheld', 'Tripod') DEFAULT NULL,
    subject VARCHAR(128) DEFAULT NULL,
    development VARCHAR(255) DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (filmID, exposureNumber),
    KEY filmTypeID_idx (filmTypeID),
    KEY lensID_idx (lensID),
    CONSTRAINT Exposures_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_filmID_fk FOREIGN KEY (filmID) REFERENCES Films (filmID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_lensID_fk FOREIGN KEY (lensID) REFERENCES Lenses (lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Filters(
    filterID SMALLINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    code VARCHAR(8) NOT NULL,
    factor DECIMAL(4, 1) NOT NULL,
    ev DECIMAL(3,1) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE ExposureFilters(
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filterID SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (filmID, exposureNumber, filterID),
    KEY filterID_idx (filterID),
    CONSTRAINT ExposureFilters_filmID_fk FOREIGN KEY (filmID, exposureNumber) REFERENCES Exposures (filmID, exposureNumber) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ExposureFilters_filterID_fk FOREIGN KEY (filterID) REFERENCES Filters (filterID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

-- Darkroom
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
    name varchar(12) NOT NULL
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
    exposureNumber TINYINT UNSIGNED NOT NULL,
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
    KEY film_exposure_fk (filmID, exposureNumber),
    CONSTRAINT prints_paperID FOREIGN KEY (paperID) REFERENCES Papers (paperID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_paperFilterID FOREIGN KEY (paperFilterID) REFERENCES PaperFilters (paperFilterID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_film_exposure FOREIGN KEY (filmID, exposureNumber) REFERENCES Exposures (filmID, exposureNumber)
) ENGINE='InnoDB';

-- Triggers
DELIMITER //
CREATE TRIGGER ProjectCountIncrement
    BEFORE INSERT ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount + 1
            WHERE binderID = NEW.binderID;
        END;
//
CREATE TRIGGER ProjectCountDecrement
    BEFORE DELETE ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount - 1
            WHERE binderID = OLD.binderID;
        END;
//

CREATE TRIGGER FilmCountIncrement
    BEFORE INSERT ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount + 1 WHERE projectID = NEW.projectID;
        END;
//

CREATE TRIGGER FilmCountDecrement
    BEFORE DELETE ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount - 1 WHERE projectID = OLD.projectID;
        END;
//

CREATE TRIGGER ExposureCountIncrement
    BEFORE INSERT ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures + 1 WHERE filmID = NEW.filmID;
        END;
//

CREATE TRIGGER ExposureCountDecrement
    BEFORE DELETE ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures - 1 WHERE filmID = OLD.filmID;
        END;
//

DELIMITER ;



