CREATE TABLE Research (
    game_id VARCHAR(255),
    player_id INT,
    turn INT,
    action VARCHAR(255),
    tech VARCHAR(255),
    score FLOAT,
    boost VARCHAR(255),
    turns INT,
    PRIMARY KEY (game_id, player_id, turn, action, tech)
)