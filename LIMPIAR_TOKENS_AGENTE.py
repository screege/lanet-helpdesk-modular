#!/usr/bin/env python3
"""
Script para limpiar tokens de agente de la base de datos
Útil para resetear tokens sin afectar otros datos
"""

import psycopg2
import sys
from datetime import datetime

def conectar_base_datos():
    """Conectar a la base de datos"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk", 
            user="postgres",
            password="Poikl55+*"
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def mostrar_tokens_existentes(cur):
    """Mostrar tokens existentes en la base de datos"""
    try:
        # Verificar si la tabla agent_tokens existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'agent_tokens'
            )
        """)
        
        if not cur.fetchone()[0]:
            print("ℹ️ La tabla 'agent_tokens' no existe en la base de datos")
            return []
        
        # Obtener tokens existentes
        cur.execute("""
            SELECT token, client_name, site_name, is_active, created_at, used_at
            FROM agent_tokens 
            ORDER BY created_at DESC
        """)
        
        tokens = cur.fetchall()
        
        if tokens:
            print(f"📋 Tokens encontrados: {len(tokens)}")
            print("-" * 80)
            for i, (token, client, site, active, created, used) in enumerate(tokens, 1):
                status = "✅ Activo" if active else "❌ Inactivo"
                used_str = used.strftime('%Y-%m-%d %H:%M') if used else "Nunca usado"
                created_str = created.strftime('%Y-%m-%d %H:%M') if created else "N/A"
                
                print(f"{i:2d}. {token}")
                print(f"    Cliente: {client or 'N/A'}")
                print(f"    Sitio: {site or 'N/A'}")
                print(f"    Estado: {status}")
                print(f"    Creado: {created_str}")
                print(f"    Usado: {used_str}")
                print()
        else:
            print("ℹ️ No hay tokens en la base de datos")
        
        return tokens
        
    except Exception as e:
        print(f"❌ Error consultando tokens: {e}")
        return []

def limpiar_todos_tokens(cur, conn):
    """Eliminar todos los tokens de agente"""
    try:
        # Contar tokens antes de eliminar
        cur.execute("SELECT COUNT(*) FROM agent_tokens")
        total_tokens = cur.fetchone()[0]
        
        if total_tokens == 0:
            print("ℹ️ No hay tokens para eliminar")
            return True
        
        print(f"🗑️ Eliminando {total_tokens} tokens...")
        
        # Eliminar todos los tokens
        cur.execute("DELETE FROM agent_tokens")
        deleted_count = cur.rowcount
        
        # Confirmar cambios
        conn.commit()
        
        print(f"✅ Eliminados {deleted_count} tokens exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error eliminando tokens: {e}")
        conn.rollback()
        return False

def limpiar_tokens_especificos(cur, conn, tokens):
    """Eliminar tokens específicos seleccionados por el usuario"""
    try:
        print("\n📋 Selecciona los tokens a eliminar:")
        print("   Formato: 1,3,5 (números separados por comas)")
        print("   O 'all' para eliminar todos")
        print("   O 'cancel' para cancelar")
        
        selection = input("\nSelección: ").strip().lower()
        
        if selection == 'cancel':
            print("❌ Operación cancelada")
            return True
        
        if selection == 'all':
            return limpiar_todos_tokens(cur, conn)
        
        # Parsear selección de números
        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            tokens_to_delete = []
            
            for idx in indices:
                if 1 <= idx <= len(tokens):
                    tokens_to_delete.append(tokens[idx-1][0])  # token string
                else:
                    print(f"⚠️ Índice {idx} fuera de rango, ignorado")
            
            if not tokens_to_delete:
                print("❌ No se seleccionaron tokens válidos")
                return False
            
            # Eliminar tokens seleccionados
            for token in tokens_to_delete:
                cur.execute("DELETE FROM agent_tokens WHERE token = %s", (token,))
                print(f"✅ Token eliminado: {token}")
            
            conn.commit()
            print(f"\n✅ Eliminados {len(tokens_to_delete)} tokens exitosamente")
            return True
            
        except ValueError:
            print("❌ Formato de selección inválido")
            return False
        
    except Exception as e:
        print(f"❌ Error eliminando tokens específicos: {e}")
        conn.rollback()
        return False

def limpiar_historial_uso_tokens(cur, conn):
    """Limpiar historial de uso de tokens"""
    try:
        # Verificar si la tabla existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'agent_token_usage_history'
            )
        """)
        
        if not cur.fetchone()[0]:
            print("ℹ️ La tabla 'agent_token_usage_history' no existe")
            return True
        
        # Contar registros
        cur.execute("SELECT COUNT(*) FROM agent_token_usage_history")
        total_records = cur.fetchone()[0]
        
        if total_records == 0:
            print("ℹ️ No hay historial de uso de tokens")
            return True
        
        print(f"🗑️ Eliminando {total_records} registros de historial de uso...")
        
        # Eliminar historial
        cur.execute("DELETE FROM agent_token_usage_history")
        deleted_count = cur.rowcount
        
        conn.commit()
        print(f"✅ Eliminados {deleted_count} registros de historial")
        return True
        
    except Exception as e:
        print(f"❌ Error limpiando historial: {e}")
        conn.rollback()
        return False

def main():
    """Función principal"""
    print("🧹 LIMPIEZA DE TOKENS DE AGENTE LANET")
    print("=" * 50)
    
    # Conectar a la base de datos
    conn = conectar_base_datos()
    if not conn:
        input("Presiona Enter para salir...")
        return False
    
    cur = conn.cursor()
    
    try:
        # Mostrar tokens existentes
        tokens = mostrar_tokens_existentes(cur)
        
        if not tokens:
            print("\n✅ No hay tokens para limpiar")
            input("Presiona Enter para salir...")
            return True
        
        # Menú de opciones
        print("\n📋 Opciones de limpieza:")
        print("1. Eliminar TODOS los tokens")
        print("2. Eliminar tokens específicos")
        print("3. Limpiar historial de uso de tokens")
        print("4. Limpieza completa (tokens + historial)")
        print("5. Cancelar")
        
        while True:
            try:
                opcion = input("\nSelecciona una opción (1-5): ").strip()
                
                if opcion == '1':
                    # Confirmar eliminación total
                    confirm = input(f"\n⚠️ ¿Eliminar TODOS los {len(tokens)} tokens? (si/no): ").strip().lower()
                    if confirm in ['si', 's', 'yes', 'y']:
                        success = limpiar_todos_tokens(cur, conn)
                    else:
                        print("❌ Operación cancelada")
                        success = True
                    break
                
                elif opcion == '2':
                    success = limpiar_tokens_especificos(cur, conn, tokens)
                    break
                
                elif opcion == '3':
                    success = limpiar_historial_uso_tokens(cur, conn)
                    break
                
                elif opcion == '4':
                    confirm = input(f"\n⚠️ ¿Limpieza completa (tokens + historial)? (si/no): ").strip().lower()
                    if confirm in ['si', 's', 'yes', 'y']:
                        success1 = limpiar_todos_tokens(cur, conn)
                        success2 = limpiar_historial_uso_tokens(cur, conn)
                        success = success1 and success2
                    else:
                        print("❌ Operación cancelada")
                        success = True
                    break
                
                elif opcion == '5':
                    print("❌ Operación cancelada")
                    success = True
                    break
                
                else:
                    print("❌ Opción inválida, intenta de nuevo")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario")
                success = False
                break
        
        # Verificar resultado final
        if success:
            print("\n🎉 Limpieza completada exitosamente!")
            
            # Mostrar estado final
            cur.execute("SELECT COUNT(*) FROM agent_tokens")
            remaining_tokens = cur.fetchone()[0]
            print(f"📊 Tokens restantes: {remaining_tokens}")
        else:
            print("\n❌ Hubo errores durante la limpieza")
        
    except Exception as e:
        print(f"❌ Error durante la operación: {e}")
        success = False
    
    finally:
        cur.close()
        conn.close()
    
    input("\nPresiona Enter para salir...")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
