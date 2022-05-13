import time
#Inteligencia Artificial PIA
#Matricula 1941588 
# %%
class Accion:
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __str__(self):
        return self.nombre

# %% 
class Estado:
    def __init__(self, nombre, acciones):
        self.nombre = nombre
        self.acciones = acciones 

    def __str__(self):
        return self.nombre

# %% 
class Problema:
    def __init__(self, estado_inicial, estados_objetivos, acciones, costes = None, heuristicas = None):
        self.estado_inicial = estado_inicial
        self.estados_objetivos = estados_objetivos
        self.acciones = acciones 
        self.costes = costes 
        self.heuristicas = heuristicas
        self.infinito = 99999
        if not self.costes:
            self.costes = {}
            for estado in self.acciones.keys():
                self.costes[estado] = {}
                for accion in self.acciones[estado].keys():
                    self.costes[estado][accion] = 1
        if not self.heuristicas:
            self.heuristicas = {}
            for estado in self.acciones.keys():
                self.heuristicas[estado] = {}
                for objetivo in self.estados_objetivos:
                    self.heuristicas[estado][objetivo] = self.infinito

    def __str__(self):
        msg = "Estado Inicial: {0} -> Objetivos: {1}"
        return msg.format(self.estado_inicial.nombre, self.estados_objetivos)
    
    def es_objetivo(self, estado):
        return estado in self.estados_objetivos

    def resultado(self, estado, accion):
        if estado.nombre not in self.acciones.keys():
            return None
        acciones_estado = self.acciones[estado.nombre]
        if accion.nombre not in acciones_estado.keys():
            return None
        return acciones_estado[accion.nombre]
    
    def coste_accion(self, estado, accion):
        if estado.nombre not in self.costes.keys():
            return self.infinito
        costes_estado = self.costes[estado.nombre]
        if accion.nombre not in costes_estado.keys():
            return self.infinito
        return costes_estado[accion.nombre]

    def coste_camino(self, nodo):
        total = 0
        while nodo.padre:
            total += self.coste_accion(nodo.padre.estado, nodo.accion)
            nodo = nodo.padre
        return total 

# %%
#En esta clase definimos nodo
class Nodo: 
    def __init__(self, estado, accion = None, acciones = None, padre = None):
        self.estado = estado
        self.accion = accion
        self.acciones = acciones
        self.padre = padre
        self.hijos = []
        self.coste = 0
        self.heuristicas = {}
        self.valores = {}
        self.alfa = 0
        self.beta = 0

    def __str__(self):
        return self.estado.nombre

    def expandir(self, problema):
        self.hijos = []
        if not self.acciones:
            if self.estado.nombre not in problema.acciones.keys():
                return self.hijos
            self.acciones = problema.acciones[self.estado.nombre]
        for accion in self.acciones.keys():
            accion_hijo = Accion(accion)
            nuevo_estado = problema.resultado(self.estado, accion_hijo)
            acciones_nuevo = {}
            if nuevo_estado.nombre in problema.acciones.keys():
                acciones_nuevo = problema.acciones[nuevo_estado.nombre]
            hijo = Nodo(nuevo_estado, accion_hijo, acciones_nuevo, self)
            coste = self.padre.coste if self.padre else 0
            coste += problema.coste_accion(self.estado, accion_hijo)
            hijo.coste = coste
            hijo.heuristicas = problema.heuristicas[hijo.estado.nombre]
            hijo.valores = {estado: heuristica + hijo.coste for estado, heuristica in hijo.heuristicas.items()}
            self.hijos.append(hijo)
        return self.hijos

    def hijo_mejor(self, problema, metrica = 'valor', criterio = 'menor'):
        if not self.hijos:
            return None
        mejor = self.hijos[0]
        for hijo in self.hijos:
            for objetivo in problema.estados_objetivos:
                if metrica == 'valor':
                    valor_hijo = hijo.valores[objetivo.nombre]
                    valor_mejor = mejor.valores[objetivo.nombre]
                    if (criterio == 'menor' and valor_hijo < valor_mejor):
                        mejor = hijo
                    elif (criterio == 'mayor' and valor_hijo > valor_mejor):
                        mejor = hijo 
                elif metrica == 'heuristica':
                    heuristica_hijo = hijo.heuristicas[objetivo.nombre]
                    heuristica_mejor = mejor.heuristicas[objetivo.nombre]
                    if (criterio == 'menor' and heuristica_hijo < heuristica_mejor):
                        mejor = hijo 
                    elif (criterio == 'mayor' and heuristica_hijo > heuristica_mejor): 
                        mejor = hijo 
                elif metrica == 'coste':
                    coste_camino_hijo = problema.coste_camino(hijo)
                    coste_camino_mejor = problema.coste_camino(mejor)
                    if (criterio == 'menor' and coste_camino_hijo < coste_camino_mejor):
                        mejor = hijo
                    elif (criterio == 'mayor' and coste_camino_hijo > coste_camino_mejor):
                        mejor = hijo 
                elif metrica == 'alfa':
                    if (criterio == 'menor' and hijo.alfa < mejor.alfa):
                        mejor = hijo 
                    elif (criterio == 'mayor' and hijo.alfa > mejor.alfa):
                        mejor = hijo
                elif metrica == 'beta':
                    if (criterio == 'menor' and hijo.beta < mejor.beta):
                        mejor = hijo 
                    elif (criterio == 'mayor' and hijo.beta > mejor.beta):
                        mejor = hijo
        return mejor

#Funcion donde se realiza el metodo de costo uniforme  
def coste_unifirme(problema):
    raiz = crea_nodo_raiz(problema)
    frontera = [raiz,]
    explorados = set()
    while True:
        if not frontera:
            return None
        nodo = frontera.pop(0)
        if problema.es_objetivo(nodo.estado):
            return nodo
        explorados.add(nodo.estado)
        if not nodo.acciones:
            continue
        for nombre_accion in nodo.acciones.keys():
            accion = Accion(nombre_accion)
            hijo = crea_nodo_hijo(problema, nodo, accion)
            estados_frontera = [nodo.estado for nodo in frontera]
            if (hijo.estado not in explorados and hijo.estado not in estados_frontera):
                frontera.append(hijo)
            else: 
                buscar = [nodo for nodo in frontera if nodo.estado == hijo.estado]
                if buscar:
                    if hijo.coste < buscar[0].coste:
                        indice = frontera.index(buscar[0])
                        frontera[indice] = hijo
            frontera.sort(key=lambda nodo: nodo.coste)

# %%
#Funcion que cre nodo raiz
def crea_nodo_raiz(problema):
    estado_raiz = problema.estado_inicial
    acciones_raiz = {}
    if estado_raiz.nombre in problema.acciones.keys():
        acciones_raiz = problema.acciones[estado_raiz.nombre]
    raiz = Nodo(estado_raiz, None, acciones_raiz, None)
    raiz.coste = 0
    return raiz

# %%
#Funcion que crea nodo hijo
def crea_nodo_hijo(problema, padre, accion):
    nuevo_estado = problema.resultado(padre.estado, accion)
    acciones_nuevo = {}
    if nuevo_estado.nombre in problema.acciones.keys():
        acciones_nuevo = problema.acciones[nuevo_estado.nombre]
    hijo = Nodo(nuevo_estado, accion, acciones_nuevo, padre)
    coste = padre.coste
    coste += problema.coste_accion(padre.estado, accion)
    hijo.coste = coste
    padre.hijos.append(hijo)
    return hijo

# %%
#Funcion para mostrrar la solucion 
def muestra_solucion(objetivo=None):
    if not objetivo:
        print("No hay solucion")
        return 
    nodo = objetivo
    while nodo:
        msg = "Estado: {0}, Coste Total: {1}"
        estado = nodo.estado.nombre
        coste_total = nodo.coste
        print(msg.format(estado, coste_total))
        if nodo.accion:
            accion = nodo.accion.nombre
            padre = nodo.padre.estado
            coste = problema_resolver.coste_accion(padre, nodo.accion)
            msg = "<--- {0} [{1}] ---"
            print(msg.format(accion, coste))
        nodo = nodo.padre

# %%%
if __name__ == "__main__":
    #Aqui se definen los puntos cardinales de los estados 
    accN = Accion('A')
    accS = Accion('N')
    accE = Accion('E')
    accO = Accion('O')
    accNE = Accion('NE')
    accNO = Accion('NO')
    accSE = Accion('SE')
    accSO = Accion('SO')

    lanoi = Estado('Lanoi', [accNE])
    nohoi = Estado('Nohoi', [accSO, accNO, accNE])
    ruun = Estado('Ruun', [accNO, accNE, accE, accSE])
    milos = Estado('Milos', [accO, accSO, accN])
    ghiido = Estado('Ghiido', [accN, accE, accSE])
    kuart = Estado('Kuart', [accO, accSO, accNE])
    boomon = Estado('Boomon', [accN, accSO])
    goorum = Estado('Goorum', [accO, accS])
    shiphos = Estado('Shipos', [accO, accE])
    nokshos = Estado('Nokshos', [accNO, accS, accE])
    pharis = Estado('Pharis', [accNO, accSO])
    khamin = Estado('Khamin', [accSE, accNO, accO])
    tarios = Estado('Tarios', [accO, accNO, accNE, accE])
    peranna = Estado('Peranna', [accO, accE])
    khandan = Estado('Khandan', [accO, accS])
    tawa = Estado('Tawa', [accSO, accSE, accNE])
    theer = Estado('Theer', [accSO, accSE])
    roria = Estado('Roria', [accNO, accSO, accE])
    kosos = Estado ('Kosos', [accO])

    #Aqui se definen los estados y sus vecinos (diccionario de diccionarios) 
    acciones = { 'Lanoi': {'NE': nohoi},
                 'Nohoi': {'SO': lanoi,
                           'NO': ruun,
                           'NE': milos},
                 'Ruum': {'NO': ghiido,
                          'NE': kuart,
                          'E': milos,
                          'SE': nohoi},
                 'Milos': {'O': ruun,
                           'SO': nohoi,
                           'N': khandan},
                 'Ghiido': {'N': nokshos,
                            'E': kuart,
                            'SE': ruun},
                 'Kuart': {'O': ghiido,
                            'SO': ruun,
                            'NE': boomon},
                 'Boomon': {'N': goorum,
                            'SO': kuart},
                 'Goorum': {'O': shiphos,
                            'S': boomon},
                 'Shiphos': {'O': nokshos,
                            'E': goorum},
                 'Nokshos': {'NO': pharis,
                            'S': ghiido,
                            'E': shiphos},
                 'Pharis': {'NO': khamin,
                            'SO': nokshos},
                 'Khamin': {'SE': pharis,
                            'NO': tawa,
                            'O': tarios},
                 'Tarios': {'O': khamin,
                            'NO': tawa,
                            'NE': roria,
                            'E': peranna},
                 'Peranna': {'O': tarios,
                            'E': khandan},
                 'Khandan': {'O': peranna,
                            'S': milos},
                 'Tawa': {'SO': khamin,
                         'SE': tarios,
                         'NE': theer},
                 'Theer': {'SO': tawa,
                          'SE': roria},
                 'Roria': {'NO': theer,
                           'SO': tarios,
                           'E': kosos},
                 'Kosos': {'O': roria}
                }
    #Aqui se definen los costes de transportarse en entre estados (Diccionario de diccionarios)
    costes = { 'Lanoi': {'NE': 42},
                 'Nohoi': {'SO': 42,
                           'NO': 21,
                           'NE': 95},
                 'Ruum': {'NO': 88,
                          'NE': 16,
                          'E': 90,
                          'SE': 21},
                 'Milos': {'O': 98,
                           'SO': 95,
                           'N': 133},
                 'Ghiido': {'N': 17,
                            'E': 92,
                            'SE': 88},
                 'Kuart': {'O': 92,
                            'SO': 16,
                            'NE': 83},
                 'Boomon': {'N': 8,
                            'SO': 83},
                 'Goorum': {'O': 59,
                            'S': 8},
                 'Shiphos': {'O': 71,
                            'E': 59},
                 'Nokshos': {'NO': 5,
                            'S': 17,
                            'E': 71},
                 'Pharis': {'NO': 29,
                            'SO': 5},
                 'Khamin': {'SE': 29,
                            'NO': 121,
                            'O': 98},
                 'Tarios': {'O': 98,
                            'NO': 83,
                            'NE': 57,
                            'E': 82},
                 'Peranna': {'O': 82,
                            'E': 44},
                 'Khandan': {'O': 44,
                            'S': 133},
                 'Tawa': {'SO': 121,
                         'SE': 83,
                         'NE': 11},
                 'Theer': {'SO': 11,
                          'SE': 36},
                 'Roria': {'NO': 36,
                           'SO': 57,
                           'E': 104},
                 'Kosos': {'O': 104}
                }



print('PIA')
#Se despliega el menu principal hasta que el usuario salga del programa
ans = True
while ans:
    print("FORE 1.0")
    print("Opciones de movilidad de la ciudad")
    print("""
    1.Iniciar busqueda 
    3.Salir
    """)
    ans=input("Seleccione una opcion: ")
    #Aqui se validan las opciones del menu y se dirige a la opcion seleccionada 
    if ans=="1":
      
      print("Usted se encuentra en: Lanoi")
      #Kosos
      objetivo_1 = [kosos]
      problema_1 = Problema(lanoi, objetivo_1, acciones, costes)
      #Goorum
      objetivo_2 = [goorum]
      problema_2 = Problema(lanoi, objetivo_2, acciones, costes)
      #Nohoi
      objetivo_3 = [nohoi]
      problema_3 = Problema(lanoi, objetivo_3, acciones, costes)
      #Ruun
      objetivo_4 = [ruun]
      problema_4 = Problema(lanoi, objetivo_4, acciones, costes)
      #Milos
      objetivo_5 = [milos]
      problema_5 = Problema(lanoi, objetivo_5, acciones, costes)
      #Ghiido
      objetivo_6 = [ghiido]
      problema_6 = Problema(lanoi, objetivo_6, acciones, costes)
      #Kuart 
      objetivo_7 = [kuart]
      problema_7 = Problema(lanoi, objetivo_7, acciones, costes)
      #Boomon 
      objetivo_8 = [boomon]
      problema_8 = Problema(lanoi, objetivo_8, acciones, costes)
      #Shiphos
      objetivo_9 = [shiphos]
      problema_9 = Problema(lanoi, objetivo_9, acciones, costes)
      #Nokshos
      objetivo_10 = [nokshos]
      problema_10 = Problema(lanoi, objetivo_10, acciones, costes)
      #Pharis
      objetivo_11 = [pharis]
      problema_11 = Problema(lanoi, objetivo_11, acciones, costes)
      #Khamin
      objetivo_12 = [khamin]
      problema_12 = Problema(lanoi, objetivo_12, acciones, costes)
      #Tarios
      objetivo_13 = [tarios]
      problema_13 = Problema(lanoi, objetivo_13, acciones, costes)
      #Peranna
      objetivo_14 = [peranna]
      problema_14 = Problema(lanoi, objetivo_14, acciones, costes)
      #Khandan
      objetivo_15 = [khandan]
      problema_15 = Problema(lanoi, objetivo_15, acciones, costes)
      #Tawa
      objetivo_16 = [tawa]
      problema_16 = Problema(lanoi, objetivo_16, acciones, costes)
      #Theer
      objetivo_17 = [theer]
      problema_17 = Problema(lanoi, objetivo_17, acciones, costes)
      #Roria
      objetivo_18 = [roria]
      problema_18 = Problema(lanoi, objetivo_18, acciones, costes)


      print("Destinos disponibles: ")
      for i in acciones:
        print(i)

      destino=input("Elija su destino: ")
      inicio = time.time() #Inicia contador de tiempo
      if destino == "kosos":
      #En este caso se mostrara el camino y coste de Lanoi a Kosos
        problema_resolver = problema_1
        solucion = coste_unifirme(problema_resolver)
      elif destino == "goorum":
        problema_resolver = problema_2
        solucion = coste_unifirme(problema_resolver)
      elif destino == "nohoi":
        problema_resolver = problema_3
        solucion = coste_unifirme(problema_resolver)
      elif destino == "ruun":
        problema_resolver = problema_4
        solucion = coste_unifirme(problema_resolver)
      elif destino == "milos":
        problema_resolver = problema_5
        solucion = coste_unifirme(problema_resolver)
      elif destino == "ghiido":
        problema_resolver = problema_6
        solucion = coste_unifirme(problema_resolver)
      elif destino == "kuart":
        problema_resolver = problema_7
        solucion = coste_unifirme(problema_resolver)
      elif destino == "boomon":
        problema_resolver = problema_8
        solucion = coste_unifirme(problema_resolver)
      elif destino == "shiphos":
        problema_resolver = problema_9
        solucion = coste_unifirme(problema_resolver)
      elif destino == "nokshos":
        problema_resolver = problema_10
        solucion = coste_unifirme(problema_resolver)
      elif destino == "pharis":
        problema_resolver = problema_11
        solucion = coste_unifirme(problema_resolver)
      elif destino == "khamin":
        problema_resolver = problema_12
        solucion = coste_unifirme(problema_resolver)
      elif destino == "tarios":
        problema_resolver = problema_13
        solucion = coste_unifirme(problema_resolver)
      elif destino == "peranna":
        problema_resolver = problema_14
        solucion = coste_unifirme(problema_resolver)
      elif destino == "khandan":
        problema_resolver = problema_15
        solucion = coste_unifirme(problema_resolver)
      elif destino == "tawa":
        problema_resolver = problema_16
        solucion = coste_unifirme(problema_resolver)
      elif destino == "theer":
        problema_resolver = problema_17
        solucion = coste_unifirme(problema_resolver)
      elif destino == "roria":
        problema_resolver = problema_18
        solucion = coste_unifirme(problema_resolver)
      muestra_solucion(solucion)
      fin = time.time() #Termina contador de tiempo
      print("Tiempo de ejecuccion:")
      print(fin-inicio) #Calcula la diferencia del tiempo
    elif ans=="2":
      print("\n Adios") 
      ans = None
    else:
       print("\n Opcion invalida, intente de nuevo")