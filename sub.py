import asyncio
import signal
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

    # Subscribe to a topic
    print("Subscribing")
    sub = await nc.subscribe("my-subject")
    print("Subscription OK")

    def signal_handler():
        print("Disconnecting...")
        asyncio.create_task(sub.unsubscribe())
        asyncio.create_task(nc.close())
        print("Disconnection OK")

    for sig in ('SIGINT', 'SIGTERM'):
        asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), signal_handler)
    try:
        async for msg in sub.messages:
            print(f"Received a message on '{msg.subject}': {msg.data.decode()}")
            print(f"Headers maybe: {msg.headers}")
    except Exception as e:
        pass

if __name__ == '__main__':
    asyncio.run(main())
