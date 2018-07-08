
def test_toppage(client):
    resp = client.get('/')
    assert b'DOC' in resp.data
