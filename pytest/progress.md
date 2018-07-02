# Tests available

| done | description                         | api endpoint             |  test_method name |
|:----:|-----------------------------------  |--------------------------|-------------------|
|      | attempt to goto '/'                 | /                        | test_toppage      |
|  O   | login with 'application/json'       | /api/auth/               | test_login        |
|  O   | login with 'form'                   |  |-                      | test_login_form   |
|  O   | login with Unsupported Content-Type |  |-                      | test_login_invaild|
|  O   | test whether given token is vaild   |  |-                      | test_auth_token   |
|  O   | test whether given status is vaild  | /api/status              | test_status       |

|      |                                     | /api/users               | test_users_list   |
|      |                                     | /api/users/<id> [GET]    | test_user_find    |
|      |                                     | /api/users/<id> [DELETE] | test_user_find    |
|      |                                     | /api/classrooms       |                      |
|      |                                     | /api/classrooms/<id>/ |                      |
|      |                                     | /api/classrooms/<id>/winners |               |
|      |                                     | /api/classrooms/<id>/winners/<id> |          |
|      |                                     | /api/lotteries               |               |
|      |                                     | /api/lotteries/<id> [GET]    |               |
|      |                                     | /api/lotteries/<id> [POST    |               |
|      |                                     | /api/lotteries/<id> [DELETE] |               |
|      |                                     | /api/lotteries/<id>/draw     |               |
