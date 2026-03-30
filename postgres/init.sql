-- postgres/init.sql
-- PAP/CHAP
CREATE TABLE radcheck (
    id serial PRIMARY KEY,
    username varchar(64) NOT NULL DEFAULT '',
    attribute varchar(64) NOT NULL DEFAULT '',
    op char(2) NOT NULL DEFAULT '==',
    value varchar(253) NOT NULL DEFAULT ''
);

-- Response
CREATE TABLE radreply (
    id serial PRIMARY KEY,
    username varchar(64) NOT NULL DEFAULT '',
    attribute varchar(64) NOT NULL DEFAULT '',
    op char(2) NOT NULL DEFAULT '=',
    value varchar(253) NOT NULL DEFAULT ''
);

-- Accounting
CREATE TABLE radacct (
    radacctid bigserial PRIMARY KEY,
    acctsessionid varchar(64) NOT NULL DEFAULT '',
    username varchar(64) NOT NULL DEFAULT '',
    nasipaddress inet NOT NULL,
    acctstarttime timestamp with time zone,
    acctstoptime timestamp with time zone,
    acctsessiontime interval,
    acctinputoctets bigint,
    acctoutputoctets bigint
);
