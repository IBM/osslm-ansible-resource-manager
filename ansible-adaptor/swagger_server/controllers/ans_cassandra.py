"""
Database functions (create schema, connect,..)

IBM Corporation, 2017, jochen kappel
"""

from flask import current_app as app
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


class CassandraHandler:
    """
    database handler singleton
    """
    class __CassandraHandler:
        """ inner signelton class"""
        def __init__(self):
            self.keyspace = "alm_ansible"
            self.dbSession = None

        def __del__(self):
            self.dbSession.close()

        def get_session(self):
            """ get a DB conenction """
            if self.dbSession:
                app.logger.info('using cassandra session to ' + self.keyspace)
            else:
                app.logger.info('creating cassandra session ' + self.keyspace)

                try:
                    self.cluster = Cluster(['alm-ansible-rm-db'])

                    self.dbSession = self.cluster.connect()
                    app.logger.info('connected to cassandra, keyspace: ' + self.keyspace)
                except ConnectionRefusedError as err:
                    app.logger.error("No connection error: {0}".format(err))
                    self.dbSession = None
                    raise
                except Exception as e:
                    # handle any other exception
                    self.dbSession = None
                    app.logger.error(str(e))
                    raise

                else:
                    self.dbSession.execute("""
                        CREATE KEYSPACE IF NOT EXISTS %s
                        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                        """ % self.keyspace)

                    self.dbSession.set_keyspace(self.keyspace)
                    self.dbSession.row_factory = dict_factory

            return self.dbSession

        def create_tables(self):
            """
            creates all RM tables
            requests
            instances
            locations
            """
            session = self.get_session()

            try:
                session.execute("""
                CREATE TABLE  IF NOT EXISTS requests (
                    requestId UUID,
                    requestState text,
                    requestStateReason text,
                    resourceId UUID,
                    startedAt timestamp,
                    finishedAt timestamp,
                    context map<text, boolean>,
                    PRIMARY KEY ( (requestId) ))
                    """)
                app.logger.info('table requests created')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            try:
                session.execute("""
                CREATE TABLE IF NOT EXISTS instances (
                    resourceId UUID,
                    resourceType text,
                    resourceName text,
                    resourceManagerId text,
                    deploymentLocation text,
                    metricKey text,
                    createdAt timestamp,
                    lastModifiedAt timestamp,
                    properties map<text, text>,
                    internalProperties map<text, text>,
                    internalResourceInstances list<frozen <map <text, text>>>,
                    PRIMARY KEY ( ( deploymentLocation ), resourceId  ))
                    """)
                app.logger.info('table instances created')
                session.execute("""
                    CREATE INDEX IF NOT EXISTS idx_instances_id
                    ON instances ( resourceId )
                    """)

                session.execute("""
                    CREATE INDEX IF NOT EXISTS idx_instances_type
                    ON instances ( resourceType )
                    """)

                session.execute("""
                    CREATE INDEX IF NOT EXISTS idx_instances_metrickey
                    ON instances ( metricKey )
                    """)

            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            try:
                session.execute("""
                   CREATE TABLE IF NOT EXISTS locations (
                      name text,
                      type text,
                      description text,
                      properties map<text, text>,
                      PRIMARY KEY ( name  ))
                      """)
                app.logger.info('table locations created')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            # add sample location for hello world test
            try:
                session.execute("""
                   INSERT INTO locations (name, type, description, properties)
                   VALUES ( %s, %s, %s, %s )
                      """, ('world', 'planet', 'a test location', {}))
                app.logger.info('sample locatiob inserted')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            return 201

        def delete_tables(self):
            """
            deletes all tables and indeces
            """
            session = self.get_session()

            try:
                session.execute("DROP TABLE  IF EXISTS alm_ansible.requests")
                app.logger.info('table requests deleted')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            try:

                session.execute("DROP INDEX IF EXISTS idx_instances_id")
                session.execute("DROP INDEX IF EXISTS idx_instances_type")
                session.execute("DROP INDEX IF EXISTS idx_instances_metrickey")
                session.execute("DROP TABLE IF EXISTS alm_ansible.instances")
                app.logger.info('table instances deleted')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            try:
                session.execute("DROP TABLE IF EXISTS locations")
                app.logger.info('table locations deleted')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 400

            return 200

        def truncate_table(self, tablename):
            """
            truncates a table
            """
            session = self.get_session()

            try:
                session.execute("TRUNCATE TABLE " + tablename)
                app.logger.info('table '+tablename+' truncated')
            except Exception as e:
                # handle any other exception
                app.logger.error(str(e))
                return 404

            return 200

    instance = None

    def __init__(self):
        if not CassandraHandler.instance:
            CassandraHandler.instance = CassandraHandler.__CassandraHandler()

    def __getattr__(self, name):
        return getattr(self.instance, name)
