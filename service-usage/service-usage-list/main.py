"""
Copyright 2022 Google. This software is provided as-is, without 
warranty or representation for any use or purpose. Your use of 
it is subject to your agreement with Google. 
"""

from distutils.log import info
import functions_framework
import json
import requests
from util import util
import gcsfs
import sys
import datetime
import time

# utilities object is a global object which will help other functions with lazy load
script_name = 'main.py'

util_ins_start_time = datetime.datetime.now()
utilities = util('load-file')
logger = utilities.logger

logger.info("{}:{} Start Time {}".format(script_name, 'InstatingUtilities', util_ins_start_time))
util_ins_time_diff = utilities.time_diff_ms(util_ins_start_time)
logger.info("{}:{} Execution time {} End time={} InstatingUtilities".format(script_name, 'InstatingUtilities', util_ins_time_diff, datetime.datetime.now()))



def time_diff_ms(start_time):
  secs = (datetime.datetime.now() - start_time)
  ts = secs.total_seconds()
  return round(secs.total_seconds(), 3)


@functions_framework.http
def main(request):

  local_func_name = 'main'
  main_start_time = datetime.datetime.now()

  log_prefix = ':'.join([script_name, local_func_name])

  return_msg = "{} Execution Starts at {}".format(log_prefix, datetime.datetime.now())  
  logger.info(return_msg)

  try:
    start_time = datetime.datetime.now()
    time_diff = time_diff_ms(start_time)
    logger.debug("{} Execution Time {} API Payload executed".format(log_prefix, time_diff))
    #get_bearer_token
    token, token_message, token_status = utilities.get_bearer_token()
    time_diff = time_diff_ms(start_time)
    logger.debug("{} Execution Time {} Bearer token execution".format(log_prefix, time_diff))
    if token_status == utilities.return_status_success:
      logger.debug("{} Bearer token acquired".format(log_prefix))
    else:
      return_msg = "Cannot acquire the bearer token {}".format(token_message)
      # Failed Return,  If can't build payload then no need to retry
      raise ValueError(return_msg, utilities.return_status_200)

    #Call dw api to upload file  
    start_time = datetime.datetime.now()

    #Calling upload_document
    #response, upload_status = upload_document(utilities.doc_wh_url, payload, token)

    api_time_diff = time_diff_ms(start_time)
    logger.debug("{} API Execution Time {} API Response:{}".format(log_prefix, api_time_diff, response))

  except Exception as err:
    exc_type, exc_obj, tb = sys.exc_info()
    lineno = str(tb.tb_lineno)
    time_diff = time_diff_ms(start_time)
    return_code = utilities.return_status_500
    
    if isinstance(err, ValueError):
      return_msg = "{} Execution Time {} Error at line {}:{}".format(log_prefix, time_diff, lineno, err.args[0])
      return_code = err.args[1] # Capture the code as propagated from ValueError
    else:
      # Default Return Code = 500 (Also signaling re-try for cloud tasks)
      return_msg = "{} Execution Time {} Error at line {}:{}".format(log_prefix, time_diff, lineno, str(err))
    
    if result[1] == utilities.return_status_success:
      return_msg = "{} Status for auto_gen_id {} updated to {}".format(return_msg, str(auto_gen_id), utilities.status_error)
    else: # Can't update DB
      return_msg = "{} {}".format(return_msg, result[0])  # Get the message as from update function

    logger.error(return_msg)
    return return_code