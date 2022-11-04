from inmanta.config import Config
from inmanta_ui import config as cfg

def test_config_deprecated_sections(caplog):
    for (deprecated_option, new_option) in [
        # (cfg.dash_path, cfg.web_ui_path),
        (cfg.dash_realm, cfg.web_ui_realm),
        # (cfg.dash_auth_url, cfg.web_ui_auth_url),
        # (cfg.dash_client_id, cfg.web_ui_client_id),
    ]:
        with caplog.at_level('WARNING'):
            Config.set(deprecated_option.section, deprecated_option.name, "22")
            caplog.clear()
            assert new_option.get() == "22"
            assert "Config option %s is in deprecated section %s. Use option %s in section %s instead" % (deprecated_option.name, deprecated_option.section, new_option.name, new_option.section) in caplog.text

            Config.set(new_option.section, new_option.name, "23")
            caplog.clear()
            assert new_option.get() == "23"
            assert "Config option %s is in deprecated section %s. Use option %s in section %s instead" % (deprecated_option.name, deprecated_option.section, new_option.name, new_option.section) not in caplog.text

            Config.load_config()  # Reset config options to default values
            assert new_option.get() != "23"
            assert deprecated_option.get() != "23"
            Config.set(new_option.section, new_option.name, "24")
            caplog.clear()
            assert new_option.get() == "24"
            assert "Config option %s is in deprecated section %s. Use option %s in section %s instead" % (deprecated_option.name, deprecated_option.section, new_option.name, new_option.section) not in caplog.text
