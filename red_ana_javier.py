from math import inf
from random import randint
from collections import defaultdict

signal_time = 10  #declaracion del signal time

def binary_to_int(n_bin):
    n = 0
    for i,bit in enumerate(n_bin):
        n += int(bit)*(2**(len(n_bin) - i - 1))
    
    return n

def binary_to_hex(n_bin):
    map_int_hex = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'A', 11:'B', 12:'C', 13:'D', 14:'E', 15:'F'}
    
    n = binary_to_int(n_bin)
    
    n_hex = ""
    
    while n != 0:
        n_hex = map_int_hex[n%16] + n_hex
        n /= 16
    
    return n
    
    
    

class Network_item(object):  #clase de la que heredan los elementos de la red hub y host
    def __init__(self,name,p_number):  #se inicializa con los parametros nombre y cantidad de puertos
        self.name = name  #propiedad nombre del elemento
        self.p_number = p_number   #propiedad cantidad de puertos
        self.state = [-1 for i in range(p_number)]  #arreglo donde por cada puerto se tendra el valor del bit 
                                                    #que esta transmitiendo en ese momento (-1 no transmite nada) 
        self.p_sending = [-1 for i in range(p_number)]  #arreglo que por cada puerto tiene la informacion de 
                                                        #si esta recibiendo informacion(1), enviando(0) o ninguna(-1)
                                                        #en el caso de las computadoras si tiene colision el estado 
                                                        #se representara con 2
        self.send_state = [-1 for i in range(p_number)]
        self.flow_data = None   #valor del bit que se esta transmitiendo
        

class Hub(Network_item):  #clase correspondiente a elemento hub
    def __init__(self,name,p_number):
        super(Hub,self).__init__(name,p_number)

class Switch(Network_item):
    def __init__(self,name,p_number):
        super(Switch,self).__init__(name,p_number)
        self.MAC_table = {}
        self.aging_time = 600000  #aging_time, 10 min (si un host esta sin enviar mas d 10 min se quita d ese puerto)
        self.buf = [{} for i in range(p_number + 1)] #un bufer por cada puerto del switch, para guardar el frame 
        self.buf_index = [0 for i in range(p_number + 1)] #en la posición i guarda el número de bit que ha recibido el puerto i
        self.buf_index_send = [0 for i in range(p_number + 1)] #en la posición i guarda el número de bit hasta el que se ha enviado por el puerto i
        self.buf_to_send = [[] for i in range(p_number + 1)] 
        self.time_slot = [0 for i in range(p_number + 1)]
        self.time_slot_send = [0 for i in range(p_number + 1)]
        
    def assign_MAC_to_table(self,mac,port,time):
        self.MAC_table[mac] = (port,time)
    
    def check_aging_time(self,time): #quitar los host que llevan tiempo sin enviar
        for item in self.MAC_table:
            if time - self.MAC_table[item][2] > self.aging_time:
                self.MAC_table.pop(i)
    
    def transfer_frame_to_send(port):
        dest_mac = str(self.buf[port]["dest_mac"])
        src_mac = str(self.buf[port]["source_mac"])
        dest_mac = binary_to_hex(dest_mac) ##implementar convertir de bin a hex
        if dest_mac == src_mac:
            pass
        elif dest_mac != "FFFF" and dest_mac in self.MAC_table:
            port_send = self.MAC_table[dest_mac][1]
            # if port_send == 
            self.buf_to_send[port_send].append(self.buf[port])
        else:                              ###BROADCAST
            for port_send in range(1,self.p_number + 1):
                self.buf_to_send[port_send].append(self.buf[port])
    
    def save_bit(self,bit,port):
        if self.buf_index[port] == 0:
            self.buf[port].append({"dest_mac":[],"source_mac":[],"size":[],"ext_field":[],"data":[]})
        
        index = self.buf_index[port]
        
        if not self.time_slot[port]:
            if index < 16:
                self.buf[port]["dest_mac"].append(int(bit))
            elif index < 32:
                self.buf[port]["source_mac"].append(int(bit))
            elif index < 40:
                self.buf[port]["size"].append(int(bit))
            elif index < 48:
                self.buf[port]["ext_field"].append(int(bit))
            else:
                self.buf[port]["data"].append(int(bit))
        
        if index == 32:
            self.assign_MAC_to_table(str(self.buf[port]["source_mac"]))
        
        self.time_slot[port] += 1
        
        if self.time_slot[port] == signal_time:
            if index < 48:
                self.buf_index[port] += 1
            elif index < 48 + binary_to_int(str(self.buf[port]["size"])):
                self.buf_index[port] += 1
            else:
                self.buf_index[port] = 0
                self.transfer_frame_to_send(port)
            self.time_slot[port] = [0]   
    
    def send_data(self,port):
        if not self.buf_to_send[port]:
            return -1
        index = self.buf_index_send[port]
        
        if not self.time_slot_send[port]:
            if index < 16:
                self.state_send[port] = self.buf_to_send[port][0]["dest_mac"][index] #creo q debemos poner esto pq pueden hacer las dos cosas en cada puerto
            elif index < 32:
                self.state_send[port] = self.buf_to_send[port][0]["source_mac"][index - 16] #creo q debemos poner esto pq pueden hacer las dos cosas en cada puerto
            elif index < 40:
                self.state_send[port] = self.buf_to_send[port][0]["size"][index - 32] #creo q debemos poner esto pq pueden hacer las dos cosas en cada puerto
            elif index < 48:
                self.state_send[port] = self.buf_to_send[port][0]["ext_fiel"][index - 40] #creo q debemos poner esto pq pueden hacer las dos cosas en cada puerto
            else:
                self.state_send[port] = self.buf_to_send[port][0]["data"][index - 48] #creo q debemos poner esto pq pueden hacer las dos cosas en cada puerto
        
        self.time_slot_send[port] += 1
        if self.time_slot_send[port] == signal_time:
            self.buf_index[port] += 1
            if not index < 48 + binary_to_int(str(self.buf_to_send[port][0]["size"])):
                self.buf_index_send[port] = 0
                self.buf_to_send[port].pop(0)
            self.time_slot[port] = 0 
            
        
class Host(Network_item):  #clase correspondiente a las computadoras
    def __init__(self,name):
        super(Host,self).__init__(name,1)  #se llama al constructor de la clase Network_item 
                                            #pasandole name y 1 como cantidad de puertos
        self.time_to_send = inf  #tiempo en el que la computadora debe enviar datos 
        self.time_slot = 0       #esta variable se usa para controlar que cada bit se transmita durante un tiempo igual a 
                                #signal_time
        self.data = []          #datos que deben ser enviados por la computadora almacenados bit a bit
        self.bit_to_send_pos = 0  #esta variable se usa para definir por donde va la transmicion de informacion de la 
                                #computadora en el arreglo de los bit a transmitir
        self.consecutive_collisions = 0  #colisiones consecutivas que ha sufrido la computadora
        self.MAC = None
        self.buf = {"dest_mac":[],"source_mac":[],"size":[],"ext_field":[],"data":[]}
        self.buf_index = 0
        self.time_slot_save = 0
        self.ignore_frame = 0
        self.recieved_frame = 0
        
    def set_MAC(self,mac):
        if self.MAC == None:
            self.MAC = mac
        else: 
            pass
    
    def add_data_to_send(self,data,time):  #cuando la computadora va a enviar un dato se agrega a la data y 
                                            #se actualiza el time_to_send
        for bit in data:
            self.data.append(bit)
        self.time_to_send = time

    
    def manage_collision(self):   ##funcion para manejar las colisiones
        if self.consecutive_collisions == 3:  #si la computadora sufre 3 colisiones consecutivas se decide no intentar mas el envio
            self.consecutive_collisions = 0
            self.time_to_send = inf
            self.data = []
            pass
        if self.p_sending[0] == 0:
            self.flow_data = None
        self.p_sending[0] = 2  #se actualiza el estado del puerto
        self.bit_to_send_pos = 0  #se vuelve a iniciar la transmicion por el primer bit
        self.consecutive_collisions = self.consecutive_collisions + 1
        temp = randint(signal_time, self.consecutive_collisions * signal_time) #se elige de forma aleatoria el tiempo en que
                                                                            #la computadora volvera a intentar enviar la informacion
                                                                            #el intervalo debe crecer con la cantidad de intentos
        self.time_to_send = self.time_to_send + temp
        self.time_slot = 0

    def send_data(self):  #funcion que se ejecuta cuando una computadora envia un bit a traves de la red en un milisegundo dado
        self.time_slot += 1 
        self.time_to_send += 1
        self.send_state[0] = self.data[self.bit_to_send_pos] #el bit que fluye es el bit en turno en el arreglo data
        self.flow_data = self.data[self.bit_to_send_pos] #el bit que fluye es el bit en turno en el arreglo data
        if self.time_slot == signal_time:  #si time_slot llega al signal time se sigue al siguiente bit
            self.bit_to_send_pos += 1
            
            if self.bit_to_send_pos == len(self.data):  #esta condicion se cumple cuando se ha enviado toda la informacion
                                                        #del arreglo data, o sea concluyo el envio de esta computadora
                self.time_to_send = inf   #se reestablecen los valores de las variables involucradas
                self.bit_to_send_pos = 0
                self.time_slot = 0
                self.data = []
            else:
                self.time_slot = 0  ##ver si esto  cambia algo
    
    def save_bit(self,bit):
        index = self.buf_index
        
        if not self.time_slot_save:
            if index < 16:
                self.buf["dest_mac"].append(int(bit))
            elif index < 32:
                self.buf["source_mac"].append(int(bit))
            elif index < 40:
                self.buf["size"].append(int(bit))
            elif index < 48:
                self.buf["ext_field"].append(int(bit))
            elif index < 48 + binary_to_int(self.buf[size]):
                self.buf["data"].append(int(bit))
        
        self.time_slot_save += 1
        
        if self.time_slot_save == signal_time:
            self.time_slot_save = 0
            self.buf_index += 1
            if not self.buf_index < 48 + binary_to_int(self.buf[size]):
                self.buf_index = 0
                if self.ignore_frame:
                    self.buf = {"dest_mac":[],"source_mac":[],"size":[],"ext_field":[],"data":[]}
                    self.ignore_frame = 0
                else:
                    self.recieved_frame = 1
                pass
        
        if  self.buf_index == 16 and str(self.buf["dest_mac"]) != "0000000000000000" and binary_to_hex(str(self.buf["dest_mac"])) != self.MAC:
            self.ignore_frame = 1
                    

class Network(object):
    def __init__(self,queries):
        self.hubs = []   #lista de hubs de la red
        self.hosts = []  #lista de computadoras de la red
        self.switches = []
        self.dict_name_to_item = {}   #diccionario por nombre de los dispositivos de la red
        self.queries = queries
        self.connections = {}  #diccionario para almacenar las conexiones de la red(llave elemento de la red
                                #valor un arreglo del tamaño de la cantidad de puertos del dispositivo
                                #para guardar el elemento y puerto al q se conecta cada uno)
        self.time = 0    #esto va a ser el tiempo de ejecucion
        self.host_sending = [] 
        self.host_collision = []
        
    def run(self):
        flag = 0 #variable que se usa para saber el estado de la red, si queda informacion por enviar
        q_n = 0  #variable que almacena el valor de la cantidad de queries procesadas en cada milisegundo
        while flag == 0 or len(self.queries) > 0: #se continua la ejecucion mientras queden queries por analizar o datos por enviar
            for query in self.queries:   #en cada milisegundo primero veo si hay queries por hacer
                if int(query[0]) == self.time:
                    self.query_parse(query)
                    q_n = q_n + 1
                else:
                    break
            while q_n > 0:   #se eliminan de la lista de queries las que ya fueron procesadas
                self.queries.pop(0)
                q_n = q_n -1

            flag = self.check_local_network() #se chequea el estado de la red
            self.print_states()  #se imprime el estado de cada dispositivo
            self.time = self.time + 1

            for s in self.switches:
                s.check_aging_time()
                    
    
    def query_parse(self,query):  #analizar la query y ejecutar la funcion q corresponda
        name_query = query[1] #nombre d la query
        time = int(query[0])  #tiempo en el q se ejecuta
        
        if name_query == "create":
            item = query[2]   #elemento a crear: hub, host o switch
            name = query[3]   #nombre del elemento
            
            if item == "hub":  
                n_ports = int(query[4])   #cantidad de puertos del hub
                self.add_hub(name,n_ports)  
            
            elif item == "host":
                self.add_Host(name)

            elif item == "switch":
                n_ports = int(query[4])   #cantidad de puertos del switch
                self.add_switch(name, n_ports)

            else:   #si el elemento no es ni hub ni host, se devuelve -1 (error)
                return -1
        
        elif name_query == "connect":  #query para crear una conexion en la red
            port1 = query[2]
            port2 = query[3]
            self.connect(port1,port2)
        
        elif name_query == "disconnect":  #query correspondiente a desconectar un puerto
            port = query[2]
            self.disconnect(port)
        
        elif name_query == "send":   #query send
            host_name = query[2]  #nombre de la computadora q va a enviar
            mac_destiny = query[3] #mac del host al que se le envía la información
            data = query[4]  #numero a enviar
            self.send(host_name,data)

        elif name_query == "mac":
            host_name = query[2]
            mac = query[3]
            self.assign_MAC(host_name,mac)
        else:
            return -1 
            
    def add_hub(self,name,n_ports): #funcion para agregar un hub a la red, con nombre name y n_ports puertos
        if name in self.dict_name_to_item: #no se crea el elemento si ya existe otro con ese nombre
            return -1
        DIR_OUTPUT = "./network_state/"  #se crea el archivo en que se actualiza el estado del dispositivo
        fd = open(DIR_OUTPUT + name + ".txt", 'w+')
        fd.close()
        hub_ = Hub(name,n_ports)  #se crea el elemento
        self.dict_name_to_item[name] = hub_
        self.hubs.append(hub_)
        self.connections[hub_] = [None for i in range(n_ports)]  #las conexiones se inicializan en None
    
    def add_Host(self,name):  ##funcion para agregar una computadora a la red
        if name in self.dict_name_to_item:  #no se crea el elemento si ya existe otro con ese nombre
            return -1
        DIR_OUTPUT = "./network_state/"
        fd = open(DIR_OUTPUT + name + ".txt", 'w+')
        fd.close()
        DIR_OUTPUT = "./network_state/"
        fd = open(DIR_OUTPUT + name + "_data.txt", 'w+')
        fd.close()
        host_ = Host(name)  #se crea el elemnto
        self.dict_name_to_item[name] = host_
        self.hosts.append(host_)
        self.connections[host_] = [None]
    
    def add_switch(self,name,p_number):
        if name in self.dict_name_to_item: #no se crea el elemento si ya existe otro con ese nombre
            return -1
        switch_ = Switch(name,n_ports)  #se crea el elemento
        self.dict_name_to_item[name] = switch_
        self.switches.append(switch_)
        self.connections[switch_] = [None for i in range(p_number)]  #las conexionse se inicializan en None
        
    def connect(self,port_1,port_2):  #funcion para conectar dos puertos en la red
        port1_name,port1_number = port_1.split('_')
        port2_name,port2_number = port_2.split('_') 
        port1_number = int(port1_number)
        port2_number = int(port2_number)

        if port1_name not in self.dict_name_to_item or port2_name not in self.dict_name_to_item: #el nombre no corresponde con ningun elemento de la red
            return -1
        
        item1 = self.dict_name_to_item[port1_name]  #elemento de la red que corresponde al primer puerto
        item2 = self.dict_name_to_item[port2_name]  #elemento de la red que corresponde al segundo puerto
        
        if port1_number > item1.p_number or port2_number > item2.p_number:  # el numero del puerto es mayor que la cantidad de puertos del elemento corerespondiente en la red
            return -1
        
        if self.connections[item1][port1_number-1] is not None or self.connections[item2][port2_number-1] is not None: #alguno de los puertos ya esta ocupado
            return -1
        
        self.connections[item1][port1_number-1] = (item2,port2_number - 1)  #equivale a agregar el cable entre los dos puertos
        self.connections[item2][port2_number-1] = (item1,port1_number - 1)
    
    def disconnect(self,port):  #desconectar el puerto port de la red
        port_name,port_number = port.split('_')  
        port_number = int(port_number)

        if port_name not in self.dict_name_to_item:   #el nombre no se corresponde a ningun elemento de la red
            return -1
        
        item = self.dict_name_to_item[port_name]   #elemento correspondiente al nombre del puerto
        
        if port_number > item.p_number:  #el numero del puerto es mayor q la cantidad de puertos del elemento correspondiente
            return -1
        
        item_connected = self.connections[item][port_number-1]  #elemento al que esta conectado el puerto
        
        self.connections[item_connected[0]][item_connected[1]] = None  #se elimnan las conexiones
        self.connections[item][port_number - 1] = None 
        
    def send(self, host_name, data):  #funcion para la query send
        
        if host_name not in self.dict_name_to_item:  #la computadora no pertenece a la red
            return -1
        
        host_ = self.dict_name_to_item[host_name]  #computadora correspondiente a ese nombre
        
        if not isinstance(host_,Host):  #chequear si es una computadora (un hub no puede enviar)
            return -1
        
        host_.add_data_to_send(data,self.time)
        
    def assign_MAC(self, host_name, mac):
        if host_name not in self.dict_name_to_item:
            return -1
        
        host_ = self.dict_name_to_item[host_name]
        
        host_.set_MAC(mac)

    def check_local_network(self):  #funcion para chequear el estado de la red
        reachable_devices = self.dfs()  #se realiza un dfs para ver los dispositivos conectados entre si en la red
        hosts_attempting_to_send = self.detect_collisions(reachable_devices)  #esta funcion devuelve las computadoras que 
                                                                            #enviaran datos en este milisegundo
        if not (hosts_attempting_to_send and switches_attempting_to_send):  #se chequea si ninguna computadora enviara en este momento
            for i in self.hosts + self.switches:   #por cada computadora y switch se chequea si tiene data pendiente de enviar para saber que no
                                    #puede terminarse la ejecucion
                if (isinstance(i, Host) and host.data) or (isinstance(i, Switch) and any([len(b) > 0 for b in i.buf_to_send])):
                    return 0
            return 1
        self.dfs_update_states(hosts_attempting_to_send, switches_attempting_to_send)  #se realiza un dfs para actualizar el estado de cada dispositivo
        return 0
    
    # def dfs(self):  #dfs para chequear los dispositivos interconectados en la red
    #     connected_devices = {value : [] for value in self.dict_name_to_item.values()} #por cada elemento tendra el valor de la componente 
    #                                                                                     #conexa que le corresponde en la red
    #     count_cc = 1
    #     for i in self.hosts + self.switches: #se inicia el dfs partiendo de cada computadora que no se haya visitado
    #         # if not visited[i]:
    #         visited = {value : False for value in self.dict_name_to_item.values()}
    #         visited[i] = True
    #         connected_devices[i].append(count_cc)
    #         self.dfs_visit(i, connected_devices, visited, count_cc)
    #         count_cc += 1
    #     return connected_devices

    # def dfs_visit(self, i, connected_devices, visited, count_cc): #funcion para el dfs_visit
    #     for item in self.connections[i]:
    #         device = item[0]
    #         port_connected_to = item[1]
    #         if not item == None and not visited[device]:
    #             visited[device] = True
    #             connected_devices[device].append(count_cc)
    #             if not isinstance(device, Host) and nor isinstance(device, Switch):
    #                 self.dfs_visit(device,connected_devices,visited,count_cc)

    def dfs(self):
        reachable_devices = {value : [] for value in self.hosts + self.switchs}

        for i in self.hosts + self.switches:
            visited = {value : False for value in self.dict_name_to_item.values()}
            visited[i] = True
            self.dfs_visit(i, reachable_devices, visited, i)

        return reachable_devices

    def dfs_visit(self, i, reachable_devices, visited, start_device):
        for item in self.connections[i]:
            device = item[0]
            port_connected_to = item[1]
            if not item == None and not visited[device]:
                visited[start_device] = True
                reachable_devices[start_device].append(device)
                if not isinstance(device, Host) and not isinstance(device, Switch):
                    self.dfs_visit(device,reachable_devices,visited, start_device)


    def detect_collisions(self, reachable_devices):  #funcion para detectar las posibles colisiones en la red
        xor = {_host : int(_host.data[_host.bit_to_send_pos]) for device in reachable_devices if isinstance(device, Host)}  #por cada componente conexa se tendra el xor de los valores que
                                                        #pretenden enviar las computadoras de la misma
        hosts_attempting_to_send = []  #computadoras que van a enviar data en este milisegundo
        switches_attempting_to_send = []  #computadoras que van a enviar data en este milisegundo

        for _host in self.hosts:  #se chequea por cada computadora si tiene que enviar en este milisegundo
            if _host.time_to_send == self.time:
                if len(reachable_devices[_host]) > 1 and xor[_host] == None:
                    connected_hosts = [_host]
                    for i in reachable_devices[_host]:
                        if isinstance(i, Host) and i.time_to_send == self.time:
                            xor ^= int(i.data[i.bit_to_send_pos])
                            connected_hosts.append(i)
                    for i in connected_hosts:
                        xor[i] = xor

                hosts_attempting_to_send.append(item)

        items_to_remove = []  #lista de las computadoras que no van a poder enviar porque detectan colisiones
        for item in hosts_attempting_to_send: 
            if int(item.data[item.bit_to_send_pos]) != xor[item]: 
                item.manage_collision()  #funcion para que la computadora maneje la colision
                items_to_remove.append(item)

        hosts_attempting_to_send = list(set(hosts_attempting_to_send) - set(items_to_remove))

        switches_attempting_to_send = [switch for switch in self.switches if any([len(b) > 0 for b in switch.buf_to_send])]

        return hosts_attempting_to_send, switches_attempting_to_send



    def dfs_update_states(self, hosts_attempting_to_send, switches_attempting_to_send):  #funcion para actualizar el estado de cada dispositivo usando dfs
        for i in hosts_attempting_to_send:  #se comienza el dfs por cada computadora y switch que tiene que enviar datos en este milisegundo
            i.p_sending[0] = 0  #se acutaliza el estado del puerto con 0 (enviar)
            i.send_data() 
            visited = {value : False for value in self.dict_name_to_item.values()}
            self.dfs_visit_update_states(i, visited)  #dfs en la componente conexa de la computadora en turno
        
        for i in switches_attempting_to_send:
            for j, data in enumerate(i.buf_to_send):
                if data:
                    if isinstance(connections[i][j][0], hub) and i.p_sending[j] == 1:
                        break
                    i.p_sending[j] = 0
                    i.send_data()
                    visited = {value : False for value in self.dict_name_to_item.values()}
                    self.dfs_visit_update_states(i, visited)  #dfs en la componente conexa de la computadora en turno



    def dfs_visit_update_states(self, i, visited):  #funcion del dfs en una componente conexa
        for port in range(len(self.connections[i])):  #se revisa cada puerto del dispositivo
            item = self.connections[i][port]  #elemento conectado a port
            
            if not item == None and (not visited[item[0]] or (isinstance(item[0],Hub) and isinstance(i,Host) and (item[0].p_sending[item[1]] == 0 or item[0].p_sending[item[1]] == -1))):
                  #se chequea que este conectado a algun dispositivo y que este no haya sido visitado o sean un puerto de un hub
                                    #que no estaba recibiendo antes
                if isinstance(i, Hub):    #si i es un hub se actualiza su estado a 0(enviando)
                    i.p_sending[port] = 0
                if (isinstance(item[0], Host) and item[0].p_sending[0] != 2) or isinstance(item[0], Hub): #chequea si item[0] es una
                                                                                    #computadora que no esta colisionando o un hub y se 
                                                                                    #actualiza su esta a 1(recibiendo)
                    item[0].p_sending[item[1]] = 1
                if isinstance(item[0], Switch):
                    item[0].p_sending[item[1]] = 1
                    item[0].save_bit(i.send_state[port], item[1])
                    break


                item[0].send_state[item[1]] = i.send_state[port]
                if not visited[item[0]] and not isinstance(item[0],Host) and not isinstance(item[0], Switch):  #se llama dfs si no se ha visitado el
                                                                            #dispositivo y no es una computadora porque 
                                                                            #la computadora tiene un solo puerto que si recibe no envia
                    self.dfs_visit_update_states(item[0],visited)  ##cambie aqui


    def print_states(self):   #funcion para imprimir el estado de cada dispositivo
        DIR_OUTPUT = "./network_state/"
        for item in self.dict_name_to_item.values():
            fd = open(DIR_OUTPUT + item.name + ".txt", 'a')
            state = ""
            waiting = ""
            if isinstance(item,Host):
                if item.p_sending[0] == -1:
                    if item.data:
                        waiting = "waiting to send"
                    fd.write(str(self.time) + " " + item.name + " None " + waiting + '\n')
                    fd.close()  ##este
                    continue
                elif item.p_sending[0] == 1:
                    if item.data:
                        waiting = "waiting to send"
                    state = "receive"
                    result = "ok"
                elif item.p_sending[0] == 0:
                    state = "send"
                    result = "ok"
                else:
                    if item.p_sending[0] == 1:
                        state = "receive"
                    result = "collision"
                if state == "":
                    fd.write(str(self.time) + " " + item.name + " " + result + ' ' + waiting + '\n')
                else:
                    fd.write(str(self.time) + " " + item.name + " " + state + " " + str(item.flow_data) + " " + result + ' ' + waiting + '\n')
                item.state[0] = -1
                item.p_sending[0] = -1
            
                fd.close()
                if item.recieved_frame:
                    fd = open(DIR_OUTPUT + item.name + "_data.txt", 'a')
                    fd.write(str(self.time) + " " + binary_to_hex(str(item.buf["source_mac"])) + " " + binary_to_hex(str(item.buf["source_mac"])) + '\n')
                    item.buf = {"dest_mac":[],"source_mac":[],"size":[],"ext_field":[],"data":[]}
                    item.recieved_frame = 0
                    fd.close()
                    
            else:
                for port in range(item.p_number):
                    if item.p_sending[port] == -1:
                        fd.write(str(self.time) + " " + item.name + "_" + str(port + 1) + " None\n")
                    elif item.p_sending[port] == 0:
                        fd.write(str(self.time) + " " + item.name + "_" + str(port + 1) + " send " + str(item.flow_data) + '\n')
                    else:
                        fd.write(str(self.time) + " " + item.name + "_" + str(port + 1) + " receive " + str(item.flow_data) + '\n')
                    
                    item.p_sending[port] = -1
                item.flow_data = None
                
                fd.close()
              

def read_queries():  ##Leer el archivo con las queries
    file = open("data\script.txt",'r+')
    queries = file.read().split('\n')
    queries = [queries[i].split(' ') for i in range(len(queries))]
    queries = sorted(queries, key = lambda x:int(x[0]))
    file.close()
    return queries
