"""
ansible playbook executor wrapper

IBM Corporation, 2017, jochen kappel
"""
import json
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor import playbook_executor

from ansible.plugins.callback import CallbackBase
from flask import current_app as app
from .ans_kafka import *
from swagger_server.models.transition_request import TransitionRequest


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
                # build the dict of all internal resource properties
                for i in self.facts['msg']:
                    int_resource.update(dict(item.split(':', maxsplit=1) for item in i.replace(' ', '').split(',')))
                # add the new internal resource to the list
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

class Runner(object):
    """
    wraps ansible playbook execution
    """

    def __init__(self, hostnames, playbook,
                 private_key_file, run_data, location,
                 become_pass, request_id, started_at,
                 config, dbsession, tr, verbosity=5):

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
        self.resInstance = {}

        Options = namedtuple('Options',
                             ['connection',
                              'remote_user',
                              'ask_sudo_pass',
                              'verbosity',
                              'ack_pass',
                              'module_path',
                              'forks',
                              'become',
                              'become_method',
                              'become_user',
                              'check',
                              'listhosts',
                              'listtasks',
                              'listtags',
                              'syntax',
                              'sudo_user',
                              'sudo',
                              'diff',
                              'private_key_file',
                              'ansible_python_interpreter',
                              'host_key_checking'])

        self.options = Options(connection='ssh',
                               remote_user=None,
                               ack_pass=None,
                               sudo_user=None,
                               forks=20,
                               sudo=None,
                               ask_sudo_pass=False,
                               verbosity=verbosity,
                               module_path='/var/alm_ansible_rm/library',
                               become=True,
                               become_method='sudo',
                               become_user='root',
                               check=False,
                               diff=False,
                               listhosts=None,
                               listtasks=None,
                               listtags=None,
                               syntax=None,
                               private_key_file=private_key_file,
                               ansible_python_interpreter = '/usr/bin/python3',
                               host_key_checking=False)


        # Gets data from YAML/JSON files
        self.loader = DataLoader()

        # create temporary inventory file
        self.hosts = NamedTemporaryFile(delete=False)
        self.hosts.write(b'[run_hosts]\n')
        self.hosts.write(b'localhost ansible_connection=local ansible_python_interpreter="/usr/bin/env python3" host_key_checking=False')
        self.hosts.close()

        # set Inventory
        self.inventory = InventoryManager(loader=self.loader,
                                          sources=self.hosts.name)

        # All the variables from all the various places
        self.variable_manager = VariableManager(loader=self.loader,
                                           inventory=self.inventory)
        self.variable_manager.extra_vars = self.run_variables

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': become_pass}


        # Setup playbook executor, but don't run until run() called
        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords
        )

        if (self.transition_request) and (isinstance(self.transition_request, TransitionRequest)):
            # log only if transition request, not for netowrk/image scans)
            self.logger.debug('transition request ' + str(self.transition_request))
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

            if not self.callback.resource_id:
                self.logger.error('Resource ID MUST be set')
            resource_id = self.callback.resource_id
            self.logger.debug('resource created id ' + resource_id)

            # if self.transition_request.transition_name == 'Install':
            # removed, properties and instances are part of every reponse now
            if not self.callback.internal_resource_instances:
                self.logger.error('Internal Resources MUST be set')
            internal_resources = self.callback.internal_resource_instances
            self.logger.debug('internal resources ' + str(internal_resources))

            prop_output = {}
            prop_output.update(self.run_data)
            prop_output.update(self.callback.properties)

            # remove location and ansible variables (hard wired for now :-()
            del prop_output['user_id']
            del prop_output['keys_dir']
            del prop_output['metric_key']

            self.logger.debug(str(prop_output))
            self.logger.debug(str(self.callback.properties))

            properties = dict(set(prop_output.items()) - set(self.location.items()))
            self.logger.debug('properties: ' + str(properties))

            if self.transition_request.transition_name == 'Install':
                self.logger.debug('creating instance')
                self.resInstance = self.create_instance(resource_id, properties, internal_resources)

            if self.transition_request.transition_name == 'Uninstall':
                self.logger.debug('deleting instance')
                self.delete_instance(resource_id, self.transition_request.deployment_location)

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
        write log status to db or push to kafka
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
            if status == 'PENDING':
                self.dbsession.execute(
                    """
                    INSERT INTO requests (requestId, requestState, requestStateReason,startedAt, context)
                    VALUES  (%s, %s, %s, %s, %s)
                    USING TTL """ + str(ttl) + """
                    """,
                    (self.request_id, status, reason, started, self.config.getSupportedFeatures())
                    )
            else:
                self.dbsession.execute(
                    """
                    INSERT INTO requests (requestId, requestState, requestStateReason, resourceId, finishedAt)
                    VALUES  (%s, %s, %s, %s, %s)
                    USING TTL """ + str(ttl) + """
                    """,
                    (self.request_id, status, reason, resource_id, finished)
                    )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.info('request logged to DB: ' + str(self.request_id))

        if is_async_mode:
            if (status == 'COMPLETED') or (status == 'FAILED'):
                # call kafka
                self.logger.info('async mode and status is '+status)
                kafkaClient = Kafka(self.logger)

                kmsg = {}
                kmsg['resourceInstance'] = dict(self.resInstance)
                kmsg['requestId'] = str(self.request_id)
                kmsg['resourceManagerId'] = self.transition_request.resource_manager_id
                kmsg['deploymentLocation'] = self.transition_request.deployment_location
                kmsg['resourceType'] = self.transition_request.resource_type
                kmsg['transitionName'] = self.transition_request.transition_name
                kmsg['context'] = {}
                kmsg['requestState'] = status
                kmsg['requestStateReason'] = reason
                kmsg['startedAt'] = started
                kmsg['finishedAt'] = finished

                self.logger.debug('sending message to kafka: ' + str(kmsg))
                kafkaClient.sendLifecycleEvent(kmsg)

        return

    def create_instance(self, resource_id, out_props, internal_resources):
        """
        save instance details to db
        """
        self.logger.info('create instance  ' + resource_id)

        # a little cheating, need to get this from OS
        created_at = self.finished_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_modified_at = created_at

        pitem = {'resourceId': resource_id,
                 'deploymentLocation': self.transition_request.deployment_location,
                 'resourceType': self.transition_request.resource_type,
                 'resourceName': self.transition_request.resource_name,
                 'resourceManagerId': self.transition_request.resource_manager_id,
                 'properties': out_props,
                 'internalResourceInstances': internal_resources,
                 'metricKey': self.transition_request.metric_key,
                 'createdAt': created_at,
                 'lastModifiedAt': last_modified_at
                 }

        try:
            self.dbsession.execute("""
                INSERT INTO instances
                (resourceId, resourceType, resourceName, resourceManagerId,
                deploymentLocation, createdAt, lastModifiedAt,
                properties, internalResourceInstances, metricKey)
                VALUES  (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
                """,
                (uuid.UUID(pitem['resourceId']), pitem['resourceType'],
                pitem['resourceName'], pitem['resourceManagerId'],
                pitem['deploymentLocation'], pitem['createdAt'],
                pitem['lastModifiedAt'], pitem['properties'],
                pitem['internalResourceInstances'], pitem['metricKey'])
            )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.info('instance logged to DB: ' + str(pitem['resourceId']))
        self.logger.debug('instance created ' + str(pitem))
        return pitem

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
                [uuid.UUID(resource_id), deployment_location]
            )
        except Exception as err:
            # handle any other exception
            self.logger.error(str(err))
            raise

        self.logger.debug('instance deleted ' + resource_id)
        return
