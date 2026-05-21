import asyncio
import uuid
from aiohttp import ClientSession
from thinqconnect import ThinQApi

# --- CONFIGURACIÓN ---
ACCESS_TOKEN = "thinqpat_81ab00baba4110552df988e909ff06d25a701585131ba3f880b4"
COUNTRY_CODE = "AR"  # Argentina
CLIENT_ID = str(uuid.uuid4())
# --------------------

async def main():
    async with ClientSession() as session:
        # 1. Inicializar la API
        api = ThinQApi(
            session=session, 
            access_token=ACCESS_TOKEN,
            country_code=COUNTRY_CODE, 
            client_id=CLIENT_ID
        )

        # 2. Obtener la lista de dispositivos
        print("Obteniendo lista de dispositivos...")
        devices = await api.async_get_device_list()
        
        # 3. Mostrar los dispositivos encontrados
        print(f"Dispositivos encontrados: {len(devices) if devices else 0}")
        if not devices:
            print("  No se encontraron dispositivos.")
            return
            
        for device in devices:
            device_id = device.get('deviceId')
            device_name = device.get('deviceInfo', {}).get('alias', 'Sin nombre')
            device_type = device.get('deviceInfo', {}).get('deviceType')
            
            print(f"  - Nombre: {device_name} | ID: {device_id} | Tipo: {device_type}")
            
            # Guardar el ID del primer aire acondicionado
            if device_type == "DEVICE_AIR_CONDITIONER":
                ac_device_id = device_id
                ac_device_name = device_name
                print(f"\n✅ Aire acondicionado encontrado: {ac_device_name}")
                print(f"   ID: {ac_device_id}")
                
                # 4. Obtener el estado del dispositivo
                print("\nObteniendo estado...")
                status = await api.async_get_device_status(device_id=ac_device_id)
                print(f"Estado: {status}")
                
                # 5. Controlar el dispositivo
                # Los comandos se envían usando post_device_control
                # Métodos disponibles: set_air_con_operation_mode, set_target_temperature, set_wind_strength
                
                # Ejemplo: Encender el AC
                # control_result = await api.post_device_control(
                #     device_type=device_type,
                #     device_id=ac_device_id,
                #     control_method="set_air_con_operation_mode",
                #     control_params={"operation": "POWER_ON"}
                # )
                # print(f"Control: {control_result}")
                
                # Ejemplo: Apagar el AC
                # control_result = await api.post_device_control(
                #     device_type=device_type,
                #     device_id=ac_device_id,
                #     control_method="set_air_con_operation_mode",
                #     control_params={"operation": "POWER_OFF"}
                # )
                
                break

if __name__ == "__main__":
    asyncio.run(main())
