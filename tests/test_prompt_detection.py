import unittest

from mcp_ssh_reloaded.session_manager import SSHSessionManager


class TestPromptDetection(unittest.TestCase):
    def setUp(self):
        self.manager = SSHSessionManager()

    def test_password_detection(self):
        # Should match
        assert (
            self.manager._detect_awaiting_input("Please enter password: ") == "password"
        )
        assert self.manager._detect_awaiting_input("Password:") == "password"
        assert (
            self.manager._detect_awaiting_input("user@host's password: ") == "password"
        )
        assert (
            self.manager._detect_awaiting_input("[sudo] password for user:")
            == "password"
        )

        # Should NOT match (false positives)
        assert self.manager._detect_awaiting_input("password=secret\nDone.") is None
        assert (
            self.manager._detect_awaiting_input("Labels:\n - password: secret\n")
            is None
        )
        assert (
            self.manager._detect_awaiting_input("http://example.com?password=123")
            is None
        )
        assert (
            self.manager._detect_awaiting_input('"password": "value"') is None
        )  # JSON
        assert self.manager._detect_awaiting_input('var password="123"') is None  # Code
        assert (
            self.manager._detect_awaiting_input("password=secret") is None
        )  # URL param at end

    def test_pager_detection(self):
        # Should match
        assert self.manager._detect_awaiting_input("lines\n(END)") == "pager"
        assert self.manager._detect_awaiting_input("lines\n:") == "pager"

        # Should NOT match
        assert self.manager._detect_awaiting_input("(END)\nSome output") is None
        assert (
            self.manager._detect_awaiting_input("The end of the file (END) is near")
            is None
        )

    def test_press_key_detection(self):
        # Should match
        assert (
            self.manager._detect_awaiting_input("Press any key to continue...")
            == "press_key"
        )
        assert (
            self.manager._detect_awaiting_input("Press Enter to continue")
            == "press_key"
        )

        # Should NOT match
        assert (
            self.manager._detect_awaiting_input(
                "1. Press any key to continue\n2. Next step"
            )
            is None
        )


if __name__ == "__main__":
    unittest.main()
