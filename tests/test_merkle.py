from eth_account._utils.signing import sign_message_hash
from eth_keys.datatypes import PrivateKey
from eth_utils import to_bytes

from script.make_merkle import DEFAULT_AMOUNT

proof = [
    bytes.fromhex("8ebcc963f0588d1ded1ebd0d349946755f27e95d1917f9427a207d8935e04d4b"),
    bytes.fromhex("e5ebd1e1b5a5478a944ecab36a9a954ac3b6b8216875f6524caa7a1d87096576"),
]


def test_merkle(merkle, token, user):
    starting_balance = token.balanceOf(user)
    bytes_signable_message = merkle.get_message_hash(user.address, DEFAULT_AMOUNT)
    v, r, s, _ = sign_message_hash(PrivateKey(user.key), bytes_signable_message)

    merkle.claim(
        user.address,
        DEFAULT_AMOUNT,
        proof,
        v,
        to_bytes(r),
        to_bytes(s),
    )

    ending_balance = token.balanceOf(user)

    assert ending_balance == starting_balance + DEFAULT_AMOUNT
