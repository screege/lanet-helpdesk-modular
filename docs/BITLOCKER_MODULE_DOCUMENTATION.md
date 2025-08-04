# 🔐 BitLocker Module Documentation - LANET Helpdesk V3

## 📋 **Overview**

El módulo BitLocker proporciona gestión completa de claves de recuperación BitLocker para activos Windows en el sistema MSP. Incluye recolección automática de datos, almacenamiento seguro de claves, y acceso controlado por roles.

**Estado:** ✅ **COMPLETAMENTE IMPLEMENTADO Y FUNCIONAL**  
**Fecha de Implementación:** 25 de Enero 2025  
**Versión:** 1.0.0

---

## 🏗️ **Arquitectura del Módulo**

### **Componentes Principales:**

1. **🗄️ Backend API** (`backend/modules/bitlocker/`)
2. **🔧 Agente Collector** (`lanet_agent/modules/bitlocker.py`)
3. **🎨 Frontend Component** (`frontend/src/components/assets/BitLockerTab.tsx`)
4. **🔒 Database Schema** (`bitlocker_keys` table)

---

## 🗄️ **Backend Implementation**

### **Database Schema**

```sql
-- Tabla: bitlocker_keys
CREATE TABLE bitlocker_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    volume_letter VARCHAR(10) NOT NULL, -- C:, D:, etc.
    volume_label VARCHAR(255),
    protection_status VARCHAR(50) NOT NULL, -- 'Protected', 'Unprotected', 'Unknown'
    encryption_method VARCHAR(50), -- 'AES-128', 'AES-256', etc.
    key_protector_type VARCHAR(100), -- 'TPM', 'TPM+PIN', 'Password', etc.
    recovery_key_id VARCHAR(100),
    recovery_key_encrypted TEXT, -- Encrypted recovery key
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_verified_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(asset_id, volume_letter)
);
```

### **API Endpoints**

#### **GET /api/bitlocker/<asset_id>**
- **Descripción:** Obtiene información BitLocker para un asset
- **Autenticación:** JWT requerido
- **Permisos:** Todos los roles autenticados (con restricciones de datos)
- **Respuesta:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_volumes": 2,
      "protected_volumes": 1,
      "unprotected_volumes": 1,
      "protection_percentage": 50.0
    },
    "volumes": [
      {
        "id": "uuid",
        "volume_letter": "C:",
        "volume_label": "Windows",
        "protection_status": "Protected",
        "encryption_method": "AES-256",
        "key_protector_type": "TPM + PIN",
        "recovery_key": "123456-789012-345678-901234-567890-123456-789012-345678" // Solo para superadmin/technician
      }
    ]
  }
}
```

#### **POST /api/bitlocker/<asset_id>/update**
- **Descripción:** Actualiza información BitLocker desde agente
- **Autenticación:** JWT requerido
- **Permisos:** Solo superadmin y technician
- **Payload:**
```json
{
  "volumes": [
    {
      "volume_letter": "C:",
      "volume_label": "Windows",
      "protection_status": "Protected",
      "encryption_method": "AES-256",
      "key_protector_type": "TPM",
      "recovery_key_id": "key-id",
      "recovery_key": "recovery-key-string"
    }
  ]
}
```

### **Security Features**

1. **🔒 Encryption:** Claves de recuperación encriptadas con Fernet
2. **🛡️ Access Control:** Control de acceso por roles
3. **📝 Audit Trail:** Timestamps de creación, actualización y verificación
4. **🔐 Data Isolation:** Acceso restringido por organización/sitio

---

## 🔧 **Agent Implementation**

### **BitLockerCollector Class**

**Archivo:** `lanet_agent/modules/bitlocker.py`

#### **Métodos Principales:**

```python
class BitLockerCollector:
    def get_bitlocker_info(self) -> Dict
    def _get_bitlocker_volumes(self) -> List[Dict]
    def _process_volume_data(self, volume_data: Dict) -> Optional[Dict]
    def is_bitlocker_available(self) -> bool
```

#### **PowerShell Command Used:**
```powershell
Get-BitLockerVolume | ForEach-Object {
    $volume = $_
    $keyProtectors = $volume.KeyProtector
    $recoveryKey = $keyProtectors | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' } | Select-Object -First 1
    
    [PSCustomObject]@{
        MountPoint = $volume.MountPoint
        VolumeLabel = if ($volume.VolumeLabel) { $volume.VolumeLabel } else { "Local Disk" }
        ProtectionStatus = $volume.ProtectionStatus.ToString()
        EncryptionMethod = $volume.EncryptionMethod.ToString()
        RecoveryPassword = if ($recoveryKey) { $recoveryKey.RecoveryPassword } else { $null }
        # ... más campos
    }
} | ConvertTo-Json -Depth 3
```

### **Integration with Monitoring**

BitLocker data is collected during **TIER 2 heartbeats** (every 2-3 days) and included in the hardware inventory:

```python
# En monitoring.py
def get_bitlocker_info(self) -> Dict[str, Any]:
    if not self.bitlocker_collector:
        return {'supported': False, 'reason': 'BitLocker collector not available', 'volumes': []}
    
    return self.bitlocker_collector.get_bitlocker_info()

# En heartbeat.py  
hardware_inventory['bitlocker'] = self.monitoring.get_bitlocker_info()
```

---

## 🎨 **Frontend Implementation**

### **BitLockerTab Component**

**Archivo:** `frontend/src/components/assets/BitLockerTab.tsx`

#### **Props Interface:**
```typescript
interface BitLockerTabProps {
  assetId: string;
  userRole: string;
}
```

#### **Key Features:**

1. **📊 Summary Dashboard:**
   - Total volumes
   - Protected/Unprotected counts
   - Protection percentage
   - Refresh button

2. **💿 Volume Details:**
   - Volume letter and label
   - Protection status with color coding
   - Encryption method
   - Key protector type
   - Recovery key (with show/hide toggle)

3. **🔒 Role-Based Access:**
   - **Superadmin/Technician:** Full access including recovery keys
   - **Client Admin:** Status only (no recovery keys)
   - **Solicitante:** No access to BitLocker tab

#### **Integration:**
```typescript
// En AssetDetailModal.tsx
const canViewBitLocker = hasRole(['superadmin', 'technician', 'client_admin']);

// Tab definition
{ id: 'bitlocker', name: 'BitLocker', icon: Shield }

// Tab content
{activeTab === 'bitlocker' && canViewBitLocker && (
  <BitLockerTab assetId={asset.asset_id} userRole={user?.role || ''} />
)}
```

---

## 🔒 **Security & Access Control**

### **Role-Based Permissions:**

| Role | View Tab | View Status | View Recovery Keys | Update Data |
|------|----------|-------------|-------------------|-------------|
| **Superadmin** | ✅ | ✅ | ✅ | ✅ |
| **Technician** | ✅ | ✅ | ✅ | ✅ |
| **Client Admin** | ✅ | ✅ | ❌ | ❌ |
| **Solicitante** | ❌ | ❌ | ❌ | ❌ |

### **Data Access Restrictions:**

- **Superadmin/Technician:** Access to all assets and recovery keys
- **Client Admin:** Only assets from their organization, no recovery keys
- **Solicitante:** No access to BitLocker functionality

---

## 🚀 **Deployment & Configuration**

### **Database Migration:**

```bash
# Run migration script
python backend/migrations/add_bitlocker_table.sql
```

### **Dependencies:**

#### **Backend:**
```python
# requirements.txt
cryptography>=3.4.8  # For key encryption
```

#### **Frontend:**
```typescript
// Already included in existing dependencies
lucide-react  // For Shield icon
```

### **Environment Variables:**

```bash
# Optional: Custom encryption key (defaults to development key)
BITLOCKER_ENCRYPTION_KEY=your-production-encryption-key
```

---

## 🧪 **Testing**

### **Test Scripts Included:**

1. **`test_bitlocker_collection.py`** - Test agent collection
2. **`test_bitlocker_with_login.py`** - Test API endpoints
3. **`check_assets_table.py`** - Verify database structure

### **Manual Testing:**

1. **Agent Collection:**
```bash
python test_bitlocker_collection.py
```

2. **API Endpoints:**
```bash
python test_bitlocker_with_login.py
```

3. **Frontend Integration:**
   - Login as superadmin/technician
   - Navigate to Assets → Select asset → BitLocker tab
   - Verify data display and access controls

---

## 📝 **Maintenance & Monitoring**

### **Log Locations:**

- **Agent:** `lanet_agent.modules.bitlocker`
- **Backend:** `backend.modules.bitlocker.routes`
- **Frontend:** Browser console for API calls

### **Common Issues:**

1. **PowerShell Execution Policy:** Ensure agent can run PowerShell commands
2. **BitLocker Not Available:** System without BitLocker support
3. **Permission Errors:** Insufficient privileges to read BitLocker data

### **Monitoring:**

- BitLocker data is collected every 2-3 days via TIER 2 heartbeat
- Check agent logs for collection errors
- Monitor API response times for BitLocker endpoints

---

## 🔄 **Future Enhancements**

### **Planned Features:**

1. **📊 BitLocker Reports:** Compliance reporting across all clients
2. **🚨 Alerts:** Notifications for unprotected volumes
3. **📤 Key Export:** Secure export functionality for backup
4. **📋 Policies:** Automated BitLocker policy enforcement
5. **📈 Trends:** Historical protection status tracking

### **Technical Debt:**

- Consider implementing key rotation for encryption
- Add bulk operations for multiple assets
- Implement key escrow functionality

---

## 👥 **Support & Troubleshooting**

### **Common Commands:**

```bash
# Check BitLocker status on Windows
Get-BitLockerVolume

# Test agent collection
python lanet_agent/modules/bitlocker.py

# Verify database schema
\d bitlocker_keys
```

### **Contact:**

For technical support or feature requests related to BitLocker module, refer to the main project documentation and issue tracking system.

---

**📅 Last Updated:** 25 de Enero 2025  
**👤 Implemented By:** Augment Agent  
**🔄 Version:** 1.0.0
