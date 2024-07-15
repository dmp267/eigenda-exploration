import os
import ipfshttpclient, multiaddr

# DEFAULTS
DEFAULT_HOST = "http://0.0.0.0:5001"


def get_ipfs_client():
    host_from_env = os.getenv("IPFS_HOST", DEFAULT_HOST)
    host = host_from_env.split(":")[1][2:]
    port = host_from_env.split(":")[2].split("/")[0]
    daemon = multiaddr.Multiaddr(f"/dns4/{host}/tcp/{port}/http")
    client = ipfshttpclient.connect(daemon, timeout=None, session=True)
    return client


def retrieve_from_ipfs(cid: str):
    client = get_ipfs_client()
    try:
        data = client.cat(cid)
        return data
    except Exception as e:
        print(f'error pulling ipfs cid {cid}: {e}')
        raise e
