import ovirtsdk4 as sdk


connection = sdk.Connection(
    url='http://ovirt-engine:8080/ovirt-engine/api',
    username='admin@internal',
    password='123456',
)

