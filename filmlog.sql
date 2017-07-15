CREATE TABLE Cameras (
    cameraID INT UNSIGNED NOT NULL PRIMARY KEY,
    filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
    name varchar(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE FilmTypes (
    fileTypeID SMALLINT UNSIGNED NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE Films (
    filmID INT UNSIGNED NOT NULL PRIMARY KEY,
    cameraID TINYINT UNSIGNED DEFAULT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    fileDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fileNo varchar(32) NOT NULL,
    title varchar(64) NOT NULL,
    development varchar(128) NOT NULL,
    KEY films_cameraID_fk (cameraID),
    KEY films_filmTypeID_fk (filmTypeID),
    CONSTRAINT films_cameraID_fk FOREIGN KEY (cameraID) REFERENCES Cameras (cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT films_filmTypeID_fk FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON DELETE RESTRICT ON UPDATE CASCDE
) ENGINE='InnoDB';
