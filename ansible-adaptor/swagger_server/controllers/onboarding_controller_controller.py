import connexion
import six
import os

from swagger_server import util
from flask import abort
from flask import current_app as app
from werkzeug.utils import secure_filename

from .ans_driver_config import ConfigReader
from .vnf_package_loader import *

def types_upload(resource_name, resource_version, upfile=None):  # noqa: E501
    """Upload VNF packages

     # noqa: E501

    :param resource_name: Unique name for the resource type
    :type resource_name: str
    :param resource_version: version of the resource type
    :type resource_version: str
    :param upfile: The file to upload.
    :type upfile: werkzeug.datastructures.FileStorage

    :rtype: None
    """
    app.logger.info('VNF pack for resource ' + resource_name + ' version ' + resource_version)

    if not upfile:
        abort(400, 'no file uploaded')

    app.logger.info('File received: ' + upfile.filename )

    if upfile.filename.rsplit('.', 1)[1].lower() != 'csar':
        abort(400, 'not a .csar archive')

    if upfile.filename == '':
        abort(400, 'no file attached')

    filename = secure_filename(upfile.filename)
    res_dir = ConfigReader().getResourceDir()

    # .csar found
    app.logger.info('working on archive ' + str(filename))

    # create tmp dir
    tmpdir = create_tmpdir()
    # move .csar from inbox to vault
    archive_file = move_archive( upfile, filename, tmpdir)

    archiveOK, msg = isValidPackage(archive_file, tmpdir, resource_name, resource_version)
    if archiveOK:
         # create a directory to extract to
         csar_dir = create_targetdir(res_dir, resource_name, resource_version)
         if not unpack(archive_file, csar_dir):
             abort(400, 'cant extract to target')
         remove_tmpdir(tmpdir)
         return 'all OK'


    else:
        remove_tmpdir(tmpdir)
        abort(400, msg)
