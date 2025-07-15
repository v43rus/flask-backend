-- posts table
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT,
    author TEXT,
    points INTEGER,
    created_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW()
);

-- tags table
CREATE TABLE IF NOT EXISTS tags (
    tag TEXT NOT NULL,
    post_id TEXT REFERENCES posts(id),
    PRIMARY KEY (tag, post_id)
);

-- tag_statistics table
CREATE TABLE IF NOT EXISTS tag_statistics (
    tag TEXT NOT NULL,
    date DATE NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (tag, date)
);
