import ovirtsdk4 as sdk

connection = None


def init_connection(url, username, password):
    global connection
    connection = sdk.Connection(
        url=url,
        username=username,
        password=password,
    )
