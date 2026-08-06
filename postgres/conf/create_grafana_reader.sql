SELECT format('CREATE ROLE grafana_reader LOGIN PASSWORD %L', :'reader_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='grafana_reader')\gexec
SELECT format('ALTER ROLE grafana_reader PASSWORD %L', :'reader_password')\gexec
GRANT CONNECT ON DATABASE sofia TO grafana_reader;
GRANT USAGE ON SCHEMA public TO grafana_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_reader;
