import time

from flask import Blueprint, jsonify, request
import requests

from src import config, p2p_utils, db
from src.models import MiningNode


bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return "Welcome to P2P server"


@bp.route("/update", methods=["GET"])
def update() -> dict:
    client_ip = request.args.get("ip")
    client_port = request.args.get("port")

    if not client_ip or not client_port:
        return jsonify(
            {
                "status": "fail",
                "contents": f"cannot update using ip({client_ip}) and port({client_port})",
            }
        )

    client_exist = p2p_utils.check_node_exist(client_ip, client_port)

    if not client_exist:
        p2p_utils.add_new_node(client_ip, client_port)

    else:
        client_exist.timestamp = time.time()

        db.session.commit()

    seed_exist = p2p_utils.check_node_exist(config.SEED_NODE_IP, config.PORT_P2P)

    if not seed_exist:
        p2p_utils.add_new_node(config.SEED_NODE_IP, config.PORT_P2P)

    nodes = MiningNode.query.all()

    for node in nodes:
        if node.ip == config.MY_PUBLIC_IP and node.port == config.PORT_P2P:
            continue

        url = f"http://{node.ip}:{node.port}/neighbors"

        try:
            response = requests.get(url, timeout=3)

        except:
            print(f"Cannot access to {url}")
            continue

        neighbors_data = response.json()
        neighbors = neighbors_data.values()

        for neighbor in neighbors:
            neighbor_exist = p2p_utils.check_node_exist(
                neighbor["ip"],
                neighbor["port"],
            )

            if neighbor_exist is False:
                p2p_utils.add_new_node(neighbor["ip"], neighbor["port"])

            else:
                neighbor_exist.timestamp = time.time()

                db.session.commit()

    return jsonify({"status": "success", "contents": "updated"}), 200


@bp.route("/neighbors", methods=["GET"])
def neighbors() -> dict:
    my_info = p2p_utils.check_node_exist(config.MY_PUBLIC_IP, config.PORT_P2P)

    if not my_info:
        p2p_utils.add_new_node(config.MY_PUBLIC_IP, config.PORT_P2P)

    p2p_data = MiningNode.query.all()
    p2p_data_dic = {}

    for index, node in enumerate(p2p_data):
        p2p_data_dic[index] = {
            "ip": node.ip,
            "port": node.port,
            "timestamp": node.timestamp,
        }

    try:
        return jsonify(p2p_data_dic), 200

    except Exception as e:
        print(f"Error in neighbors: {e}")

    return jsonify({"status": "fail"}), 400
