#!/usr/bin/env python3
"""
Script para eliminar TODOS los assets de la base de datos
"""

import psycopg2
import sys

def eliminar_todos_assets():
    """Eliminar TODOS los assets de la base de datos"""
    try:
        print("🗄️ Conectando a la base de datos...")
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Contar assets actuales
        cur.execute("SELECT COUNT(*) FROM assets")
        total_assets = cur.fetchone()[0]
        
        print(f"📊 Assets encontrados: {total_assets}")
        
        if total_assets == 0:
            print("✅ No hay assets para eliminar")
            return True
        
        # Mostrar algunos ejemplos
        cur.execute("SELECT asset_id FROM assets LIMIT 3")
        sample_assets = cur.fetchall()
        print("📋 Ejemplos de assets:")
        for asset in sample_assets:
            print(f"   - {asset[0]}")
        
        # Confirmar eliminación
        print(f"\n⚠️ ADVERTENCIA: Se eliminarán {total_assets} assets y TODOS sus datos relacionados")
        response = input("¿Continuar? (si/no): ").strip().lower()
        
        if response not in ['si', 's', 'yes', 'y']:
            print("❌ Operación cancelada")
            return False
        
        print("\n🗑️ Eliminando todos los assets...")
        
        # Eliminar en orden correcto para evitar errores de foreign key
        tables_to_clean = [
            'agent_token_usage_history',
            'asset_software',
            'asset_hardware', 
            'asset_network',
            'asset_bitlocker',
            'asset_heartbeats',
            'assets'
        ]
        
        total_deleted = 0
        for table in tables_to_clean:
            try:
                cur.execute(f"DELETE FROM {table}")
                deleted = cur.rowcount
                total_deleted += deleted
                if deleted > 0:
                    print(f"   ✅ {table}: {deleted} registros eliminados")
                else:
                    print(f"   ℹ️ {table}: ya estaba vacía")
            except psycopg2.Error as e:
                if "no existe la relación" in str(e):
                    print(f"   ℹ️ {table}: tabla no existe (normal)")
                else:
                    print(f"   ⚠️ {table}: error - {e}")
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar que se eliminaron
        cur.execute("SELECT COUNT(*) FROM assets")
        remaining_assets = cur.fetchone()[0]
        
        print(f"\n📊 Resultado:")
        print(f"   - Registros eliminados: {total_deleted}")
        print(f"   - Assets restantes: {remaining_assets}")
        
        if remaining_assets == 0:
            print("✅ TODOS los assets eliminados exitosamente")
            print("✅ Base de datos lista para pruebas desde cero")
        else:
            print("⚠️ Algunos assets no se pudieron eliminar")
        
        cur.close()
        conn.close()
        
        return remaining_assets == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧹 ELIMINACIÓN COMPLETA DE ASSETS")
    print("=" * 40)
    
    success = eliminar_todos_assets()
    
    if success:
        print("\n🎉 Limpieza completada exitosamente!")
        print("📋 Ahora puedes:")
        print("   1. Ejecutar el nuevo instalador")
        print("   2. Probar el registro desde cero")
        print("   3. Verificar que aparece como nuevo asset")
    else:
        print("\n❌ Hubo problemas en la limpieza")
    
    input("\nPresiona Enter para salir...")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
