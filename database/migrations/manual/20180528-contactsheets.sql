ALTER TABLE ContactSheets 
MODIFY COLUMN paperID tinyint unsigned DEFAULT NULL,
MODIFY COLUMN paperFilterID tinyint unsigned DEFAULT NULL,
MODIFY COLUMN fileID INT UNSIGNED DEFAULT NULL;

ALTER TABLE Prints
MODIFY COLUMN paperID tinyint unsigned DEFAULT NULL,
MODIFY COLUMN paperFilterID tinyint unsigned DEFAULT NULL,
MODIFY COLUMN size ENUM ('4x5', '4x6', '5x7', '8x10', '11x14', 'Other') NOT NULL;

ALTER TABLE Prints
ADD COLUMN fileID INT UNSIGNED DEFAULT NULL AFTER paperFilterID;

ALTER TABLE Prints
ADD CONSTRAINT Prints_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Prints ADD INDEX index_tmp (userID, filmID, exposureNumber, printID);
ALTER TABLE Prints DROP PRIMARY KEY;
ALTER TABLE Prints ADD PRIMARY KEY (userID, printID);
ALTER TABLE Prints ADD INDEX user_film_exposure (userID, filmID, exposureNumber);
ALTER TABLE Prints DROP INDEX index_tmp;

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
