import requests
from amadeus import Client, ResponseError
from geopy.distance import geodesic
from predictive_model import predecir_viaje

# Configuración de Amadeus
amadeus = Client(
    client_id='esGI3kzqQ3JP6KntlOY3EWELoX0sAEOd',
    client_secret='VukKshnDEPj2cYD3'
)

def obtener_coordenadas_ciudad(ciudad):


    response = amadeus.reference_data.locations.get(
        keyword=ciudad,
        subType='CITY'
    )
    if response.data:
        latitud = response.data[0]['geoCode']['latitude']
        longitud = response.data[0]['geoCode']['longitude']
        return latitud, longitud
    else:
        return None


def obtener_destinos_populares(origen, max_distancia_km):

    # Obtener las coordenadas del origen
    coordenadas_origen = obtener_coordenadas_ciudad(origen)
    if not coordenadas_origen:
        print(f"No se pudieron obtener las coordenadas del origen: {origen}")
        return []

    latitud_origen, longitud_origen = coordenadas_origen

    # Solicitar destinos populares desde Amadeus
    response = amadeus.reference_data.locations.airports.get(
        longitude=longitud_origen,
        latitude=latitud_origen
    )

    destinos_data = response.data

    # Filtrar destinos dentro del rango de distancia
    destinos_filtrados = []
    for destino in destinos_data:
        destino_nombre = destino["name"]  # Nombre del aeropuerto
        destino_codigo = destino["iataCode"]  # Código IATA del aeropuerto
        destino_ciudad = destino["address"]["cityName"]  # Nombre de la ciudad
        destino_coords = (destino["geoCode"]["latitude"], destino["geoCode"]["longitude"])

        # Calcular la distancia entre el origen y el destino
        distancia = geodesic(coordenadas_origen, destino_coords).kilometers
        if distancia <= max_distancia_km:
            destinos_filtrados.append({
                "nombre": destino_nombre,
                "codigo": destino_codigo,
                "ciudad": destino_ciudad,
                "distancia": distancia
            })

    return destinos_filtrados

def clasificar_clima_ciudad(ciudad):

    # Configuración de la API de OpenWeatherMap
    api_key = "9e50cd73a502ed90c0372481a8109ad6"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": ciudad,
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }

    try:
        # Realizar la solicitud a la API
        response = requests.get(url, params=params)
        data = response.json()


        # Obtener la temperatura actual
        temperatura = data["main"]["temp"]

        # Clasificar la ciudad según la temperatura
        if temperatura >= 25:
            return temperatura ,"tropical"
        elif temperatura <= 0:
            return temperatura, "polar"
        else:
            return temperatura, "dry"

    except Exception as e:
        print(f"Error al obtener el clima de {ciudad}: {e}")
        return "desconocido"


def buscar_vuelos_y_hoteles(numero, rango_ini_precio, rango_fin_precio, distancia_max, date_departure, date_arrival, departure, clima_preferido):

    resultados = []

    if not numero:
        raise ValueError("Número de personas no válido.")
    if not (rango_ini_precio and rango_fin_precio):
        raise ValueError("Rango de precios no válido.")
    if not (distancia_max and date_departure and date_arrival):
        raise ValueError("Distancia máxima o fechas no válidas.")
    
    

    departure_iata = amadeus.reference_data.locations.get(
        keyword=departure,
        subType='CITY'
    ).data[0]['iataCode']
    pais_origen = amadeus.reference_data.locations.get(
        keyword=departure,
        subType='CITY'
    ).data[0]['address']['countryCode']

    # Obtener las coordenadas de la ciudad de origen
    coordenadas_origen = obtener_coordenadas_ciudad(departure)
    if not coordenadas_origen:
        print("No se pudieron obtener las coordenadas de la ciudad de origen.")
        return []


    # API de Amadeus para buscar destinos populares

    destinos_data = obtener_destinos_populares(departure, distancia_max) 
  # Filtrar destinos según el presupuesto y duración del viaje
    for destino in destinos_data:
        destino_code = destino["codigo"]
        destino_name = destino["nombre"]
        destino_ciudad = destino["ciudad"]
        distancia = destino["distancia"]

        # Verificar que el origen y el destino sean diferentes
        if departure_iata == destino_code:
            continue

        # API de Amadeus para buscar vuelos
        try:
            response_vuelos = amadeus.shopping.flight_offers_search.get(
                originLocationCode=departure_iata,
                destinationLocationCode=destino_code,
                departureDate=date_departure,
                returnDate=date_arrival,
                adults=numero,
                currencyCode="EUR"
            )
            vuelos_data = response_vuelos.data[:1]  # Obtener solo el primer vuelo
        except ResponseError as error:
            print("Error al buscar vuelos:")
            print("Código de estado:", error.response.status_code)
            print("Mensaje de error:", error.response.body)
            continue

        for vuelo in vuelos_data:
            precio = float(vuelo["price"]["total"])
            clima = clasificar_clima_ciudad(destino_ciudad)
            temperatura, clima = clima
            clima_lista = ["polar", "dry", "tropical"]
            # Calificar del 1 al 10 el clima según la preferencia, estando frio, seco y tropical, siel el clima de preferencia es igual sera 10, si esta a uno de distancia en el array sera 6 y sino sera 3
            if clima_preferido == clima:
                clima = 10
            else:
                if abs(clima_lista.index(clima) - clima_lista.index(clima_preferido)) == 1:
                    clima = 5
                else:
                    clima = 2

            if rango_ini_precio <= precio <= rango_fin_precio:
                itineraries = vuelo["itineraries"]
                duracion = itineraries[0]["duration"] if itineraries else "N/A"

                pais_destino = amadeus.reference_data.locations.get(
                    keyword=destino_ciudad,
                    subType='CITY'
                ).data[0]['address']['countryCode']

                if pais_origen == pais_destino:
                    nativo = 0
                else:
                    nativo = 1

                resultados.append({
                    "tipo": "vuelo",
                    "personas": numero,
                    "origen": departure,
                    "precio": precio,
                    "destino": destino_name,
                    "nombre_vuelo": vuelo["itineraries"][0]["segments"][0]["carrierCode"],
                    "vuelo_id": vuelo["id"],
                    "duracion": duracion,
                    "distancia": distancia,
                    "temperatura": temperatura,
                    "clima": clima,
                    "nativo": nativo,
                    "ciudad": destino_ciudad,
                })
                break
    return resultados

