import json

class Helper():

    def getSecretFile(self):

        secret_path = "/home/kali/Desktop/TS/TS/secret.json"

        return secret_path

    def jsonPath(self):
        atr_path = "/home/kali/Desktop/TS/TS/atributos.json"

        return atr_path

    def hashFilePath(self):

        hash_path = "/home/kali/Desktop/TS/TS/catfile.txt"

        return hash_path

    def getFileIds(self, dict_, path):
        gid = -111
        uid = -111
        file_name = ""

        for j, i in dict_.items():
            for x, z in i.items():
                #print(z['file_name'])
                if path == z['file_name']:
                    #print("entrou")
                    uid = z['st_uid']
                    gid = z['st_gid']
                    file_name = z['file_name']
                    return gid, uid, file_name
        
        return gid, uid, file_name
        
if __name__ == "__main__":
    h = Helper()
    x = h.jsonPath()

    dict_ = {}

    with open(x ,'r') as f:
        dict_ = json.load(f)

    gid, uid, file_name = h.getFileIds(dict_, "/passwd")
    print(gid)
    print(uid)
    print(file_name)
    