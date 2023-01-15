import click
from csv import DictWriter
from datetime import datetime
from ping3 import ping
from time import sleep
from typing import Optional


@click.command("internet_check")
@click.option(
    "--output-file",
    "-o",
    type=click.File("w"),
    default="connection_data.csv",
    help="The file to write the connection data to"
)
@click.option("--target", "-t", default="8.8.8.8", help="Host to ping")
@click.option(
    "interval_s",
    "--interval",
    "-i",
    type=click.INT,
    default=1,
    help="Interval between pings in seconds"
)
@click.option("--verbose", "-v", is_flag=True, default=False, help="Verbose output")
def main(output_file: click.File, target: str, interval_s: int, verbose: bool):
    is_connction_ok = True
    break_timestamp: Optional[datetime] = None
    csv_headers = ["interruption_start", "interruption_end"]
    csv_writer = DictWriter(output_file, csv_headers)
    csv_writer.writeheader()
    while True:
        try:
            response = ping(target)
            now = datetime.now()
            if is_connction_ok and not isinstance(response, float):
                print(f"Connection lost at {now}.")
                is_connction_ok = False
                break_timestamp = datetime.now().astimezone()
            elif not is_connction_ok and isinstance(response, float):
                print(f"Connection restored at {now}.")
                is_connction_ok = True
                csv_writer.writerow({
                    "interruption_start": break_timestamp.isoformat(),
                    "interruption_end": now.isoformat()
                })
            elif verbose:
                print(f"{now.isoformat()}: {target} {response}ms")

            sleep(interval_s)
        except KeyboardInterrupt:
            if is_connction_ok or break_timestamp is None:
                raise

            csv_writer.writerow({
                "interruption_start": break_timestamp.isoformat(),
                "interruption_end": "-"
            })
            raise


if __name__ == "__main__":
    main()
