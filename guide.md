1. Gt init to initialise the repo
2. Skeleton implementation - Folder Structure
3. Creating init files inside all folders so python ships this dirs as packages
4. Creating gitignore, env and env.template 
5. Since using PostgreSQL and pgvector, prepare the toml file, install dependencies using uv and the docker compose
6. Run `docker compose exec db psql -U ragpoc -d ragpoc -c "Select 1;"` 
7. Configure the config file and one health chekpoint in health.py and call it via router in main.py

