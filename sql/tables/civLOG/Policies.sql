CREATE TABLE Policies (
    game_id         VARCHAR(255) NOT NULL,
    turn            INT NOT NULL,
    player_id       TINYINT NOT NULL,
    action          VARCHAR(255) NOT NULL,
    policy          VARCHAR(255) NOT NULL,
    score           FLOAT,
    turns           INT,
    PRIMARY KEY (game_id, turn, player_id, action, policy)
);