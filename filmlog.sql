CREATE TABLE Cameras (
    cameraID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
    name varchar(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE Lenses(
    lensID SMALLINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name VARCHAR(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE CameraLenses(
    cameraID TINYINT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (cameraID, lensID),
    KEY lensID_idx (lensID),
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
    kind ENUM ('Color Negative', 'Black & White Negative', 'Color Slide'),
    UNIQUE brand_name_iso_uq (filmBrandID, name, iso),
    KEY filmtypes_filmBrandID_fk (filmBrandID),
    CONSTRAINT filmtypes_filmBrandID FOREIGN KEY (filmBrandID) REFERENCES FilmBrands (filmBrandID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Binders(
    binderID SMALLINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    binderCode varchar(32) NOT NULL,
    name varchar(64) NOT NULL,
    startDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    endDate TIMESTAMP NULL
) ENGINE='InnoDB';

CREATE TABLE Projects(
    projectID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    binderID SMALLINT UNSIGNED NOT NULL,
    filmCount TINYINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name varchar(64) NOT NULL,
    UNIQUE KEY name_uq (name),
    KEY projects_binderID_fk (binderID),
    CONSTRAINT projects_binderID_fk FOREIGN KEY (binderID) REFERENCES Binders (binderID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Films (
    filmID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,    
    projectID INT UNSIGNED NOT NULL,
    cameraID TINYINT UNSIGNED DEFAULT NULL,
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
    CONSTRAINT films_projectID_fk FOREIGN KEY (projectID) REFERENCES Projects (projectID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT films_cameraID_fk FOREIGN KEY (cameraID) REFERENCES Cameras (cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT films_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Exposures(
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    lensID SMALLINT UNSIGNED DEFAULT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    shutter SMALLINT DEFAULT NULL,
    aperture DECIMAL(4,1) UNSIGNED DEFAULT NULL,
    flash ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    metering ENUM('Incident', 'Reflective') DEFAULT NULL,
    subject VARCHAR(128) DEFAULT NULL,
    developed VARCHAR(255) DEFAULT NULL,
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
    factor DECIMAL(4, 1) NOT NULL
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

-- Triggers
DELIMITER //
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
    BEFORE DELETE ON Exposues
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures - 1 WHERE filmID = OLD.filmID;
        END;
//

DELIMITER ;
