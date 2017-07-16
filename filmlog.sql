CREATE TABLE Cameras (
    cameraID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
    name varchar(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE FilmBrands(
    filmBrandID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name varchar(64) NOT NULL,
    UNIQUE name_uq (name)
) ENGINE='InnoDB';

INSERT INTO FilmBrands VALUES (1, 'Kodak');
INSERT INTO FilmBrands VALUES (2, 'Fuji');
INSERT INTO FilmBrands VALUES (3, 'Ilford');

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

INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Ektar', 100, 'Color Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Portra', 160, 'Color Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Portra', 400, 'Color Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Portra', 800, 'Color Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'T-Max', 100, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'T-Max', 400, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Tri-X', 320, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (1, 'Tri-X', 400, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (2, 'Velvia', 50, 'Color Slide');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (2, 'Velvia', 100, 'Color Slide');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (3, 'Delta', 100, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (3, 'Delta', 400, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (3, 'Delta', 3200, 'Black & White Negative');
INSERT INTO FilmTypes (filmBrandID, name, iso, kind) VALUES (3, 'HP5+', 400, 'Black & White Negative');

CREATE TABLE Films (
    filmID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    cameraID TINYINT UNSIGNED DEFAULT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    fileDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fileNo varchar(32) NOT NULL,
    title varchar(64) NOT NULL,
    development varchar(128) NOT NULL,
    KEY films_cameraID_fk (cameraID),
    KEY films_filmTypeID_fk (filmTypeID),
    CONSTRAINT films_cameraID_fk FOREIGN KEY (cameraID) REFERENCES Cameras (cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT films_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';
