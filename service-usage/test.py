import sys, json

try:
    request_mock = {"action":"LIST", "project_number":"76786460898","service_api":""}
    print(type(request_mock))
    _json = json.dumps(request_mock)
    print(type(_json))
except Exception as err:
    exc_type, exc_obj, tb = sys.exc_info()
    lineno = str(tb.tb_lineno)
    print(type(exc_type), exc_type)

    print(type(exc_obj), exc_obj)

    print(tb.tb_lineno)