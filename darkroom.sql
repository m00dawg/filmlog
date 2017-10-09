CREATE TABLE Prints (
    filmID int(10) unsigned NOT NULL,
    exposureNumber tinyint(3) unsigned NOT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    filter ENUM('00', '0', '1/2', '1', '1 1/2', '2', '2 1/2', '3', '3 1/2', '4', '4 1/2', '5') DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    time TIME NOT NULL,
    type ENUM('Enlargement', 'Contact') NOT NULL,
    width DECIMAL(3,1) NOT NULL,
    height DECIMAL(3,1) NOT NULL
) ENGINE='InnoDB';
