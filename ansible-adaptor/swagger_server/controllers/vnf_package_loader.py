"""
IBM Corporation, 2017, jochen kappel
process VNF .csar archives
 - move to staging directry
 - extract
 - check completeness
     . must have lifecycle folder
     . must have Meta-Inf folder
     . must have Install.* file in lifecycle
     . must have manifest.MF in meta-inf folder
     . opt if AD + RD exist, must be valid Ds and YAML

"""
import os
import sys
import stat
import re
import yaml
import tempfile
from pathlib import Path
from shutil import move, copy, rmtree
from zipfile import ZipFile, ZipInfo, BadZipFile
from flask import current_app as app

def move_archive(src_file, filename, target_dir):
    """
    move csar from src to target
    return full path to target
    """
    # move file to target
    src_file.save(os.path.join(target_dir, filename))
    app.logger.info('Archive moved to '+str(target_dir))
    return Path(str(target_dir)+'/'+filename)

def create_tmpdir():
    """ create a staging folder """
    # first create a sub dir in staging
    newdir = tempfile.mkdtemp()
    app.logger.info('target folder created: '+str(newdir))
    return newdir

def remove_tmpdir(tmpdir):
    rmtree(tmpdir)
    app.logger.info('removed ' + tmpdir)

def create_targetdir(res_dir, res_name, res_ver):
    """ create target folder """
    newdir = str(Path(res_dir, res_name, res_ver ))
    os.makedirs( newdir, exist_ok=True )
    app.logger.info('target folder created: '+str(newdir))
    return newdir

def unpack(archive_file, extract_dir):
    """ try to unzip the .csar """

    try:
        app.logger.info('extracting archive ' + str(archive_file) + ' to folder '+str(extract_dir))
        with ZipFile(str(archive_file), 'r') as zipf:
            zipf.extractall(str(extract_dir))
        return True
    except Exception as err:
        app.logger.error(str(err))
        return False


def existsFileInArchive(archive_file, filename):
    with ZipFile(str(archive_file), 'r') as zipf:
        content = zipf.namelist()
        if filename not in content:
            app.logger.error('There is no item named ' + filename + ' in the archive')
            return False
        else:
            app.logger.info(filename + ' exists in '+str(archive_file))
            return True


def existsAnyFileInArchiveFolder(archive_file, fileexpr):
    with ZipFile(str(archive_file), 'r') as zipf:
        content = zipf.namelist()
        # build the regex
        regex = re.compile(fileexpr)
        filesfound = list(filter(regex.match, content))
        if len(filesfound) <= 0:
            app.logger.error('There isnt any file like ' + fileexpr + ' in the archive')
            return False
        else:
            app.logger.info('found ' + str(filesfound) + ' files in '+str(archive_file))
            return True

def isValidDescriptor(zipfile, tmpdir, folder, type, desc_name):
    # get all files from folder
    with ZipFile(str(zipfile), 'r') as zipf:
        content = zipf.namelist()
        # build the regex
        regex = re.compile(folder + '/.*\.yml')
        filesfound = list(filter(regex.match, content))

        for descriptorname in filesfound:
            # extract file
            app.logger.info('extracting descriptor ' + descriptorname)
            descriptor = zipf.extract(descriptorname, path=tmpdir)

            with open(descriptor, 'r') as f:
                try:
                    # load as YAML
                    app.logger.info('loading as YAML')
                    yamlf = yaml.load(f)

                    if type+'::' not in yamlf['name']:
                        app.logger.error('Not a valid ' + type + ' descriptor, found ' + yamlf['name'])
                        return False
                    else:
                        app.logger.info('contains ' + type + 'descriptor: ' + yamlf['name'])

                    if (type == 'resource') and (desc_name != yamlf['name']):
                        app.logger.error('Resource descriptor name does not match. Is '
                                         + yamlf['name'] + ' - should be '+desc_name  )
                        return False

                except yaml.YAMLError as exc:
                    app.logger.error(exc)
                    return False
        return True

def isValidManifest( zipfile, tmpdir, folder):
    # get all files from folder
    with ZipFile(str(zipfile), 'r') as zipf:
        content = zipf.namelist()
        # build the regex
        regex = re.compile(folder + '/.*\.MF')
        filesfound = list(filter(regex.match, content))

        for mfname in filesfound:
            # extract file
            app.logger.info('extracting manifest ' + mfname)
            mf = zipf.extract(mfname, path=tmpdir)

            goodMF = True
            with open(mf, 'r') as f:
                try:
                    # load as YAML
                    app.logger.info('loading as YAML')
                    yamlf = yaml.load(f)

                    if not yamlf['name']:
                        app.logger.error('No name for resource provided')
                        goodMF = False
                    else:
                        app.logger.info('resource name: ' + yamlf['name'])

                    if not yamlf['resource-manager']:
                        app.logger.error('No target resource-manager for resource provided')
                        goodMF = False
                    else:
                        app.logger.info('resource-manager: ' + yamlf['resource-manager'])

                    if not yamlf['version']:
                        app.logger.error('No version for resource provided')
                        goodMF = False
                    else:
                        app.logger.info('resource version: ' + str(yamlf['version']))

                except yaml.YAMLError as exc:
                    app.logger.error(exc)
                    goodMF =  False
        return goodMF


def isValidPackage(archive_file, tmpdir, res_name, res_ver):
    # archive
    try:
        with ZipFile(str(archive_file), 'r') as zipf:
            badFile = zipf.testzip()
            if badFile is None:
                app.logger.info('archive is zipfile ')
                archiveIsOk = True
            else:
                app.logger.error('found bad file in archive: ' + badFile)
                archiveIsOk = False
    except BadZipFile as err:
        app.logger.error(err)
        return False, 'Bad archive file'

    if not existsFileInArchive(archive_file, 'lifecycle/'):
        app.logger.info('A lifecycle folder MUST exist in the csar')
        return False, 'A lifecycle folder MUST exist in the csar'

    if not existsFileInArchive(archive_file, 'Meta-Inf/'):
        app.logger.info('A Meta-Inf folder MUST exist in the csar')
        return False, 'A Meta-Inf folder MUST exist in the csar'

    if not existsFileInArchive(archive_file, 'Meta-Inf/manifest.MF'):
        app.logger.info('A manifest.MF MUST exist in the Meta-Inf folder')
        return False, 'A manifest.MF MUST exist in the Meta-Inf folder'

    if not existsAnyFileInArchiveFolder(archive_file, 'lifecycle/Install.yml'):
        app.logger.info('The lifecycle folder MUST at least contain an Install script')
        return False, 'The lifecycle folder MUST at least contain an Install script'

    if not isValidManifest(archive_file, tmpdir, 'Meta-Inf'):
        return False, 'no valid Manifest file'

    if not isValidDescriptor(archive_file, tmpdir, 'descriptor', 'resource', 'resource::'+res_name+'::'+res_ver):
        return False, 'no valid resource descriptor'

    if not isValidDescriptor(archive_file, tmpdir, 'Service-Template', 'assembly', ''):
        return False, 'no valid assembly descriptor'

    return True, ''
