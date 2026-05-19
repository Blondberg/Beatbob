import wavelink
import asyncio


async def main():
    nodes = [wavelink.Node(uri="0.0.0.0:2333", password="youshallnotpass")]
    await wavelink.Pool.connect(nodes=nodes)


asyncio.run(main())
