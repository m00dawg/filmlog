USE FilmLogDev;

INSERT INTO FilmBrands VALUES (1, 'Kodak');
INSERT INTO FilmBrands VALUES (2, 'Fuji');
INSERT INTO FilmBrands VALUES (3, 'Ilford');

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


INSERT INTO Projects (name) VALUES ('Black and White Practice');
INSERT INTO Projects (name) VALUES ('Medium Format Practice');
INSERT INTO Projects (name) VALUES ('Alaska 2017');

INSERT INTO Cameras VALUES (1, 'Nikon N80', '35mm');
INSERT INTO Cameras VALUES (2, 'Mamiya 645 1000s', '120');

INSERT INTO Lenses VALUES (1, 'Nikon 50mm');
INSERT INTO Lenses VALUES (2, 'Mamiya 80mm f/2.4');

INSERT INTO CameraLenses VALUES (1, 1);
INSERT INTO CameraLenses VALUES (2, 2);


INSERT INTO Films (projectID, cameraID, filmTypeID, iso, fileNo, title, development, notes)
VALUES (1, 1, 1, 100, 'test1', 'Test 1', 'ID-11', 'Some sample notes going here.');

INSERT INTO Filters VALUES (1, 'Circular Polarizer', 'CP');
INSERT INTO Filters vALUES (2, 'Yellow 8', 'YEL8');
INSERT INTO Filters VALUES (3, 'Red 25', 'RED25');

INSERT INTO Exposures VALUES (1, 1, 1, '125', 8);
INSERT INTO ExposureFilters VALUES (1, 1, 1);
INSERT INTO ExposureFilters VALUES (1, 1, 2);
INSERT INTO Exposures VALUES (1, 2, 1, '250', 16);
INSERT INTO ExposureFilters VALUES (1, 1, 3);
INSERT INTO Exposures VALUES (1, 3, 1, '1000', 5.8);
INSERT INTO Exposures VALUES (1, 4, 1, '0', 5.8);
INSERT INTO Exposures VALUES (1, 5, 1, '-1', 5.8);
