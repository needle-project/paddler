#!/usr/bin/python3

import pika
import sys
import yaml
import os
from google.cloud import datastore

def log(message, level="Debug"):
	'''
	Verbose capabilities
	'''
	if len(sys.argv) == 4 and sys.argv[3] == "-v" and level == "Debug":
		print("[",level.upper(),"]", message)

def getArgumentFromConfig():
	'''
	Identify CLI arguments and load config file
	from YAML
	'''
	if (len(sys.argv) < 3 or sys.argv[1] != "-c"):
		print("You must provide a config file. Config files should be stored in /etc/paddler/conf/")
		print("Example:", __file__, "-c my-config-file.yaml")
		sys.exit(1)

	try:
		configFile = sys.argv[2]
		configFile = os.path.join("/etc/paddler/conf/", configFile)

		stream = open(configFile, "r")
		return yaml.load(stream)
	except Exception as e:
		print("Could not load config file, got", str(e))
		sys.exit(1)

def createAmqpConnect(connectionConfig):
	'''
	Create an AMQP connection based on config parameters

	@param dict connectionConfig	A dictionary containing connection details:
									config = {
										"hostname": "localhost"
										"port": "5672"
										"vhost": ""
										"username": "guest"
										"password": "guest"
									}
	'''
	try:
		connection = pika.BlockingConnection(
			pika.ConnectionParameters(
				connectionConfig['hostname'],
				int(connectionConfig['port']),
				connectionConfig['vhost'],
				pika.PlainCredentials(connectionConfig['username'], connectionConfig['password']),
				socket_timeout=300
			)
		)
		log("Connected to AMQP:"+ connectionConfig['hostname']+":"+str(connectionConfig['port'])+"/"+connectionConfig['vhost'])
		return connection
	except Exception as e:
		print("Could not connect to AMQP, got", str(e))
		sys.exit(1)

def buildQueueAndExchange(channel, queueConfig, exchangeConfig):
	'''
	Create queue and exchange if they do not already exists!
	'''
	try:
		# Create queue
		channel.queue_declare(
			queue=queueConfig['name'],
			passive=queueConfig['passive'],
			durable=queueConfig['durable'],
			exclusive=queueConfig['exclusive']
		)
		# Create exchange
		channel.exchange_declare(
			exchange=exchangeConfig['name'],
			exchange_type=exchangeConfig['type'],
			passive=exchangeConfig['passive'],
			durable=exchangeConfig['durable']
		)
		# Bind queue to exchage
		channel.queue_bind(exchange=exchangeConfig['name'],queue=queueConfig['name'])
	except pika.exceptions.ChannelClosed as e:
		print(str(e.args[1]))
		sys.exit(1)


def write(config, message):
	datastore_client = datastore.Client(project=config['datastore']['project'], namespace=config['datastore']['namespace'])

	kind = config['datastore']['kind']
	name = config['alias']

	key = datastore_client.key(kind,exclude_from_indexes=['message'])
	entity = datastore.Entity(key=key)
	entity['message'] = str(message)

	datastore_client.put(entity)


def consumeMessage(ch, method, properties, body):
	message = body.decode()

	log("Got message %r" % message)
	write(config, str(message))
	log("Succesfully written %r" % message)

	# ACK Message after successfully consumption it
	ch.basic_ack(delivery_tag=method.delivery_tag)


''' Code execution '''
config = getArgumentFromConfig()
log("Loaded config for <" + config['alias'] + ">")
amqpConnection = createAmqpConnect(config["connection"])
channel = amqpConnection.channel()
channel.basic_qos(prefetch_count=1)


buildQueueAndExchange(channel, config['queue'], config['exchange'])

channel.basic_qos(prefetch_count=1)
channel.basic_consume(consumeMessage,
                      queue=config['queue']['name'],
                      no_ack=False)

print("Started listening for AMQP Messages. To exit press CTRL+C")
try:
	channel.start_consuming()
except KeyboardInterrupt:
	channel.close()
	amqpConnection.close()
	print("Exiting on request!")
	sys.exit(0)
except Exception as e:
	print("Unpexpected error has ocurred, got", str(e))
	sys.exit(1)