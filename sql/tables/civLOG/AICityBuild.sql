CREATE TABLE AICityBuild (
    game_id                 VARCHAR(255) NOT NULL,
    turn                    INT NOT NULL,
    player_id               TINYINT NOT NULL,
    city                    VARCHAR(255) NOT NULL,
    food_adv                VARCHAR(255),
    prod_adv                VARCHAR(255),
    construct               VARCHAR(255),
    food                    VARCHAR(255),
    production              VARCHAR(255),
    gold                    VARCHAR(255),
    science                 VARCHAR(255),
    culture                 VARCHAR(255),
    faith                   VARCHAR(255)   
);