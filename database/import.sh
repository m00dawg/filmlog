#!/bin/bash
DB="FilmLogDev"
mysql -Bse "DROP DATABASE $DB"
mysql -Bse "CREATE DATABASE $DB"
mysql $DB < schema.sql
mysql $DB < base-data.sql
mysql $DB < users.sql

