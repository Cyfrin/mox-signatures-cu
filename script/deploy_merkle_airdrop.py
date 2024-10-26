from eth_utils import to_wei
from moccasin.boa_tools import VyperContract

from script.make_merkle import generate_merkle_tree
from src import merkle_airdrop, snek_token

INITIAL_SUPPLY = to_wei(100, "ether")


def deploy_merkle_airdrop() -> VyperContract:
    token = snek_token.deploy(INITIAL_SUPPLY)
    _, root = generate_merkle_tree()
    airdrop_contract = merkle_airdrop.deploy(root, token.address)
    token.transfer(airdrop_contract.address, INITIAL_SUPPLY)
    print(f"Merkle Airdrop contract deployed at {airdrop_contract.address}")
    return airdrop_contract


def moccasin_main():
    deploy_merkle_airdrop()
