import json
import asyncio
from google.oauth2 import service_account
from google.cloud.billing import budgets_v1

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


async def main_async(credentials, budget_id_list):
    try:
        budget_client = budgets_v1.BudgetServiceAsyncClient(credentials=credentials)

        for budget_id in budget_id_list:

            request = budgets_v1.DeleteBudgetRequest(
                name = budget_id
            )

            await budget_client.delete_budget(request = request)

            print("Budget - ", budget_id, " deleted successfully.")

    except Exception as e:
        print("Error in main_async() function: ", e)



if __name__ == "__main__":
    try:
        with open('budget_id_list.json', 'r') as budget_ids:
            budget_id_list = json.load(budget_ids)
    except FileNotFoundError:
            print("File budget_id_list.json not found!")
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

    asyncio.run(main_async(credentials, budget_id_list))
    
