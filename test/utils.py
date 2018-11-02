import json
def test_publish_function(response):
    data = response.json()["data"][0]
    data["published"] = True
    return {"app_data": json.dumps(data), "localAppId": data["localAppId"], "localAppVersion": data["version"]}

def test_notpublish(response):
    data = response.json()
    return data["published"] == False
