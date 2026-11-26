# ============================================================
# Software FJ
# Nombre del estudiante: NATALIA GALLARDO PONARE
# Asignatura: PROGRAMACIÓN
# Código Fuente: Autoría propia
# ============================================================



import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from abc import ABC, abstractmethod
from datetime import datetime
import logging

logging.basicConfig(
    filename="registro_sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# ========================= EXCEPCIONES PERSONALIZADAS =========================
class ErrorSistema(Exception):
    pass

class DatosInvalidosError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaError(ErrorSistema):
    pass

class ClienteNoEncontradoError(ErrorSistema):
    pass


# ================================ ENTIDAD ====================================
class Entidad(ABC):
    def __init__(self, identificador):
        if identificador is None or str(identificador).strip() == "":
            raise DatosInvalidosError("El identificador es obligatorio.")
        self.identificador = identificador
        self.fecha_creacion = datetime.now()

    @abstractmethod
    def describir(self):
        pass


# ================================ CLIENTE ===================================
class Cliente(Entidad):
    def __init__(self, identificador, nombre, documento, correo, telefono):
        super().__init__(identificador)
        self.__nombre = self._validar_texto(nombre, "nombre")
        self.__documento = self._validar_texto(documento, "documento")
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_texto(telefono, "teléfono")

    @staticmethod
    def _validar_texto(valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            raise DatosInvalidosError(f"El campo {campo} es obligatorio.")
        return valor.strip()

    @staticmethod
    def _validar_correo(correo):
        correo = Cliente._validar_texto(correo, "correo")
        if correo.count("@") != 1 or "." not in correo.split("@")[1]:
            raise DatosInvalidosError("Ingrese un correo válido.")
        return correo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def describir(self):
        return f"{self.__nombre} | CC: {self.__documento} | {self.__correo} | {self.__telefono}"


# ================================ SERVICIO ==================================
class Servicio(Entidad, ABC):
    def __init__(self, identificador, nombre, precio_base, disponible=True):
        super().__init__(identificador)
        if not str(nombre).strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")
        if float(precio_base) <= 0:
            raise DatosInvalidosError("La tarifa debe ser mayor que cero.")
        self.nombre = nombre.strip()
        self.precio_base = float(precio_base)
        self.disponible = bool(disponible)

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def calcular_costo(self, duracion):
        pass

    def calcular_total(self, duracion, descuento=0, impuesto=0):
        # Variante de cálculo: sin descuento/impuesto, o con ambos parámetros.
        self.verificar_disponibilidad()
        self.validar_parametros(duracion)
        descuento = float(descuento)
        impuesto = float(impuesto)
        if not 0 <= descuento <= 100:
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100%.")
        if impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")
        subtotal = self.calcular_costo(duracion)
        subtotal -= subtotal * descuento / 100
        total = subtotal + subtotal * impuesto / 100
        return round(total, 2)

    def verificar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' no está disponible.")

    def describir(self):
        return f"{self.nombre} | Tarifa base: ${self.precio_base:,.0f}"


class ReservaSala(Servicio):
    def __init__(self, identificador, nombre, precio_base, capacidad, disponible=True):
        super().__init__(identificador, nombre, precio_base, disponible)
        self.capacidad = int(capacidad)
        if self.capacidad <= 0:
            raise DatosInvalidosError("La capacidad debe ser mayor que cero.")

    def validar_parametros(self, duracion):
        duracion = float(duracion)
        if duracion <= 0 or duracion > 12:
            raise DatosInvalidosError("La sala debe reservarse entre 0 y 12 horas.")

    def calcular_costo(self, duracion):
        self.validar_parametros(duracion)
        return self.precio_base * float(duracion)

    def describir(self):
        return f"SALA | {self.nombre} | Capacidad: {self.capacidad} personas | ${self.precio_base:,.0f}/hora"


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, precio_base, equipo, disponible=True):
        super().__init__(identificador, nombre, precio_base, disponible)
        self.equipo = str(equipo).strip()
        if not self.equipo:
            raise DatosInvalidosError("Debe indicar el equipo.")

    def validar_parametros(self, duracion):
        duracion = float(duracion)
        if duracion <= 0 or duracion > 168:
            raise DatosInvalidosError("El alquiler debe ser entre 0 y 168 horas.")

    def calcular_costo(self, duracion):
        self.validar_parametros(duracion)
        return self.precio_base * float(duracion)

    def describir(self):
        return f"EQUIPO | {self.nombre} ({self.equipo}) | ${self.precio_base:,.0f}/hora"


class Asesoria(Servicio):
    def __init__(self, identificador, nombre, precio_base, especialidad, disponible=True):
        super().__init__(identificador, nombre, precio_base, disponible)
        self.especialidad = str(especialidad).strip()
        if not self.especialidad:
            raise DatosInvalidosError("Debe indicar la especialidad.")

    def validar_parametros(self, duracion):
        duracion = float(duracion)
        if duracion <= 0 or duracion > 8:
            raise DatosInvalidosError("La asesoría debe ser entre 0 y 8 horas.")

    def calcular_costo(self, duracion):
        self.validar_parametros(duracion)
        return self.precio_base * float(duracion)

    def describir(self):
        return f"ASESORÍA | {self.nombre} | Especialidad: {self.especialidad} | ${self.precio_base:,.0f}/hora"


# ================================= RESERVA =================================
class Reserva:
    def __init__(self, identificador, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Seleccione un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Seleccione un servicio válido.")
        servicio.verificar_disponibilidad()
        servicio.validar_parametros(float(duracion))
        self.identificador = identificador
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = float(duracion)
        self.estado = "Pendiente"
        self.total = 0.0

    def confirmar(self, descuento=0, impuesto=0):
        if self.estado != "Pendiente":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")
        try:
            self.total = self.servicio.calcular_total(self.duracion, descuento, impuesto)
            self.estado = "Confirmada"
            logging.info("Reserva #%s confirmada por $%.2f", self.identificador, self.total)
            return self.total
        except Exception as error:
            logging.exception("Error confirmando reserva #%s", self.identificador)
            raise ReservaError("No fue posible confirmar la reserva.") from error

    def cancelar(self):
        if self.estado != "Pendiente":
            raise ReservaError("Solo se pueden cancelar reservas pendientes.")
        self.estado = "Cancelada"
        logging.info("Reserva #%s cancelada.", self.identificador)

    def describir(self):
        return (f"#{self.identificador} | {self.cliente.nombre} | {self.servicio.nombre} | "
                f"{self.duracion:g} h | {self.estado} | ${self.total:,.0f}")


# ============================= SISTEMA / DATOS ==============================
class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self._id_cliente = 1
        self._id_servicio = 1
        self._id_reserva = 1
        logging.info("Sistema Software FJ iniciado.")

    def registrar_cliente(self, nombre, documento, correo, telefono):
        cliente = Cliente(self._id_cliente, nombre, documento, correo, telefono)
        if any(c.documento == cliente.documento for c in self.clientes):
            raise DatosInvalidosError("Ya existe un cliente con ese documento.")
        self.clientes.append(cliente)
        self._id_cliente += 1
        logging.info("Cliente registrado: %s", cliente.nombre)
        return cliente

    def crear_servicio(self, tipo, nombre, precio, dato):
        ident = self._id_servicio
        tipo = tipo.lower()
        if tipo == "sala":
            nuevo = ReservaSala(ident, nombre, precio, dato)
        elif tipo == "equipo":
            nuevo = AlquilerEquipo(ident, nombre, precio, dato)
        elif tipo == "asesoria":
            nuevo = Asesoria(ident, nombre, precio, dato)
        else:
            raise DatosInvalidosError("Tipo de servicio no reconocido.")
        self.servicios.append(nuevo)
        self._id_servicio += 1
        logging.info("Servicio creado: %s", nuevo.nombre)
        return nuevo

    def crear_reserva(self, cliente_id, servicio_id, duracion):
        cliente = next((c for c in self.clientes if c.identificador == cliente_id), None)
        servicio = next((s for s in self.servicios if s.identificador == servicio_id), None)
        if cliente is None:
            raise ClienteNoEncontradoError("No se encontró el cliente.")
        if servicio is None:
            raise ServicioNoDisponibleError("No se encontró el servicio.")
        reserva = Reserva(self._id_reserva, cliente, servicio, duracion)
        self.reservas.append(reserva)
        self._id_reserva += 1
        logging.info("Reserva #%s creada.", reserva.identificador)
        return reserva

    def buscar_reserva(self, reserva_id):
        reserva = next((r for r in self.reservas if r.identificador == reserva_id), None)
        if reserva is None:
            raise ReservaError("No se encontró la reserva.")
        return reserva


# =============================== INTERFAZ GUI ===============================
class AplicacionSoftwareFJ(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sistema = SistemaSoftwareFJ()
        self.title("Software FJ | Gestión de clientes, servicios y reservas")
        self.geometry("1120x720")
        self.minsize(1000, 650)
        self.configure(bg="#e792d5")
        self._estilos()
        self._crear_layout()
        self._actualizar_tablas()
        self.protocol("WM_DELETE_WINDOW", self._salir)

    def _estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(12, 8))

    def _crear_layout(self):
        header = tk.Frame(self, bg="#91b7e2", height=95)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SOFTWARE FJ", font=("Segoe UI", 23, "bold"),
                 fg="white", bg="#8ca0e2").pack(anchor="w", padx=25, pady=(14, 0))
        tk.Label(header, text="Sistema integral de gestión de clientes, servicios y reservas",
                 font=("Segoe UI", 11), fg="#dbeafe", bg="#91b7e2").pack(anchor="w", padx=27)

        self.status = tk.StringVar(value="Sistema listo. Información gestionada en memoria.")
        tk.Label(self, textvariable=self.status, bg="#dbeafe", fg="#12345a",
                 font=("Segoe UI", 9), anchor="w", padx=12, pady=6).pack(fill="x")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=14)

        self.tab_clientes = ttk.Frame(self.tabs, padding=12)
        self.tab_servicios = ttk.Frame(self.tabs, padding=12)
        self.tab_reservas = ttk.Frame(self.tabs, padding=12)
        self.tab_pruebas = ttk.Frame(self.tabs, padding=12)
        self.tab_logs = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.tab_clientes, text="Clientes")
        self.tabs.add(self.tab_servicios, text="Servicios")
        self.tabs.add(self.tab_reservas, text="Reservas")
        self.tabs.add(self.tab_pruebas, text="Pruebas del sistema")
        self.tabs.add(self.tab_logs, text="Registro / Logs")
        self._crear_tab_clientes()
        self._crear_tab_servicios()
        self._crear_tab_reservas()
        self._crear_tab_pruebas()
        self._crear_tab_logs()

        footer = tk.Frame(self, bg="#eef2f7")
        footer.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(footer, text="UNAD | Curso Programación 213023 | Aplicación académica",
                 bg="#eef2f7", fg="#526274", font=("Segoe UI", 9)).pack(side="left")
        ttk.Button(footer, text="Cerrar aplicación", command=self._salir).pack(side="right")

    def _form(self, parent, title, fields):
        box = ttk.LabelFrame(parent, text=title, padding=12)
        box.pack(fill="x", pady=(0, 12))
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(box, text=label).grid(row=i, column=0, sticky="w", padx=(0, 10), pady=5)
            entry = ttk.Entry(box, width=42)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            entries[key] = entry
        box.columnconfigure(1, weight=1)
        return box, entries

    def _crear_tab_clientes(self):
        _, self.cli_entries = self._form(
            self.tab_clientes, "Registrar cliente",
            [("Nombre completo:", "nombre"), ("Documento:", "documento"),
             ("Correo electrónico:", "correo"), ("Teléfono:", "telefono")]
        )
        ttk.Button(self.tab_clientes, text="Registrar cliente", command=self._registrar_cliente).pack(anchor="w", pady=(0, 12))
        frame = ttk.LabelFrame(self.tab_clientes, text="Clientes registrados", padding=8)
        frame.pack(fill="both", expand=True)
        cols = ("id", "nombre", "documento", "correo", "telefono")
        self.tree_clientes = ttk.Treeview(frame, columns=cols, show="headings")
        labels = {"id":"ID", "nombre":"Nombre", "documento":"Documento", "correo":"Correo", "telefono":"Teléfono"}
        widths = {"id":55, "nombre":190, "documento":140, "correo":250, "telefono":140}
        for c in cols:
            self.tree_clientes.heading(c, text=labels[c])
            self.tree_clientes.column(c, width=widths[c], anchor="w")
        self.tree_clientes.pack(fill="both", expand=True)

    def _registrar_cliente(self):
        try:
            e = self.cli_entries
            cliente = self.sistema.registrar_cliente(*(e[k].get() for k in ("nombre", "documento", "correo", "telefono")))
            self._actualizar_tablas()
            for campo in e.values():
                campo.delete(0, "end")
            messagebox.showinfo("Registro exitoso", f"Cliente {cliente.nombre} registrado.")
            self.status.set("Cliente registrado correctamente.")
        except Exception as exc:
            logging.exception("Fallo en formulario de cliente")
            messagebox.showerror("No se pudo registrar", str(exc))
            self.status.set("Se detectó un error en el registro del cliente.")

    def _crear_tab_servicios(self):
        frame = ttk.LabelFrame(self.tab_servicios, text="Crear servicio", padding=12)
        frame.pack(fill="x", pady=(0, 12))
        ttk.Label(frame, text="Tipo:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.s_tipo = ttk.Combobox(frame, values=("sala", "equipo", "asesoria"), state="readonly", width=39)
        self.s_tipo.current(0)
        self.s_tipo.grid(row=0, column=1, sticky="ew", pady=5)
        labels = [("Nombre:", "nombre"), ("Tarifa por hora ($):", "precio"),
                  ("Dato adicional (capacidad/equipo/especialidad):", "dato")]
        self.s_entries = {}
        for i, (label, key) in enumerate(labels, start=1):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", padx=(0, 10), pady=5)
            entry = ttk.Entry(frame, width=42)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            self.s_entries[key] = entry
        frame.columnconfigure(1, weight=1)
        ttk.Button(frame, text="Crear servicio", command=self._crear_servicio).grid(row=4, column=1, sticky="w", pady=8)
        listado = ttk.LabelFrame(self.tab_servicios, text="Servicios creados", padding=8)
        listado.pack(fill="both", expand=True)
        cols = ("id", "tipo", "nombre", "precio", "detalle")
        self.tree_servicios = ttk.Treeview(listado, columns=cols, show="headings")
        for c, label, width in zip(cols, ("ID", "Tipo", "Nombre", "Tarifa", "Detalle"), (55, 100, 180, 120, 380)):
            self.tree_servicios.heading(c, text=label)
            self.tree_servicios.column(c, width=width, anchor="w")
        self.tree_servicios.pack(fill="both", expand=True)

    def _crear_servicio(self):
        try:
            tipo = self.s_tipo.get()
            nombre = self.s_entries["nombre"].get()
            precio = convertir_numero(self.s_entries["precio"].get())
            dato = self.s_entries["dato"].get()
            if tipo == "sala":
                dato = int(convertir_numero(dato))
            servicio = self.sistema.crear_servicio(tipo, nombre, precio, dato)
            self._actualizar_tablas()
            for e in self.s_entries.values():
                e.delete(0, "end")
            messagebox.showinfo("Servicio creado", f"Se creó: {servicio.nombre}")
            self.status.set("Servicio creado correctamente.")
        except Exception as exc:
            logging.exception("Fallo en formulario de servicio")
            messagebox.showerror("Error de servicio", str(exc))

    def _crear_tab_reservas(self):
        frame = ttk.LabelFrame(self.tab_reservas, text="Crear reserva", padding=12)
        frame.pack(fill="x", pady=(0, 12))
        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.r_cliente = ttk.Combobox(frame, state="readonly", width=55)
        self.r_cliente.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Servicio:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.r_servicio = ttk.Combobox(frame, state="readonly", width=55)
        self.r_servicio.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Duración (horas):").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.r_duracion = ttk.Entry(frame, width=42)
        self.r_duracion.grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="Crear reserva pendiente", command=self._crear_reserva).grid(row=3, column=1, sticky="w", pady=8)
        frame.columnconfigure(1, weight=1)

        acciones = ttk.Frame(self.tab_reservas)
        acciones.pack(fill="x", pady=(0, 8))
        ttk.Button(acciones, text="Confirmar reserva seleccionada", command=self._confirmar_reserva).pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Cancelar reserva seleccionada", command=self._cancelar_reserva).pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Actualizar listado", command=self._actualizar_tablas).pack(side="left")

        listado = ttk.LabelFrame(self.tab_reservas, text="Reservas", padding=8)
        listado.pack(fill="both", expand=True)
        cols = ("id", "cliente", "servicio", "duracion", "estado", "total")
        self.tree_reservas = ttk.Treeview(listado, columns=cols, show="headings")
        for c, label, width in zip(cols, ("ID", "Cliente", "Servicio", "Horas", "Estado", "Total"), (55, 180, 200, 80, 110, 130)):
            self.tree_reservas.heading(c, text=label)
            self.tree_reservas.column(c, width=width, anchor="w")
        self.tree_reservas.pack(fill="both", expand=True)

    def _crear_reserva(self):
        try:
            if not self.r_cliente.get() or not self.r_servicio.get():
                raise DatosInvalidosError("Seleccione cliente y servicio.")
            cliente_id = int(self.r_cliente.get().split(" | ")[0])
            servicio_id = int(self.r_servicio.get().split(" | ")[0])
            duracion = convertir_numero(self.r_duracion.get())
            reserva = self.sistema.crear_reserva(cliente_id, servicio_id, duracion)
            self._actualizar_tablas()
            self.r_duracion.delete(0, "end")
            messagebox.showinfo("Reserva creada", f"Reserva #{reserva.identificador} creada en estado Pendiente.")
        except Exception as exc:
            logging.exception("Fallo creando reserva desde GUI")
            messagebox.showerror("Error al crear reserva", str(exc))

    def _seleccion_reserva(self):
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Seleccione una reserva en la tabla.")
            return None
        return int(self.tree_reservas.item(seleccion[0], "values")[0])

    def _confirmar_reserva(self):
        try:
            reserva_id = self._seleccion_reserva()
            if reserva_id is None:
                return
            descuento = simpledialog.askfloat("Descuento", "Ingrese descuento (%)", parent=self, minvalue=0, maxvalue=100)
            if descuento is None:
                return
            impuesto = simpledialog.askfloat("Impuesto", "Ingrese impuesto (%)", parent=self, minvalue=0, maxvalue=100)
            if impuesto is None:
                return
            reserva = self.sistema.buscar_reserva(reserva_id)
            total = reserva.confirmar(descuento, impuesto)
            self._actualizar_tablas()
            messagebox.showinfo("Reserva confirmada", f"Total de la reserva: ${total:,.0f}")
        except Exception as exc:
            logging.exception("Fallo confirmando reserva")
            messagebox.showerror("No se pudo confirmar", str(exc))

    def _cancelar_reserva(self):
        try:
            reserva_id = self._seleccion_reserva()
            if reserva_id is None:
                return
            self.sistema.buscar_reserva(reserva_id).cancelar()
            self._actualizar_tablas()
            messagebox.showinfo("Reserva cancelada", "La reserva quedó cancelada.")
        except Exception as exc:
            logging.exception("Fallo cancelando reserva")
            messagebox.showerror("No se pudo cancelar", str(exc))

    def _crear_tab_pruebas(self):
        intro = ttk.Label(self.tab_pruebas, text="Ejecuta una secuencia de operaciones válidas e inválidas para demostrar el funcionamiento y control de errores.",
                          wraplength=900)
        intro.pack(anchor="w", pady=(0, 12))
        ttk.Button(self.tab_pruebas, text="Ejecutar 15 pruebas automáticas", command=self._ejecutar_pruebas).pack(anchor="w", pady=(0, 10))
        self.test_text = tk.Text(self.tab_pruebas, height=24, wrap="word", font=("Consolas", 10), bg="#ffffff")
        self.test_text.pack(fill="both", expand=True)
        self.test_text.insert("end", "Aquí aparecerá el resultado de las pruebas automáticas.\n")
        self.test_text.configure(state="disabled")

    def _ejecutar_pruebas(self):
        # Las pruebas se ejecutan en un sistema independiente para no alterar los datos de la interfaz.
        test = SistemaSoftwareFJ()
        resultados = []
        def prueba(nombre, accion):
            try:
                accion()
                resultados.append(f"✓ {nombre} — OK")
                logging.info("Prueba OK: %s", nombre)
            except Exception as ex:
                resultados.append(f"✗ {nombre} — {ex}")
                logging.error("Prueba fallida %s: %s", nombre, ex)

        def prueba_error_esperado(nombre, accion):
            try:
                accion()
                resultados.append(f"✗ {nombre} — Se esperaba un error, pero la operación fue aceptada")
                logging.error("Prueba fallida: no se generó el error esperado: %s", nombre)
            except ErrorSistema as ex:
                resultados.append(f"✓ {nombre} — Error controlado correctamente ({ex})")
                logging.info("Prueba de error esperado OK: %s", nombre)
            except Exception as ex:
                resultados.append(f"✗ {nombre} — Tipo de error inesperado: {ex}")
                logging.exception("Prueba de error inesperado: %s", nombre)

        c1 = test.registrar_cliente("Carlos Ramírez", "100100100", "carlos@gmail.com", "3001234567")
        prueba("1. Registro cliente válido", lambda: None)
        prueba_error_esperado("2. Rechazo de cliente con correo inválido",
               lambda: test.registrar_cliente("Ana", "2", "correo-mal", "123"))
        c2 = test.registrar_cliente("Laura Martínez", "200200200", "laura@gmail.com", "3109876543")
        prueba("3. Registro de segundo cliente", lambda: None)
        sala = test.crear_servicio("sala", "Sala de reuniones", 50000, 20)
        prueba("4. Creación de sala", lambda: None)
        equipo = test.crear_servicio("equipo", "Portátil", 15000, "Computador")
        prueba("5. Creación de equipo", lambda: None)
        asesoria = test.crear_servicio("asesoria", "Asesoría de software", 80000, "Programación")
        prueba("6. Creación de asesoría", lambda: None)
        prueba_error_esperado("7. Rechazo de servicio con precio negativo",
               lambda: test.crear_servicio("sala", "Sala inválida", -5, 10))
        r1 = test.crear_reserva(c1.identificador, sala.identificador, 2)
        prueba("8. Creación de reserva válida", lambda: None)
        total = r1.confirmar(10, 19)
        prueba("9. Confirmación y cálculo de total", lambda: None)
        prueba_error_esperado("10. Rechazo de duración negativa",
               lambda: test.crear_reserva(c1.identificador, sala.identificador, -2))
        r2 = test.crear_reserva(c2.identificador, equipo.identificador, 3)
        prueba("11. Reserva de equipo", lambda: None)
        r2.cancelar()
        prueba("12. Cancelación de reserva pendiente", lambda: None)
        prueba_error_esperado("13. Rechazo de cancelación de reserva confirmada", lambda: r1.cancelar())
        prueba_error_esperado("14. Rechazo de servicio inexistente",
               lambda: test.crear_reserva(c1.identificador, 999, 1))
        prueba("15. Cálculo con descuento e impuesto", lambda: sala.calcular_total(2, 10, 19))
        resumen = "\n".join(resultados) + f"\n\nTotal de operaciones: {len(resultados)}\nTotal de reserva confirmada de prueba: ${total:,.0f}\n"
        self.test_text.configure(state="normal")
        self.test_text.delete("1.0", "end")
        self.test_text.insert("end", resumen)
        self.test_text.configure(state="disabled")
        messagebox.showinfo("Pruebas terminadas", f"Se ejecutaron {len(resultados)} operaciones. Consulte el resultado en esta pestaña.")
        logging.info("Pruebas GUI finalizadas.")

    def _crear_tab_logs(self):
        ttk.Button(self.tab_logs, text="Actualizar registros", command=self._mostrar_logs).pack(anchor="w", pady=(0, 8))
        self.log_text = tk.Text(self.tab_logs, wrap="word", font=("Consolas", 9), bg="white")
        self.log_text.pack(fill="both", expand=True)
        self._mostrar_logs()

    def _mostrar_logs(self):
        self.log_text.delete("1.0", "end")
        try:
            with open("registro_sistema.log", "r", encoding="utf-8") as f:
                self.log_text.insert("end", f.read() or "El archivo de registro está vacío.")
        except FileNotFoundError:
            self.log_text.insert("end", "Aún no se ha generado el archivo de logs.")

    def _actualizar_tablas(self):
        for tree in (getattr(self, "tree_clientes", None), getattr(self, "tree_servicios", None), getattr(self, "tree_reservas", None)):
            if tree:
                for item in tree.get_children():
                    tree.delete(item)
        if hasattr(self, "tree_clientes"):
            for c in self.sistema.clientes:
                self.tree_clientes.insert("", "end", values=(c.identificador, c.nombre, c.documento, c.correo, c.telefono))
        if hasattr(self, "tree_servicios"):
            for s in self.sistema.servicios:
                tipo = "Sala" if isinstance(s, ReservaSala) else "Equipo" if isinstance(s, AlquilerEquipo) else "Asesoría"
                detalle = s.describir()
                self.tree_servicios.insert("", "end", values=(s.identificador, tipo, s.nombre, f"${s.precio_base:,.0f}", detalle))
        if hasattr(self, "tree_reservas"):
            for r in self.sistema.reservas:
                self.tree_reservas.insert("", "end", values=(r.identificador, r.cliente.nombre, r.servicio.nombre, f"{r.duracion:g}", r.estado, f"${r.total:,.0f}"))
        if hasattr(self, "r_cliente"):
            self.r_cliente["values"] = [f"{c.identificador} | {c.nombre} | CC {c.documento}" for c in self.sistema.clientes]
        if hasattr(self, "r_servicio"):
            self.r_servicio["values"] = [f"{s.identificador} | {s.nombre} | ${s.precio_base:,.0f}" for s in self.sistema.servicios]

    def _salir(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar Software FJ?"):
            logging.info("Aplicación cerrada por el usuario.")
            self.destroy()


def convertir_numero(valor):
    try:
        numero = float(valor)
    except ValueError as error:
        logging.error("Entrada numérica inválida: %s", valor)
        raise DatosInvalidosError("Ingrese un número válido.") from error
    else:
        return numero


if __name__ == "__main__":
    try:
        app = AplicacionSoftwareFJ()
        app.mainloop()
    except KeyboardInterrupt:
        logging.warning("Interrupción manual.")
    except Exception as error:
        logging.exception("Error crítico al iniciar GUI")
        messagebox.showerror("Error crítico", str(error))

