import cx_Oracle
import json
from typing import Dict, Any, List, Optional
from cryptography.fernet import Fernet
import os

class OracleClient:
    """Service to handle Oracle database connections and queries"""
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for database passwords"""
        key_path = os.getenv('DB_ENCRYPTION_KEY_PATH', '/tmp/db_key.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt database password"""
        return self.cipher_suite.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt database password"""
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()
    
    def test_connection(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Oracle database connection"""
        try:
            password = self.decrypt_password(connection_config.get('password', ''))
            
            # Build connection string
            dsn = cx_Oracle.makedsn(
                connection_config['host'],
                connection_config.get('port', 1521),
                service_name=connection_config.get('service_name'),
                sid=connection_config.get('sid')
            )
            
            connection = cx_Oracle.connect(
                user=connection_config['username'],
                password=password,
                dsn=dsn
            )
            
            # Test with simple query
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM dual")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'message': 'Connection successful',
                'server_version': connection.version
            }
            
        except cx_Oracle.Error as e:
            error_obj, = e.args
            return {
                'success': False,
                'error': f'Oracle Error {error_obj.code}: {error_obj.message}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_query(self, connection_config: Dict[str, Any], query: str, 
                     parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute SQL query on Oracle database"""
        try:
            password = self.decrypt_password(connection_config.get('password', ''))
            
            # Build connection string
            dsn = cx_Oracle.makedsn(
                connection_config['host'],
                connection_config.get('port', 1521),
                service_name=connection_config.get('service_name'),
                sid=connection_config.get('sid')
            )
            
            connection = cx_Oracle.connect(
                user=connection_config['username'],
                password=password,
                dsn=dsn
            )
            
            cursor = connection.cursor()
            
            # Execute query with parameters if provided
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            # Determine query type and handle accordingly
            query_type = query.strip().upper()
            
            if query_type.startswith('SELECT'):
                # For SELECT queries, fetch results
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # Convert rows to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                result = {
                    'success': True,
                    'query_type': 'SELECT',
                    'columns': columns,
                    'data': results,
                    'row_count': len(results)
                }
                
            elif query_type.startswith(('INSERT', 'UPDATE', 'DELETE')):
                # For DML queries, commit and return affected rows
                connection.commit()
                result = {
                    'success': True,
                    'query_type': query_type.split()[0],
                    'affected_rows': cursor.rowcount
                }
                
            else:
                # For DDL or other queries
                result = {
                    'success': True,
                    'query_type': 'DDL',
                    'message': 'Query executed successfully'
                }
            
            cursor.close()
            connection.close()
            
            return result
            
        except cx_Oracle.Error as e:
            error_obj, = e.args
            return {
                'success': False,
                'error': f'Oracle Error {error_obj.code}: {error_obj.message}',
                'query': query
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def get_table_schema(self, connection_config: Dict[str, Any], 
                        table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """Get table schema information"""
        try:
            if schema:
                query = """
                    SELECT column_name, data_type, nullable, data_default
                    FROM all_tab_columns
                    WHERE table_name = :table_name AND owner = :schema
                    ORDER BY column_id
                """
                parameters = {'table_name': table_name.upper(), 'schema': schema.upper()}
            else:
                query = """
                    SELECT column_name, data_type, nullable, data_default
                    FROM user_tab_columns
                    WHERE table_name = :table_name
                    ORDER BY column_id
                """
                parameters = {'table_name': table_name.upper()}
            
            result = self.execute_query(connection_config, query, parameters)
            
            if result['success']:
                return {
                    'success': True,
                    'table_name': table_name,
                    'schema': schema,
                    'columns': result['data']
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_database_tables(self, connection_config: Dict[str, Any], 
                           schema: Optional[str] = None) -> Dict[str, Any]:
        """Get list of tables in database"""
        try:
            if schema:
                query = """
                    SELECT table_name, owner
                    FROM all_tables
                    WHERE owner = :schema
                    ORDER BY table_name
                """
                parameters = {'schema': schema.upper()}
            else:
                query = """
                    SELECT table_name
                    FROM user_tables
                    ORDER BY table_name
                """
                parameters = None
            
            result = self.execute_query(connection_config, query, parameters)
            
            if result['success']:
                return {
                    'success': True,
                    'schema': schema,
                    'tables': result['data']
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def demo_oracle_connection():
    """Demo function for Oracle database connection"""
    client = OracleClient()
    
    # Demo connection config (you would get this from database)
    demo_config = {
        'host': 'localhost',
        'port': 1521,
        'service_name': 'XE',
        'username': 'demo_user',
        'password': client.encrypt_password('demo_password')
    }
    
    # Test connection
    test_result = client.test_connection(demo_config)
    
    if test_result['success']:
        # Execute demo query
        query_result = client.execute_query(
            demo_config, 
            "SELECT sysdate as current_date, user as current_user FROM dual"
        )
        return {
            'connection_test': test_result,
            'query_result': query_result
        }
    else:
        return {
            'connection_test': test_result,
            'query_result': None
        }