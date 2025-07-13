#!/usr/bin/env python3
"""
TESTS CRUD COMPLETOS PARA LANET HELPDESK V3 API
Pruebas de seguridad y funcionalidad
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = 'http://localhost:5001/api'

class APITester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Registra resultado de test"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def test_login(self):
        """Test de autenticación con múltiples usuarios"""
        print("\n🔐 TESTING AUTENTICACIÓN")
        print("=" * 50)
        
        users_to_test = [
            {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!', 'role': 'superadmin'},
            {'email': 'tech@test.com', 'password': 'TestTech123!', 'role': 'technician'},
            {'email': 'prueba@prueba.com', 'password': 'Poikl55+*', 'role': 'client_admin'},
            {'email': 'prueba3@prueba.com', 'password': 'Poikl55+*', 'role': 'solicitante'}
        ]
        
        for user in users_to_test:
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json={
                    'email': user['email'], 
                    'password': user['password']
                })
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and 'data' in result and 'access_token' in result['data']:
                        self.tokens[user['role']] = result['data']['access_token']
                        self.log_test(f"Login {user['role']}", True, f"Token obtenido para {user['email']}")
                    else:
                        self.log_test(f"Login {user['role']}", False, "No access_token en respuesta")
                else:
                    self.log_test(f"Login {user['role']}", False, f"Status {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Login {user['role']}", False, f"Error: {e}")
    
    def test_users_crud(self):
        """Test CRUD completo de usuarios"""
        print("\n👥 TESTING USUARIOS CRUD")
        print("=" * 50)
        
        if 'superadmin' not in self.tokens:
            self.log_test("Users CRUD", False, "No hay token de superadmin")
            return
            
        headers = {'Authorization': f'Bearer {self.tokens["superadmin"]}'}
        
        # GET - Listar usuarios
        try:
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_test("GET Users", True, f"Obtenidos {len(users.get('users', []))} usuarios")
            else:
                self.log_test("GET Users", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("GET Users", False, f"Error: {e}")
            
        # POST - Crear usuario de prueba
        test_user_data = {
            "name": "Usuario Test API",
            "email": "test_api@test.com",
            "password": "test123",
            "role": "technician",
            "is_active": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/users", json=test_user_data, headers=headers)
            if response.status_code == 201:
                created_user = response.json()
                # Buscar user_id en diferentes ubicaciones de la respuesta
                user_id = None
                if 'data' in created_user and 'user_id' in created_user['data']:
                    user_id = created_user['data']['user_id']
                elif 'user_id' in created_user:
                    user_id = created_user['user_id']
                elif 'data' in created_user and 'id' in created_user['data']:
                    user_id = created_user['data']['id']
                elif 'id' in created_user:
                    user_id = created_user['id']

                self.log_test("POST User", True, f"Usuario creado con ID: {user_id}")

                if user_id:
                    # PUT - Actualizar usuario
                    update_data = {"name": "Usuario Test API Actualizado"}
                    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data, headers=headers)
                    if response.status_code == 200:
                        self.log_test("PUT User", True, "Usuario actualizado correctamente")
                    else:
                        self.log_test("PUT User", False, f"Status {response.status_code}: {response.text}")

                    # DELETE - Eliminar usuario
                    response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
                    if response.status_code == 200:
                        self.log_test("DELETE User", True, "Usuario eliminado correctamente")
                    else:
                        self.log_test("DELETE User", False, f"Status {response.status_code}: {response.text}")
                else:
                    self.log_test("PUT User", False, "No se pudo obtener user_id para actualizar")
                    self.log_test("DELETE User", False, "No se pudo obtener user_id para eliminar")

            else:
                self.log_test("POST User", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST User", False, f"Error: {e}")
    
    def test_clients_crud(self):
        """Test CRUD completo de clientes"""
        print("\n🏢 TESTING CLIENTES CRUD")
        print("=" * 50)

        if 'superadmin' not in self.tokens:
            self.log_test("Clients CRUD", False, "No hay token de superadmin")
            return

        headers = {'Authorization': f'Bearer {self.tokens["superadmin"]}'}

        # GET - Listar clientes
        try:
            response = requests.get(f"{BASE_URL}/clients", headers=headers)
            if response.status_code == 200:
                clients = response.json()
                clients_data = clients.get('clients', clients.get('data', []))
                self.log_test("GET Clients", True, f"Obtenidos {len(clients_data)} clientes")
            else:
                self.log_test("GET Clients", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("GET Clients", False, f"Error: {e}")

        # POST - Crear cliente de prueba
        test_client_data = {
            "name": "Cliente Test API",
            "email": "cliente_test@api.com",
            "phone": "5555551234",
            "address": "Dirección Test API"
        }

        try:
            response = requests.post(f"{BASE_URL}/clients", json=test_client_data, headers=headers)
            if response.status_code == 201:
                created_client = response.json()
                # Buscar client_id en la respuesta
                client_id = None
                if 'data' in created_client and 'client_id' in created_client['data']:
                    client_id = created_client['data']['client_id']
                elif 'client_id' in created_client:
                    client_id = created_client['client_id']

                self.log_test("POST Client", True, f"Cliente creado con ID: {client_id}")

                if client_id:
                    # PUT - Actualizar cliente
                    update_data = {"name": "Cliente Test API Actualizado"}
                    response = requests.put(f"{BASE_URL}/clients/{client_id}", json=update_data, headers=headers)
                    if response.status_code == 200:
                        self.log_test("PUT Client", True, "Cliente actualizado correctamente")
                    else:
                        self.log_test("PUT Client", False, f"Status {response.status_code}")

                    # DELETE - Eliminar cliente
                    response = requests.delete(f"{BASE_URL}/clients/{client_id}", headers=headers)
                    if response.status_code == 200:
                        self.log_test("DELETE Client", True, "Cliente eliminado correctamente")
                    else:
                        self.log_test("DELETE Client", False, f"Status {response.status_code}")
                else:
                    self.log_test("PUT Client", False, "No se pudo obtener client_id")
                    self.log_test("DELETE Client", False, "No se pudo obtener client_id")

            else:
                self.log_test("POST Client", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST Client", False, f"Error: {e}")
    
    def test_tickets_crud(self):
        """Test CRUD completo de tickets"""
        print("\n🎫 TESTING TICKETS CRUD")
        print("=" * 50)

        if 'superadmin' not in self.tokens:
            self.log_test("Tickets CRUD", False, "No hay token de superadmin")
            return

        headers = {'Authorization': f'Bearer {self.tokens["superadmin"]}'}

        # GET - Listar tickets
        try:
            response = requests.get(f"{BASE_URL}/tickets", headers=headers)
            if response.status_code == 200:
                tickets = response.json()
                tickets_data = tickets.get('tickets', tickets.get('data', []))
                self.log_test("GET Tickets", True, f"Obtenidos {len(tickets_data)} tickets")
            else:
                self.log_test("GET Tickets", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("GET Tickets", False, f"Error: {e}")

        # Obtener un cliente y sitio para crear ticket
        try:
            clients_response = requests.get(f"{BASE_URL}/clients", headers=headers)
            if clients_response.status_code == 200:
                clients = clients_response.json()
                clients_data = clients.get('clients', clients.get('data', []))

                if clients_data:
                    client_id = clients_data[0].get('client_id')

                    # Obtener sitios del cliente
                    sites_response = requests.get(f"{BASE_URL}/clients/{client_id}/sites", headers=headers)
                    if sites_response.status_code == 200:
                        sites = sites_response.json()
                        sites_data = sites.get('sites', sites.get('data', []))

                        if sites_data:
                            site_id = sites_data[0].get('site_id')

                            # POST - Crear ticket de prueba
                            test_ticket_data = {
                                "subject": "Ticket Test API",
                                "description": "Descripción del ticket de prueba desde API",
                                "priority": "media",
                                "client_id": client_id,
                                "site_id": site_id,
                                "category": "technical",
                                "affected_person": "Usuario Test API",
                                "contact_email": "test@api.com",
                                "contact_phone": "5555551234"
                            }

                            response = requests.post(f"{BASE_URL}/tickets", json=test_ticket_data, headers=headers)
                            if response.status_code == 201:
                                created_ticket = response.json()
                                ticket_id = None
                                if 'data' in created_ticket and 'ticket_id' in created_ticket['data']:
                                    ticket_id = created_ticket['data']['ticket_id']
                                elif 'ticket_id' in created_ticket:
                                    ticket_id = created_ticket['ticket_id']

                                self.log_test("POST Ticket", True, f"Ticket creado con ID: {ticket_id}")

                                if ticket_id:
                                    # PUT - Actualizar ticket
                                    update_data = {"status": "in_progress", "priority": "high"}
                                    response = requests.put(f"{BASE_URL}/tickets/{ticket_id}", json=update_data, headers=headers)
                                    if response.status_code == 200:
                                        self.log_test("PUT Ticket", True, "Ticket actualizado correctamente")
                                    else:
                                        self.log_test("PUT Ticket", False, f"Status {response.status_code}")
                                else:
                                    self.log_test("PUT Ticket", False, "No se pudo obtener ticket_id")
                            else:
                                self.log_test("POST Ticket", False, f"Status {response.status_code}: {response.text}")
                        else:
                            self.log_test("POST Ticket", False, "No hay sitios disponibles para crear ticket")
                    else:
                        self.log_test("POST Ticket", False, f"Error obteniendo sitios: {sites_response.status_code}")
                else:
                    self.log_test("POST Ticket", False, "No hay clientes disponibles para crear ticket")
            else:
                self.log_test("POST Ticket", False, f"Error obteniendo clientes: {clients_response.status_code}")
        except Exception as e:
            self.log_test("POST Ticket", False, f"Error: {e}")
    
    def test_security(self):
        """Tests de seguridad"""
        print("\n🔒 TESTING SEGURIDAD")
        print("=" * 50)
        
        # Test sin token
        try:
            response = requests.get(f"{BASE_URL}/users")
            if response.status_code == 401:
                self.log_test("Security No Token", True, "Acceso denegado sin token")
            else:
                self.log_test("Security No Token", False, f"Acceso permitido sin token: {response.status_code}")
        except Exception as e:
            self.log_test("Security No Token", False, f"Error: {e}")
            
        # Test con token inválido
        try:
            headers = {'Authorization': 'Bearer token_invalido'}
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            if response.status_code == 401:
                self.log_test("Security Invalid Token", True, "Acceso denegado con token inválido")
            else:
                self.log_test("Security Invalid Token", False, f"Acceso permitido con token inválido: {response.status_code}")
        except Exception as e:
            self.log_test("Security Invalid Token", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("🧪 INICIANDO TESTS CRUD COMPLETOS DE LA API")
        print("=" * 60)
        
        self.test_login()
        self.test_security()
        self.test_users_crud()
        self.test_clients_crud()
        self.test_tickets_crud()
        
        # Resumen final
        print("\n📊 RESUMEN DE TESTS")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - successful_tests
        
        print(f"Total tests: {total_tests}")
        print(f"✅ Exitosos: {successful_tests}")
        print(f"❌ Fallidos: {failed_tests}")
        print(f"📈 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTS FALLIDOS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  - {test['test']}: {test['details']}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
