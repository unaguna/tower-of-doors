# Experiment of Grafana with MySQL

We use Docker to begin experimenting with Grafana with ease.

## Prerequisite

Dockers must be available. The following commands can be used to check.

```shell
docker --version
docker ps
Docker-Compose --version
```

## Start Up

1. Create a network for docker containers with the following command:

    ```shell
    docker network create tower-of-doors-network
    ```

2. (Optional) Put file to initialize MySQL on `./DB/`. For example, [the samples by MySQL](https://dev.mysql.com/doc/index-other.html) are useful.

3. Build images with the following command:

    ```shell
    Docker-Compose build 
    ```

4. Run containers with the following command:

    ```shell
    Docker-Compose up -d
    ```
5. You can use Grafana at http://127.0.0.1:3000

## Caution

- Grafana data is persistent.
- MySQL data is NOT persistent and changes are lost when the container is deleted. This is because it is assumed that only SQL for viewing purposes by Grafana will be executed while the container is running.









