# Tests available

| done | description                           | api endpoint                       | status code |  test_method name                      |
|:----:|---------------------------------------|------------------------------------|-------------|----------------------------------------|
|      | attempt to goto '/'                   | /                                  |             | test_toppage                           |
|  O   | login with 'application/json'         | /api/auth/                         | 200         | test_login                             |
|  O   | login with 'form'                     |   -                                | 200         | test_login_form                        |
|  O   | login with Unsupported Content-Type   |   -                                | 400         | test_login_invaild                     |
|  O   | test whether given token is vaild     |   -                                | 400         | test_auth_token                        |
|  O   | test whether given status is vaild    | /api/status                        | 200         | test_status                            |
|  O   | attempt without proper auth           | /api/status                        | 400         | test_status_invaild_auth               |
|  O   | attempt with wrong header             | /api/status                        | 400         | test_status_wrong_header               |
|  O   | test whether given list is correct    | /api/classrooms                    | 200         | test_get_allclassrooms                 |
|  O   | test whether given list is correct    | /api/classrooms/<id>/              | 200         | test_get_specific_classroom            |
|  O   | attempt to give invaild id            | /api/classrooms/<id>/              | 400         | test_get_specific_classroom_invaild_id |
|  O   | test whether given list is correct    | /api/lotteries                     | 200         | test_get_alllotteries                  |
|  O   | test whether given list is correct    | /api/lotteries/<id>                | 200         | test_get_specific_lottery              |
|      | attempt to give invaild id            | /api/lotteries/<id>                | 400         | test_get_specific_lottery_invalid_id   |
|  O   | check DB is changed correctly         | /api/lotteries/<id>/apply [PUT]    | 200         | test_apply                             |
|      | attempt to apply with wrong header    | /api/lotteries/<id>/apply [PUT]    | 400         | test_apply_invaild_header              |
|      | attempt to apply with wrong auth data | /api/lotteries/<id>/apply [PUT]    | 401         | test_apply_invaild_auth                |
|      | attempt to apply without permission   | /api/lotteries/<id>/apply [PUT]    | 403         | test_apply_noperm                      |
|      | attempt to apply invaild lottery      | /api/lotteries/<id>/apply [PUT]    | 404         | test_apply_invaild                     |
|      | check DB is changed correctly         | /api/lotteries/<id>/apply [DELETE] | 200         | test_cancel                            |
|      | attempt to apply with wrong header    | /api/lotteries/<id>/apply [DELETE] | 400         | test_cancel_invaild_header             |
|      | attempt to apply with wrong auth      | /api/lotteries/<id>/apply [DELETE] | 401         | test_cancel_invaild_auth               |
|      | attempt to apply without permission   | /api/lotteries/<id>/apply [DELETE] | 403         | test_cancel_noperm                     |
|      | attempt to apply invaild lottery      | /api/lotteries/<id>/apply [DELETE] | 404         | test_cancel_invaild                    |
|      | draw lottery & check DB is changed    | /api/lotteries/<id>/draw           | 200         | test_draw                              |
|      | attempt to draw with wrong header     | /api/lotteries/<id>/draw           | 400         | test_draw_invaild_header               |
|      | attempt to draw with wrong auth       | /api/lotteries/<id>/draw           | 401         | test_draw_invaild_auth                 |
|      | attempt to draw without permission    | /api/lotteries/<id>/draw           | 403         | test_draw_noperm                       |
|      | attempt to draw invaild lottery       | /api/lotteries/<id>/draw           | 404         | test_draw_invaild                      |
