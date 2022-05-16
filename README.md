# scaleway-messaging-python

Quick tutorial to show how to use Scaleway MnQ Service with Python. In this tutorial we will use [nats-py](https://github.com/nats-io/nats.py) to interact with MnQ using the [NATS protocol](https://nats.io/).

The first part of this tutorial is based on this documentation: [Messaging and queuing API](https://developers.scaleway.com/en/products/messaging_and_queuing/api/v1alpha1/)

## Tools needed

For this tutorial you will need:

- [curl](https://curl.se/)
- [jq](https://stedolan.github.io/jq/)
- [python 3](https://www.python.org/downloads/)
- [nats-py](https://github.com/nats-io/nats.py)

You also need to:

- Set your Scaleway token's secret key in the environment variable: **SCW_SECRET_KEY**. For more information you can refer to [the official Scaleway documentation](https://www.scaleway.com/en/docs/console/my-project/how-to/generate-api-key/)
- Set the id of the Scaleway project you want to use in the environment variable: **SCW_PROJECT_ID**. For more information you can refer to [the Scaleway CLI documentation](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/config.md)

## Create your Scaleway Messaging Namespace

A namespace is a way to isolate your application's messages from one another.

We use curl to create our first namespace. We named it `nats-broker`, and we save it's information in the `nats-broker.json` file.

```bash
curl -s --request POST 'https://api.scaleway.com/mnq/v1alpha1/regions/fr-par/namespaces' \
    --header 'Content-Type: application/json' \
    --header 'X-Auth-Token: '$SCW_SECRET_KEY \
    --data-raw '{
        "name": "nats-broker",
        "project_id": "'$SCW_PROJECT_ID'",
        "protocol": "nats"
    }' | tee nats-broker.json
```

The `nats-broker.json` file looks like this:

```json
{
    "region":"fr-par",
    "id":"XXXXXXX",
    "project_id":"XXX-XXX",
    "name":"nats-broker",
    "endpoint":"nats://IP:4222",
    "protocol":"nats"
}
```

## Create you credentials

In order to connect to our namespace and publish messages, we need to create credentials for our python scripts.
The credentials are named `my-nats-credentials` and we store them in the `my-credentials.json` file.
We then extract the credentials we need in the `nats.creds` file. We will use the `nats.creds`file in our python scripts.

```bash
curl -s --request POST 'https://api.scaleway.com/mnq/v1alpha1/regions/fr-par/credentials' \
    --header 'Content-Type: application/json' \
    --header 'X-Auth-Token: '$SCW_SECRET_KEY \
    --data-raw '{
        "name": "my-nats-credentials",
        "namespace_id": "'$(jq -r .id nats-broker.json)'"
    }' | tee my-credentials.json


jq -r .nats_credentials.content my-credentials.json > nats.creds
```

The `nats.creds`file should looks like this:

```bash
-----BEGIN NATS USER JWT-----
XXX
------END NATS USER JWT------
-----BEGIN USER NKEY SEED-----
XXX
------END USER NKEY SEED------
```

## Run the scripts

Modify the 2 scripts `pub.py` and `sub.py`. You must change the following line:

```python
options = {
        "servers": ["nats://IP:4222"],
        "user_credentials": "nats.creds"
    }
```

Replace `IP` with the IP you'll find in the `nats-broker.json` file, it's the endpoint's IP.

Open 2 differents terminal. In the first one, run `python3 sub.py`.
You should see an output and then the script awaits new messages.

```bash
Connected to NATS at XXX:4222...
Subscribing
Subscription OK
```

In the second terminal, run `python3 pub.py`
You should see 2 output in the first terminal:

```bash
Received a message on 'my-subject': This is a simple message with some datas
Headers maybe: None
Received a message on 'my-subject': This is still a simple message but with some headers inside
Headers maybe: {'Example': 'True', 'RandomHeaders': 'True'}
```

## Scripts details

### In both scripts

In both scripts, we have the connection part. It connects to our message broker using the broker adress and the credentials in the `nats.creds` file.

```python
    # Modify this with your informations
    options = {
        "servers": ["nats://51.159.73.139:4222"],
        "user_credentials": "nats.creds"
    }

    # Connect using the previous options
    print("Connection")
    await nc.connect(**options)
    print(f"Connected to NATS at {nc.connected_url.netloc}...")

```

### In sub.py

In the `sub.py` script, we then subscribe to a topic.

```python
    # Subscribe to a topic
    print("Subscribing")
    sub = await nc.subscribe("my-subject")
    print("Subscription OK")
```

Then we define a handler, it will allow us to close the connection when we ctrl+c to exit the script.

```python
    def signal_handler():
        print("Disconnecting...")
        asyncio.wait_for(sub.unsubscribe(), 5)
        asyncio.wait_for(nc.close(), 5)
        print("Disconnection OK")
        exit()
```

Then we assign our handler to our main loop:

```python
    for sig in ('SIGINT', 'SIGTERM'):
        asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), signal_handler)
```

Finally, we launch the main loop

```python
try:
        async for msg in sub.messages:
            print(f"Received a message on '{msg.subject}': {msg.data.decode()}")
            print(f"Headers maybe: {msg.headers}")
    except Exception as e:
        pass
```

### In pub.py

We use the publish function to push messages to the broker:

```python
    # Simple publishing
    await nc.publish("my-subject", b'This is a simple message with some datas')

    # Publish with headers
    await nc.publish("my-subject", b'This is still a simple message but with some headers inside', headers={'Example':'True','RandomHeaders':'True'})
```
