"""
Copyright 2023 Google. This software is provided as-is, without 
warranty or representation for any use or purpose. Your use of 
it is subject to your agreement with Google. 
"""
import configparser
import base64
import datetime
from google.cloud import logging as cloudlogging
import logging
import json
import os
import time
from google.auth.transport import requests
import google
#from google.cloud.pubsub import SchemaServiceClient

from google.cloud import service_usage_v1

class MyUtilities:
  def __init__(self, function_name):
    """
    The constructor initializes all the required parameters for 
    estabising connection between MySql (hosted in Cloud SQL)
    with cloud function version 1.
    Input  : Function name
    Output : util object
    """

    self.function_name = function_name
    self.script_name = 'util.py'
    print('Done')

    self.config = configparser.ConfigParser()
    self.config.read('config.ini')

    # Config [DEFAULT] section
    self.project_id = self.config.get('DEFAULT', 'PROJECT_ID', fallback='None')
    self.region = self.config.get('DEFAULT', 'REGION', fallback='None')

    # Config [RETURN_STATUS] section
    self.return_status_success = self.config.get('RETURN_STATUS', 'RETURN_STATUS_SUCCESS', fallback='0')
    self.return_status_fail = self.config.get('RETURN_STATUS', 'RETURN_STATUS_FAIL', fallback='1')
    self.return_status_500 = self.config.get('RETURN_STATUS', 'RETURN_STATUS_500', fallback='500')
    self.return_status_200 = self.config.get('RETURN_STATUS', 'RETURN_STATUS_200', fallback='200')
    self.return_status_not_found = self.config.get('RETURN_STATUS', 'RETURN_STATUS_NOT_FOUND', fallback='404')
    self.return_status_token_expired = self.config.get('RETURN_STATUS', 'RETURN_STATUS_TOKEN_EXPIRED', fallback='401')

    # Config [API_RESPONSE_CODES] section
    self.status_attempt = self.config.get('API_RESPONSE_CODES', 'STATUS_ATTEMPT', fallback='100')
    self.status_success = self.config.get('API_RESPONSE_CODES', 'STATUS_SUCCESS', fallback='200')
    self.status_error = self.config.get('API_RESPONSE_CODES', 'STATUS_ERROR', fallback='500')

    # Config [LOGGING] section
    self.current_log_level = self.config.get('LOGGING', 'CURRENT_LOG_LEVEL', fallback='DEBUG')
    self.log_level_debug = self.config.get('LOGGING', 'LOG_LEVEL_DEBUG', fallback='DEBUG')
    self.log_level_info = self.config.get('LOGGING', 'LOG_LEVEL_INFO', fallback='INFO')
    self.log_level_error = self.config.get('LOGGING', 'LOG_LEVEL_ERROR', fallback='ERROR')

    # Config [ENCODING] section
    self.encoding = self.config.get('ENCODING', 'ASCII', fallback='ASCII')

    # Get Clients
    self.logger = self.get_logger(self.function_name + '-custom')

  def get_logger(self, logger_name):
    print('Setting logger: {}'.format(logger_name))
    try:
      logging_client = cloudlogging.Client()
      logging_handler = logging_client.get_default_handler()
      logger = logging.getLogger(logger_name)
      print('Logger: Required Current Level is {}'.format(self.current_log_level))
      if self.current_log_level == self.log_level_error:
        print('Logger: Error Level')
        logger.setLevel(logging.ERROR)
      elif self.current_log_level == self.log_level_info:
        print('Logger: Info Level')
        logger.setLevel(logging.INFO)
      elif self.current_log_level == self.log_level_debug:
        print('Logger: Debug Level')
        logger.setLevel(logging.DEBUG)
      else:
        print('Logger: Default Info Level')
        logger.setLevel(logging.INFO)

      logger.addHandler(logging_handler)
    except Exception as exp:
      return None

    return logger

  def get_new_token(self):
    '''
    Returns new bearer token
    Input : None
    Output : Returns latest <str> token value from db.
    '''
    local_func_name = 'get_new_token'
    try:
      #Defining Scope
      CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
        
      #Assining credentials and project value
      credentials, PROJECT_ID = google.auth.default(scopes=CREDENTIAL_SCOPES)

      #Refreshing credentials data
      credentials.refresh(requests.Request())
      self.logger.debug(f"{self.script_name}:{local_func_name} Token credentials refreshed.")

      #Get refreshed token
      token = credentials.token
      self.logger.debug(f"{self.script_name}:{local_func_name} Token fetched from refreshed credentials")

      #Encode Token
      encoded_string_bytes = token.encode(self.encoding)
      base64_bytes = base64.b64encode(encoded_string_bytes)
      new_token = base64_bytes.decode(self.encoding)
      self.logger.debug(f"{self.script_name}:{local_func_name} Token value encoded.")

      return new_token
    except Exception as error:
      self.logger.error(f"{self.script_name}:{local_func_name} Failed to refresh token. Error:{error}")
      raise

  def list_services(self, project_number: int) -> list[str]:
    try:
      local_func_name = 'get_new_token'
      # Create a client
      self.logger.debug(f"{self.script_name}:{local_func_name} Creating Client")
      client = service_usage_v1.ServiceUsageClient()
      self.logger.debug(f"{self.script_name}:{local_func_name} Client created")

      # Initialize request argument(s)
      request = service_usage_v1.ListServicesRequest()
      request.parent = 'projects/{}'.format(str(project_number))
      request.filter = 'state:ENABLED'
      self.logger.debug(f"{self.script_name}:{local_func_name} Request:{request}")

      # Make the request
      self.logger.debug(f"{self.script_name}:{local_func_name} Sending request for project-number:{project_number}")
      page_result = client.list_services(request=request)

      # Handle the response
      self.logger.debug(f"{self.script_name}:{local_func_name} Response for request for project-number:{project_number}")
      return_val = [response.name for response in page_result]

      return return_val
    except Exception as error:
      raise


  def enable_service(self, project_number: int, service_name: str) -> str:
    # Create a client
    try:
      
      local_func_name = 'enable_service'
      # Create a client
      self.logger.debug(f"{self.script_name}:{local_func_name} Creating Client")
      client = service_usage_v1.ServiceUsageClient()
      self.logger.debug(f"{self.script_name}:{local_func_name} Client created")

      # Initialize request argument(s)
      request = service_usage_v1.EnableServiceRequest()
      request.name = 'projects/{}/services/{}'.format(str(project_number), service_name)
      self.logger.debug(f"{self.script_name}:{local_func_name} Request:{request}")

      # Make the request
      operation = client.enable_service(request=request)
      response = operation.result()
      self.logger.info(f"{self.script_name}:{local_func_name} response:{response}")
      if response.service.state.name == 'ENABLED':
        return response
      else: 
        return_msg = f"{self.script_name}:{local_func_name} response:{response}"
        raise ValueError(return_msg, self.return_status_500)
    except Exception as error:
      raise

  def disable_service(self, project_number: int, service_name: str) -> str:
    
    try:
      local_func_name = 'disable_service'
      # Create a client
      self.logger.debug(f"{self.script_name}:{local_func_name} Creating Client")
      client = service_usage_v1.ServiceUsageClient()
      self.logger.debug(f"{self.script_name}:{local_func_name} Client created")    
      client = service_usage_v1.ServiceUsageClient()

      # Initialize request argument(s)
      self.logger.debug(f"{self.script_name}:{local_func_name} Setting Request")    
      request = service_usage_v1.DisableServiceRequest()
      request.name = 'projects/{}/services/{}'.format(str(project_number), service_name)
      request.check_if_service_has_usage = 'SKIP'
      self.logger.debug(f"{self.script_name}:{local_func_name} Request:{request}")

      # Make the request
      self.logger.debug(f"{self.script_name}:{local_func_name} Maning Request")
      operation = client.disable_service(request=request)
    
      while not operation.done():
        time.sleep(2)
      
      response = operation.result()
      self.logger.info(f"{self.script_name}:{local_func_name} response:{response}")
      if response.service.state.name == "DISABLED":
        return response
      else: 
        print('Raising Error DISABLING')
        return_msg = f"{self.script_name}:{local_func_name} response:{response}"
        raise ValueError(return_msg, self.return_status_500)

    except Exception as error:
      raise

if __name__ == '__main__':
    util = MyUtilities('sandeep')
    #print(util.list_services(76786460898))