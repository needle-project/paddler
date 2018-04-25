# Paddler

Paddler is a lightweight system that consumes messages from RabbitMQ and store them in GoogleDataStore

The system is build for a Debian Google VM (But it can be adapted for any other system).

## Installing

Prerequisites:
- Google VM with debian installed
- DataStore

Installing the machine can be done using an installer script:
```
wget https://raw.githubusercontent.com/needle-project/paddler/latest/install
sudo sh install
```

The current system will create a new directory in `/etc/`
All consumer configs should live in `/etc/paddler/conf`

## Configuring
The RabbitMQ consumer is configured with an YAML file:

```
# Just for identification purpose
alias: Orders
# RabbitMQ Connection details
connection:
  hostname: localhost
  port: 5672
  vhost: '' # empty string for root vhost or "/my-custom-vhost"
  username: guest
  password: guest
# Queue details 
queue:
  name: abc.queue
  passive: False
  durable: True
  exclusive: False
# Exchange details
exchange:
  name: abc.exchange
  type: fanout
  passive: False
  durable: True
# GoogleDataStore Config
datastore:
  namespace: test.bucket
  kind: test
  project: project-id
```

The YAML config file should be stored in `/etc/paddler/conf/`
# Usage
The script can be run only along-side a config file.

Direct usage:
```
paddler -c config-file.yml
```

Using with supervisor:
In `/etc/paddler/` you can find a helper to create and add a config to supervisor

```
./etc/paddler/make-supervisor-conf alias-name config.yml
```
