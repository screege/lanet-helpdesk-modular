#!/usr/bin/env python3
"""
Script para limpiar completamente la base de datos para prueba final
"""
import psycopg2
import sys

def limpiar_base_datos():
    """Limpiar completamente la base de datos"""
    try:
        # Conectar a la base de datos
        print("🔌 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        print("🗑️  Eliminando datos...")
        
        # Eliminar en orden correcto para evitar errores de llaves foráneas
        cursor.execute("DELETE FROM agent_token_usage_history;")
        print("   ✅ agent_token_usage_history eliminada")
        
        cursor.execute("DELETE FROM asset_heartbeats;")
        print("   ✅ asset_heartbeats eliminados")
        
        cursor.execute("DELETE FROM assets;")
        print("   ✅ assets eliminados")
        
        cursor.execute("DELETE FROM agent_installation_tokens;")
        print("   ✅ agent_installation_tokens eliminados")
        
        # Confirmar cambios
        conn.commit()
        
        print("\n🔍 Verificando limpieza...")
        
        # Verificar conteos
        cursor.execute("""
            SELECT 'Assets' as tabla, COUNT(*) as cantidad FROM assets
            UNION ALL
            SELECT 'Tokens' as tabla, COUNT(*) as cantidad FROM agent_installation_tokens
            UNION ALL
            SELECT 'Heartbeats' as tabla, COUNT(*) as cantidad FROM asset_heartbeats
            UNION ALL
            SELECT 'Token Usage' as tabla, COUNT(*) as cantidad FROM agent_token_usage_history
        """)
        
        resultados = cursor.fetchall()
        
        print("\n📊 CONTEOS FINALES:")
        print("=" * 30)
        for tabla, cantidad in resultados:
            print(f"   {tabla}: {cantidad}")
        
        # Verificar que todo esté en 0
        total = sum(cantidad for _, cantidad in resultados)
        
        if total == 0:
            print("\n✅ BASE DE DATOS COMPLETAMENTE LIMPIA")
            print("🚀 Lista para instalación desde cero")
            return True
        else:
            print(f"\n❌ ERROR: Aún quedan {total} registros")
            return False
            
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🔥 LIMPIEZA COMPLETA DE BASE DE DATOS")
    print("=" * 40)
    
    if limpiar_base_datos():
        print("\n🎯 LIMPIEZA EXITOSA")
        print("Ahora puedes proceder con la instalación desde cero")
        sys.exit(0)
    else:
        print("\n❌ LIMPIEZA FALLÓ")
        print("Revisa los errores anteriores")
        sys.exit(1)
