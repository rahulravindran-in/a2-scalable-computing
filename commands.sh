docker stack services drs
docker node ls
docker stack deploy -c docker-redis-stack.yml drs
vi docker-redis-stack.yml
docker ps
docker stack rm drs