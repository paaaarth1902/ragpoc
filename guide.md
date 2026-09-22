1. Gt init to initialise the repo
2. Skeleton implementation - Folder Structure
3. Creating init files inside all folders so python ships this dirs as packages
4. Creating gitignore, env and env.template 
5. Since using PostgreSQL and pgvector, prepare the toml file, install dependencies using uv and the docker compose
6. Run `docker compose exec db psql -U ragpoc -d ragpoc -c "Select 1;"` 
7. Configure the config file and one health chekpoint in health.py and call it via router in main.py
8. Commit it to main.

----------------------------------------------------------------------------------------------------------------------

1. Create new branch wherein, work SQLAlchemy models, schemas and migration logic will be pushed
2. Configure a session file that will setup AsyncSession (creates short lived sessions based on demand) with the help of AsynEngine (creates connection pool) - which basicaly opens 5 connections with database to and from which data can travel as needed and whenever we need to establish connection, we will invoke get_db_session via DI
3. Configure models file with ORM mappings for 3 tables - Documents, Document chunks, Ingestion jobs
4. Setup alembic migrations after creating the models to actually create the table in our database, provided to use by docker in one of its container
5. Import Vector from pgvector.sqlalchey in the env file
6. Set up migrations by running uv run alembic upgrade head
7. Create vector extension in DB before we create any table, with `upgrade()` along with Custom Vector & Full-Text Search Indexes (in this oder)
8. Check tables created or not and if downgrade is also working
9. Implement readiness probe that borrows a db connection from engine pool and execute a lightweight sql query to see if db is reachable and up or not. If not, we not raise any exception, we just report the issue in json format 
10. Smoke Test by creating sample doc i documents and document chunks and check if cosine similarity is working for embedding with <=> by computing distance between 2 embeddings, it should be 0 for demo.
11. Commit to feature branch

----------------------------------------------------------------------------------------------------------------------
__branch__ = feat/markdown-loader

1. Add pyyml and setup branch
2. This is a start of ingestion pipeline - wherein we implement abse file that will act as a blueprint
3. We will need base as we will need consistent input for our downstream stages
4. Implement base.py that has Loader class, and has structure of PrasedDocument that is expected
5. Implement markdown loader that will be built on base
6. This markdown loader will split the front-matter and YAMlise into a dict, convert normal flat lines into sections [flush() + buffer + stack]
7. Test it with demo md file
8. Implement a CLI script that will parse one .md file using argparse and return structure as we desire.
9. Test the CLI script with a test md file which has typical format with front matter and heading s and flat lines
10. It should be printed as Front matter and sections [with headings and normal lines]
11. test with pyyaml
12. Commit to feature branch



