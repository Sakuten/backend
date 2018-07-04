# Tests available

| done | description                         | api endpoint                       |  test_method name                |
|:----:|-------------------------------------|------------------------------------|----------------------------------|
|      | attempt to goto '/'                 | /                                  | test_toppage                     |
|  O   | login with 'application/json'       | /api/auth/                         | test_login                       |
|  O   | login with 'form'                   |   -                                | test_login_form                  |
|  O   | login with Unsupported Content-Type |   -                                | test_login_invaild               |
|  O   | test whether given token is vaild   |   -                                | test_auth_token                  |
|  O   | test whether given status is vaild  | /api/status                        | test_status                      |
|      | test whether given list is correct  | /api/users                         | test_users_list                  |
|      | search user with id                 | /api/users/<id> [GET]              | test_user_find                   |
|      | ban user                            | /api/users/<id> [DELETE]           | test_user_ban                    |
|  O   | test whether given list is correct  | /api/classrooms                    | test_get_allclassrooms           |
|  O   | test whether given list is correct  | /api/classrooms/<id>/              | test_get_specific_classroom      |
|      | test whether given list is correct  | /api/classrooms/<id>/winners       |                                  |
|      | test whether given list is correct  | /api/classrooms/<id>/winners/<id>  |                                  |
|  O   | test whether given list is correct  | /api/lotteries                     |                                  |
|  O   | test whether given list is correct  | /api/lotteries/<id>                |                                  |
|      | test whether given list is correct  | /api/lotteries/<id>/apply [PUT]    |                                  |
|      |                                     | /api/lotteries/<id>/apply [DELETE] |                                  |
|      | draw lottery & check DB is changed  | /api/lotteries/<id>/draw           |                                  |
