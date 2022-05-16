import asyncio

from nats.aio.client import Client as NATS

async def main():
    nc = NATS()

    # Modify this with your informations
    options = {
        "servers": ["nats://IP:4222"],
        "user_credentials": "nats.creds"
    }

    # Connect using the previous options
    await nc.connect(**options)
    print(f"Connected to NATS at {nc.connected_url.netloc}...")

    # Simple publishing
    await nc.publish("my-subject", b'This is a simple message with some datas')

    # Publish with headers
    await nc.publish("my-subject", b'This is still a simple message but with some headers inside', headers={'Example':'True','RandomHeaders':'True'})

    # Close connection
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
