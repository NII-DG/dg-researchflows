import os

from osfclient.cli import OSF, split_storage


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

    store = project.storage(storage)
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