1. the moment we run doker compose up -d,  It takes the configuration (docker compose yaml) file and instantly launches a fully configured, isolated server on the machine without us having to install Postgres natively, or any service that we might require. so docker compose is like a blueprint for services thatw eneed from docker

2. when we create config file, its kinda imp to understand what its actual need is. As name suggests, it stores all configurations that we will need. A configuration is something that we know will change per environment. Like DB stuff, secrets, env falgs and feature flags etc

3. when we setup a session file, we can imagine it as setting up restaurant, where the database is kitchen. We have manager [AsyncEngines], which knows kitchen address and knows how many waiters we will need to serve the clients (http reqs) for the system work

4. The manager has one notepad [AsyncSession], created per HTTP request or per client entry, which has the details of incmoing guests and when they leave the restaurant. It uses this to efficiently manage the waiters. Lets say all waiters are occupied, it makes the new clients wiat outside and allow them as any waiter gets free and any table is free.

5. Starting the ingestion layer, first part is to make sure all document follow a certain protocol/blueprint.
We implement this in the base loader which has a dataclass of ParsedDocument, which shows how ay parsed document should look like in order to pass for further embedding process

6. Structurally, this ParsedDocument has front matter and multiple sections along with title captured in ParsedDocument class we defined

7. We build one markdown loader extending this Base Loader that returns Front matter and sections. 
We use stacks to manage how headings and their content will be pushed.