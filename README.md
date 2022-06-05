# Tower of Doors

This project is a fictional operation tool for the facility "Tower of Doors" that appears in a work of fiction, "[Kakegurui](https://ja.wikipedia.org/wiki/%E8%B3%AD%E3%82%B1%E3%82%B0%E3%83%AB%E3%82%A4)".

**This project is created for my learning.**

## Structure

The project consists of the following elements:

- Operation monitoring view ([Grafana](https://grafana.com/))
- Operation command (plain [Python](https://www.python.org/))
- Game progression process (plain [Python](https://www.python.org/))
- Database ([MySQL](https://www.mysql.com/))

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

2. Build images with the following command:

    ```shell
    Docker-Compose build 
    ```

3. Run containers with the following command:

    ```shell
    Docker-Compose up -d
    ```

## Operation

After completing the startup described above, you can do the following operation.

### Watch the operation monitoring view

After completing the startup described above, you can see the operation monitoring view on <http://localhost:3000>. The login ID and password are both `admin`. If necessary, change the password and create a new user.

### Start a game, open doors, etc.

Changing the status of the tower is done using the CUI tool.

1. Enter the container that controls the business logic of the tower.

    ```shell
    docker exec -it tower-of-doors-db-update /bin/bash
    ```

2. Use `tod` commands as follows

    ```shell
    # Open the door between the 5th and 4th floors
    # (IDs of each door can be found on the operation monitoring view, etc.)
    tod open F5F4-001

    # Close all doors
    tod close all

    # Start a game
    tod start

    # Terminate the game
    tod end
    ```

    You can see more information with the command `tod --help`.

### Request SQL directly.

You can execute SQL directly without using the above tools.

1. Enter the container that controls the business logic of the tower.

    ```shell
    docker exec -it tower-of-doors-db-update /bin/bash
    ```

2. Enter MySQL

    ```shell
    mysql
    ```

    User information and database name are provided in the [configuration file](db-update/root_my.cnf) and do not need to be entered as command arguments.

## Caution

- Grafana data is persistent.
- MySQL data is NOT persistent and changes are lost when the container is deleted. This is because we believe that the data underlying the system is created and modified only during initialization.
