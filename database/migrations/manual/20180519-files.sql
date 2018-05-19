

CREATE TABLE Files(
    fileID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    PRIMARY KEY (fileID, userID),
    CONSTRAINT Files_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID)
) ENGINE='InnoDB';

CREATE TABLE ContactSheets(
    filmID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    fileID INT UNSIGNED NOT NULL,
    paperID TINYINT UNSIGNED NOT NULL,
    paperFilterID TINYINT UNSIGNED NOT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime TIME NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (filmID, userID),
    CONSTRAINT ContactSheets_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID)
)
