CREATE TABLE Score (
    game_id VARCHAR(255) NOT NULL,
    player_id INT NOT NULL,
    category_civics INT,
    category_empire INT,
    category_great_people INT,
    category_religion INT,
    category_tech INT,
    category_wonder INT, 
    category_trade INT,
    category_pillage INT,
    category_income INT,
    category_scenario1 INT,
    category_scenario2 INT,
    category_scenario3 INT,
    category_e INT,
    PRIMARY KEY (game_id, player_id)
);