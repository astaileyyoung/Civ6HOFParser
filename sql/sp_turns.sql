CREATE PROCEDURE Turns()
BEGIN
    CREATE TEMPORARY TABLE CivStats (
        Turn                INT,
        Player_ID           INT,
        LeaderName          VARCHAR(255),
        CivilizationName    VARCHAR(255),
        Science             INT,
        Culture             INT,
        Faith               INT,
        Gold                INT
    );

    # Get Player IDs so that we can pull civ yields from the DataSetValues table
    WHILE NULL 
    BEGIN 
        

    END;

END;
