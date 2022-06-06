class Helper():

    def jsonPath(self):
        atr_path = "/home/kali/Desktop/TS/TS/atributos.json"

        return atr_path

    def hashFilePath(self):

        hash_path = "/home/kali/Desktop/TS/TS/catfile.txt"

        return hash_path

    def getFileIds(self, dict, path):

        gid = 0
        uid = 0
        for j, i in dict.items():
            for x, z in i.items():
                #print(z)
                uid = z['st_uid']
                gid = z['st_gid']

        return gid, uid

            