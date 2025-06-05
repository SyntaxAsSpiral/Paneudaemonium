from pathlib import Path
import sys
import random
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from glyphs.novonox import summon_novonox


def test_summon_novonox_cycle(tmp_path: Path) -> None:
    options = ['a', 'b']
    cache = tmp_path / 'cache.txt'
    log = tmp_path / 'log.txt'

    random.seed(1)
    first = summon_novonox(options, cache, limit=2, echo_log=log)
    second = summon_novonox(options, cache, limit=2, echo_log=log)

    assert {first, second} == set(options)

    third = summon_novonox(options, cache, limit=2, echo_log=log)
    assert third in options
    text = log.read_text(encoding='utf-8')
    assert '# Nōvonox Cycle Reset' in text
