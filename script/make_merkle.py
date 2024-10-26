import json
from typing import Dict, List, Tuple

from eth_abi import encode
from eth_utils import keccak

DEFAULT_AMOUNT = 25000000000000000000
DEFAULT_INPUT = {
    "values": {
        "0": {
            "0": "0x537C8f3d3E18dF5517a58B3fB9D9143697996802",
            "1": DEFAULT_AMOUNT,
        },
        "1": {
            "0": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            "1": DEFAULT_AMOUNT,
        },
        "2": {
            "0": "0x2ea3970Ed82D5b30be821FAAD4a731D35964F7dd",
            "1": DEFAULT_AMOUNT,
        },
        "3": {
            "0": "0xf6dBa02C01AF48Cf926579F77C9f874Ca640D91D",
            "1": DEFAULT_AMOUNT,
        },
    }
}


def hash_pair(a: bytes, b: bytes) -> bytes:
    """Hash two bytes32 values in order."""
    # Sort the hashes before concatenating
    return keccak(min(a, b) + max(a, b))


def generate_leaf(address: str, amount: str) -> bytes:
    """Generate a leaf node by encoding and hashing address and amount."""
    # Create an array of bytes32 matching Solidity's approach
    data = []

    # Handle address: bytes32(uint256(uint160(address)))
    address_int = int(address, 16)  # Convert hex address to int
    address_bytes32 = address_int.to_bytes(32, "big", signed=False)
    data.append(address_bytes32)

    # Handle amount: bytes32(amount)
    amount_int = int(amount)
    amount_bytes32 = amount_int.to_bytes(32, "big", signed=False)
    data.append(amount_bytes32)

    encoded = encode(["bytes32[]"], [data])
    encoded = encoded[64:]
    first_hash = keccak(encoded)
    return keccak(first_hash)


def get_merkle_root(leaves: List[bytes]) -> bytes:
    """Calculate Merkle root from list of leaves."""
    if not leaves:
        return keccak(b"")

    layer = leaves
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])

        next_layer = []
        for i in range(0, len(layer), 2):
            next_layer.append(hash_pair(layer[i], layer[i + 1]))
        layer = next_layer

    return layer[0]


def get_proof(leaves: List[bytes], index: int) -> List[str]:
    """Generate Merkle proof for leaf at given index."""
    if not leaves:
        return []

    proof = []
    layer = leaves
    target_idx = index

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])

        next_layer = []
        for i in range(0, len(layer), 2):
            if i == target_idx - (target_idx % 2):
                # Add sibling to proof
                proof.append("0x" + layer[i + (1 - (target_idx % 2))].hex())
            next_layer.append(hash_pair(layer[i], layer[i + 1]))

        layer = next_layer
        target_idx = target_idx // 2

    return proof


def generate_merkle_tree(input_data: Dict | None = None) -> Tuple[List[Dict], bytes]:
    """Generate complete Merkle tree data structure from input data."""
    if input_data is None:
        input_data = DEFAULT_INPUT

    # Extract and sort leaves
    leaves = []
    inputs = []

    for i in range(len(input_data["values"])):
        address = input_data["values"][str(i)]["0"]
        amount = input_data["values"][str(i)]["1"]
        leaf = generate_leaf(address, amount)
        leaves.append(leaf)
        inputs.append([address, amount])

    # Calculate root
    root = get_merkle_root(leaves)
    root_hex = "0x" + root.hex()

    # Generate output for each leaf
    output = []
    for i in range(len(leaves)):
        entry = {
            "inputs": inputs[i],
            "proof": get_proof(leaves.copy(), i),
            "root": root_hex,
            "leaf": "0x" + leaves[i].hex(),
        }
        output.append(entry)

    return output, root


def cli_run():
    output, root = generate_merkle_tree()

    with open("merkle_output.json", "w") as f:
        json.dump(output, f, indent=4)

    print("Merkle tree data written to merkle_output.json")
    print(f"Merkle root: {output[0]['root']}")


def moccasin_main():
    cli_run()


if __name__ == "__main__":
    cli_run()
