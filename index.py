import argparse
import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

# ------------------------- Utilidades de entrada (interactivo) -------------------------
def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} [s/n]: ").strip().lower()
        if ans in ("s", "si", "sí", "y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("👉 Responde con 's' para sí o 'n' para no.")

def ask_choice(prompt: str, options: List[str]) -> str:
    opts = {str(i + 1): opt for i, opt in enumerate(options)}
    while True:
        print(prompt)
        for num, opt in opts.items():
            print(f"  {num}. {opt}")
        ans = input("Elige una opción: ").strip()
        if ans in opts:
            return opts[ans]
        print("👉 Opción inválida, intenta de nuevo.")

# ------------------------- Estructuras de Regla -------------------------
@dataclass
class Rule:
    name: str
    check: Callable[[Dict[str, object]], bool]
    diagnosis: str
    explanation: str

# ------------------------- Motor de inferencia -------------------------
class ExpertSystem:
    def __init__(self, rules: List[Rule], facts: Dict[str, object]):
        self.rules = rules
        self.facts: Dict[str, object] = facts

    def infer(self) -> List[Tuple[Rule, str]]:
        results: List[Tuple[Rule, str]] = []
        for rule in self.rules:
            try:
                if rule.check(self.facts):
                    results.append((rule, rule.diagnosis))
            except Exception as e:
                print(f"(Advertencia) Error en la regla '{rule.name}': {e}")
        return results

    def show_results(self, matches: List[Tuple[Rule, str]]) -> None:
        print("\n=== Resultado ===")
        if not matches:
            print("No se encontró un diagnóstico con las reglas actuales.")
            return
        for i, (rule, diag) in enumerate(matches, 1):
            print(f"{i}. Posible causa: {diag}")
            print(f"   (Regla: {rule.name})")
            print(f"   ¿Por qué?: {rule.explanation}\n")

# ------------------------- Reglas -------------------------
def build_rules() -> List[Rule]:
    return [
        Rule(
            name="No arranca + tablero apagado",
            check=lambda f: (f.get("arranca") is False) and (f.get("tablero") is False),
            diagnosis="batería descargada",
            explanation="Si el auto no arranca y el tablero está apagado, suele ser batería descargada.",
        ),
        Rule(
            name="No arranca + tablero encendido",
            check=lambda f: (f.get("arranca") is False) and (f.get("tablero") is True),
            diagnosis="fallo en el motor de arranque",
            explanation="Si el tablero enciende pero el motor no gira, suele ser el motor de arranque o su circuito.",
        ),
        Rule(
            name="Se apaga al acelerar",
            check=lambda f: (f.get("arranca") is True) and (f.get("apaga_al_acelerar") is True),
            diagnosis="problema en el suministro de combustible",
            explanation="Apagarse al acelerar apunta a filtro tapado, bomba débil o inyección.",
        ),
        Rule(
            name="Humo negro",
            check=lambda f: (f.get("humo") == "negro"),
            diagnosis="mezcla rica de combustible",
            explanation="El humo negro indica exceso de combustible en la mezcla aire/combustible.",
        ),
        Rule(
            name="Humo blanco constante",
            check=lambda f: (f.get("humo") == "blanco_constante"),
            diagnosis="falla en la junta de culata",
            explanation="El humo blanco continuo puede ser refrigerante quemándose por daño en la junta de culata.",
        ),
    ]

# ------------------------- Modo interactivo -------------------------
def run_interactive():
    print("=== Sistema Experto: Diagnóstico de Fallas de Automóvil (Interactivo) ===\n")
    facts: Dict[str, object] = {}

    arranca = ask_yes_no("¿El auto arranca?")
    facts["arranca"] = arranca

    if not arranca:
        tablero = ask_yes_no("¿Las luces del tablero encienden?")
        facts["tablero"] = tablero
    else:
        apaga = ask_yes_no("¿El auto se apaga al acelerar?")
        facts["apaga_al_acelerar"] = apaga
        # Si arranca, el tablero no es relevante; lo marcamos como True por neutralidad
        facts.setdefault("tablero", True)

    hay_humo = ask_yes_no("¿Sale humo notable por el escape?")
    if hay_humo:
        color = ask_choice("¿De qué color es el humo?", ["Negro", "Blanco", "Blanco (constante)", "Ninguno/No seguro"])
        if color.lower().startswith("negro"):
            facts["humo"] = "negro"
        elif color.lower().startswith("blanco (constante)"):
            facts["humo"] = "blanco_constante"
        elif color.lower().startswith("blanco"):
            # Solo blanco NO constante no dispara la regla de junta (sigues sin diagnóstico por humo)
            facts["humo"] = "blanco"
        else:
            facts["humo"] = "ninguno"
    else:
        facts["humo"] = "ninguno"

    es = ExpertSystem(build_rules(), facts)
    matches = es.infer()
    es.show_results(matches)

# ------------------------- Modo CLI -------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Sistema Experto de Diagnóstico Automotriz")
    parser.add_argument("--modo", choices=["cli", "interactivo"], default=None,
                        help="Selecciona 'cli' para parámetros o 'interactivo' para preguntas.")
    # En CLI, todos los argumentos son OPCIONALES (tienen default) para que no bloquee.
    parser.add_argument("--arranca", choices=["si", "no"], default=None,
                        help="¿El auto arranca? (si/no)")
    parser.add_argument("--tablero", choices=["si", "no"], default=None,
                        help="¿El tablero enciende? (solo importa si arranca=no)")
    parser.add_argument("--apaga_al_acelerar", choices=["si", "no"], default=None,
                        help="¿Se apaga al acelerar? (solo importa si arranca=si)")
    parser.add_argument("--humo", choices=["ninguno", "negro", "blanco", "blanco_constante"],
                        default=None, help="Tipo de humo (ninguno/negro/blanco/blanco_constante)")
    return parser.parse_args()

def run_cli(args):
    print("=== Sistema Experto: Diagnóstico de Fallas de Automóvil (CLI) ===\n")

    # Defaults sensatos si no pasaron flags
    arranca = {"si": True, "no": False}.get(args.arranca, True)  # por defecto asumimos que arranca
    tablero = {"si": True, "no": False}.get(args.tablero, True)
    apaga = {"si": True, "no": False}.get(args.apaga_al_acelerar, False)
    humo = args.humo or "ninguno"

    # Coherencia mínima: si arranca=True, el tablero es irrelevante; si arranca=False y tablero no fue dado, asumimos False.
    if arranca and args.tablero is None:
        tablero = True
    if not arranca and args.tablero is None:
        tablero = False

    facts = {
        "arranca": arranca,
        "tablero": tablero,
        "apaga_al_acelerar": apaga,
        "humo": humo,
    }

    es = ExpertSystem(build_rules(), facts)
    matches = es.infer()
    es.show_results(matches)

# ------------------------- Main -------------------------
def main():
    args = parse_args()

    # Si el usuario pide explícitamente un modo, respétalo.
    if args.modo == "cli":
        run_cli(args)
        return
    if args.modo == "interactivo":
        run_interactive()
        return

    # Si NO se especifica modo:
    # - Si llegaron flags relevantes, asumimos CLI.
    # - Si no, vamos a interactivo (preguntas).
    passed_flags = any(
        v is not None for v in [args.arranca, args.tablero, args.apaga_al_acelerar, args.humo]
    )
    if passed_flags:
        run_cli(args)
    else:
        run_interactive()

if __name__ == "__main__":
    main()
