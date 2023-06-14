"""
Copyright 2022 Google. This software is provided as-is, without 
warranty or representation for any use or purpose. Your use of 
it is subject to your agreement with Google. 
"""
import sqlalchemy
import configparser
import base64
import datetime
from google.cloud import logging as cloudlogging
import logging
import json
import os
from google.auth.transport import requests
import google
#from google.cloud.pubsub import SchemaServiceClient


class util:
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

    self.config = configparser.ConfigParser()
    self.config.read('config.ini')

    # Config [DEFAULT] section
    # self.source_folder = self.config['DEFAULT']['SOURCE_FOLDER'] # TODO: NOT USING IN LOAD-FILE
    self.project_id = self.config['DEFAULT']['PROJECT_ID']
    self.upload_max_tries = self.config['DEFAULT']['UPLOAD_MAX_TRIES']

    # Config [LOAD_STATUS] section
    self.status_wait = self.config['LOAD_STATUS']['STATUS_WAIT']
    self.status_ready = self.config['LOAD_STATUS']['STATUS_READY']
    self.status_queued = self.config['LOAD_STATUS']['STATUS_QUEUED']
    self.status_processing = self.config['LOAD_STATUS']['STATUS_PROCESSING']
    self.status_comlpeted = self.config['LOAD_STATUS']['STATUS_COMPLETED']
    self.status_error = self.config['LOAD_STATUS']['STATUS_ERROR']
    
    # Config [RETURN_STATUS] section
    self.return_status_200 = self.config['RETURN_STATUS']['RETURN_STATUS_200']
    self.return_status_500 = self.config['RETURN_STATUS']['RETURN_STATUS_500']
    self.return_status_success = self.config['RETURN_STATUS']['RETURN_STATUS_SUCCESS']
    self.return_status_fail = self.config['RETURN_STATUS']['RETURN_STATUS_FAIL']
    
    # Config [LOGGING] section
    self.current_log_level = self.config['LOGGING']['CURRENT_LOG_LEVEL']
    self.log_level_info = self.config['LOGGING']['LOG_LEVEL_INFO']
    self.log_level_debug = self.config['LOGGING']['LOG_LEVEL_DEBUG']
    self.log_level_error = self.config['LOGGING']['LOG_LEVEL_ERROR']

    # Get Clients
    self.logger = self.get_logger(self.function_name + '-custom')
    self.db_pool = self.get_db_pool()


  def time_diff_ms(self, start_time):
    secs = (datetime.datetime.now() - start_time)
    ts = secs.total_seconds()
    return round(secs.total_seconds(), 3)


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


  # Defining in utils so that we should avoid reading file again again, 
  # its like DB Pool, don't repeat unless really required
  def get_payload_template(self):

    local_func_name = 'get_payload_template'
    try:
      pass
    except Exception as error:
      self.logger.info("{}:{} Error reading the payload template".format(self.script_name, local_func_name, str(error)))
      return (None, self.return_status_fail)