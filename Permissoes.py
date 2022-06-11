import json
import os
import subprocess
from Helper import Helper
class Permissoes():

    def createNecessaryFiles(self, secret, name, issuer_name):

        helper = Helper()

        secret_path = helper.getSecretFile()

        atr_path = helper.jsonPath()

        hash_path = helper.hashFilePath()

        dict_ = {}

        dict_['secret'] = secret
        dict_['name'] = name
        dict_['issuer_name'] = issuer_name

        j = json.dumps(dict_)

        print(dict_)

        with open(secret_path, 'w') as f:
            print("The txt file is created")
            f.write(j)
            p = subprocess.Popen("sudo chown root:root " + secret_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + secret_path, stdout=subprocess.PIPE, shell=True)
            f.close()
        
        with open(atr_path, 'w') as f:
            print("The txt file is created")
            p = subprocess.Popen("sudo chown root:root " + atr_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + atr_path, stdout=subprocess.PIPE, shell=True)
            f.close()

        with open(hash_path, 'w') as f:
            print("The json file is created")
            p = subprocess.Popen("sudo chown root:root " + hash_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + hash_path, stdout=subprocess.PIPE, shell=True)
            f.close()   
             


if __name__ == "__main__":

    secret = input("Insira o seu segredo: ")
    name = input("Insira o name: ")
    issuer_name = input("Insira o issuer_name: ")

    p = Permissoes()
    p.createNecessaryFiles(secret, name, issuer_name) 