-- 1. radcheck: Stores user credentials (username and password)
CREATE TABLE IF NOT EXISTS radcheck (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT 'Crypt-Password',
    op CHAR(2) NOT NULL DEFAULT ':=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 2. radreply: Stores specific attributes to return to a user
CREATE TABLE IF NOT EXISTS radreply (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op CHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 3. radusergroup: Links users to groups (e.g., 'kerem' belongs to 'admin')
CREATE TABLE IF NOT EXISTS radusergroup (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 1
);

-- 4. radgroupreply: Stores attributes assigned to a group (e.g., VLAN10 for 'admin')
CREATE TABLE IF NOT EXISTS radgroupreply (
    id SERIAL PRIMARY KEY,
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op CHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 5. radacct: Stores Accounting records (session start/stop, data usage)
CREATE TABLE IF NOT EXISTS radacct (
    radacctid BIGSERIAL PRIMARY KEY,
    acctsessionid VARCHAR(64) NOT NULL DEFAULT '',
    acctuniqueid VARCHAR(32) NOT NULL DEFAULT '',
    username VARCHAR(64) NOT NULL DEFAULT '',
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    nasipaddress INET NOT NULL,
    nasportid VARCHAR(32) DEFAULT NULL,
    acctstarttime TIMESTAMP WITH TIME ZONE,
    acctupdatetime TIMESTAMP WITH TIME ZONE,
    acctstoptime TIMESTAMP WITH TIME ZONE,
    acctsessiontime BIGINT DEFAULT NULL,
    acctinputoctets BIGINT DEFAULT NULL,
    acctoutputoctets BIGINT DEFAULT NULL,
    callingstationid VARCHAR(120) DEFAULT '',
    framedipaddress INET DEFAULT NULL
);

-- INSERTING TEST DATA FOR DEMO --
-- 1. Add Users with Bcrypt Hashes
INSERT INTO radcheck (username, attribute, op, value) VALUES 
('kerem', 'Crypt-Password', ':=', '$2a$12$h010wbrxBjD0HZCeoptnhu.uWcVR.dwvpnwYSw0stGml9TtnJ7byG'), -- secure1234
('mert', 'Crypt-Password', ':=', '$2a$12$T.zb8uBqHMK0kQE5JPBmqugC6k9zje7vCMqw8BjjEtPAYTc4S4AM6'); -- secure123

-- 2. Define Groups (VLAN Assignments)
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES 
('employee_group', 'Tunnel-Private-Group-Id', ':=', '10'), -- VLAN 10
('guest_group', 'Tunnel-Private-Group-Id', ':=', '20');    -- VLAN 20

-- 3. Assign Users to Groups
INSERT INTO radusergroup (username, groupname) VALUES 
('kerem', 'employee_group'),
('mert', 'guest_group');