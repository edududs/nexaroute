import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nexaroute.application.bootstrap import create_simple_runtime


async def main() -> None:
    runtime = create_simple_runtime(triggers=[], handlers={})
    await runtime.start()
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
