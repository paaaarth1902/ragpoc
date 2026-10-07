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
5. Implement markdown loader, wherein we fulffil the contract by implementing the load method (so basically duck typing)
6. This markdown loader will split the front-matter and YAMlise into a dict, convert normal flat lines into sections [flush() + buffer + stack]
7. Test it with demo md file
8. Implement a CLI script that will parse one .md file using argparse and return structure as we desire.
9. Test the CLI script with a test md file which has typical format with front matter and heading s and flat lines
10. It should be printed as Front matter and sections [with headings and normal lines]
11. test with pyyaml
12. Commit to feature branch

----------------------------------------------------------------------------------------------------------------------
__branch__ = feat/chunker

1. A chunker's job is to break each parsed doc into pieces small enough so they can be embedded accurately, but big enough that doesnt destroy the overall sematics of it all
2. This chunker will produce a list of chunks for us which we will pass to the embedder. 
3. we need to finalize where do we split? what exactly should be the chunk size.
4. There needs to be a sweet spot between 200 tokens (a small chunk size) to 1500 token(a large chunk size)
5. Lets say we finalize at 600 tokens, as in each chunk will be of 600 tokens
6. Post that we can finalize 80 tokens as `overlap` - when splitting oversized section into, lets say 2 chunks, resulting chunks share some text at boundary and last 80 80 tokens of chunk A also appear in cunk b
7. Tiktoken is used as an exact token counter to keep chunks under the target size and never exceed the embedding API's hard limit.

----------------------------------------------------------------------------------------------------------------------
__branch__ = feat/embedder

1. Before making any calls to OpenAI's embedding API, implementing a fake embedder to mock the service and understand shape and dimensions.
2. this will live in embedding layer, parallel to the ingestion layer
3. First understand and define what embedder is and what any embedded chunk will look like in action
4. The EmbeddedChunk inherits props of Chunk and adds a vector attribute which is list of floatts and a Embedder protocol with dim and a embed method. meaning any class implementing this method and var will automatically satify embedder
5. Post this implement a mock embedder with help of hashlib.sha256.
6. We will have a embed function defined in FakeEmbdder, which takes n strings, returnong n vectors
7. This is done by one of helper methods that actually creates the vectors for us (still mock)
8. Once tested, implement actual embedding with openAI's [text-embedding-3-small] model
9. This will take a strem of texts, batch it into like 100 tokens, sending it to OpenAI client.
10. OpenAI will process them and send a response of lists of list with each inner list having 1536 numbers, which we will pull out and collect the numbers and store them in some list and return that list.
11. Test theis with some sample stream of sentences by passing them to the embedder and observe what is the o/p
12. A wrapper can be implemented which will retry API call if errors like 429, 500, 502 happen, but errors like 401, 403 wont be. We can have unit test for this too which will mock the external call and see if retrying actually happens.
13. We pass the chunked doc to this RetryingEmbedder wrapper, which passes this to our actual caller to send chunks to OpenAI for embedding

----------------------------------------------------------------------------------------------------------------------

__branch__ = feat/first-http-endpoints

1. up untill now we are relying on seed_corpus scripts and various other scripts such as embed_one and all. Now we can move this to more production ready states like  applications so users can access.
2. For this, 2 HTTP endpoints will be created, both of which will be living in the ingestion plane
3. one will be POST /documents which will do all the heavy lifting including accepting and saving file, parsing it, chunking it, embedding it and storing it in DB
4. Other will be GET /jobs/{id}, that will simple handle `is the job done?`
5. Its also important to note that all of the steps mentioned for POST /documents will not be gandled solely by thsi endpoint in one go, sequentially
6. fast jobs will be executed immedialtely like saving the uploaded file to disk, creating job row and returning job_id, whereas other stuff, time taking stuff will be handled as part of background tasks. This includes parsing, chunking, embedding, storing, updating job row etc.
7. First, a document ingestion and saving file to disk stuff can be handled - w/o the BG stuff in documets.py
8. Once we get 202, meaning file is accepted and saved to disk, we can trigger a BG task that picks up the job and runs actua pipeline. This task can live inside a different worker file.
9. This is because BG task needs to do work AFTER the response has been sent. 
10. This worker will have one resource allocation blcok that sets up brand new Db session as HTTP request that triggered the task is already finished, (202 one) and DB connection session must have been destroyed
11. In worker post allocation, we can mark ongoing job as running in step 1
12. In step 2 we can do all our I/O stuff and keep this outside DB transaction and pass the session only if seed_document saves to DB at the end
13. Mark job as succeded if session is succesfully completed and throw exception if not.
14. Its also very important to perform idempotency check post running to see if we upload same doc or runbook tewo times, the content hash check is working and NO NEW CHUNKS GET ADDED

----------------------------------------------------------------------------------------------------------------------