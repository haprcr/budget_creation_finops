# python3 -m venv <your-env>
# source <your-env>/bin/activate
# chmod +x script.sh
# ./script.sh
# python3 budget_create.py


import ast
import json
import asyncio
import pandas as pd
from google.cloud import monitoring_v3
from google.oauth2 import service_account
from google.cloud.billing import budgets_v1
import google.api_core.exceptions as gcp_exceptions



import ast
import json
import asyncio
import pandas as pd
from google.cloud import monitoring_v3
from google.oauth2 import service_account
from google.cloud.billing import budgets_v1
import google.api_core.exceptions as gcp_exceptions

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


def create_notification_channel(project_id, email_id, credentials):
        try:
            print("Creating the Monitoring Notification Channel Client")
            channel_client = monitoring_v3.NotificationChannelServiceClient(credentials=credentials)

            display_name = "Budget Notification Channel to " + email_id
            print("Initialising the Notification Channel with the required arguments")
            notification_channel = monitoring_v3.NotificationChannel(
                type="email",
                display_name=display_name,
                enabled=True
            )
            notification_channel.labels['email_address'] = email_id

            # NotificationChannelDescriptor.labels
            
            print("Creating the Notification Channel Request object")
            channel_request = monitoring_v3.CreateNotificationChannelRequest(
                name=project_id,
                notification_channel=notification_channel
            )

            print("Creating the request to  create a Notification Channel")
            channel_response = channel_client.create_notification_channel(
                request=channel_request
            )

            print("Response received from the client")
            print(f"Notification channel {channel_response.name} created.")

            return channel_response.name

        except gcp_exceptions.InvalidArgument as err:
            print("InvalidArgument Error in create_channel(): ", err)
        except Exception as err:
            err_msg = f"Error while creating the Notification Channel in create_channel(): {err}"
            print(err_msg)


def create_notification_channels(project_id, email_list, credentials):
        channel_ids = [create_notification_channel(project_id, email_id, credentials) for email_id in email_list]
        return channel_ids


async def main_async(credentials):
    try:
        try:
            # print("Retrieving the contents from the file budget_list.xlsx")
            # data = pd.read_excel('budget_list.xlsx')
            # # process to  list
            # data['threshold_percent'] = data['threshold_percent'].apply(lambda x: ast.literal_eval(x))
            # data['email_list'] = data['email_list'].apply(lambda x: ast.literal_eval(x))
            # data_json = data.to_json(orient='records')
            # config = json.loads(data_json)

            with open("config_rest.json" , "r") as config_list:
                    config = json.load(config_list)
            budget_client = budgets_v1.BudgetServiceAsyncClient(credentials=credentials)
        except FileNotFoundError:
            print("File budget_list.xlsx is not present. Please create this file with budget configurations.")
            exit(1)



        for budget_config in config:
                try:
                    billing_account_id = "billingAccounts/"+ budget_config["billing_account_id"]

                    project_ID = "projects/" + budget_config["project_ID"]
                    channel_id_list = create_notification_channels(project_ID, budget_config['email_list'], credentials)

                    channel_id_list_main.append(channel_id_list)
                    budget_object = budgets_v1.Budget(
                        display_name = budget_config['display_name'],
                        amount = budgets_v1.BudgetAmount(last_period_amount = budgets_v1.LastPeriodAmount()),
                        notifications_rule = budgets_v1.NotificationsRule
                        (
                            disable_default_iam_recipients=True,
                            monitoring_notification_channels=channel_id_list
                        ),
                        budget_filter = budgets_v1.Filter
                        (
                            calendar_period=budget_config['calendar_period'],
                            projects=["projects/" + budget_config["project_ID"]],
                            credit_types_treatment=budgets_v1.Filter.CreditTypesTreatment.INCLUDE_SPECIFIED_CREDITS,
                            credit_types=[
                                "SUSTAINED_USAGE_DISCOUNT",
                                "DISCOUNT",
                                "COMMITTED_USAGE_DISCOUNT",
                                "FREE_TIER",
                                "COMMITTED_USAGE_DISCOUNT_DOLLAR_BASE",
                                "SUBSCRIPTION_BENEFIT"
                            ]
                        )
                    )

                    


                    threshold_percent = budget_config["threshold_percent"]
                    spend_basis = budget_config["spend_basis"]
    
    
                    for ele in threshold_percent:
                        budget_object.threshold_rules.append(
                            budgets_v1.ThresholdRule(threshold_percent = ele, spend_basis = spend_basis)
                    )

                    request = budgets_v1.CreateBudgetRequest(
                            parent = billing_account_id,
                            budget = budget_object
                    )

                    
                    response = await budget_client.create_budget(request=request)
                    # print(type(response))
                    budget_id_list.append(response.name)
                    
                    print("Budget Successfully created for Project ID: ", budget_config["project_ID"])
                except gcp_exceptions.InvalidArgument  as ia:
                    print(ia)
                except Exception as e:
                    print("Error while creating budget for Project ID:", budget_config["project_ID"],". Error information: ", e)
                    print(e.with_traceback)
    except Exception as e:
        print("Error in function main_async(): ", e)


if __name__ == "__main__":
    global budget_id_list, channel_id_list_main

    try:
        with open('budget_id_list.json', 'r') as budget_ids:
            budget_id_list = json.load(budget_ids)
    except FileNotFoundError:
        budget_id_list = []
    
    try:
        with open('notification_channel_list.json', 'r') as channel_ids:
            channel_id_list_main = json.load(channel_ids)
    except FileNotFoundError:
        channel_id_list_main = []

    oauth_scope = 'https://www.googleapis.com/auth/cloud-platform'

    #  *****************************************************************
    #  *** INSERT THE SERVICE ACCOUNT ID HAVING THE REQUIRED ROLES ***
    #  *****************************************************************
    service_account = 'budget-create@ci-alloy-db-1-7f45.iam.gserviceaccount.com'
    # Credentials 
    credentials = get_access_token(service_account, oauth_scope)

    asyncio.run(main_async(credentials))

    with open('budget_id_list.json', 'w') as budget_id_map:
        json.dump(budget_id_list, budget_id_map, indent=4)
    
    with open('notification_channel_list.json', 'w') as channel_id_map:
        json.dump(channel_id_list_main, channel_id_map, indent=4)
