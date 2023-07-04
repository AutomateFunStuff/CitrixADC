import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import csv
import getpass
#Gathering User Creds and Host details 
Host = input("Enter the CitrixADCMGMTIP: ")
User = input("Enter the Username: ")
Password = getpass.getpass()
VIPIP = input("Enter the VIP IP: ")
if Password =="":
    print ("Password can't be empty , please provide the password")
    Password = getpass.getpass()
    #print(Password)
    if Password =="":
        print ("password is blank even second time , hence existing")
        exit ()
#Generating the Auth Token to reuse in the script
try:
  Auth_URL = "https://%s/nitro/v1/config/login" %(Host)
  Auth_data = { "login":  
               { "username":User, 
                "password":Password }
              }
  AuthRequest = requests.post(Auth_URL,data=json.dumps(Auth_data),headers={ 'Content-Type':'application/json'},verify=False)
  Auth_Response = AuthRequest.json()['sessionid']
  print(Auth_Response)
except KeyError:
      print ( "Creds provided are wrong , please re-run program with right creds" ) 
      exit ()
lbvs_URI = "https://%s/nitro/v1/config/lbvserver" %(Host)
Auth_Token = { 'Cookie':f'NITRO_AUTH_TOKEN={Auth_Response}','Content-Type':'application/json'}
lbvs_response = requests.get(lbvs_URI,headers=Auth_Token,verify=False)
lbvs_data = lbvs_response.json()
lbvs_dic = {}
for i in lbvs_data['lbvserver']:
    name = i['name']
    IP = i['ipv46']
    port = i['port']
    ipport = (str(IP)+":"+str(port))
    lbvs_dic[ipport] = name
print (lbvs_dic)
delimiter = ':'
Vserver_list = []
for key, value in lbvs_dic.items():
    parts = key.split(delimiter)
    if len(parts) == 2:
     new_key = parts[0]
     print (value)
     if new_key == VIPIP:
        Vserver_list.append(value)
print (Vserver_list)
for i1 in Vserver_list:
 lbvserver_URL = "https://%s/nitro/v1/config/lbvserver/%s" %(Host,i1)
 Auth_Token = { 'Cookie':f'NITRO_AUTH_TOKEN={Auth_Response}','Content-Type':'application/json'}
 lbVserver_Details = requests.get(lbvserver_URL,headers=Auth_Token,verify=False)
 lbVserver_data= lbVserver_Details.json()
 for i in lbVserver_data['lbvserver']:
    vsvrname = str (i['name'])
    vsvrbip = str (i ['ipv46'])
    vsvrport = str (i['port'])
    #print (name,vsvrbip,vsvrport + "\n")
    # try check block catches if vserver doesn't have servicegroup assiocated to vserver
    try:
        lbvserver_servicegroup_bindings= "https://%s/nitro/v1/config/lbvserver_servicegroup_binding/%s" %(Host,vsvrname)
        lbvserver_response_servicegroup_bindings = requests.get(lbvserver_servicegroup_bindings,headers=Auth_Token,verify=False)    
        svcgroup_bindings = lbvserver_response_servicegroup_bindings.json()
        for j in svcgroup_bindings['lbvserver_servicegroup_binding']:
          svcgroup_bindings_data = j['servicegroupname']
          #print (vsvrname,vsvrbip,vsvrport,svcgroup_bindings_data + "\n")
          svcgroup_svcgroupmember_binding_URI = "https://%s/nitro/v1/config/servicegroup_servicegroupmember_binding/%s" %(Host,svcgroup_bindings_data)
          svcgroup_svcgroupmember_binding_response = requests.get(svcgroup_svcgroupmember_binding_URI,headers=Auth_Token,verify=False)
          svcgroup_svcgroupmember_binding_output = svcgroup_svcgroupmember_binding_response.json()
          print (svcgroup_svcgroupmember_binding_output)
          # Try except block catches if servicegroup has zero members tagged to service group
          try:
            servicegroup_member = []
            for k in svcgroup_svcgroupmember_binding_output["servicegroup_servicegroupmember_binding"]:
                service_member_ip = k['ip']
                service_member_port = k['port']
                servicegroup_member.append(str(service_member_ip) + ":" + str(service_member_port))
            #print (vsvrname,vsvrbip,vsvrport,str(servicegroup_member)+ "\n")
          except KeyError:
              servicegroup_member.append("Empty Servicegroup without members")
              #print (vsvrname,vsvrbip,vsvrport,str(servicegroup_member)+ "\n")
          servicegroup_monitor_bindings_URL = "https://%s/nitro/v1/config/servicegroup_lbmonitor_binding/%s" %(Host,svcgroup_bindings_data)
          servicegroup_monitor_bindings_URL_response = requests.get(servicegroup_monitor_bindings_URL,headers=Auth_Token,verify=False)
          servicegroup_monitor_bindings_URL_output = servicegroup_monitor_bindings_URL_response.json()
          #Try check block checks if servicegroup has monitor tagged to the group
          try:
              for k1 in servicegroup_monitor_bindings_URL_output['servicegroup_lbmonitor_binding']:
                  monitor_name = str(k1['monitor_name'])
                  print (vsvrname,vsvrbip,vsvrport,str(servicegroup_member),monitor_name+ "\n")
          except KeyError:
               monitor_name = "No monitor bounded to the vserver"
               print (vsvrname,vsvrbip,vsvrport,str(servicegroup_member),monitor_name+ "\n")
    except KeyError:
           svcgroup_bindings_data = "none"
           print (vsvrname,vsvrbip,vsvrport,"N/A","N/A","N/A"+ "\n")

   




