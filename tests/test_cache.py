import uuid

from swit.api.cache import CacheManager


def test_cache_initialization():
    mgr = CacheManager()
    assert mgr.cache_dir.exists()
    assert mgr.cache_dir.is_dir()


def test_cache_packages():
    mgr = CacheManager()
    uid = uuid.uuid4().hex[:8]
    pkg = f"test-custom-pkg-{uid}"
    assert not mgr.is_package_cached(pkg)

    mgr.cache_package(pkg)
    assert mgr.is_package_cached(pkg)
    assert mgr.is_package_cached(f"test_custom_pkg_{uid}")


def test_cache_requirements_sync(tmp_path):
    mgr = CacheManager()
    fake_req = tmp_path / "requirements.txt"
    fake_req.write_text("rich>=13.0\npyyaml==6.0.2\n", encoding="utf-8")

    mgr.save_requirements_sync(fake_req)
    assert mgr.is_requirements_synced(fake_req)

    # Change requirements
    fake_req.write_text("rich>=14.0\n", encoding="utf-8")
    assert not mgr.is_requirements_synced(fake_req)


def test_cache_custom_data():
    mgr = CacheManager()
    mgr.set("test_key", {"version": 1, "loaded": True})

    data = mgr.get("test_key")
    assert data == {"version": 1, "loaded": True}
