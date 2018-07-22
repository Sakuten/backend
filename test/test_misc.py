def test_trailing_slash(client):
    """test the behavior of trailing slash
        target_url: /api/classrooms, /api/classrooms/
        both urls are expected to behave samely
    """
    resp = client.get('/api/classrooms', follow_redirects=False)
    resp_with_slash = client.get('/api/classrooms/', follow_redirects=False)

    assert resp_with_slash.status_code != 300
    assert resp.get_json() == resp_with_slash.get_json()
