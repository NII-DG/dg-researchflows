import os
import six
from requests.exceptions import ConnectionError

from osfclient.cli import OSF, split_storage
from osfclient.models.core import OSFCore
from osfclient.models.file import ContainerMixin
from osfclient.models.file import File, Folder, _WaterButlerFolder
from osfclient.utils import checksum
from osfclient.utils import file_empty
from osfclient.utils import get_local_file_size
from osfclient.utils import norm_remote_path

from ...file import File as ff

script_dir = os.path.dirname(os.path.abspath(__file__))
logfilepath = os.path.abspath(os.path.join(script_dir, "sync_log"))
logfile = ff(logfilepath)
if not os.path.exists(logfilepath):
    logfile.create()


class Storage(OSFCore, ContainerMixin):
    _files_key = ('relationships', 'files', 'links', 'related', 'href')

    def _update_attributes(self, storage):
        if not storage:
            return

        self.id = self._get_attribute(storage, 'id')

        self.path = self._get_attribute(storage, 'attributes', 'path')
        self.name = self._get_attribute(storage, 'attributes', 'name')
        self.node = self._get_attribute(storage, 'attributes', 'node')
        self.provider = self._get_attribute(storage, 'attributes', 'provider')

        self._files_url = self._get_attribute(storage, *self._files_key)

        self._new_folder_url = self._get_attribute(storage,
                                                   'links', 'new_folder')
        self._new_file_url = self._get_attribute(storage, 'links', 'upload')

    def __str__(self):
        return '<Storage [{0}]>'.format(self.id)

    @property
    def files(self):
        """Iterate over all files in this storage.

        Recursively lists all files in all subfolders.
        """
        return self._iter_children(self._files_url, 'file', File,
                                   self._files_key)

    def create_file(self, path, fp, force=False, update=False):
        """Store a new file at `path` in this storage.

        The contents of the file descriptor `fp` (opened in 'rb' mode)
        will be uploaded to `path` which is the full path at
        which to store the file.

        To force overwrite of an existing file, set `force=True`.
        To overwrite an existing file only if the files differ, set `update=True`
        """
        if 'b' not in fp.mode:
            raise ValueError("File has to be opened in binary mode.")

        # all paths are assumed to be absolute
        path = norm_remote_path(path)

        directory, fname = os.path.split(path)
        directories = directory.split(os.path.sep)
        # navigate to the right parent object for our file
        parent = self
        for directory in directories:
            # skip empty directory names
            if directory:
                parent = parent.create_folder(directory, exist_ok=True)

        url = parent._new_file_url

        # When uploading a large file (>a few MB) that already exists
        # we sometimes get a ConnectionError instead of a status == 409.
        connection_error = False
        
        # peek at the file to check if it is an empty file which needs special
        # handling in requests. If we pass a file like object to data that
        # turns out to be of length zero then no file is created on the OSF.
        # See: https://github.com/osfclient/osfclient/pull/135
        if file_empty(fp):
            response = self._put(url, params={'name': fname}, data=b'')
        else:
            try:
                response = self._put(url, params={'name': fname}, data=fp)
            except ConnectionError:
                connection_error = True

        if connection_error or response.status_code == 409:
            if not force and not update:
                # one-liner to get file size from file pointer from
                # https://stackoverflow.com/a/283719/2680824
                file_size_bytes = get_local_file_size(fp)
                large_file_cutoff = 2**20 # 1 MB in bytes
                if connection_error and file_size_bytes < large_file_cutoff:
                    msg = (
                        "There was a connection error which might mean {} " +
                        "already exists. Try again with the `--force` flag " +
                        "specified."
                    ).format(path)
                    raise RuntimeError(msg)
                else:
                    # note in case of connection error, we are making an inference here
                    raise FileExistsError(path)

            else:
                # find the upload URL for the file we are trying to update
                for file_ in self.files:
                    if norm_remote_path(file_.path) == path:
                        if not force:
                            if checksum(path) == file_.hashes.get('md5'):
                                # If the hashes are equal and force is False,
                                # we're done here
                                break
                        # in the process of attempting to upload the file we
                        # moved through it -> reset read position to beginning
                        # of the file
                        fp.seek(0)
                        file_.update(fp)
                        break
                else:
                    raise RuntimeError("Could not create a new file at "
                                       "({}) nor update it.".format(path))


class UpdateArgs:

    def __init__(self, project_id, source, destination, recursive=False, force=False) -> None:
        self.project = project_id
        self.source = source
        self.destination = destination
        self.recursive = recursive
        self.force = force
        self.update = False


def upload(token, base_url, args):
    if args.source is None or args.destination is None:
        raise KeyError("too few arguments: source or destination")

    osf = OSF(token=token, base_url=base_url)
    if not osf.has_auth:
        raise KeyError('To upload a file you need to provide a username and'
                    ' password or token.')

    project = osf.project(args.project)
    storage, remote_path = split_storage(args.destination)

    #store = project.storage(storage)

    store = None
    stores = project._json(project._get(project._storages_url), 200)
    stores = stores['data']
    for sto in stores:
        provides = project._get_attribute(sto, 'attributes', 'provider')
        if provides == storage:
            store = Storage(sto, project.session)
            break
    else:
        raise RuntimeError("Project has no storage "
                           "provider '{}'".format(storage))


    if args.recursive:
        if not os.path.isdir(args.source):
            raise RuntimeError("Expected source ({}) to be a directory when "
                                "using recursive mode.".format(args.source))

        # local name of the directory that is being uploaded
        _, dir_name = os.path.split(args.source)

        for root, _, files in os.walk(args.source):
            subdir_path = os.path.relpath(root, args.source)
            for fname in files:
                local_path = os.path.join(root, fname)
                with open(local_path, 'rb') as fp:
                    # build the remote path + fname
                    name = os.path.join(remote_path, dir_name, subdir_path,
                                        fname)
                    store.create_file(name, fp, force=args.force,
                                        update=args.update)

    else:
        with open(args.source, 'rb') as fp:
            store.create_file(remote_path, fp, force=args.force,
                                update=args.update)