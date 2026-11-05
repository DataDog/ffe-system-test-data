import unittest

from dependency_key_encryption import encrypt


class DependencyKeyEncryptionTest(unittest.TestCase):
    def test_matches_independent_node_crypto_vector(self):
        self.assertEqual(
            "Eb_cST-0-FZKdvcpKLHbDDG_CX2hK4Xfrw7h5o-47Gp6GyFntOGTZO3wmLg",
            encrypt(
                "checkout-redesign",
                "new-payment-flow",
                bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
            ),
        )

    def test_root_key_changes_ciphertext(self):
        salt = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        self.assertNotEqual(
            encrypt("first-root", "parent", salt),
            encrypt("second-root", "parent", salt),
        )


if __name__ == "__main__":
    unittest.main()
