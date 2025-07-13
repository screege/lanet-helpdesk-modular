# Frontend Debugging Checklist - LANET Helpdesk V3

## 🚨 **CUANDO EL FRONTEND NO MUESTRA DATOS**

### **1. VERIFICAR API BACKEND (SIEMPRE PRIMERO)**
```bash
# En terminal
curl -H "Authorization: Bearer [token]" http://localhost:5001/api/[endpoint]
```

### **2. VERIFICAR EN NAVEGADOR**
```javascript
// En consola del navegador
fetch('/api/[endpoint]', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => {
  console.log('API Response:', data);
  console.log('Data count:', data.data ? data.data.length : 0);
});
```

### **3. VERIFICAR TOKEN**
```javascript
// En consola del navegador
console.log('Token:', localStorage.getItem('access_token'));
console.log('User:', JSON.parse(localStorage.getItem('user') || '{}'));
```

---

## 🔧 **PROBLEMAS COMUNES Y SOLUCIONES**

### **1. Dropdown Vacío**
**Causa:** Servicio procesa mal la estructura de datos
**Solución:** Verificar `response.data` vs `response.data.items`

### **2. Error 401 Unauthorized**
**Causa:** Falta `set_rls_context()` en backend
**Solución:** Agregar en endpoint:
```python
current_app.db_manager.set_rls_context(
    user_id=user_id,
    user_role=user_role,
    client_id=user_client_id
)
```

### **3. Promise.all Falla**
**Causa:** Una API falla y rompe todas
**Solución:** Cargar individualmente con try/catch

### **4. CORS Errors**
**Causa:** URL directa en lugar de proxy
**Solución:** Usar `/api/` en lugar de `http://localhost:5001/api/`

---

## 📋 **CHECKLIST DE VERIFICACIÓN**

- [ ] API backend responde correctamente
- [ ] Token existe y es válido
- [ ] Estructura de datos es la esperada
- [ ] Servicio procesa respuesta correctamente
- [ ] Componente renderiza datos
- [ ] RLS context configurado en backend
- [ ] Permisos de rol incluidos
- [ ] Logs de debug habilitados

---

## 🔄 **WORKFLOW DE DEBUGGING**

1. **API Test** → 2. **Browser Test** → 3. **Service Check** → 4. **Component Check**

**¡SIEMPRE EMPEZAR POR LA API BACKEND!**
