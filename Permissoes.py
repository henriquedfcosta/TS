import json
import os
import subprocess

class Permissoes():

    def createNecessaryFiles(self, ):

        secret_path = "/home/kali/Desktop/TS/TS/secret.txt"

        atr_path = "/home/kali/Desktop/TS/TS/atributos.json"

        hash_path = "/home/kali/Desktop/TS/TS/catfile.txt"

        with open(secret_path, 'r') as f:
            print("The txt file is created")
            #f.write(secret)
            p = subprocess.Popen("sudo chown root:root " + secret_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + secret_path, stdout=subprocess.PIPE, shell=True)
            f.close()
        
        with open(atr_path, 'r') as f:
            print("The txt file is created")
            p = subprocess.Popen("sudo chown root:root " + atr_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + atr_path, stdout=subprocess.PIPE, shell=True)
            f.close()

        with open(hash_path, 'r') as f:
            print("The json file is created")
            p = subprocess.Popen("sudo chown root:root " + hash_path, stdout=subprocess.PIPE, shell=True)
            p = subprocess.Popen("sudo chmod 700 " + hash_path, stdout=subprocess.PIPE, shell=True)
            f.close()   
             


if __name__ == "__main__":

    secret = input("Insira o seu segredo (min 16 caracters): ")

    p = Permissoes()
    p.createNecessaryFiles()