# Deploying Ansible-RM #

These instructions detail how to deploy:

* Ansible RM
* A single node Cassandra

It is expected that the user already has a Kubernetes installation, with the Lifecycle Manager already deployed.

It is recommended that you install the Ansible RM into the same Kubernetes namespace as the Lifecycle Manager.

## Install dependencies ##

Ensure you have the incubator repo:
```
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
```

Download dependencies to "charts" directory:

```
helm dependency update osslm-ansible-resource-manager
```

Create Persistent Volume directories (if leaving createVolumes as true in helm chart values). Ensure current user owns the directories and give write access.

```
sudo mkdir -p /var/lib/osslm/
(opt.) sudo chown dvs:dvs /var/lib/osslm/
mkdir /var/lib/osslm/volume-r00
mkdir /var/lib/osslm/volume-r01
mkdir /var/lib/osslm/volume-r02
mkdir -p /var/lib/osslm/volume-r03/ssl
chmod 777 /var/lib/osslm/*
```

NOTE: You can skip the need for persistent volumes by settings cassandra.persistence, kafka.persistence and kafka.zookeeper.persistence to false in the helm chart values.

## Install Ansible RM ##

Install Helm Chart

```
helm install osslm-ansible-resource-manager-1.3.5.tgz --name osslm-ansible-rm --namespace default --values osslm-ansible-rm.values.yaml --debug
```

## Uninstall ##

Uninstall Helm chart

```
helm delete osslm-ansible-rm --purge
```

Manually remove PV and PVs

```
kubectl delete pv -l createdBy=osslm-ansible-rm
kubectl delete pvc -l release=osslm-ansible-rm
```

Remove PV directories

```
sudo rm -rf /var/lib/osslm/volume-*
```

### Configuring connections to Cassandra/Kafka ###
By default the container relies on Kubernetes to find a service named "kafka" for Kafka and "alm-ansible-rm-db" for Cassandra. By default this helm chart will create a Cassandra deplyoment and service this name.

The helm chart may also create a Kafka deployment, however by default this is disabled. Instead the chart expects there is an existing Kafka deployed as part of LM, called foundation-kafka, so creates only a service for Kafka which selects the existing pods.

Alternatively you may use hosts to direct "kafka" and "alm-ansible-rm-db" to a fixed IP address.

Create values file

```
touch ansible-rm-values.yaml
vi ansible-rm-values.yaml
```

Add the following content

```
app:
  config:
    kafka:
      hostEnabled: true
      host: <some ip address>
    cassandra:
      hostEnabled: true
      host: <some ip address>
```

### Enabling Secured Access (HTTPS)
Security can be en/dis-abled with this section:

```
app:
  config:
    security:
      ssl:
        enabled: <true or false>
        secretName: <a k8s secret name>
```

If SSL is enabled you MUST create a secret on kubernetes that holds the TLS certificate and key files.
* Create your self-signed certificate like
```
openssl genrsa 1024 > tls.key
openssl req -new -x509 -nodes -sha1 -days 365 -key tls.key > tls.cert
```
* then create the kubernetes secret
```
kubectl create secret  tls <secretName from above> --cert=tls.crt --key=tls.key --namespace=default
```


### Configure Docker Image ###

By default the Helm chart looks for a Docker image called osslm-ansible-rm:1.3.5 locally. If different then update image and version as shown below:

Add to ansible-rm-values.yaml

```
docker:
  image: different-name-for-osslm-ansible-rm
  version: 1.2
  imagePullPolicy: IfNotPresent
```

## Accessing the Ansible-RM ##

The Ansible-RM can be accessed in the Kubernetes network via **osslm-ansible-rm:8080** (only pods in the same namespace can access it this way).

The Ansible-RM can be accessed externally via **<kubernetes-ip>:31080** where "kubernetes-ip" is the IP address of one of your Kubernetes nodes.

Swagger-UI:
http://<kubernetes-ip>:31080/api/v1.0/resource-manager/ui/
