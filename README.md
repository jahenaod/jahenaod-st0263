# info de la materia: ST0263 Top. especiales en telematica
#
# Estudiante(s): Juan Andres Henao Diaz, jahenaod@eafit.edu.co
#
# Profesor: Alvaro Enrique Ospina, aeospinas@eafit.edu.com

#
# Reto 1 y 2 P2P
#
# 1. breve descripción de la actividad
Este proyecto consiste en diseñar e implementar un sistema de compartición de archivos distribuido y descentralizado usando un esquema de red P2P (peer-to-peer) no estructurada. En este sistema, cada nodo o peer alberga uno o más microservicios que actúan como servidores (PServidor) y un módulo cliente (PCliente). Los microservicios soportan concurrencia y utilizan RPC (Remote Procedure Call) para comunicarse, pero específicamente a través de API REST y gRPC, omitiendo MOM (Message-Oriented Middleware).

El sistema permite a los peers compartir índices o listados de los archivos disponibles en cada nodo, junto con su URI/URL, pero inicialmente no se enfoca en la transferencia real o sincronización de archivos. Sin embargo, cada peer debe ofrecer servicios simulados para la descarga y carga de archivos.
#

## 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- Se estableció un servidor central para agilizar la búsqueda de peers y archivos.
- Se implementó una comunicacion y transferencia de archivos mediante GRCP
- Se habilitaron servicios para la consulta de recursos y el intercambio de índices de archivos.
- Se implementó la comunicación entre componentes mediante el uso de API REST.


## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
- La comunicacion entre peers puede resultar mas simbolica que funcional, ya que simula la conexion mas no hace la funcion en si 
- No se desplego en AWS 

# 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

- Se utilizo API rest para la comunicacion de la data entre el Pclient y el server
- Para la comunicacion de archivos como upload, listFiles y Download se utilizo GRCP comunicandose el Pclient con el Pserver.

- Se aplicó el patrón MVC "Modelo Vista Controlador", distinguiendo claramente las responsabilidades: el modelo (gestión de datos mediante SQLAlchemy), la vista (creación de la interfaz de usuario y servicios REST), y el controlador (desarrollo de la lógica de negocio y servicios gRPC).
- Se empleó el patrón DAO "Data Access Object" con SQLAlchemy para gestionar las interacciones con la base de datos, permitiendo así aislar la lógica de acceso a datos del resto del código.

![Imagen de la arquitectura](https://github.com/jahenaod/jahenaod-st0263/blob/main/Arquitectura%20TI.jpg)

# 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

Lenguaje de Programación: Python 3.10

Librerías:
- grpcio: 1.62.01
- grpcio-tools: 1.62.02
- requests: 2.31.03
- Flask: 3.0.26
- python-dotenv: 1.0.17
- flask_sqlalchemy
- socket

## como se compila y ejecuta.

- server.py (Server principal): Este se ejecuta de primero e inicial en el localhost en el puerto 4001 junto con la base de datos SQLAlchemy y sus tablas modelo 

- pserver.py: El Peer server se ejecuta despues en el puerto 5001 y medida que se unen nuevos peers su puerto aumenta proporcional. Este espera la conexion de un peer cliente

- pclient.py: El peer cliente es las UI que nos acompañara a ser posible graficamente los metodos y transacciones expresadas en la arquitectura.

## detalles del desarrollo.

-**Base de Datos (SQLAlchemy):** El proyecto utiliza SQLAlchemy para la persistencia de data en 2 tablas una para los peers y otra para los archivos montados comunicados entre si por un peerId y el Username para hacer las consultas 

**Metodos server.py :**

- Index: Indexar el proyecto para la ejecucion 
- login: Endpoint para el logueo de peers en el sistema, esta informacion se guarda en la base de datos 
- upload: Endpoint para montar archivos a la base de datos para cada uno de los peers
- listFiles: Endpoint para listar los files de la base de datos y que peer pertenece, este es invocado por el Pserver mediante GRCP
- Download: Endpoint para descargar archivo solicitado por el peer cliente, este es invocado por el Pserver mediante GRCP
- ListPeers: Endpoint para mostrar al usuario los peers registrados en la base de datos y poder conectarse a uno 

**Metodos Pserver.py**

- Class FileService: Clase embebida para manejar todos las transacciones GRCP como DownloadFiles y ListFiles sin esta no se podria manejar GRCP
- CheckPortAvalible: Metodo para manejar los puertos disponibles para cuando se quieran conectar mas peers a nuevos Pserver y asi no utilizar puertos ya ocupado y por ende error
- Find_free_port: Para encontrar puertos disponibles y cuales no, la logica es intentar conectarse al siguente el cual ya se encuentra ocuapado, ej: 5001, 5002, 5003
- serve_grcp: metodo para inicializar el GRCP en el Pserver
-start_peer_server: metodo para manejar la conexion a los peer clientes correctamente


## detalles técnicos
```
|   .env-peer1
|   .env-Peer2
|   .env-peer3
|   files_db.json
|   p2p.proto
|   p2p_pb2.py
|   p2p_pb2_grpc.py
|   Pclient.py
|   Pserver.py
|   README.md
|   Server.py
|   
+---instance
|       p2p_network.db
|
+---static
\---__pycache__
        database.cpython-310.pyc
        p2p_pb2.cpython-310.pyc
        p2p_pb2.cpython-312.pyc
        p2p_pb2_grpc.cpython-310.pyc
        p2p_pb2_grpc.cpython-312.pyc
        Server.cpython-310.pyc
        VariablesEnviroment.cpython-310.pyc
```


# 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

**1. iniciar el servidor**: Como primer paso debemos inicializar el servidor que a su vez inicializa la base de datos SQLAlchemy

**2. Iniciar el Peer Servidor:** Se inicia el Peer servidor que estara esperando una conexcion de parte del peer cliente

**3. Iniciar peer cliente:** Se inicia el peer cliente que si es el primero debe si o si conectarse a un servidor pero si es el segundo en adelante puede escoger si quiere conectarse a un peer o al servidor tambien, segun el caso de uso 

## una mini guia de como un usuario utilizaría el software o la aplicación

```
Do you want connect to a peer or to a server?server
Enter username: Juanan
Enter password: Juanan
Enter ip address: localhost
Enter port: 5001
Do you want to be peer1, peer2 or peer3 ? : peer1
Logged in as Juanan

What do you want to do?   
1. Download file with gRPC
2. Upload file with HTTP  
3. List peers
4. List file
5. exit
Enter choice: 2
Enter file name to upload: prueba
Enter file URL: prueba.com
Enter peer name or number: Juanan
File prueba uploaded successfully

What do you want to do?   
1. Download file with gRPC
2. Upload file with HTTP  
3. List peers
4. List file
5. exit
Enter choice: 3
Username: hola, IP: localhost, Port: 5001
Username: juli, IP: localhost, Port: 5001
Username: Juanan, IP: localhost, Port: 5001

What do you want to do?
1. Download file with gRPC
2. Upload file with HTTP
3. List peers
4. List file
5. exit
Enter choice: 4
File Name: lol, URL: lol.com, Username: hola
File Name: kill, URL: kill.com, Username: juli
File Name: het, URL: het.com, Username: juli
File Name: po, URL: po.com, Username: juli
File Name: prueba, URL: prueba.com, Username: Juanan

What do you want to do?
1. Download file with gRPC
2. Upload file with HTTP
3. List peers
4. List file
5. exit
Enter choice: 1
Enter file name to download: prueba
File URL: prueba.com
Peer Owner: Juanan

What do you want to do?
1. Download file with gRPC
2. Upload file with HTTP
3. List peers
4. List file
5. exit
Enter choice: 5
```

# 5. otra información que considere relevante para esta actividad.

Para siguentes ocasiones deberiamos implementar

- Seguridad avanzada: Implementar autenticacion real para los peers 

- Orquestacion en nube para que este sistema sea altamente escalable y resiliente a fallos

- Mejorar la logica del codigo para que maneje muchas mas transacciones y usuarios conectados en simultaneo

# referencias:

- https://grpc.io/

- https://economia3.com/peer-to-peer/
