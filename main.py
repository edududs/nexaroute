import asyncio

from nexaroute.application.bootstrap import create_simple_runtime


async def main() -> None:
    runtime = create_simple_runtime(triggers=[], handlers={})
    await runtime.start()
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
