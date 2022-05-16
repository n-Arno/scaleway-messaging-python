import sys
import asyncio
from nats.aio.client import Client as NATS


async def main(server_ip):
    nc = NATS()

    # Modify this with your informations
    options = {
        "servers": [f"nats://{server_ip}:4222"],
        "user_credentials": "nats.creds",
    }

    # Connect using the previous options
    await nc.connect(**options)
    print(f"Connected to NATS at {nc.connected_url.netloc}...")

    # Simple publishing
    await nc.publish("my-subject", b"This is a simple message with some datas")

    # Publish with headers
    await nc.publish(
        "my-subject",
        b"This is still a simple message but with some headers inside",
        headers={"Example": "True", "RandomHeaders": "True"},
    )

    # Close connection
    await nc.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <NAT server IP>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
