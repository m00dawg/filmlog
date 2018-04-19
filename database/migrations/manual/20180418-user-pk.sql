set foreign_key_checks=0;
insert into Users SELECT * FROM FilmLog.Users;
INSERT INTO Binders SELECT 1, binderId, name, projectCount, createdOn FROM FilmLog.Binders;
insert into CameraLenses SELECT 1, cameraID, lensID FROM FilmLog.CameraLenses;
INSERT INTO Cameras SELECT 1, cameraID, filmSize, name FROM FilmLog.Cameras;
INSERT INTO ExposureFilters SELECT 1, filmID, exposureNumber, filterID FROM FilmLog.ExposureFilters;
INSERT INTO Exposures SELECT 1, filmID, exposureNumber, filmTypeID, lensID, iso, shutter, aperture,flash,metering,NULL,subject,development,notes FROM FilmLog.Exposures;
INSERT INTO FilmBrands SELECT * FROM FilmLog.FilmBrands;
INSERT INTO FilmStock SELECT * FROM FilmLog.FilmStock;
INSERT INTO FilmTypes SELECT * FROM FilmLog.FilmTypes;
INSERT INTO Films SELECT 1, filmID, projectID, cameraID, NULL, filmTypeID, iso, fileDate, loaded, unloaded, developed,exposures, fileNo, title,development,notes FROM FilmLog.Films;
INSERT INTO Filters SELECT 1, filterID, name, code, factor, ev FROM FilmLog.Filters;
INSERT INTO Lenses SELECT 1, lensID, name FROM FilmLog.Lenses;
INSERT INTO PaperBrands SELECT * FROM FilmLog.PaperBrands;
INSERT INTO PaperFilters SELECT * FROM FilmLog.PaperFilters;
INSERT INTO Papers SELECT * FROM FilmLog.Papers;
INSERT INTO Projects SELECT 1, projectID, binderID, filmCount, createdOn, name FROM FilmLog.Projects;

