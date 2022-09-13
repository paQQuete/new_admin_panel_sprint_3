import os


def init_schema():
    with open('es_schema.txt', 'r') as f:
        command = f.read()
        os.system(command)

if __name__ == '__main__':
    init_schema()