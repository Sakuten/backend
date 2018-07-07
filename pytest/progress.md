# Tests available

| done | description                           | permission | api endpoint                       | status code |  test_method name                      | misk        |
|:----:|---------------------------------------|------------|------------------------------------|-------------|----------------------------------------|-------------|
|      | attempt to goto '/'                   |  -         | /                                  |             | test_toppage                           |             |
|  O   | login with 'application/json'         |  -         | /api/auth/                         | 200         | test_login                             |             |
|  O   | login with 'form'                     |  -         |   -                                | 200         | test_login_form                        |             |
|  O   | login with Unsupported Content-Type   |  -         |   -                                | 400         | test_login_invaild                     |             |
|  O   | test whether given token is vaild     |  -         |   -                                | 400         | test_auth_token                        |             |
|  O   | test whether given status is vaild    |  user      | /api/status                        | 200         | test_status                            |             |
|  O   | attempt with invaild header           |  user      | /api/status                        | 401         | test_status_invaild_header             |             |
|  O   | attempt without proper auth           |  user      | /api/status                        | 401         | test_status_invaild_auth               |             |
|  O   | test whether given list is correct    |  -         | /api/classrooms                    | 200         | test_get_allclassrooms                 |             |
|  O   | test whether given list is correct    |  -         | /api/classrooms/<id>/              | 200         | test_get_specific_classroom            |             |
|  O   | attempt to give invaild id            |  -         | /api/classrooms/<id>/              | 400         | test_get_specific_classroom_invaild_id |             |
|  O   | test whether given list is correct    |  -         | /api/lotteries                     | 200         | test_get_alllotteries                  |             |
|  O   | test whether given list is correct    |  -         | /api/lotteries/<id>                | 200         | test_get_specific_lottery              |             |
|  O   | attempt to give invaild id            |  -         | /api/lotteries/<id>                | 400         | test_get_specific_lottery_invalid_id   |             |
|  O   | check DB is changed correctly         |  user      | /api/lotteries/<id>/apply [PUT]    | 200         | test_apply                             |             |
|  O   | attempt to apply without permission   |  user      | /api/lotteries/<id>/apply [PUT]    | 403         | test_apply_noperm                      | for future  |
|  O   | attempt to apply invaild lottery      |  user      | /api/lotteries/<id>/apply [PUT]    | 400         | test_apply_invaild                     |             |
|      | attempt to apply already-done lottery |  user      | /api/lotteries/<id>/apply [PUT]    | 400         | test_apply_already_done                |             |
|      | attempt to apply the same period      |  user      | /api/lotteries/<id>/apply [PUT]    | 400         | test_apply_same_period                 |             |
|  O   | check DB is changed correctly         |  user      | /api/lotteries/<id>/apply [DELETE] | 200         | test_cancel                            |             |
|      | attempt to cancel invaild lottery     |  user      | /api/lotteries/<id>/apply [DELETE] | 400         | test_cancel_invaild                    |             |
|      | attempt to cancel already-done lottery|  user      | /api/lotteries/<id>/apply [DELETE] | 400         | test_cancel_already_done               |             |
|      | attempt to cancel without permission  |  user      | /api/lotteries/<id>/apply [DELETE] | 403         | test_cancel_noperm                     | for future  |
|      | draw lottery & check DB is changed    |  admin     | /api/lotteries/<id>/draw           | 200         | test_draw                              |             |
|      | attempt to draw invaild lottery       |  admin     | /api/lotteries/<id>/draw           | 400         | test_draw_invaild                      |             |
|      | attempt to draw already-done lottery  |  admin     | /api/lotteries/<id>/draw           | 400         | test_draw_already_done                 |             |
|      | attempt to draw without permission    |  admin     | /api/lotteries/<id>/draw           | 403         | test_draw_noperm                       |             |
