from swit.api.utils.package import install_package


def test_install_package_already_installed():
    # pyyaml and discord-py are installed in environment.
    # install_package should detect them immediately without running pip.
    assert install_package("pyyaml") is True
    assert install_package("discord-py") is True
    assert install_package("rich") is True
