import pytest

from mail_agent import MailError, create_error_message, create_success_message, get_tud_credentials


def test_success_message():
    msg = create_success_message("from@example.org", "to@example.org", "Exp1", additional_text="extra")
    assert msg["To"] == "to@example.org"
    assert msg["Subject"] == "Successful run of experiment Exp1"
    assert "extra" in msg.get_content()


def test_error_message_custom_subject():
    msg = create_error_message("from@example.org", "to@example.org", "Exp1", "Traceback ...", individual_subject="Oops")
    assert msg["Subject"] == "Oops"
    assert "Traceback ..." in msg.get_content()


def test_credentials_from_file(tmp_path, monkeypatch):
    monkeypatch.delenv("TUD_MAIL_USERNAME", raising=False)
    monkeypatch.delenv("TUD_MAIL_PASSWORD", raising=False)
    env_file = tmp_path / "mail.env"
    env_file.write_text("TUD_MAIL_USERNAME=user@example.org\nTUD_MAIL_PASSWORD=secret\n")

    assert get_tud_credentials(env_file) == ("user@example.org", "secret")


def test_credentials_from_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TUD_MAIL_USERNAME", "env@example.org")
    monkeypatch.setenv("TUD_MAIL_PASSWORD", "pw")

    assert get_tud_credentials() == ("env@example.org", "pw")


def test_missing_credentials_file_raises_mail_error(tmp_path):
    with pytest.raises(MailError):
        get_tud_credentials(tmp_path / "does_not_exist.env")
