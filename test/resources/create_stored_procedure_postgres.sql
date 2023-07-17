DROP ROUTINE IF EXISTS no_params;
CREATE FUNCTION no_params()
RETURNS VOID
LANGUAGE plpgsql
AS
'
BEGIN
-- Do nothing
END
';

DROP ROUTINE IF EXISTS get_second_name;
CREATE FUNCTION
get_second_name (IN person_first_name VARCHAR(20),
OUT person_second_name VARCHAR(20))
LANGUAGE plpgsql
AS
'
BEGIN
SELECT LAST_NAME INTO person_second_name
FROM person
WHERE FIRST_NAME = person_first_name;
END
';

DROP ROUTINE IF EXISTS get_all_second_names;
CREATE FUNCTION
get_all_second_names()
RETURNS TABLE (second_names VARCHAR(20))
LANGUAGE plpgsql
AS
'
BEGIN
RETURN QUERY SELECT LAST_NAME FROM person;
END
';


DROP ROUTINE IF EXISTS get_all_first_and_second_names;
CREATE FUNCTION
get_all_first_and_second_names(result1 refcursor, result2 refcursor)
RETURNS SETOF refcursor
LANGUAGE plpgsql
AS
'
BEGIN
OPEN result1 FOR SELECT FIRST_NAME FROM person;
RETURN NEXT result1;
OPEN result2 FOR SELECT LAST_NAME FROM person;
RETURN NEXT result2;
END
';