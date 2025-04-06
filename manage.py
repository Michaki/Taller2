import sys
import argparse
import asyncio

from database.migrations.m001_create_sensor_index import clear_and_create_sensor_index
from database.seeds.seed_sensor_data import seed_sensor_data

def main():
    parser = argparse.ArgumentParser(description="Project management commands")
    parser.add_argument(
        "command",
        help="Command to run",
        choices=["migrate", "seed", "all"],
        type=str
    )
    args = parser.parse_args()

    if args.command == "migrate":
        print("Running migrations...")
        asyncio.run(clear_and_create_sensor_index())
    elif args.command == "seed":
        print("Running seed scripts...")
        asyncio.run(seed_sensor_data())
    elif args.command == "all":
        print("Running migrations...")
        asyncio.run(clear_and_create_sensor_index())
        print("Running seed scripts...")
        asyncio.run(seed_sensor_data())
    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()
