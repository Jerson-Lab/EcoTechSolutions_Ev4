
from base_datos import inicializar_base_datos
from proyectos import Proyecto, RepositorioProyectos


inicializar_base_datos()

repositorio = RepositorioProyectos()

proyecto = Proyecto(
    nombre="Instalación de paneles solares",
    descripcion="Implementación de energía renovable",
    ciudad="Chillán",
    fecha_inicio="2026-12-01",
    fecha_fin="2027-02-15",
    presupuesto_centavos=150000000,
    moneda="CLP",
    estado="planificado"
)

nuevo_id = repositorio.registrar(proyecto)

print(f"\nProyecto registrado con ID: {nuevo_id}")

print("\n=== PROYECTOS REGISTRADOS ===")

for p in repositorio.listar():
    print(f"ID: {p.id}")
    print(f"Nombre: {p.nombre}")
    print(f"Ciudad: {p.ciudad}")
    print(f"Estado: {p.estado}")
    print(f"Presupuesto: {p.presupuesto_centavos / 100:.2f} {p.moneda}")
    print("---------------------------")
