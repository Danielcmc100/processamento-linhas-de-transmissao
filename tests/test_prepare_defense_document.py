"""Version-aware copying of standalone manuscript evidence assets."""

from pathlib import Path

import pytest

from scripts.prepare_defense_document import main


def test_copier_follows_each_reference_version(tmp_path: Path) -> None:
    document = tmp_path / "doc"
    document.mkdir()
    references = [
        "evidence/v2/tables/probability.tex",
        "evidence/v3/tables/probability.tex",
        "evidence/v3/figures/distribution.pdf",
    ]
    for reference in references:
        relative = Path(reference).relative_to("evidence")
        source = tmp_path / "results/defense-evidence" / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(reference.encode())
    historical = document / "evidence/v1/keep.txt"
    historical.parent.mkdir(parents=True)
    historical.write_bytes(b"historical")
    (document / "main.tex").write_text(
        "\n".join("{" + reference + "}" for reference in references),
        encoding="utf-8",
    )

    main(root=tmp_path)

    for reference in references:
        assert (document / reference).read_bytes() == reference.encode()
    assert historical.read_bytes() == b"historical"


def test_missing_v3_asset_does_not_fall_back_to_v2(tmp_path: Path) -> None:
    document = tmp_path / "doc"
    document.mkdir()
    (document / "main.tex").write_text(
        "{evidence/v3/tables/probability.tex}", encoding="utf-8"
    )
    old = tmp_path / "results/defense-evidence/v2/tables/probability.tex"
    old.parent.mkdir(parents=True)
    old.write_bytes(b"old")

    with pytest.raises(FileNotFoundError):
        main(root=tmp_path)
    assert not (document / "evidence/v3/tables/probability.tex").exists()
