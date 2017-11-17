# Installation
## Get the code
Download or clone the repository to your target host.

## Pre-Install Configuration
Adjust these settings to fit your needs.

File: _osslm-ansible-resource-manager/alm-ansible-rm-docker-compose.yml_

| property | default | comment|
|----------|---------|--------|
|`networks.default.ipam.config.subnet`|172.28.0.0/16|docker network, modify if clashes with existing subnet configs |
|`services.alm-osm-rm.ports`|8080|swagger API port|
|`services.alm-osm-rm.environment.LOG_LEVEL`|DEBUG|log level. Supported values: INFO, ERROR, WARNING, DEBUG|
|`services.alm-osm-rm.environment.extra_hosts.kafka`|192.168.63.179|IP address of your ALM kafka/zookeeper instance|

File: _osslm-ansible-resource-manager/ansible-adaptor/config.yml_

| property | default | comment|
|----------|---------|--------|
|`driver.supportedFeatures.AsynchronousTransitionResponses|false| set to _true_ if you want to support async mode |

## Run

```
cd into the AlmAnsibleRMD directory
docker-compose -f alm-ansible-rm-docker-compose.yml build
docker-compose -f alm-ansible-rm-docker-compose.yml up -d
```

You can modify the port the RM is listening in the docker-compose file (see pre-install config section above).

## Access
you can access the swagger API using: http://yourserverip:8080/api/v1.0/resource-manager/ui/#/

## Post-install Configuration
1. launch the swagger API page and
2. expand the "Driver janitor" section

### Create the Database Schema
3. run the "Create database tables" operation

This creates the alm_ansible keyspace and all required tables in the db.
A sample location 'world' is inserted for the hello-world example.
