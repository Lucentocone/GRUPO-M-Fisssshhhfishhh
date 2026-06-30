Feature: Inscripción a eventos académicos

  Scenario: Inscripción exitosa con cupos disponibles

    Given un evento con 10 cupos disponibles
    And un participante registrado
    When el participante solicita la inscripción
    Then la inscripción es aprobada
    And los cupos disponibles pasan a ser 9