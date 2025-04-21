DELIMITER //

CREATE PROCEDURE civDW.CreateTurns()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE n INT DEFAULT 1;
    DECLARE category VARCHAR(255);
    DECLARE done BOOLEAN DEFAULT FALSE;
    DECLARE dataset_cursor CURSOR FOR
        SELECT DISTINCT(`DataSet`) AS `Category`
        FROM `civDW`.`Yields`;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    CREATE TABLE IF NOT EXISTS civDW.Turns (
        GameId              INT,
        Turn                INT,
        DataSet             VARCHAR(255)
        PRIMARY KEY(GameId, Turn)       
    );
    TRUNCATE TABLE civDW.Turns;

    OPEN dataset_cursor;
    WHILE i <= 130 DO
        SET done = FALSE;
        FETCH dataset_cursor INTO category;
        read_loop: LOOP
        IF done THEN
            LEAVE read_loop;
        END IF;
        INSERT INTO civDW.Turns (GameId, Turn, DataSet) VALUES (1, i, category);
    END LOOP read_loop;
    CLOSE dataset_cursor;

    
        SET i = i + 1;
    END WHILE;
    CLOSE dataset_cursor;

END //
DELIMITER ;
