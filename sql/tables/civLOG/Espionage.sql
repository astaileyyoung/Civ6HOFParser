CREATE TABLE Espionage (
    game_id VARCHAR(255) NOT NULL,
    player_id INT NOT NULL,
    turn INT NOT NULL,
    city VARCHAR(255) NOT NULL,
    unitoperation_spy_listening_post FLOAT,
    unitoperation_spy_gain_sources FLOAT,
    unitoperation_spy_steal_tech_boost FLOAT,
    unitoperation_spy_great_work_heist FLOAT,
    unitoperation_spy_sabotage_production FLOAT,
    unitoperation_spy_siphon_funds FLOAT,
    unitoperation_spy_rec FLOAT,
    a FLOAT,
    b FLOAT,
    c FLOAT,
    d FLOAT,
    PRIMARY KEY (game_id, player_id, turn, city)
);