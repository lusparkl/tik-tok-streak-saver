import configparser
from datetime import date
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import typer
from playwright.sync_api import expect, sync_playwright
from typer.testing import CliRunner

from streak_saver.modules import send_messages as sender


class SendingTests(unittest.TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config["users"] = {"alice": "Привет ❤️", "bob": "Hello"}
        self.config["SETTINGS"] = {"last_send": "", "default_message": "❤️"}
        self.today = str(date.today())
        self.runtime = MagicMock()
        self.browser = self.runtime.chromium.launch.return_value
        self.patches = [
            patch.object(sender, "get_config", return_value=self.config),
            patch.object(sender, "get_cookies", return_value=[{"name": "test"}]),
            patch.object(sender, "get_user_message", side_effect=lambda message: message),
            patch.object(sender, "save_config"),
            patch.object(sender, "sync_playwright"),
            patch.object(sender, "_send_message"),
            patch.object(sender, "send_error_message"),
            patch.object(sender, "send_script_message"),
            patch.object(sender, "send_success_message"),
        ]
        mocks = [self.enterContext(p) for p in self.patches]
        self.save, self.playwright, self.send, self.error = mocks[3:7]
        self.success = mocks[8]
        self.playwright.return_value.__enter__.return_value = self.runtime

    def test_all_recipients_are_sent_and_saved_individually(self):
        sender.send_messages()
        self.assertEqual([call.args[1:] for call in self.send.call_args_list], [
            ("alice", "Привет ❤️"), ("bob", "Hello")
        ])
        self.assertEqual(dict(self.config["sent_dates"]), {"alice": self.today, "bob": self.today})
        self.assertEqual(self.config["SETTINGS"]["last_send"], self.today)
        self.assertEqual(self.save.call_count, 3)
        self.browser.close.assert_called_once()

    def test_partial_failure_retries_only_failed_recipient(self):
        self.send.side_effect = [None, RuntimeError("composer unavailable")]
        with self.assertRaises(typer.Exit) as caught:
            sender.send_messages()
        self.assertEqual(caught.exception.exit_code, 1)
        self.assertNotEqual(self.config["SETTINGS"]["last_send"], self.today)
        self.assertNotIn("bob", self.config["sent_dates"])
        self.success.assert_not_called()
        self.assertIn("composer unavailable", self.error.call_args_list[0].args[0])
        self.send.reset_mock(side_effect=True)
        sender.send_messages()
        self.assertEqual([call.args[1] for call in self.send.call_args_list], ["bob"])
        self.assertEqual(self.config["SETTINGS"]["last_send"], self.today)

    def test_progress_survives_config_reload_and_cli_failure_is_nonzero(self):
        from streak_saver.main import app
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "config.ini")

            def save(config):
                with open(path, "w", encoding="utf-8") as stream:
                    config.write(stream)

            self.save.side_effect = save
            self.send.side_effect = [None, RuntimeError("missing editor")]
            result = CliRunner().invoke(app, ["send_messages"])
            self.assertEqual(result.exit_code, 1)
            reloaded = configparser.ConfigParser()
            reloaded.read(path, encoding="utf-8")
            self.assertEqual(reloaded["sent_dates"]["alice"], self.today)
            self.assertNotIn("bob", reloaded["sent_dates"])
            self.send.reset_mock(side_effect=True)
            with patch.object(sender, "get_config", return_value=reloaded):
                result = CliRunner().invoke(app, ["send_messages"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual([call.args[1] for call in self.send.call_args_list], ["bob"])

    def test_failure_does_not_prevent_later_recipient(self):
        self.send.side_effect = [RuntimeError("missing recipient"), None]
        with self.assertRaises(typer.Exit):
            sender.send_messages()
        self.assertEqual(self.config["sent_dates"].get("bob"), self.today)
        self.assertNotIn("alice", self.config["sent_dates"])
        self.browser.close.assert_called_once()

    def test_previous_day_is_sent_again(self):
        self.config["sent_dates"] = {"alice": "2000-01-01", "bob": "2000-01-01"}
        sender.send_messages()
        self.assertEqual(self.send.call_count, 2)

    def test_legacy_completed_day_is_not_sent_again(self):
        self.config["SETTINGS"]["last_send"] = self.today
        sender.send_messages()
        self.send.assert_not_called()
        self.playwright.assert_not_called()

    def test_browser_failure_is_reported_and_does_not_mark_complete(self):
        self.runtime.chromium.launch.side_effect = RuntimeError("browser missing")
        with self.assertRaises(typer.Exit):
            sender.send_messages()
        self.assertNotEqual(self.config["SETTINGS"]["last_send"], self.today)
        self.save.assert_not_called()

    def test_config_write_failure_stops_and_closes_browser(self):
        self.save.side_effect = OSError("disk full")
        with self.assertRaises(typer.Exit):
            sender.send_messages()
        self.assertEqual(self.send.call_count, 1)
        self.assertNotEqual(self.config["SETTINGS"]["last_send"], self.today)
        self.browser.close.assert_called_once()


# The inbox includes similar usernames and hidden elements. Opening a chat
# renders a localized editor asynchronously, and sending clears it only after
# the mock UI accepts the draft. All network traffic stays inside the fixture.
INBOX = """<!doctype html><html><body>
<span style="display:none">alice</span>
<input aria-label="Send a message..." style="display:none">
<button onclick="openChat('alice_extra')"><span>alice_extra</span></button>
<button onclick="openChat('alice')"><span>alice</span></button>
<button onclick="openChat('bob')"><span>bob</span></button>
<div id="conversation"></div>
<script>
function openChat(user) {
  setTimeout(() => {
    document.querySelector('#conversation').innerHTML =
      '<div contenteditable="true" data-e2e="message-input-area" aria-label="Отправить сообщение"></div>' +
      '<button data-e2e="message-send">Отправить</button>';
    const editor = document.querySelector('[contenteditable]');
    document.querySelector('[data-e2e="message-send"]').onclick = () => {
      setTimeout(() => {
        console.log(JSON.stringify({user, message: editor.textContent}));
        editor.textContent = '';
      }, 100);
    };
  }, 50);
}
</script></body></html>"""


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("STREAK_SAVER_TEST_BROWSER_PATH") or shutil.which("chromium")
        try:
            cls.browser = cls.playwright.chromium.launch(executable_path=executable)
        except Exception:
            cls.playwright.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.addCleanup(self.page.close)
        self.page.route("**/*", lambda route: route.fulfill(body=INBOX, content_type="text/html"))
        self.sent = []
        self.page.on("console", lambda event: self.sent.append(json.loads(event.text)))

    def test_multiple_recipients_with_russian_and_english_messages(self):
        sender._send_message(self.page, "alice", "Привет, сохраним серию! ❤️")
        sender._send_message(self.page, "bob", "Hello ❤️")
        self.assertEqual(self.sent, [
            {"user": "alice", "message": "Привет, сохраним серию! ❤️"},
            {"user": "bob", "message": "Hello ❤️"},
        ])

    def test_original_partial_username_match_selects_wrong_recipient(self):
        self.page.goto("https://www.tiktok.com/messages")
        self.page.locator('span[style="display:none"]').evaluate("element => element.remove()")
        self.page.locator("span").get_by_text("alice").first.click()
        editor = self.page.locator('[data-e2e="message-input-area"]')
        editor.fill("Привет")
        self.page.locator('[data-e2e="message-send"]').click()
        expect(editor).to_be_empty()
        self.assertEqual(self.sent, [{"user": "alice_extra", "message": "Привет"}])

    def test_old_accessible_label_layout_remains_supported(self):
        self.page.unroute("**/*")
        old_layout = INBOX.replace('data-e2e="message-input-area" aria-label="Отправить сообщение"',
                                   'aria-label="Send a message..."')
        self.page.route("**/*", lambda route: route.fulfill(body=old_layout, content_type="text/html"))
        sender._send_message(self.page, "bob", "Привет")
        self.assertEqual(self.sent, [{"user": "bob", "message": "Привет"}])

    def test_unconsumed_draft_is_a_failure(self):
        self.page.unroute("**/*")
        stuck_layout = INBOX.replace("editor.textContent = '';", "/* Send did not consume the draft. */")
        self.page.route("**/*", lambda route: route.fulfill(body=stuck_layout, content_type="text/html"))
        with self.assertRaises(AssertionError):
            sender._send_message(self.page, "bob", "Привет")


if __name__ == "__main__":
    unittest.main()
