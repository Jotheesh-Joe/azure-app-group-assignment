import os
import requests
import sys
import json
import logging

#os.environ["AZURE_CLIENT_ID"]}
app_id = os.environ["APP_ID"]  # (Application ID)
client_secret = os.environ["CLIENT_SECRET"]  # (Client Secret)
tenant_id = os.environ["TENANT_ID"]  # (Tenant ID)
app_sp_id = os.environ["APP_SP_ID"]  # (Enterprise App Object ID)
ad_group_name = os.environ["AD_GROUP_NAME"]  # (AD group to be assigned for enterprise app)


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


def put_app_group_role_assignment(add_approle_url, app_sp_id, ad_group_id, token):
    add_approle_data = {
      "principalId": ad_group_id,
      "resourceId": app_sp_id,
      }
    head = {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
    add_app_role_assignment = requests.post(add_approle_url, json=add_approle_data, headers=head)
    if add_app_role_assignment.status_code > 299:
        print("ERROR: Role Assignment already exists , or something went wrong, please check the logs: {} ".format(add_app_role_assignment.json()))
        sys.exit()
    else:
        print("INFO:: Role Assignment completed successfully, check the  response from Azure AD: {} ".format(add_app_role_assignment.json()))

    return add_app_role_assignment

try:
    token_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(tenant_id)
    print("###########################################################################################################################")
    token_r = get_ms_graph_token(app_id, client_secret, token_url)
    print(token_r)
    token = token_r.json().get('access_token')
    print(token)
    print("###########################################################################################################################")
    ad_group_id = get_ad_group_id(ad_group_name, token)
    print(ad_group_id)
    print("###########################################################################################################################")
    add_approle_url = "https://graph.microsoft.com/v1.0/servicePrincipals/{}/appRoleAssignments".format(app_sp_id)
    app_group_role_assignment_r = put_app_group_role_assignment(add_approle_url, app_sp_id, ad_group_id, token)
    print("###########################################################################################################################")

except Exception as e:
    print(str(e))