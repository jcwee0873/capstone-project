import datetime


def logger(
    log: str,
    title: str = ""
):
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H:%M:%S')

    print(f"{now} {title}\t{log}")