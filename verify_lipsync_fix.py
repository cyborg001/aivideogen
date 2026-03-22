import sys
import os

# Simulamos el entorno de Django para verificar imports
sys.path.append(os.path.join(os.getcwd(), 'aivideogen'))

try:
    from aivideogen.scripts.local_lipsync import LipSyncEngine
    print("✅ Módulo local_lipsync importado correctamente sin errores!")
    
    # Intentar instanciar dummy (sin cargar modelos pesados)
    try:
        engine = LipSyncEngine(None, None)
        print("✅ Clase LipSyncEngine instanciable.")
    except Exception as e:
        print(f"⚠️ Error al instanciar (esperado si faltan paths): {e}")

except Exception as e:
    print(f"❌ Error CRITICO al importar local_lipsync: {e}")
    import traceback
    traceback.print_exc()
