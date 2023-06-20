"""
Copyright 2023 Google. This software is provided as-is, without 
warranty or representation for any use or purpose. Your use of 
it is subject to your agreement with Google. 
"""

from distutils.log import info
import functions_framework
import json
import requests
import sys
import datetime
import time
import traceback

from util import MyUtilities
utilities = MyUtilities('list-apis')
logger = utilities.logger

# utilities object is a global object which will help other functions with lazy load
script_name = 'main.py'

util_ins_start_time = datetime.datetime.now()

def time_diff_ms(start_time):
  secs = (datetime.datetime.now() - start_time)
  ts = secs.total_seconds()
  return round(secs.total_seconds(), 3)


@functions_framework.http
def main(request):

  try:

    local_func_name = 'main'
    main_start_time = datetime.datetime.now()

    log_prefix = ':'.join([script_name, local_func_name])

    return_msg = "{} Execution Starts at {} with request:{}".format(log_prefix, datetime.datetime.now(), request)  
    logger.info(return_msg)
    
    return_msg = "{} Converting request to JSON".format(log_prefix)  
    logger.debug(return_msg)
    request_dict = json.loads(request)
    return_msg = "{} Converted successfully request to JSON".format(log_prefix)  

    start_time = datetime.datetime.now()
    if request_dict["action"].upper() == "LIST":
      _response = utilities.list_services(project_number=request_dict["project_number"])
    elif request_dict["action"].upper() == "ENABLE":
      _response = utilities.enable_service(project_number=request_dict["project_number"], service_name=request_dict["service_api"])
    elif request_dict["action"].upper() == "DISABLE":
      _response = utilities.disable_service(project_number=request_dict["project_number"], service_name=request_dict["service_api"])

    print(_response)
    time_diff = time_diff_ms(start_time)
    return_msg = "{} Completed Successfully. Execution time: {} ms getting list of service".format(log_prefix, time_diff)
    logger.info(return_msg)

  except Exception as err:
    exc_type, exc_obj, tb = sys.exc_info()
    lineno = str(tb.tb_lineno)
    time_diff = time_diff_ms(start_time)
    return_code = utilities.return_status_500

    return_msg= "{} Execution Failed. Call Stack:{}".format(log_prefix, time_diff, traceback.print_exc())
    logger.debug(return_msg)

    if isinstance(err, ValueError):
      return_msg = "{} Execution Failed. Execution Time {} Error at line {}:{}".format(log_prefix, time_diff, lineno, err.args[0])
      return_code = err.args[1] # Capture the code as propagated from ValueError
    else:
      # Default Return Code = 500 (Also signaling re-try for cloud tasks)
      return_msg = "{} Execution Failed. Execution Time {} Error at line {}:{}".format(log_prefix, time_diff, lineno, str(err))
    
    logger.error(return_msg)
    return return_code

if __name__ == '__main__':
  
  request_mock = {"action":"ENABLE", "project_number":"76786460898","service_api":"datalineage.googleapis.com"}
  main(json.dumps(request_mock))
  #request_mock = {"action":"DISABLE", "project_number":"76786460898","service_api":"datalineage.googleapis.com"}
  #main(json.dumps(request_mock))
  #request_mock = {"action":"LIST", "project_number":"76786460898","service_api":"None"}
  #main(json.dumps(request_mock))