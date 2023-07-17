DROP PROCEDURE IF EXISTS no_params;
CREATE PROCEDURE 
no_params()
BEGIN
-- Do nothing
END;

DROP PROCEDURE IF EXISTS get_second_name;
CREATE PROCEDURE 
get_second_name (IN person_first_name VARCHAR(20),
OUT person_second_name VARCHAR(20))
BEGIN
SELECT LAST_NAME
INTO person_second_name
FROM person
WHERE FIRST_NAME = person_first_name;
END;

DROP PROCEDURE IF EXISTS get_all_second_names;
CREATE PROCEDURE get_all_second_names()
BEGIN
SELECT LAST_NAME FROM person;
END;

DROP PROCEDURE IF EXISTS get_all_first_and_second_names;
CREATE PROCEDURE get_all_first_and_second_names()
BEGIN
SELECT FIRST_NAME FROM person;
SELECT LAST_NAME FROM person;
END;