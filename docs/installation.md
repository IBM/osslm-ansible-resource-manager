# Installation
Copy the repository to your target host.

## Run

```
cd into the AlmAnsibleRMD directory
docker-compose -f alm-ansible-rm-docker-compose.yml build
docker-compose -f alm-ansible-rm-docker-compose.yml up -d
```

You can modify the port the RM is listening in the docker-compose file.

## Access
you can access the swagger API using: http://yourserverip:8080/api/v1.0/resource-manager/ui/#/

## Post-install Configuration
1. launch the swagger API page and
2. expand the "Driver janitor" section

### Create the Database Schema
3. run the "Create database tables" operation

This creates the alm_ansible keyspace and all required tables in the db.
A sample location 'world' is inserted for the hello-world example.
