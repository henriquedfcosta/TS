#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import ntpath
import json

from fuse import FUSE, FuseOSError, Operations, fuse_get_context


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root
        self.getCriticalFileAtributtes()

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
        attr = {}
        counter = 0
        dict_ = {}

        try:
            for key in ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime'):
                attr['file_Name'] = ntpath.basename(path)
                attr[key] = st[counter]
                counter = counter + 1
        except:
            print("E link")

        """file = self.open(full_path, os.O_RDONLY)
        attr['hash'] = hashlib.sha256(file).hexdigest() 
        print(attr['hash'])"""

        #dict_["szsadsadsa"] = attr
        #dict_ = attr
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
    def getCriticalFileAtributtes(self):

        #listCriticalFolders = ["/etc/", "/dev/hd", "/root", "/boot"]
        listCriticalFolders = ["/etc/"]
        shpfiles = []

        print("Sistema de ficheiros iniciado")

        # Obter todas diretorias e ficheiros dentro das definidas na lista listCriticalFolders
        for i in range(len(listCriticalFolders)):

            for dirpath, subdirs, files in os.walk(listCriticalFolders[i]):
                for x in files:
                    if not x.endswith("supervise") and not x.endswith(".service") and not x.endswith(".conf") :
                        shpfiles.append(os.path.join(dirpath, x))
     
        count = 0
        loaded = {}

        # Transformar em JSON
        for x in range(len(shpfiles)):

            print("Atributos: ")
            print("path", shpfiles[x])

            self.getattr(shpfiles[x])
            with open("/home/kali/Desktop/TS/atributos.json", "r") as f:

                try:
                    loaded = json.load(f)
                except:
                    pass

            with open("/home/kali/Desktop/TS/atributos.json", "w") as f:

                loaded[list(self.getattr(shpfiles[x]).keys())[0]] = self.getattr(shpfiles[x]).get(list(self.getattr(shpfiles[x]).keys())[0])
                json.dump(loaded, f, indent=6)
                
            count += 1

            #print
            print("\n\n")
        print(count)
                
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