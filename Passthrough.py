from __future__ import with_statement
from genericpath import isdir, isfile

import os
from posixpath import split
import sys
import errno
import ntpath
import json
from traceback import print_tb
from turtle import xcor

from sqlalchemy import true
from Helper import Helper
import subprocess
import qrcode
import pyotp
import pwd
import time
from IPython.display import display, Image
import stat

from fuse import FUSE, FuseOSError, Operations, fuse_get_context


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root
        self.FLAG_HASH = True
        self.FLAG_AUTH = False
        self.atr_path, self.hash_path = self.getPaths()
        self.listCriticalFiles = ['/etc/ipsec.conf', '/etc/passwd', '/etc/login.defs','/etc/rearj.cfg']
        #self.authenticate('dancrossss')
        self.getCriticalFileAttributes()

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

    #Get file attributes
    def getattr(self, path, fh=None):

        full_path = self._full_path(path)
        st = os.stat(path)
        attr = {}
        counter = 0

        #Testar se o path que mandei é readability
        read = os.access(full_path, os.R_OK)
        #Testar se o path que mandei é writable
        write = os.access(full_path, os.W_OK)
        #Testar se o path que mandei é executável
        execute = os.access(full_path, os.X_OK)

        for key in ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime'):
                
            attr['file_name'] = ntpath.basename(full_path)
            attr['read'] = read
            attr['write'] = write
            attr['execute'] = execute

            if self.FLAG_HASH:
                #print("dentro do attr no if", self.FLAG_HASH)
                try:
                    with open(self.hash_path, "w") as fs:
                        child3 = subprocess.Popen(["sha1sum", full_path], stdout = fs, stderr=subprocess.DEVNULL)
                        with open(self.hash_path, "r") as f:
                            for line in f:
                                line = line.split(" ")
                                attr['hash'] = line[0]
                except FileNotFoundError:
                    print("Ficheiro 'catfile.txt' não existe")   
            else:
                #print("dentro do attr no else", self.FLAG_HASH)
                pass


            attr[key] = st[counter]
            counter = counter + 1

        #print("attr", attr)

        return attr 

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

        if ntpath.basename(path) in self.listCriticalFiles:
            self.checkPermission(path)
        
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

    # Our methods
    # ============

    # Obter json path 
    def getPaths(self):

        helper = Helper()

        self.atr_path = helper.jsonPath()
        self.hash_path = helper.hashFilePath()

        return self.atr_path, self.hash_path

    def loadJson(self):
        dict_ = {}

        with open(self.atr_path, 'r') as f:
            dict_ = json.load(f)
        
        return dict_

    def authentication(self):
        t = pyotp.TOTP('3232323232323232')
        auth_str = t.provisioning_uri(name='dancrossss',issuer_name='dancrossss')
        print(auth_str)
        code = t.now()
        print(code)
        print('Enter code:')
        x = input()
        print(x)
        if code == x:
            return True
            # if t.verify(code):
            #     return True
            # time.sleep(30)
            # return t.verify(code)
        else:
            print("Codigo invalido")
            return False

    def checkPermission(self, path):

        file_ = ntpath.basename(path)
        print(file_)

        dict_ = self.loadJson()

        helper = Helper()

        gid, uid = helper.getFileIds(dict_, path)

        userId = os.getuid()
        groupId = os.getgid()
        
        if not isdir(path):
            if userId == uid and groupId == gid:
                return True
            else:
                return self.authentication()
        else:
            return True    

    def getCriticalFileAttributes(self):

        listCriticalFolders = ["/etc/"]
        shpfiles = []

        print("Sistema de ficheiros iniciado")

        # Obter todas diretorias e ficheiros dentro das definidas na lista listCriticalFolders
        for i in range(len(listCriticalFolders)):

            for dirpath, subdirs, files in os.walk(listCriticalFolders[i]):
                #print("Diretoria", dirpath)
                #print("Ficheiros", files)
                for x in files:
                    if not x.endswith("supervise") and not x.endswith(".service") and not x.endswith(".conf") :
                        shpfiles.append(os.path.join(dirpath, x))
     
        count = 0
        res = {}
        loaded = {}

        for x in shpfiles:

            file_ = ntpath.basename(x)

            res[file_] = self.getattr(x)

            count += 1
        
        self.FLAG_HASH = False

        print(count)

        for j in range(len(listCriticalFolders)):
            loaded[listCriticalFolders[j]] = res

        j = json.dumps(loaded)

        os.chmod(self.atr_path, stat.S_IRWXU)

        with open(self.atr_path,'w') as f:
            f.write(j)
            f.close()

        os.chmod(self.atr_path, stat.S_IRUSR)

        #Testar a possibilidade de adicionar na lista
        #uma pasta e não só um ficheiro
        
        return


def main(mountpoint, root):
    FUSE(Passthrough(root),
        mountpoint, 
        nothreads=True, 
        foreground=True,
        allow_other=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])


# TODO: FALTA VER A QUESTAO DE PEDIR AUTENTICACAO EM TODOS FICHEIROS ANTES DE ABRIR