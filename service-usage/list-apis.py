#export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json

from google.cloud import service_usage_v1
import time

# Config [RETURN_STATUS] section
return_status_200 = self.config['RETURN_STATUS']['RETURN_STATUS_200']
return_status_500 = self.config['RETURN_STATUS']['RETURN_STATUS_500']
return_status_success = self.config['RETURN_STATUS']['RETURN_STATUS_SUCCESS']
return_status_fail = self.config['RETURN_STATUS']['RETURN_STATUS_FAIL']


def list_services(project_number: int) -> list[str]:

    try:
        # Create a client
        client = service_usage_v1.ServiceUsageClient()

        # Initialize request argument(s)
        request = service_usage_v1.ListServicesRequest(
        )

        request.parent = 'projects/{}'.format(str(project_number))
        request.filter = 'state:ENABLED'

        # Make the request
        page_result = client.list_services(request=request)

        # Handle the response
        return_val = [response.name for response in page_result]

        return return_val
    except 


def enable_service(project_number: int, service_name: str) -> str:
    # Create a client
    client = service_usage_v1.ServiceUsageClient()

    # Initialize request argument(s)
    request = service_usage_v1.EnableServiceRequest(
    )

    request.name = 'projects/{}/services/{}'.format(str(project_number), service_name)

    # Make the request
    operation = client.enable_service(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    return response

def disable_service(project_number: int, service_name: str) -> str:
    # Create a client
    client = service_usage_v1.ServiceUsageClient()

    # Initialize request argument(s)
    request = service_usage_v1.DisableServiceRequest(
    )

    request.name = 'projects/{}/services/{}'.format(str(project_number), service_name)

    print(request)
    request.check_if_service_has_usage = 'SKIP'

    # Make the request
    operation = client.disable_service(request=request)

    print("Waiting for operation to complete...")
    
    while not operation.done():
        time.sleep(2)

    response = operation.result()
    return response

if __name__ == '__main__':
    #print(list_services(76786460898))
    #print(enable_service(76786460898, 'datalineage.googleapis.com'))
    print(disable_service(76786460898, 'datalineage.googleapis.com'))
    #projects/76786460898/services/datalineage.googleapis.com
    
    