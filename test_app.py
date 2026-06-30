from app import registrar_inscripcion, actualizar_cupos

def test_registrar_inscripcion():
    assert registrar_inscripcion(5) == True

def test_flujo_inscripcion():
    cupos = 10

    if registrar_inscripcion(cupos):
        cupos = actualizar_cupos(cupos)

    assert cupos == 9