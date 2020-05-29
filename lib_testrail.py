def test_run(run_id):
    """iterates the given Test Run and executes each test"""
    tests = testrail_client.send_get('get_tests/' + run_id)
    for test in tests:
        test_id = test['id']
        test_name = test['custom_autotest_name']
        if test_name is not None:
            print(f"Test name: {test['title']}, autotest: {test_name}")
            assert hasattr(TestFactory, test_name)
            time1 = time.time()
            # result, comment = TestFactory.test_ma_values()
            result, comment = getattr(TestFactory, test_name)()
            elapsed = str(round(time.time() - time1)) + "s"
            print(f"Result: {results[result]}, {comment}, spent {elapsed}")
            testrail_client.send_post(f'add_result/{test_id}',
                                      {'status_id': result, 'comment': comment, 'elapsed': elapsed}
                                      )


def get_test_runs():
    items = testrail_client.send_get('get_runs/1')
    for item in items:
        print("{}: {}".format(item['id'], item['name']))

# testrail_client = APIClient('https://denwer.testrail.io')
# testrail_client.user = 'eyewall@mail.ru'
# testrail_client.password = 'testrail'