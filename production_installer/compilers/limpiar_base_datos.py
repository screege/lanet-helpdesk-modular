#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPIEZA COMPLETA DE BASE DE DATOS - LANET HELPDESK
Elimina TODOS los assets y tokens para empezar desde cero

UBICACIÓN: C:\lanet-helpdesk-v3\production_installer\compilers\limpiar_base_datos.py

USO:
    cd C:\lanet-helpdesk-v3\production_installer\compilers
    python limpiar_base_datos.py

ADVERTENCIA: Este script elimina TODOS los datos de agentes y tokens
"""

import psycopg2
from datetime import datetime

class LimpiadorBaseDatos:
    """Limpiador profesional de base de datos LANET"""
    
    def __init__(self):
        self.connection_string = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
        self.conn = None
        self.cur = None
    
    def conectar(self):
        """Conectar a la base de datos"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cur = self.conn.cursor()
            print("✅ Conexión a base de datos establecida")
            return True
        except Exception as e:
            print(f"❌ Error conectando a base de datos: {e}")
            return False
    
    def mostrar_estado_actual(self):
        """Mostrar el estado actual de la base de datos"""
        print("\n📊 ESTADO ACTUAL DE LA BASE DE DATOS")
        print("=" * 50)
        
        try:
            # Contar assets de agente
            self.cur.execute("""
            SELECT COUNT(*) 
            FROM assets 
            WHERE status = 'active' AND name LIKE '%Agent%'
            """)
            assets_count = self.cur.fetchone()[0]
            
            # Contar tokens
            self.cur.execute("SELECT COUNT(*) FROM agent_installation_tokens")
            tokens_count = self.cur.fetchone()[0]
            
            # Contar historial de tokens
            self.cur.execute("SELECT COUNT(*) FROM agent_token_usage_history")
            history_count = self.cur.fetchone()[0]
            
            print(f"📋 Assets de agente: {assets_count}")
            print(f"🎫 Tokens de instalación: {tokens_count}")
            print(f"📝 Historial de tokens: {history_count}")
            
            if assets_count > 0:
                print("\n📋 Assets de agente encontrados:")
                self.cur.execute("""
                SELECT name, asset_id, created_at, last_seen
                FROM assets 
                WHERE status = 'active' AND name LIKE '%Agent%'
                ORDER BY created_at DESC
                """)
                
                assets = self.cur.fetchall()
                for name, asset_id, created_at, last_seen in assets:
                    print(f"   - {name}: {asset_id} (creado: {created_at})")
            
            if tokens_count > 0:
                print("\n🎫 Tokens encontrados:")
                self.cur.execute("""
                SELECT 
                    t.token_value,
                    c.name as client_name,
                    s.name as site_name,
                    t.is_active,
                    t.usage_count
                FROM agent_installation_tokens t
                JOIN clients c ON t.client_id = c.client_id
                JOIN sites s ON t.site_id = s.site_id
                ORDER BY t.created_at DESC
                """)
                
                tokens = self.cur.fetchall()
                for token_value, client_name, site_name, is_active, usage_count in tokens:
                    status = "✅ Activo" if is_active else "❌ Inactivo"
                    print(f"   - {token_value} ({client_name} - {site_name}) {status} - Usado {usage_count} veces")
            
            return assets_count, tokens_count, history_count
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
            return 0, 0, 0
    
    def limpiar_assets(self):
        """Limpiar todos los assets de agente"""
        print("\n🗑️  LIMPIANDO ASSETS DE AGENTE")
        print("=" * 40)
        
        try:
            # Obtener assets a eliminar
            self.cur.execute("""
            SELECT asset_id, name 
            FROM assets 
            WHERE status = 'active' AND name LIKE '%Agent%'
            """)
            
            assets_to_delete = self.cur.fetchall()
            
            if not assets_to_delete:
                print("   ℹ️  No hay assets de agente para eliminar")
                return True
            
            print(f"   📊 Assets a eliminar: {len(assets_to_delete)}")
            
            # Limpiar referencias en tablas relacionadas
            for asset_id, name in assets_to_delete:
                print(f"   🔄 Procesando: {name} ({asset_id})")
                
                # Limpiar referencias
                self.cur.execute('UPDATE agent_token_usage_history SET asset_id = NULL WHERE asset_id = %s', (asset_id,))
                self.cur.execute('UPDATE tickets SET asset_id = NULL WHERE asset_id = %s', (asset_id,))
                
                # Eliminar asset
                self.cur.execute('DELETE FROM assets WHERE asset_id = %s', (asset_id,))
                print(f"   ✅ Eliminado: {name}")
            
            print(f"   ✅ {len(assets_to_delete)} assets eliminados exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error eliminando assets: {e}")
            return False
    
    def limpiar_tokens(self):
        """Limpiar todos los tokens de instalación"""
        print("\n🎫 LIMPIANDO TOKENS DE INSTALACIÓN")
        print("=" * 40)
        
        try:
            # Eliminar historial de uso de tokens
            self.cur.execute('DELETE FROM agent_token_usage_history')
            history_deleted = self.cur.rowcount
            print(f"   ✅ Historial eliminado: {history_deleted} entradas")
            
            # Eliminar tokens
            self.cur.execute('DELETE FROM agent_installation_tokens')
            tokens_deleted = self.cur.rowcount
            print(f"   ✅ Tokens eliminados: {tokens_deleted} tokens")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error eliminando tokens: {e}")
            return False
    
    def verificar_limpieza(self):
        """Verificar que la limpieza fue exitosa"""
        print("\n✅ VERIFICANDO LIMPIEZA")
        print("=" * 30)
        
        try:
            # Verificar assets
            self.cur.execute("SELECT COUNT(*) FROM assets WHERE status = 'active' AND name LIKE '%Agent%'")
            remaining_assets = self.cur.fetchone()[0]
            
            # Verificar tokens
            self.cur.execute("SELECT COUNT(*) FROM agent_installation_tokens")
            remaining_tokens = self.cur.fetchone()[0]
            
            # Verificar historial
            self.cur.execute("SELECT COUNT(*) FROM agent_token_usage_history")
            remaining_history = self.cur.fetchone()[0]
            
            print(f"   Assets restantes: {remaining_assets}")
            print(f"   Tokens restantes: {remaining_tokens}")
            print(f"   Historial restante: {remaining_history}")
            
            if remaining_assets == 0 and remaining_tokens == 0 and remaining_history == 0:
                print("   ✅ LIMPIEZA COMPLETA EXITOSA")
                return True
            else:
                print("   ⚠️  LIMPIEZA INCOMPLETA")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verificando limpieza: {e}")
            return False
    
    def limpiar_todo(self):
        """Proceso completo de limpieza"""
        print("🧹 LIMPIEZA COMPLETA DE BASE DE DATOS - LANET HELPDESK")
        print("=" * 70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Conectar
        if not self.conectar():
            return False
        
        try:
            # Mostrar estado actual
            assets_count, tokens_count, history_count = self.mostrar_estado_actual()
            
            if assets_count == 0 and tokens_count == 0:
                print("\n✅ BASE DE DATOS YA ESTÁ LIMPIA")
                print("   No hay assets ni tokens para eliminar")
                return True
            
            # Confirmar limpieza
            print(f"\n⚠️  ADVERTENCIA: Se eliminarán:")
            print(f"   - {assets_count} assets de agente")
            print(f"   - {tokens_count} tokens de instalación")
            print(f"   - {history_count} entradas de historial")
            print()
            
            confirm = input("¿Continuar con la limpieza COMPLETA? (escribe 'CONFIRMAR'): ").strip()
            if confirm != 'CONFIRMAR':
                print("❌ Limpieza cancelada")
                return False
            
            # Limpiar assets
            if not self.limpiar_assets():
                return False
            
            # Limpiar tokens
            if not self.limpiar_tokens():
                return False
            
            # Confirmar cambios
            self.conn.commit()
            print("\n💾 Cambios confirmados en la base de datos")
            
            # Verificar limpieza
            if self.verificar_limpieza():
                print("\n" + "=" * 70)
                print("✅ LIMPIEZA COMPLETA EXITOSA")
                print("🎯 BASE DE DATOS LISTA PARA PRUEBA DESDE CERO")
                print()
                print("📋 Próximos pasos:")
                print("   1. Limpiar agente del equipo")
                print("   2. Generar nuevo token manualmente")
                print("   3. Instalar agente desde cero")
                print("   4. Probar múltiples reinicios")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR DURANTE LA LIMPIEZA: {e}")
            self.conn.rollback()
            return False
        
        finally:
            if self.conn:
                self.conn.close()
                print("🔌 Conexión cerrada")
    
    def cerrar(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()

def main():
    """Función principal"""
    limpiador = LimpiadorBaseDatos()
    
    try:
        success = limpiador.limpiar_todo()
        
        if not success:
            print("\n❌ LIMPIEZA FALLIDA")
            print("🔧 Revisar errores anteriores")
            
    except KeyboardInterrupt:
        print("\n⚠️  Limpieza cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
    finally:
        limpiador.cerrar()
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
