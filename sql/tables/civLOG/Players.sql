CREATE TABLE Players (
    game_id VARCHAR(255),
    player_id INT,
    civilization VARCHAR(255),
    leader VARCHAR(255),
    civilization_type VARCHAR(255),
    player_type VARCHAR(255),
    PRIMARY KEY (game_id, player_id)
);