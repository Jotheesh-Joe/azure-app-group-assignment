import os
import requests
import sys


app_id = os.environ["APP_ID"]  # (Application ID)
client_secret = os.environ["CLIENT_SECRET"]  # (Client Secret)
tenant_id = os.environ["TENANT_ID"]  # (Tenant ID)
ecp_group_name = os.environ["ECP_GROUP_NAME"]
app_group_name = os.environ["APP_GROUP_NAME"]


def get_ms_graph_token(app_id, client_secret, token_url):
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': app_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
    }
    h = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_r = requests.post(token_url, data=token_data, headers=h)
    if token_r.status_code > 299:
        print("ERROR: Token Request to Azure AD Failed, check the error response from Azure AD: {} ".format(
            token_r.json()))
        sys.exit()
    else:
        print("INFO:: Get Token from AzureAD completed successfully")
    return token_r


def get_ad_group_id(ad_group_name, token):
    get_groups_url="https://graph.microsoft.com/v1.0/groups"
    parameters = {'$filter': 'displayName eq \'{}\''.format(ad_group_name)}
    head = {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json' }
    ad_group_id_r = requests.get(get_groups_url, headers=head, params=parameters)
    if ad_group_id_r.status_code > 299:
        print("ERROR: Group does not exists in Azure AD, check the error response from Azure AD: {} ".format(ad_group_id_r.json()))
        sys.exit()
    else:
        print("INFO:: Get GroupID from AzureAD completed successfully, check the  response from Azure AD: {} ".format(ad_group_id_r.json()))
    ad_group_id = ad_group_id_r.json().get('value')
    return ad_group_id[0]['id']


def add_group_role_assignment(add_group_role_url, app_group_id, token):
    add_group_role_data = {
        "@odata.id": "https://graph.microsoft.com/v1.0/groups/{}".format(app_group_id)
    }
    head = {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
    add_group_role_assignment_res = requests.post(add_group_role_url, json=add_group_role_data, headers=head)

    if add_group_role_assignment_res.status_code > 299:
        print("ERROR: Group Assignment already exists , or something went wrong, please check the logs: {} ".format(add_group_role_assignment_res.json()))
        sys.exit()
    else:
        print(add_group_role_assignment_res)
        print("INFO:: Group Assignment completed successfully")


    return add_group_role_assignment_res


try:
    token_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(tenant_id)
    print("###########################################################################################################################")
    token_r = get_ms_graph_token(app_id, client_secret, token_url)
    token = token_r.json().get('access_token')
    print("###########################################################################################################################")
    ecp_group_id = get_ad_group_id(ecp_group_name, token)
    print("###########################################################################################################################")
    app_group_id = get_ad_group_id(app_group_name, token)
    print("###########################################################################################################################")
    add_group_role_url = "https://graph.microsoft.com/v1.0/groups/{}/members/$ref".format(ecp_group_id)
    app_group_role_assignment_r = add_group_role_assignment(add_group_role_url, app_group_id, token)
except Exception as e:
    print(str(e))