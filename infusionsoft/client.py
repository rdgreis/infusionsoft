from xmlrpclib import ServerProxy, Fault
import requests
from datetime import datetime

class Infusionsoft(object):
    def __init__(self, name, api_key):
        if not name or not api_key:
            raise ValueError("You need to pass an api key and name")
        self.name = name
        self.client = ServerProxy("https://{0}.infusionsoft.com/api/xmlrpc".format(name))
        self.key = api_key

    def find_by_email(self, email):
        results = self.client.ContactService.findByEmail(self.key, email, ['Id'])
        if len(results):
            return results[0]

    def find_by_first_and_last_name(self, first_name, last_name):
        search_string = "{0} {1}".format(first_name, last_name)
        results = self.client.SearchService.quickSearch(self.key, 'FindPerson', 14, search_string, 0, 1)
        if len(results):
            return results[0]

    def get_by_id(self, id):
        FIELDS_TO_PULL = [
            "FirstName",
            "LastName",
            "Email",
            "Company",
            "City",
            "State",
            "Phone1",
            "Website",
        ]
        try:
            return self.client.ContactService.load(
                self.key,
                id,
                FIELDS_TO_PULL,
            )
        except Fault as e:
            return

    def add(self, data):
        contact_id = self.client.ContactService.add(self.key, data)
        self.client.APIEmailService.optIn(self.key, data['Email'], "You signed up on our website")
        return contact_id

    def update(self,contact_id,data):
        customer_data = self.client.ContactService.load(self.key,contact_id, data.keys())
        diff = {}
        diff_data = {}

        #Checking if update is needed
        for key in data.keys():
            if customer_data.get(key,'').lower() != data.get(key,'').lower():
                diff[key] = data.get(key,'')
                diff_data[key] = data.get(key,'')
                diff_data[key+'_old'] = customer_data.get(key,'')

        if diff.keys():
            contact_id = self.client.ContactService.update(self.key,contact_id, diff)

        return diff_data

    def load(self,contact_id,fields=['FirstName','LastName','Email']):
        return self.client.ContactService.load(self.key, contact_id,fields)

    def remove(self, contact_id):
        self.client.DataService.delete(self.key, 'Contact', contact_id)

    def get_list_of_owners(self):
        return self.client.DataService.query(self.key, 'User', 1000, 0, {'FirstName': '%'}, ['Id','FirstName','LastName'])

    def submit_web_form(self, form_id, form_name, data, infusionsoft_version='1.29.8.45'):
        data['inf_form_name'] = form_name
        data['inf_form_xid'] = form_id
        data['infusionsoft_version'] = infusionsoft_version
        data['submit'] = 'Submit'
        url = "https://{0}.infusionsoft.com/app/form/process/{1}".format(self.name, form_id)
        r = requests.post(url, data=data)
        return r.status_code == 200

    def apply_tag(self, contact_id, tag_id):
        self.client.ContactService.addToGroup(self.key, contact_id, tag_id)

    def add_note(self, contact_id, note_title, note_body):
        values = {
          'ContactId': contact_id,
          'ActionDescription': note_title,
          'CreationNotes': note_body,
        }
        self.client.DataService.add(self.key, 'ContactAction', values)

    def set_owner(self, contact_id, owner_id):
        self.client.ContactService.update(self.key, contact_id, {'OwnerID': owner_id})

    def get_owner(self, contact_id):
        record = self.client.ContactService.load(self.key, contact_id, ['OwnerID'])
        return record.get('OwnerID')

    def place_order(self, contact_id, product_ids):
        return self.client.OrderService.placeOrder(self.key,      #str
            contact_id,    #int
            0,             #int
            0,             #int
            product_ids,   #list
            [],            #list
            False,         #bool
            []             #list
        )

    def get_opportunities(self, contact_id, fields=('Id','OpportunityTitle','StageID','UserID')):
        return self.client.DataService.query(self.key, 'Lead', 1000, 0, {'ContactId': contact_id}, fields)

    def create_opportunity(self, contact_id, title, stage):
        values = {
            'OpportunityTitle': title,
            'ContactID': contact_id,
        }
        self.client.DataService.add( self.key, 'Lead', values)

    def move_opportunity_stage(self, contact_id, stage):
        opportunities = self.get_opportunities(contact_id)
        for opp in opportunities:
            self.client.DataService.update(self.key, 'Lead', opp['Id'], {'StageID': stage})

    def data_update(self,table,id,data):
        return self.client.DataService.update(self.key,table,id, data)

    def data_load(self,table,id,fields):
        return self.client.DataService.load(self.key,table,id, fields)

    def data_findByField(self,table,fieldName,fieldValue,fields,limit=100,page=0):
        return self.client.DataService.findByField(self.key,table,limit,page,fieldName,fieldValue,fields)

    def data_query(self,table,query_dict,fields,limit=100,page=0):
        return self.client.DataService.query(self.key,table,limit,page,query_dict,fields)

    def createBlankOrder(self,contactId,description='',orderDate=datetime.now(),leadAffiliateId=0,saleAffiliateId=0):
        return self.client.InvoiceService.createBlankOrder(self.key,table,limit,page,fieldName,fieldValue,fields)
