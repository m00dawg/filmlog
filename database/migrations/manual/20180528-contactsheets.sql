ALTER TABLE ContactSheets 
MODIFY COLUMN paperID tinyint unsigned DEFAULT NULL,
MODIFY COLUMN paperFilterID tinyint unsigned DEFAULT NULL;

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
