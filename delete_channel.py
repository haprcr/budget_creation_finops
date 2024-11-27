import ast
import json
import asyncio
import pandas as pd
from google.cloud import monitoring_v3



def get_access_token(service_account: str, scope: str):
    try:
        from google.auth import impersonated_credentials
        import google.auth.transport.requests

        credentials, project_id = google.auth.default()

        target_credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=service_account,
            delegates=[],
            target_scopes=[scope],
            lifetime=3600,
        )

        return target_credentials.token
    except Exception as e:
        err_msg = f"Exception {e}, in get_access_token(), while getting the Access Token for the Service Account {service_account}."
        print(err_msg)
        raise Exception(err_msg)

async def delete_channel(channel_id_list, credentials):
        try:
            print("Initializing the Monitoring Notification Channel Client")
            channel_client = monitoring_v3.NotificationChannelServiceAsyncClient(credentials=credentials)


            for channel_id_1 in channel_id_list:
                for channel_id in channel_id_1:
                    request = monitoring_v3.DeleteNotificationChannelRequest(
                        name = channel_id
                    )

                    await channel_client.delete_notification_channel(
                        request=request
                    )

                    print("Notification channel - ", channel_id, " deleted successfully.")

        except gcp_exceptions.InvalidArgument as err:
            print("InvalidArgument Error in delete_channel(): ", err)
        except Exception as err:
            err_msg = f"Error while deleting the Notification Channel: {channel_id} in delete_channel(): {err}"
            print(err_msg)


if __name__ == "__main__":

    try:
        with open("notification_channel_list.json", "r") as notification_channel_list:
            notification_channel_list = json.load(notification_channel_list)
    except FileNotFoundError:
            print("File notification_channel_list.json not found!")
            exit(1)
    except Exception as e:
        print("Error: ", e)
        exit(1)
    

    oauth_scope = 'https://www.googleapis.com/auth/cloud-platform'

    #  *****************************************************************
    #  *** INSERT THE SERVICE ACCOUNT ID HAVING THE REQUIRED ROLES ***
    #  *****************************************************************
    service_account = 'budget-create@ci-alloy-db-1-7f45.iam.gserviceaccount.com'


    # Credentials 
    credentials = get_access_token(service_account, oauth_scope)

    asyncio.run(delete_channel(notification_channel_list, credentials))

