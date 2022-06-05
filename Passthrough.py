#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import ntpath
import json
import pwd, grp
import hashlib
from Helper import Helper

from fuse import FUSE, FuseOSError, Operations, fuse_get_context

#atr_path = "/home/kali/Desktop/TS/atributos.json"

class Passthrough(Operations):
    def __init__(self, root):
        self.root = root
        self.atr_path = self.getJsonPath()
        self.getCriticalFileAttributes()
        #self.allFileUsersAccess()
    
    def getJsonPath(self):
        helper = Helper()

        self.atr_path = helper.jsonPath()

        return self.atr_path 

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    """def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    """
    #Get file attributes
    def getattr(self, path, fh=None):

        #full_path = self._full_path(path)
        st = os.stat(path)
        #os.access(full_path, os.W_OK)
        #print(st)
        attr = {}
        counter = 0
        dict_ = {}

        try:
            for key in ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime'):
                attr['file_name'] = ntpath.basename(path)
                attr[key] = st[counter]
                counter = counter + 1
                attr['rp'] = True if os.access(path, os.R_OK) == True else False
                attr['wp'] = True if os.access(path, os.W_OK) == True else False
                attr['xp'] = True if os.access(path, os.X_OK) == True else False
                #print(ntpath.basename(path))
                #print("cenas: ", self.hash_file(ntpath.basename(path)))
                #attr['hash'] = self.hash_file(ntpath.basename(path))
                #attr['rp'] = True
        except:
            print("E link")
        #print(attr)

        """file = self.open(full_path, os.O_RDONLY)
        attr['hash'] = hashlib.sha256(file).hexdigest() 
        print(attr['hash'])"""

        dict_[ntpath.basename(path)] = attr
        print(dict_)

        return dict_ 

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        uid, gid, pid = fuse_get_context()
        full_path = self._full_path(path)
        fd = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown(full_path,uid,gid) #chown to context uid & gid
        return fd

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

    def hash_file(self, filename):
        """"This function returns the SHA-1 hash
        of the file passed into it"""

        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode
        with open(filename,'rb') as file:

            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        # return the hex representation of digest
        return h.hexdigest()

    # Our methods
    # ============
    # def getAllUsers(self):
    #     dic = {}
    #     for p in pwd.getpwall():
    #         # print("p: ", p)
    #         # print("Userid: ", p[2])
    #         # print("Groupid: ",p[3])
    #         # print("groupinfo: ",grp.getgrgid(p[3]))
    #         # print("username: ",p[0])
    #         # print("groupname: ",grp.getgrgid(p[3])[0])
    #         dic[p[0]] = grp.getgrgid(p[3])[0]
    #     return dic


    def getCriticalFileAttributes(self):

        listCriticalFolders = ["/etc/", "/dev/hd"]
        shpfiles = []

        print("Sistema de ficheiros iniciado")
        
        for i in range(len(listCriticalFolders)):

            for dirpath, subdirs, files in os.walk(listCriticalFolders[i]):
                for x in files:
                    if not x.endswith("supervise") and not x.endswith(".service") and not x.endswith(".conf") :
                        shpfiles.append(os.path.join(dirpath, x))
                    
            #print("Atributos: ")
            #print(self.getattr(shpfiles[i]))
            #print("\n\n")

        count = 0

        for x in range(len(shpfiles)):

            #print("Atributos: ")
            #print("path", shpfiles[x])

            self.getattr(shpfiles[x])
            with open(str(self.atr_path)) as f:
                try:
                    loaded = json.load(f)
                except:
                    loaded = {}

            with open(str(self.atr_path), "w") as f:
                
                loaded[list(self.getattr(shpfiles[x]).keys())[0]] = self.getattr(shpfiles[x]).get(list(self.getattr(shpfiles[x]).keys())[0])
                json.dump(loaded, f, indent=6)
                
            count += 1

            #print("\n\n")
        #print(count)
                
        #Testar a possibilidade de adicionar na lista
        #uma pasta e não só um ficheiro

        #Converter para JSON
        #self.getAllUsers()
        
        return

    def allFileUsersAccess(self):
        dic = {}
        with open(self.atr_path) as f:
            dic2 = json.load(f)
        
        for key,value in dic2.items():
            for p in pwd.getpwall():
                if (value["st_gid"] == p[3]) or (value["st_uid"] == p[2]):
                    if key not in dic.keys():
                        dic[key] = [p[0]]
                    else:
                        dic[key].append(p[0])
        print(dic)


        return

def main(mountpoint, root):
    FUSE(Passthrough(root),
        mountpoint, 
        nothreads=True, 
        foreground=True,
        allow_other=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])