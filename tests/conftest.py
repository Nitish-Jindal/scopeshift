import pytest

from scopeshift.dataset import load_dataset


@pytest.fixture
def scenarios():
    return {s.id: s for s in load_dataset()}
