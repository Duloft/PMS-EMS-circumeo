import requests
import json

true = True
false = False

class PayStack:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.base_url = 'https://api.paystack.co'
    
    def _headers(self):
        return {
           "Authorization":f"Bearer {self.secret_key}",
            'Content-Type':'application/json',
        }
    
    
    def _path_handle(self, method, url, data=None):

        """
        Generic function to handle all API url calls
        Returns a python tuple of status code, status(bool), message, data
        """
        method_map = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete
        }

        payload = json.dumps(data) if data else data
        request = method_map.get(method)

        response = request(url, headers=self._headers(), data=payload, verify=True)
        
        if response.status_code == 404:
            return response.status_code, False, "The object request cannot be found", None

        if response.status_code in [200, 201]:
            response_data = response.json()
            return response_data['status'], response_data['data']
        else:
            response_data = response.json()
            return response_data

    
    def verify_payment(self, reference, *args, **kwargs):
        path = f"/transaction/verify/{reference}"
        
        url = self.base_url + path
        response = self._path_handle("GET", url)
        return response
        
    
    def get_bank_code(self, bank_name, country="Nigeria", *args, **kwargs):
        path = f"/bank?country={country.lower()}"
        url = self.base_url + path
        status, response = self._path_handle("GET", url)
        
        if status:
            for item in response:
                name = item["name"]
                if name  == bank_name:
                    print(name, item['code'], 'get bank code')
                    return item["code"]
        else:
            return None
    
    def bulktransferrecipient(self, data: list, *args, **kwargs):
        path = "/transferrecipient/bulk"
        url = self.base_url + path  
        payload = {
            "batch":data
        }
        response = self._path_handle("POST", url, payload)
        print('done with bulk transfer recipients creation')
        return  response
        
    
    def createRecipient(self, response_data: dict, account_name, account_number, 
                        bank_name,  description, *arg, **kwargs):
        """
        Creating Single Recipient
        curl https://api.paystack.co/transferrecipient
        -d '{ "type": "nuban", 
            "name": "John Doe", 
            "account_number": "0001234567", 
            "bank_code": "058", 
            "currency": "NGN",
            "description":"A description for this recipient"
            }'
        -X POST
        """
        
        recipient_path = "/transferrecipient"
        print("Creating Single Recipient...")
        # print(response_data['account_name'].lower())
        # print(account_name.lower())
        if account_name.lower() in response_data['account_name'].lower():
            url = self.base_url + recipient_path
            data = {
                "type": "nuban", 
                "name": account_name, 
                "account_number": account_number, 
                "bank_code": self.get_bank_code(bank_name), 
                "currency": "NGN",
                "description": description,
            }
            status, res = self._path_handle('POST', url, data)
            
            # print(res, 'res from create recipient')
            return status, res
        else:
            return False, "Name Error"


    def verify_account_number(self, account_number,  bank_name, *args, **kwargs):
        
        """
            curl https://api.paystack.co/bank/resolve?account_number=0001234567&bank_code=058
            -H "Authorization: Bearer YOUR_SECRET_KEY"
            -X GET
        """
        
        resolve_path = f"/bank/resolve?account_number={account_number}&bank_code={self.get_bank_code(bank_name)}"
        url = self.base_url + resolve_path
        
        return self._path_handle('GET', url)
        
    
    def bankTransfer(self, transferdetails: dict, *args, **kwargs):
        """
        Single Transfer
        Initate bank transactions mainly transfer
        curl https://api.paystack.co/transfer
        -H "Authorization: Bearer YOUR_SECRET_KEY"
        -H "Content-Type: application/json"
        -d '{ "source": "balance", "reason": "Calm down", 
            "amount":3794800, "recipient": "RCP_gx2wn530m0i3w3m"
            }'
        -X POST
        """
        
        account_number = transferdetails.get('account_number')
        bank_name = transferdetails.get('bank_name')
        account_name = transferdetails.get('account_name')
        amount = transferdetails.get('amount')
        description = transferdetails.get('description')
        reference = transferdetails.get('reference')
        
        transfer_path = "/transfer"
        finalize_transfer_path = "/transfer/finalize_transfer"
        
        # checking if the account is valid
        status, resolve_response = self.verify_account_number(account_number, bank_name)
        print('Verifying account')
        # print(status)
        # print(resolve_response)
        # print(account_name)
        
        # If account is valid, create a transfer recipient
        if status:
            reci_status, recipient_response = self.createRecipient(
                resolve_response, account_name, account_number, bank_name, description)
            
            # if recipient is created initiate transfer and load transfer details
            if reci_status:
                print('transfer recipient created...')
                # recipient_code = recipient_response["data"]["recipient_code"]
                recipient_code = recipient_response["recipient_code"]
                payload = {
                    "source":"balance",
                    "reason":description,
                    "amount":amount,
                    "recipient":recipient_code,
                    "reference":reference,
                }
                print('sending payload...')
                url = self.base_url + transfer_path
                trans_status, response = self._path_handle('POST', url, payload)
                
                if trans_status:
                    data_status = response["status"]
                    print('data status', data_status)
                    if data_status != "otp":
                        data = {
                            "status":response["status"],
                            "reference":response["reference"],
                            "transfer_code":response["transfer_code"],
                            "amount":response["amount"],
                        }
                        return  data
                    
                    else:
                        error = {
                            "message":"OTP Required",
                        }
                        return error
                    
                else:
                    error = {
                        "message":"Transfer Failed"
                    }
                    return error
                
            else:
                error = {
                    "message":"Recipient Would Not Be Created"
                }   
                return error  
            
        else:
            error = {
                "message":"Account Invaild",
            }
            return error    
        
    
    def bulkbankTransfer(self, transferdetails: list, *args, **kwargs):
        """
            curl https://api.paystack.co/transfer/bulk
            -d '{ "currency": "NGN",
                "source": "balance",
                "transfers": [{
                    "amount": 50000,
                    "recipient": "RCP_db342dvqvz9qcrn", 
                    "reference": "ref_943899312"
                },
                {
                    "amount": 50000,
                    "recipient": "RCP_db342dvqvz9qcrn",
                    "reference": "ref_943889313"
                }]
                }'
            -X POST
        """

        path = "/transfer/bulk"
        url  = self.base_url + path
        

        
        payload = {
            "currency": "NGN",
            "source": "balance",
            "transfers": transferdetails,
        }
        print("done with bulk payload Transfer creation")
        return self._path_handle("POST", url, payload)
        
    
    
    def verifytransfer(self, reference, amount):
        """
            curl https://api.paystack.co/transfer/verify/:reference
            -H "Authorization: Bearer YOUR_SECRET_KEY"
            -X GET
        """

        path = f"/transfer/verify/:{reference}"
        url = self.base_url + path
        
        status, response = self._path_handle('GET', url)
        
        if status:
            trans_amount = response["amount"] / 100
            if trans_amount == amount:
                return response["status"]
            else:
                return "Incorrect amount"
    
    def transfer_fetcher(self, transfer_id):
        '''curl https://api.paystack.co/transfer/:id_or_code
        -H "Authorization: Bearer YOUR_SECRET_KEY"
        -X GET'''
        
        
        path = f"transfer/:{transfer_id}"
        url = self.base_url + path
        
        status, response = self._path_handle('GET', url)