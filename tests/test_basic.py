"""Unit tests for the non-GUI parts: hotkey parsing and the config store."""

import json

import pytest

from screenit.hotkey import (
    MOD_CONTROL,
    MOD_SHIFT,
    HotkeyError,
    parse_hotkey,
)


def test_parse_basic_combo():
    hk = parse_hotkey("Ctrl+Shift+S")
    assert hk.modifiers & MOD_CONTROL
    assert hk.modifiers & MOD_SHIFT
    assert hk.vk == ord("S")


def test_parse_is_case_insensitive():
    assert parse_hotkey("ctrl+shift+s") == parse_hotkey("Ctrl+Shift+S")


def test_parse_function_and_named_keys():
    assert parse_hotkey("F8").vk == 0x77
    assert parse_hotkey("Win+PrintScreen").vk == 0x2C


@pytest.mark.parametrize("bad", ["", "Ctrl+", "Ctrl+Nope", "+"])
def test_parse_rejects_garbage(bad):
    with pytest.raises(HotkeyError):
        parse_hotkey(bad)


@pytest.fixture
def appdata(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    return tmp_path


def test_config_roundtrip(appdata):
    from screenit.config import Config

    Config(hotkey="Alt+X", magnifier_zoom=5).save()
    loaded = Config.load()
    assert loaded.hotkey == "Alt+X"
    assert loaded.magnifier_zoom == 5


def test_config_corrupt_falls_back_to_defaults(appdata):
    from screenit.config import Config
    from screenit.paths import config_file

    config_file().write_text("{ this is not json", encoding="utf-8")
    cfg = Config.load()  # must not raise
    assert cfg.hotkey == "Ctrl+Shift+S"


def test_config_save_is_atomic_no_tmp_left(appdata):
    from screenit.config import Config
    from screenit.paths import config_file

    Config().save()
    leftovers = list(config_file().parent.glob("*.tmp"))
    assert leftovers == []
    # and the written file is valid JSON
    json.loads(config_file().read_text(encoding="utf-8"))
