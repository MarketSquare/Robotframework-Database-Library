DROP PROCEDURE IF EXISTS no_params;
CREATE PROCEDURE no_params
AS
BEGIN
-- Do nothing
RETURN;
END;

DROP PROCEDURE IF EXISTS get_second_name;
CREATE PROCEDURE 
get_second_name
@person_first_name VARCHAR(20)
AS
BEGIN
SELECT LAST_NAME
FROM person
WHERE FIRST_NAME = @person_first_name;
RETURN;
END;

DROP PROCEDURE IF EXISTS get_all_second_names;
CREATE PROCEDURE get_all_second_names
AS
BEGIN
SELECT LAST_NAME FROM person;
RETURN;
END;

DROP PROCEDURE IF EXISTS get_all_first_and_second_names;
CREATE PROCEDURE get_all_first_and_second_names
AS
BEGIN
SELECT FIRST_NAME FROM person;
SELECT LAST_NAME FROM person;
RETURN;
END;