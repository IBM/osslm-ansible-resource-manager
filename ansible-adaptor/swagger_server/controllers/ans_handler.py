"""
ansible playbook executor wrapper

IBM Corporation, 2017, jochen kappel
"""
import json
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor import playbook_executor
from ansible.utils.display import Display

from ansible.plugins import callback_loader
from ansible.plugins.callback import CallbackBase
from flask import current_app as app



class OutputCallback(CallbackBase):
    """
    callbacks for the ansible playbook runner
    """
    def __init__(self, logger, *args, **kwargs):
        super(OutputCallback, self).__init__(*args, **kwargs)
        self.host_ok = True
        self.host_unreachable = False
        self.host_failed = False
        self.host_unreachable_log = []
        self.host_failed_log = []
        self.facts = {}
        self.failed_task = ''
        self.logger = logger
        self.logger.info('initializing ansible callback')

        # return data, will be filled if run ok
        self.resource_id = None
        self.properties = {}
        self.internal_resource_instances = []


    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        """
        ansible task failed as host was unreachable
        """
        self.failed_task = result._task.get_name()
        self.host_unreachable_log.append(dict(task=self.failed_task, result=result._result))
        self.logger.debug(result._result)
        self.logger.info('ansible playbook - host unreachable ' + str(self.host_unreachable_log))
        self.host_unreachable = True


    def v2_runner_on_ok(self, result, *args, **kwargs):
        """
        ansible task finished ok
        """
        task = result._task.get_name()
        self.logger.info('ansible playbook - task run OK ' + task)
        self.logger.debug(result._result)
        if 'results' in result._result.keys():
            self.facts = result._result['results']
        else:
            self.facts = result._result

        if 'msg' in self.facts.keys():

            if 'RESOURCE_ID' in task:
                self.resource_id = dict(item.split(':', maxsplit=1)
                                        for item in self.facts['msg'][0].replace(' ', '').split(','))['resourceId']
                self.logger.info('resource_id reported: ' + str(self.resource_id))

            elif 'PROPERTIES' in task:
                # collect all properties
                for i in self.facts['msg']:
                    self.properties.update(
                        dict(item.split(':', maxsplit=1)
                             for item in i.replace(' ', '').split(',')))
                self.logger.info('properties reported')
                self.logger.debug('properites are: ' + str(self.properties))

            elif 'INTERNAL_RESOURCE' in task:
                # remove the type element
                int_resource = {}
                #build the dict of all internal resource properties
                for i in self.facts['msg']:
                    int_resource.update(dict(item.split(':', maxsplit=1)
                                             for item in i.replace(' ', '').split(',')))
                #add the new internal resource to the list
                self.internal_resource_instances.append(int_resource)
                self.logger.info('internal resources reported')
                self.logger.debug('interal resources are : ' + str(int_resource))

            else:
                self.logger.warning('unsupported output type found in ansible playbook')


    def v2_runner_on_failed(self, result, *args, **kwargs):
        """
        ansible task failed
        """
        self.host_failed = True
        self.failed_task = result._task.get_name()
        self.host_failed_log.append(dict(task=self.failed_task, result=result._result))
        self.logger.info('ansible playbook - host failed ' + str(self.host_failed_log))
        self.logger.debug(result._result)

    def is_run_ok(self):
        """
        get overall playbook result (ok i all tasks ran ok)
        """
        success = ((not self.host_unreachable) and (not self.host_failed))
        self.logger.info('run was OK: ' + str(success))
        return success


class Options(object):
    """
    Options class to replace Ansible OptParser
    """
    def __init__(self, verbosity=None, inventory=None, listhosts=None,
                 subset=None,
                 module_paths=None, extra_vars=None, forks=None,
                 ask_vault_pass=None, vault_password_files=None,
                 new_vault_password_file=None, output_file=None, tags=None,
                 skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None,
                 ask_su_pass=None, sudo=None,
                 sudo_user=None, become=None, become_method=None, become_user=None,
                 become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None,
                 connection=None, timeout=None,
                 ssh_common_args=None, sftp_extra_args=None,
                 scp_extra_args=None, ssh_extra_args=None,
                 poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None,
                 force_handlers=None, flush_cache=None, listtasks=None,
                 listtags=None, module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = {}
        self.skip_tags = {}
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path
        self.ansible_python_interpreter = '/usr/bin/python3'

class Runner(object):
    """
    wraps ansible playbook execution
    """

    def __init__(self, hostnames, playbook,
                 private_key_file, run_data, location,
                 become_pass, request_id, started_at,
                 config, dbsession, tr, verbosity=0):

        self.logger = app.logger
        self.logger.info('initializing ansible runbook executor')

        self.config = config
        self.dbsession = dbsession
        self.transition_request = tr

        self.location = location
        self.run_data = run_data
        self.run_variables = {}
        self.run_variables.update(self.run_data)
        self.run_variables.update(self.location)
        self.logger.debug(str(self.location))
        self.logger.debug(str(self.run_data))
        self.logger.debug(str(self.run_variables))

        self.request_id = request_id
        self.started_at = started_at
        self.finished_at = None

        self.options = Options()
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = 'ssh'  # Need a connection type "smart" or "ssh"
        self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity
        # Executor appears to have it's own
        # verbosity object/setting as well
        playbook_executor.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        self.loader.set_vault_password('tsl')

        # All the variables from all the various places
        self.variable_manager = VariableManager()
        self.variable_manager.extra_vars = self.run_variables

        self.hosts = NamedTemporaryFile(delete=False)
        self.hosts.write(b'[run_hosts]\n')
        self.hosts.write(b'localhost ansible_connection=local ansible_python_interpreter="/usr/bin/env python3"')
        self.hosts.close()

        # Set inventory, using most of above objects
        self.inventory = Inventory(loader=self.loader,
                                   variable_manager=self.variable_manager,
                                   host_list=self.hosts.name)
        self.variable_manager.set_inventory(self.inventory)

        results_callback = callback_loader.get('json')

        # Setup playbook executor, but don't run until run() called
        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords
        )

        if isinstance(self.transition_request, dict):
            # log only if transition request, not for netowrk/image scans)
            self.log_request_status('PENDING', 'playbook initialized', '')

        self.logger.info('ansible runbook executor instantiated for ' + str(playbook))

        self.callback = OutputCallback(self.logger)
        self.pbex._tqm._stdout_callback = self.callback

    def run(self):
        """
        run an ansible playbook (sync mode) and return Results
        """
        self.logger.info('ansible playbook run started')
        self.pbex.run()
        return json.dumps(self.callback.facts), self.callback.is_run_ok()

    def run_async(self):
        """
        run an ansible playbook asynchronously and return results when done
        """
        self.logger.info('ansible playbook run started ' + self.started_at.isoformat())

        self.log_request_status('IN_PROGRESS', 'running playbook', '')
        self.pbex.run()
        self.finished_at = datetime.now()
        self.logger.info('ansible playbook run finished ' + self.finished_at.isoformat())

        if self.callback.is_run_ok():
            self.logger.info('ansible ran OK')

            resource_id = self.callback.resource_id
            self.logger.debug('resource created id ' + resource_id)

            if self.transition_request.transition_name == 'Install':

                internal_resources = self.callback.internal_resource_instances
                self.logger.debug('internal resources ' + str(internal_resources))

                prop_output = {}
                prop_output.update(self.run_data)
                prop_output.update(self.callback.properties)

                # remove location and ansible variables (hard wired for now :-()
                del prop_output['user_id']
                del prop_output['keys_dir']

                self.logger.debug(str(prop_output))
                self.logger.debug(str(self.callback.properties))

                properties = dict(set(prop_output.items()) - set(self.location.items()))
                self.logger.debug('properties: '+ str(properties))

                self.logger.debug('creating instance')
                self.create_instance(resource_id, properties, internal_resources)

            elif self.transition_request.transition_name == 'Uninstall':
                self.logger.debug('deleting instance')
                self.delete_instance(resource_id, self.transition_request.deployment_location )

            self.log_request_status('COMPLETED', 'Done in ' + str((self.finished_at - self.started_at).total_seconds()) + ' seconds', resource_id)
            return

        else:
            self.logger.info('ansible run failed')
            self.logger.error('ansible error')

            if self.callback.failed_task != '':
                last_task = self.callback.failed_task
            else:
                last_task = 'Unknown'
            self.log_request_status('FAILED', 'Failed on ' + last_task, '')
            return

    def log_request_status(self, status, reason, resource_id):
        """
        write log status to file or push to kafka
        """
        self.logger.info('working on status '+status)
        is_async_mode = self.config.getSupportedFeatures()['AsynchronousTransitionResponses']
        ttl = self.config.getTTL()

        self.logger.info('async request mode is ' + str(is_async_mode))
        if (status == 'COMPLETED') or (status == 'FAILED'):
            finished = self.finished_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            finished = ''

        started = self.started_at.strftime('%Y-%m-%dT%H:%M:%SZ')

        if resource_id != '':
            resource_id = uuid.UUID(resource_id)
        else:
            resource_id = None


        self.logger.info('writing request status to db')
        self.logger.debug('request id '+str(self.request_id))

        try:
            self.dbsession.execute("""
                INSERT INTO requests (requestId, requestState, requestStateReason, resourceId, startedAt, finishedAt, context)
                VALUES  (%s, %s, %s, %s, %s, %s, %s)
                USING TTL """+ str(ttl) +"""
                 """,
                (self.request_id, status, reason, resource_id,
                 started, finished, self.config.getSupportedFeatures())
                 )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.info('request logged to DB: ' + str(self.request_id))

        if is_async_mode:
            # call kafka
            self.logger.critical('is_async_mode mode using kafka is not implemented yet')

        return



    def create_instance(self, resource_id, out_props, internal_resources):
        """
        save instance details to db
        """
        self.logger.info('create instance  ' + resource_id)

        pitem = {'resource_id': uuid.UUID(resource_id),
                 'deploymentLocation': self.transition_request.deployment_location,
                 'resourceType': self.transition_request.resource_type,
                 'resourceName': self.transition_request.resource_name,
                 'resourceManagerId': self.transition_request.resource_manager_id,
                 'properties': out_props,
                 'internal_resources': internal_resources}

        # a little cheating, need to get this from OS
        created_at = self.finished_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_modified_at = created_at

        try:
            self.dbsession.execute("""
                INSERT INTO instances
                (resourceId, resourceType, resourceName, resourceManagerId,
                deploymentLocation, createdAt, lastModifiedAt,
                properties, internalResourceInstances)
                VALUES  (%s, %s, %s, %s, %s, %s, %s,%s, %s)
                """,
                (pitem['resource_id'], pitem['resourceType'],
                pitem['resourceName'], pitem['resourceManagerId'],
                pitem['deploymentLocation'], created_at, last_modified_at,
                pitem['properties'], pitem['internal_resources'])
                #(uuid.UUID(resource_id), self.transition_request.resource_type, self.transition_request.resource_name, self.transition_request.resource_manager_id, self.transition_request.deployment_location, created_at, last_modified_at, out_props, internal_resources)
            )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.info('instance logged to DB: ' + str(pitem['resource_id']))
        self.logger.debug('instance created ' + str(pitem))
        return



    def delete_instance(self, resource_id, deployment_location):
        """
        delete instance details from db
        """
        self.logger.info('deleting instance  ' + resource_id)

        try:
            self.dbsession.execute("""
                DELETE FROM instances
                WHERE resourceId = %s and deploymentLocation = %s
                """,
                [uuid.UUID(resource_id), deployment_location ]
            )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.debug('instance deleted ' + resource_id)
        return
