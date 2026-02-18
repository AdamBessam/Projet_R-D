from src import search


def test_is_authorized():
    # access_order: public=0, internal=1, confidential=2
    assert search.is_authorized("public", "public") is True
    # using access level names (not user role names)
    assert search.is_authorized("public", "internal") is True
    assert search.is_authorized("internal", "internal") is True
    assert search.is_authorized("confidential", "internal") is False
    assert search.is_authorized("confidential", "confidential") is True
