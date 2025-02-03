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

DROP PROCEDURE IF EXISTS check_condition;
CREATE PROCEDURE check_condition
AS
BEGIN
DECLARE @v_condition BIT;
SET @v_condition = 1;
IF @v_condition = 1
BEGIN
PRINT 'Condition is true';
END
ELSE
BEGIN
PRINT 'Condition is false';
END
END;

DROP PROCEDURE IF EXISTS return_out_param_without_result_sets;
CREATE PROCEDURE 
return_out_param_without_result_sets
@my_input VARCHAR(20),
@my_output INT OUTPUT
AS
BEGIN
 IF @my_input = 'give me 1'
    BEGIN
        SELECT @my_output = 1;
    END
    ELSE
    BEGIN
        SELECT @my_output = 0;
    END
END;