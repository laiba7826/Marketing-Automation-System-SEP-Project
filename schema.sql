DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS contacts;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    phone TEXT
);

CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    budget REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    message TEXT NOT NULL,
    role TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: Demo users are now handled in init_db.py

INSERT INTO campaigns (title, status, budget) VALUES 
('Q1 Product Launch', 'Planning', 50000.00),
('Social Media Blitz', 'Approved', 15000.00);

DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

INSERT INTO settings (key, value) VALUES ('theme', 'default');

DROP TABLE IF EXISTS budget_requests;
CREATE TABLE budget_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    proposed_by TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    counter_amount REAL,
    progress INTEGER DEFAULT 0,
    assigned_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES users (id)
);

-- Sample budget requests
INSERT INTO budget_requests (title, type, amount, proposed_by, status) VALUES 
('Summer Sale 2025', 'Campaign', 8000.0, 'Marketing Team', 'Pending'),
('Influencer Outreach Q3', 'Influencer', 4500.0, 'Content Creator', 'Pending');

DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    sender_name TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    receiver_role TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    platform TEXT NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT DEFAULT 'Drafting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS campaign_strategies;
CREATE TABLE campaign_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES budget_requests (id),
    FOREIGN KEY (creator_id) REFERENCES users (id)
);

-- Demo data moved to init_db.py

DROP TABLE IF EXISTS leads;
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT DEFAULT 'New',
    revenue REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demo data moved to init_db.py

DROP TABLE IF EXISTS site_content;
CREATE TABLE site_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page TEXT NOT NULL,
    section TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    UNIQUE(page, section, key)
);

DROP TABLE IF EXISTS site_features;
CREATE TABLE site_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS site_roles;
CREATE TABLE site_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    icon TEXT NOT NULL,
    description TEXT NOT NULL,
    permissions TEXT NOT NULL -- Semi-colon separated list
);

DROP TABLE IF EXISTS site_tech_stack;
CREATE TABLE site_tech_stack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL
);


DROP TABLE IF EXISTS site_steps;
CREATE TABLE site_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS training_sessions;
CREATE TABLE training_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_name TEXT NOT NULL,
    schedule_date TEXT NOT NULL,
    workshop_purpose TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

