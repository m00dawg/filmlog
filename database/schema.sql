CREATE TABLE Users (
    userID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    username varchar(64) NOT NULL,
    email varchar(255) NOT NULL,
    password varbinary(128) NOT NULL,
    UNIQUE email_uq (email),
    UNIQUE username_uq (username)
) ENGINE='InnoDB';

CREATE TABLE Files(
    fileID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    PRIMARY KEY (fileID, userID),
    CONSTRAINT Files_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID)
) ENGINE='InnoDB';

CREATE TABLE Cameras (
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
    name varchar(64) NOT NULL,
    PRIMARY KEY (userID, cameraID),
    UNIQUE user_name_eq (userID, name),
    CONSTRAINT Cameras_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Lenses(
    userID INT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY(userID, lensID),
    UNIQUE user_name_uq (userID, name),
    CONSTRAINT Lenses_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE CameraLenses(
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (userID, cameraID, lensID),
    CONSTRAINT CameraLenses_Cameras FOREIGN KEY (userID, cameraID) REFERENCES Cameras (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT CameraLenses_Lenses FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
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
    userID INT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    filmSize ENUM('35mm 24', '35mm 36', '35mm Hand Roll', '35mm 100\' Bulk Roll', '35mm Hand Rolled', '120', '220', '4x5', '8x10') NOT NULL,
    qty SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (userID, filmTypeID, filmSize),
    KEY filmtypeID_fk (filmTypeID),
    CONSTRAINT FilmStock_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FilmSTock_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Binders(
    userID INT UNSIGNED NOT NULL,
    binderID SMALLINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    projectCount TINYINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(userID, binderID),
    UNIQUE KEY user_name_uq (userID, name),
    CONSTRAINT Binders_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Projects(
    userID INT UNSIGNED NOT NULL,
    projectID SMALLINT UNSIGNED NOT NULL,
    binderID SMALLINT UNSIGNED NOT NULL,
    filmCount SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name varchar(64) NOT NULL,
    PRIMARY KEY(userID, projectID),
    UNIQUE KEY binder_name_uq (userID, binderID, name),
    CONSTRAINT Projects_Binders_fk FOREIGN KEY (userID, binderID) REFERENCES Binders (userID, binderID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Films (
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    projectID SMALLINT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED DEFAULT NULL,
    lensID SMALLINT UNSIGNED DEFAULT NULL,
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
    PRIMARY KEY (userID, filmID),
    UNIQUE KEY (userID, projectID, fileNo),
    UNIQUE KEY (userID, projectID, title),
    KEY films_projectID_fk (projectID),
    KEY films_cameraID_fk (cameraID),
    KEY films_filmTypeID_fk (filmTypeID),
    KEY lensID_fk (lensID),
    CONSTRAINT Films_projectID_fk FOREIGN KEY (userID, projectID) REFERENCES Projects (userID, projectID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_Cameras_fk FOREIGN KEY (userID, cameraID) REFERENCES Cameras (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_Lenses_fk FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

-- Both Roll and Sheet
CREATE TABLE Exposures(
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    lensID SMALLINT UNSIGNED DEFAULT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    shutter SMALLINT DEFAULT NULL,
    aperture DECIMAL(4,1) UNSIGNED DEFAULT NULL,
    flash ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    metering ENUM('Incident', 'Reflective') DEFAULT NULL,
    stability ENUM('Handheld', 'Tripod') DEFAULT NULL,
    subject VARCHAR(128) DEFAULT NULL,
    development VARCHAR(255) DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (userID, filmID, exposureNumber),
    KEY filmTypeID_idx (filmTypeID),
    KEY lensID_idx (lensID),
    KEY userID_idx (userID),
    CONSTRAINT Exposures_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_Films_fk FOREIGN KEY (userID, filmID) REFERENCES Films (userID, filmID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_Lenses_fk FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Filters(
    userID INT UNSIGNED NOT NULL,
    filterID TINYINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    code VARCHAR(8) NOT NULL,
    factor DECIMAL(4, 1) NOT NULL,
    ev DECIMAL(3,1) NOT NULL,
    PRIMARY KEY (userID, filterID),
    UNIQUE user_name (userID, name),
    UNIQUE user_code (userID, code),
    CONSTRAINT Filters_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE ExposureFilters(
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filterID TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (userID, filmID, exposureNumber, filterID),
    CONSTRAINT ExposureFilters_Exposures_fk FOREIGN KEY (userID, filmID, exposureNumber) REFERENCES Exposures (userID, filmID, exposureNumber) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ExposureFilters_Filters_fk FOREIGN KEY (userID, filterID) REFERENCES Filters (userID, filterID) ON DELETE RESTRICT ON UPDATE CASCADE
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

CREATE TABLE EnlargerLenses(
    enlargerLensID TINYINT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (enlargerLensID, userID),
    CONSTRAINT EnlargerLenses_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE ContactSheets(
    filmID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    fileID INT UNSIGNED DEFAULT NULL,
    paperID TINYINT UNSIGNED DEFAULT NULL,
    paperFilterID TINYINT UNSIGNED DEFAULT NULL,
    enlargerLensID TINYINT UNSIGNED DEFAULT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime SMALLINT UNSIGNED NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (filmID, userID),
    CONSTRAINT ContactSheets_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID),
    CONSTRAINT ContactSheets_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Prints (
    printID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    paperID TINYINT UNSIGNED DEFAULT NULL,
    paperFilterID TINYINT UNSIGNED DEFAULT NULL,
    enlargerLensID TINYINT UNSIGNED DEFAULT NULL
    fileID INT UNSIGNED DEFAULT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime TIME NOT NULL,
    printType ENUM('Enlargement', 'Contact') NOT NULL,
    size ENUM ('4x5', '4x6', '5x7', '8x10', '11x14', 'Other') NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, printID),
    KEY paperID_fk (paperID),
    KEY paperFilterID_fk (paperFilterID),
    KEY film_exposure_fk (filmID, exposureNumber),
    KEY user_film_exposure (userID, filmID, exposureNumber),
    CONSTRAINT prints_paperID_fk FOREIGN KEY (paperID) REFERENCES Papers (paperID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_paperFilterID_fk FOREIGN KEY (paperFilterID) REFERENCES PaperFilters (paperFilterID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Prints_Exposures_fk FOREIGN KEY (userID, filmID, exposureNumber) REFERENCES Exposures (userID, filmID, exposureNumber),
    CONSTRAINT Prints_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Prints_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE CASCADE ON UPDATE CASCADE;

) ENGINE='InnoDB';

-- Functions
DROP FUNCTION SECONDS_TO_DURATION;
DELIMITER //
CREATE FUNCTION SECONDS_TO_DURATION (inSeconds SMALLINT) RETURNS VARCHAR(8) DETERMINISTIC
BEGIN
    DECLARE minutes TINYINT UNSIGNED;             
    DECLARE seconds TINYINT UNSIGNED;
    SELECT ROUND(FLOOR(inSeconds / 60)) INTO minutes;
    SELECT inSeconds % 60 INTO seconds;
    IF minutes < 10
    THEN
        SELECT CONCAT('0', minutes) INTO minutes;
    END IF;
    IF seconds < 10
    THEN
        SELECT CONCAT('0', seconds) INTO seconds;
    END IF;
    RETURN CONCAT(IF(minutes < 10,CONCAT('0', minutes),minutes), ':',
        IF(seconds < 10,CONCAT('0', seconds), seconds));
END
//
DELIMITER ;

-- Triggers
DELIMITER //
CREATE TRIGGER ProjectCountIncrement
    BEFORE INSERT ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount + 1
            WHERE binderID = NEW.binderID
            AND userID = NEW.userID;
        END;
//
CREATE TRIGGER ProjectCountDecrement
    BEFORE DELETE ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount - 1
            WHERE binderID = OLD.binderID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER FilmCountIncrement
    BEFORE INSERT ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount + 1
            WHERE projectID = NEW.projectID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER FilmCountDecrement
    BEFORE DELETE ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount - 1
            WHERE projectID = OLD.projectID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER ExposureCountIncrement
    BEFORE INSERT ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures + 1
            WHERE filmID = NEW.filmID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER ExposureCountDecrement
    BEFORE DELETE ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures - 1
            WHERE filmID = OLD.filmID
            AND userID = OLD.userID;
        END;
//

DELIMITER ;

