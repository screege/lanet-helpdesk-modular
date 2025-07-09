#!/usr/bin/env python3
"""
Verificar contraseñas de usuarios de prueba
"""

import bcrypt
import psycopg2

def verify_passwords():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )

        cur = conn.cursor()

        # Obtener usuarios de prueba
        cur.execute("""
        SELECT email, password_hash, role, is_active
        FROM users 
        WHERE email IN ('ba@lanet.mx', 'tech@test.com', 'prueba@prueba.com', 'prueba3@prueba.com') 
        ORDER BY email
        """)

        users = cur.fetchall()

        # Contraseñas correctas del login page
        passwords = {
            'ba@lanet.mx': 'TestAdmin123!',
            'tech@test.com': 'TestTech123!',
            'prueba@prueba.com': 'Poikl55+*',
            'prueba3@prueba.com': 'Poikl55+*'
        }

        print('🔐 VERIFICANDO CONTRASEÑAS CON BCRYPT')
        print('=' * 60)

        all_valid = True

        for email, password_hash, role, is_active in users:
            correct_password = passwords.get(email)
            active_status = "✅ Activo" if is_active else "❌ Inactivo"
            
            if correct_password:
                try:
                    is_valid = bcrypt.checkpw(
                        correct_password.encode('utf-8'), 
                        password_hash.encode('utf-8')
                    )
                    status = '✅ VÁLIDA' if is_valid else '❌ INVÁLIDA'
                    print(f'{email:20} ({role:12}) - Password: {status} - Estado: {active_status}')
                    
                    if not is_valid or not is_active:
                        all_valid = False
                        
                except Exception as e:
                    print(f'{email:20} ({role:12}) - Password: ❌ ERROR - {e}')
                    all_valid = False
            else:
                print(f'{email:20} ({role:12}) - Password: ❌ NO HAY CONTRASEÑA DE PRUEBA')
                all_valid = False

        print('\n' + '=' * 60)
        if all_valid:
            print('✅ TODAS LAS CONTRASEÑAS SON VÁLIDAS Y USUARIOS ACTIVOS')
        else:
            print('❌ HAY PROBLEMAS CON LAS CONTRASEÑAS O ESTADOS DE USUARIOS')
            print('\n🔧 CORRIGIENDO PROBLEMAS...')
            
            # Corregir contraseñas
            for email, password in passwords.items():
                try:
                    # Generar nuevo hash
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    
                    # Actualizar en la base de datos
                    cur.execute("""
                    UPDATE users 
                    SET password_hash = %s, is_active = true 
                    WHERE email = %s
                    """, (hashed.decode('utf-8'), email))
                    
                    print(f'✅ Contraseña actualizada para {email}')
                    
                except Exception as e:
                    print(f'❌ Error actualizando {email}: {e}')
            
            conn.commit()
            print('\n✅ CORRECCIONES APLICADAS')

        conn.close()

    except Exception as e:
        print(f'❌ Error de conexión: {e}')

if __name__ == "__main__":
    verify_passwords()
