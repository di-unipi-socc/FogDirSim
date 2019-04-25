def test_create(database, device):
    dict_representation = device.to_dict()
    with database:
        new_device, = database.logic.create(device)
        assert new_device == device
    with database:
        assert dict_representation == database.logic.get_device(deviceId=dict_representation['deviceId']).to_dict()


def test_select_device(database, device):
    with database:
        database.logic.create(device)
        assert device == database.logic.get_device(device.deviceId)
        assert database.logic.get_device('not-existing-device') is None


def test_select_device_metric(database, device_metric):
    with database:
        database.logic.create(device_metric)
        database.current_session.flush()
        assert device_metric == database.logic.get_device_metric(device_metric.iterationCount, device_metric.deviceId, device_metric.metricType)
        assert database.logic.get_device_metric(device_metric.iterationCount + 1, device_metric.deviceId, device_metric.metricType) is None


def test_select_job(database, job):
    with database:
        database.logic.create(job)
        assert job == database.logic.get_job(job.jobId)
        assert database.logic.get_job('not-existing-job') is None


def test_select_job_metric(database, job, job_metric):
    with database:
        database.logic.create(job, job_metric)
        database.current_session.flush()
        assert job_metric == database.logic.get_job_metric(job_metric.iterationCount, job_metric.jobId, job_metric.metricType)
        assert database.logic.get_job_metric(job_metric.iterationCount + 1, job_metric.jobId, job_metric.metricType) is None


def test_select_application(database, application):
    with database:
        database.logic.create(application)
        database.current_session.flush()
        assert application == database.logic.get_application(application.localAppId, application.version)
        assert database.logic.get_application(application.localAppId, 'a-random-version') is None


def test_select_my_app(database, my_app):
    with database:
        database.logic.create(my_app)
        database.current_session.flush()
        assert my_app == database.logic.get_my_app(my_app.myAppId)
        assert database.logic.get_my_app(myAppId='not-existing-myApp') is None
