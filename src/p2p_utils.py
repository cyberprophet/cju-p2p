import time

from typing import Union

from src.models import MiningNode
from src import db


def check_node_exist(ip: str, port: str) -> Union[bool, MiningNode]:
    node = MiningNode.query.filter(MiningNode.ip == ip, MiningNode.port == port).first()

    if not node:
        return False

    return node


def add_new_node(ip: str, port: str) -> None:
    node = MiningNode()
    node.ip = ip
    node.port = port
    node.timestamp = time.time()

    db.session().add(node)
    db.session().commit()
