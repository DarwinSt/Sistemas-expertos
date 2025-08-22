def Taller_mecanico ():
    print("Bienvenido al Taller Mecánico")

    arrancado = input("¿El auto arranca? (s/n): ").lower()
    luces = input("¿Las luces del tablero funcionan? (s/n): ").lower()
    apagado = input("¿El auto se apaga al acelerar? (s/n): ").lower()
    humow = input("¿Sale humo blanco del escape? (s/n): ").lower()
    humob = input("¿Sale humo negro del escape? (s/n)").lower()

    if arrancado == 'n' and luces == 'n':
        print("Posible causa: batería descargada.")
    elif arrancado == 'n' and luces == 's':
        print("Posible causa: motor de arranque dañado.")
    elif arrancado == 's' and apagado == 's':
        print("Posible causa: problema en el suministro de combustible.")
    elif humob == 's':
        print ("Posible causa: mezcla rica de combustible.")
    elif humow == 's':
        print ("Posible causa: falla en la junta de culata.")
    else:
        print ("No hay una posible causa, contactese con un asesor")
    
if __name__ == "__main__":
    Taller_mecanico()