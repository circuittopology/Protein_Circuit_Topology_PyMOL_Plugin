"""Tests for the shared PyMOL object model."""
from utils.pymol_objects import PymolObjects


def test_refresh_emits_only_when_the_object_list_changes(pymol_clean, qapp, tmp_path):
    """changed fires on a real change and stays quiet otherwise."""
    from conftest import write_multimodel_pdb

    model = PymolObjects()
    model.stop()  # manual, no timer needed.
    seen: list[list[str]] = []
    model.changed.connect(seen.append)

    # First refresh against an empty session.
    model.refresh()
    assert seen == []
    assert model.objects == []

    pdb = write_multimodel_pdb(tmp_path / "m.pdb", n_models=2)
    pymol_clean.load(str(pdb), "alpha")
    model.refresh()
    assert seen == [["alpha"]]
    assert model.objects == ["alpha"]

    # Nothing changed, so no signal emitted.
    model.refresh()
    assert len(seen) == 1

    pymol_clean.load(str(pdb), "beta")
    model.refresh()
    assert len(seen) == 2
    assert seen[-1] == ["alpha", "beta"]

    pymol_clean.delete("alpha")
    model.refresh()
    assert seen[-1] == ["beta"]


def test_objects_property_is_a_copy(pymol_clean, qapp, tmp_path):
    """Callers must not be able to mutate the model's internal list."""
    from conftest import write_multimodel_pdb

    model = PymolObjects()
    model.stop()
    pymol_clean.load(str(write_multimodel_pdb(tmp_path / "m.pdb", n_models=1)), "gamma")
    model.refresh()

    snapshot = model.objects
    snapshot.append("not_real")
    assert model.objects == ["gamma"]


def test_stop_halts_polling(qapp):
    """A stopped model must leave no live timer, which is what closeEvent relies on."""
    model = PymolObjects()
    assert model._timer.isActive()
    model.stop()
    assert not model._timer.isActive()


def test_refresh_survives_a_pymol_failure(pymol_clean, qapp, monkeypatch):
    """A poll runs on a timer with no user context, so it must never propagate an exception."""
    import utils.pymol_objects as mod

    model = PymolObjects()
    model.stop()

    def boom(*_a, **_kw):
        msg = "PyMOL is busy"
        raise RuntimeError(msg)

    monkeypatch.setattr(mod.cmd, "get_object_list", boom)
    model.refresh()
    assert model.objects == []
