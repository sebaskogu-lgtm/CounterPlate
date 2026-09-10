import math

def calcular_parametros_hendido(s):
    """
    Calcula los parámetros de hendido según el espesor del cartón (s) en mm.
    Soporta Regla 2PT (0.71 mm).
    """
    regla_espesor = 0.71  # 2PT

    # 1. PERFIL SHOP FLOOR / TALLER (Regla Fija 23.80 mm en Steel 1.00 mm)
    sf_regla_altura = 23.80
    sf_chapa_espesor = 1.00
    # Profundidad: s + 0.10 mm (redondeado a 0.05 mm superior)
    sf_profundidad = round(math.ceil((s + 0.10) * 20) / 20, 2)
    sf_ancho_par = round(regla_espesor + (1.60 * s), 2)
    sf_ancho_cross = round(regla_espesor + (1.85 * s), 2)
    sf_ancho_unico = round(math.ceil(sf_ancho_cross * 20) / 20, 2)

    # 2. PERFIL MARBACH SPEC (Regla Rebajada / Variable en Steel 1.00 mm)
    mb_chapa_espesor = 1.00
    mb_profundidad = round(s + 0.05, 2)
    
    # Altura de regla según tabla Marbach para chapa metálica
    if s <= 0.35:
        mb_regla_altura = 23.60
    elif s <= 0.50:
        mb_regla_altura = 23.65
    else:
        mb_regla_altura = 23.70
        
    mb_ancho_par = round(regla_espesor + (1.50 * s), 2)
    mb_ancho_cross = round(regla_espesor + (1.75 * s), 2)
    mb_ancho_unico = round(math.ceil(mb_ancho_cross * 20) / 20, 2)

    # 3. PERFIL PERTINAX TRADICIONAL (Referencia)
    pt_profundidad = round(s, 2)
    pt_regla_altura = round(23.80 - pt_profundidad, 2)
    pt_ancho_par = round(regla_espesor + (1.40 * s), 2)
    pt_ancho_cross = round(regla_espesor + (1.60 * s), 2)
    pt_ancho_unico = round(math.ceil(pt_ancho_cross * 20) / 20, 2)

    return [
        {
            "perfil": "1. SHOP FLOOR (Regla Fija - Máxima Tolerancia)",
            "sistema": "Steel Counterplate (1.00 mm)",
            "regla_altura": f"{sf_regla_altura:.2f} mm (FIJA)",
            "profundidad": f"{sf_profundidad:.2f} mm",
            "ancho_par": f"{sf_ancho_par:.2f} mm",
            "ancho_cross": f"{sf_ancho_cross:.2f} mm",
            "ancho_unico": f"{sf_ancho_unico:.2f} mm",
            "nota": "Permite variaciones de fresado/papel. Altura de regla estándar en troquel."
        },
        {
            "perfil": "2. MARBACH SPEC (Regla Rebajada - Alta Velocidad)",
            "sistema": "Steel Counterplate (1.00 mm)",
            "regla_altura": f"{mb_regla_altura:.2f} mm (REBAJADA)",
            "profundidad": f"{mb_profundidad:.2f} mm",
            "ancho_par": f"{mb_ancho_par:.2f} mm",
            "ancho_cross": f"{mb_ancho_cross:.2f} mm",
            "ancho_unico": f"{mb_ancho_unico:.2f} mm",
            "nota": "Ajuste teórico estrecho. Requiere pedir flejes de altura especial."
        },
        {
            "perfil": "3. PERTINAX TRADICIONAL (Referencia)",
            "sistema": "Matriz Pertinax / Rillma",
            "regla_altura": f"{pt_regla_altura:.2f} mm (23.80 - D)",
            "profundidad": f"{pt_profundidad:.2f} mm",
            "ancho_par": f"{pt_ancho_par:.2f} mm",
            "ancho_cross": f"{pt_ancho_cross:.2f} mm",
            "ancho_unico": f"{pt_ancho_unico:.2f} mm",
            "nota": "La altura de regla varía directamente según el espesor de la tira."
        }
    ]

def mostrar_reporte(s):
    resultados = calcular_parametros_hendido(s)
    print("\n" + "="*75)
    print(f"   ESPECIFICACIONES DE HENDIDO PARA CARTÓN: {s:.2f} mm (Regla 2PT / 0.71 mm)")
    print("="*75)
    
    for r in resultados:
        print(f"\n---> {r['perfil']}")
        print(f"     Sistema:                  {r['sistema']}")
        print(f"     ALTURA REGLA DE MARCADO:  {r['regla_altura']}  <--- [CRÍTICO]")
        print(f"     Profundidad del Canal:    {r['profundidad']}")
        print(f"     Ancho A Favor (Parallel): {r['ancho_par']}")
        print(f"     Ancho A Contra (Cross):   {r['ancho_cross']}")
        print(f"     Ancho Unificado Seguro:   {r['ancho_unico']}")
        print(f"     Nota Técnica:             {r['nota']}")
        print("-" * 75)

# --- BUCLE PRINCIPAL EN REPLIT ---
if __name__ == "__main__":
    print("Calculadora de Matriz y Reglas de Marcado (Steel / Marbach / Pertinax)")
    while True:
        try:
            entrada = input("\nIngrese el espesor del cartón en mm (ej. 0.40) o 's' para salir: ")
            if entrada.lower() == 's':
                break
            espesor = float(entrada)
            if espesor <= 0:
                print("El espesor debe ser mayor a 0.")
                continue
            mostrar_reporte(espesor)
        except ValueError:
            print("Entrada inválida. Ingrese un número decimal (ej. 0.40 o 0.45).")