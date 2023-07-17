CREATE OR REPLACE PROCEDURE
no_params AS
BEGIN
DBMS_OUTPUT.PUT_LINE('Hello, World!');
END;

CREATE OR REPLACE PROCEDURE 
get_second_name (person_first_name IN VARCHAR, person_second_name OUT VARCHAR) AS
BEGIN
SELECT last_name
INTO person_second_name
FROM person
WHERE first_name = person_first_name;
END;

CREATE OR REPLACE PROCEDURE 
get_all_second_names (second_names_cursor OUT SYS_REFCURSOR) AS
BEGIN
OPEN second_names_cursor for
SELECT LAST_NAME FROM person;
END;

-- parsing the SQL file fails because of the semicolon before the opening of the second cursor
-- , but it's needed
CREATE OR REPLACE PROCEDURE
get_all_first_and_second_names (first_names_cursor OUT SYS_REFCURSOR, second_names_cursor OUT SYS_REFCURSOR) AS
BEGIN
OPEN first_names_cursor for
SELECT FIRST_NAME FROM person;
OPEN second_names_cursor for
SELECT LAST_NAME FROM person;
END;