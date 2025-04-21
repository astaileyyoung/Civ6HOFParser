CREATE TABLE CityBuild (
    game_id                 VARCHAR(255) NOT NULL,
    turn                    INT NOT NULL,
    player_id               TINYINT NOT NULL,
    city                    VARCHAR(255) NOT NULL,
    production_added        FLOAT,
    current_item            VARCHAR(255),
    current_production      FLOAT,
    production_needed       INT,
    overflow                FLOAT,
    PRIMARY KEY (game_id, turn, city, production_added, player_id)
);