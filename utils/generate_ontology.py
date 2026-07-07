#!/usr/bin/env python3
import rules_and_concepts as rules_and_concepts
MainOperations = rules_and_concepts.MainOperations
"""
Generate ontology.owl from Python rule definitions.

Edit BUILDING_CLASSES, FEATURE_CLASSES, HIERARCHY, EQUIV_RULES,
SUBCLASS_RULES, DISJOINT_SETS, and INDIVIDUALS below, then run:

    python generate_ontology.py

The file uses the same expression syntax as rules_and_concepts.py:
  AND(A, B)   →  ObjectIntersectionOf
  OR(A, B)    →  ObjectUnionOf
  NOT(A)      →  ObjectComplementOf
  ClassName   →  ObjectSomeValuesFrom( #has, #ClassName )
"""

BASE_IRI = "http://www.semanticweb.org/wezxe/ontologies/2026_buildings"

# ── Edit these sections ───────────────────────────────────────────────────────
'''
BUILDING_CLASSES = [
    "Building", "Feature",
    "Commercial", "Industrial", "Residential",
    "Cafe", "Hotel", "MiscCommercial", "Restaurant", "Store",
    "ConstructionSite", "MiscIndustrial", "PowerPlant", "WaterTreatment",
    "CountryHouse", "MiscResidential", "Suburban",
]

FEATURE_CLASSES = [
    "Awning", "Billboard", "Car", "Chimney", "Door",
    "Machine", "Pipe", "Porch", "Sign", "Statue",
    "Table", "TiledRoof", "Truck", "VendingMachine",
    "WallSign", "Window",
]
'''

#to remove possible duplicates, and maintain order. there shouldnt be any duplicates anyways
BUILDING_CLASSES = list(dict.fromkeys(
    rules_and_concepts.get_all_building_classes()
    + rules_and_concepts.get_super_classes()
))
 
FEATURE_CLASSES = rules_and_concepts.get_concepts()


# (child, parent) — generates SubClassOf hierarchy
#specific da ontology do datasetVCB
HIERARCHY = [
    ("Awning",        "Feature"),   ("Billboard",  "Feature"),
    ("Car",           "Feature"),   ("Chimney",    "Feature"),
    ("Door",          "Feature"),   ("Machine",    "Feature"),
    ("Pipe",          "Feature"),   ("Porch",      "Feature"),
    ("Sign",          "Feature"),   ("Statue",     "Feature"),
    ("Table",         "Feature"),   ("TiledRoof",  "Feature"),
    ("Truck",         "Feature"),   ("VendingMachine", "Feature"),
    ("WallSign",      "Feature"),   ("Window",     "Feature"),
    ("Commercial",    "Building"),  ("Industrial", "Building"),
    ("Residential",   "Building"),
    ("Cafe",          "Commercial"), ("Hotel",          "Commercial"),
    ("MiscCommercial","Commercial"), ("Restaurant",     "Commercial"),
    ("Store",         "Commercial"),
    ("ConstructionSite","Industrial"), ("MiscIndustrial","Industrial"),
    ("PowerPlant",    "Industrial"), ("WaterTreatment", "Industrial"),
    ("CountryHouse",  "Residential"), ("MiscResidential","Residential"),
    ("Suburban",      "Residential"),
]

ALL_AXIOMS = rules_and_concepts.get_all_axioms()

def split_rules(all_axioms):
    equiv_rules = []
    impl_rules = []

    for ax_obj in all_axioms:
        ax = ax_obj["axiom"]
        r = (ax["left"], ax["right"])
        if ax["main_op"] == MainOperations.EQUIVALENCE:
            
            equiv_rules.append(r)
        elif ax["main_op"] == MainOperations.IMPLICATION or ax["main_op"] == MainOperations.BUILDING_FACT:
            impl_rules.append(r)

        else:
            print(f"\n\n\n ax_obj {ax_obj} NOT IMPLEMENTED \n\n\n\n")


    print(f"equiv_rules: {equiv_rules},\n impl_rules: {impl_rules}")
    return equiv_rules, impl_rules

EQUIV_RULES, SUBCLASS_RULES = split_rules(ALL_AXIOMS)


'''
# EquivalentClasses rules: (ClassName, right_expr)
EQUIV_RULES = [
    ("Cafe",            "OR(Statue, VendingMachine)"),
    ("ConstructionSite","Machine"),
    ("CountryHouse",    "AND(Car, TiledRoof)"),
    ("Hotel",           "WallSign"),
    ("MiscCommercial",  "AND(Awning, Table)"),
    ("MiscIndustrial",  "AND(NOT(OR(Awning, Table)), Truck)"),
    ("MiscResidential", "AND(NOT(AND(Awning, Table)), TiledRoof)"),
    ("PowerPlant",      "AND(Chimney, Pipe)"),
    ("Restaurant",      "AND(OR(Car, Truck), Sign)"),
    ("Store",           "Billboard"),
    ("Suburban",        "Porch"),
    ("WaterTreatment",  "AND(Pipe, Truck)"),
]

# SubClassOf rules: (left_class_or_expr, right_expr)
# Use a plain class name on the left for IMPL/BUILDING_FACT rules.
SUBCLASS_RULES = [
    ("Building",    "NOT(AND(OR(Car, Truck), Machine))"),
    ("Building",    "NOT(AND(NOT(OR(Door, Window)), Awning))"),
    ("Building",    "NOT(AND(Car, Truck))"),
    ("Building",    "NOT(AND(Chimney, Statue))"),
    ("Industrial",  "NOT(Table)"),
    ("Residential", "NOT(OR(Chimney, Pipe))"),
]


'''
# Each tuple becomes one DisjointClasses axiom
#especifico para o datasetVCB
DISJOINT_SETS = [
    ("Awning", "Billboard", "Car", "Chimney", "Door", "Machine",
     "Pipe", "Porch", "Sign", "Statue", "Table", "TiledRoof",
     "Truck", "VendingMachine", "WallSign", "Window"),
    ("Building", "Feature"),
    ("Commercial", "Industrial", "Residential"),
]


def generate_INDIVIDUALS():
    indv = []

    for f in FEATURE_CLASSES:
        f_tuple = (f.lower(), f)

        indv.append(f_tuple)

    return indv

# (individual_name, ClassName)
INDIVIDUALS = generate_INDIVIDUALS()



# ── Generator — edit only if you need new OWL constructs ─────────────────────

def _split_args(s):
    """Split comma-separated args at depth 0, respecting nested parens."""
    parts, current, depth = [], [], 0
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return parts


def _expr_to_owl(expr, depth=2):
    """Recursively convert a rule expression string to OWL/XML indented at `depth`."""
    pad  = "    " * depth
    pad1 = "    " * (depth + 1)

    if expr.startswith("AND(") and expr.endswith(")"):
        children = "\n".join(_expr_to_owl(p, depth + 1) for p in _split_args(expr[4:-1]))
        return f"{pad}<ObjectIntersectionOf>\n{children}\n{pad}</ObjectIntersectionOf>"

    if expr.startswith("OR(") and expr.endswith(")"):
        children = "\n".join(_expr_to_owl(p, depth + 1) for p in _split_args(expr[3:-1]))
        return f"{pad}<ObjectUnionOf>\n{children}\n{pad}</ObjectUnionOf>"

    if expr.startswith("NOT(") and expr.endswith(")"):
        inner = _expr_to_owl(expr[4:-1], depth + 1)
        return f"{pad}<ObjectComplementOf>\n{inner}\n{pad}</ObjectComplementOf>"

    # Leaf class name → ObjectSomeValuesFrom( #has, #ClassName )
    return (f"{pad}<ObjectSomeValuesFrom>\n"
            f"{pad1}<ObjectProperty IRI=\"#has\"/>\n"
            f"{pad1}<Class IRI=\"#{expr}\"/>\n"
            f"{pad}</ObjectSomeValuesFrom>")


def _left_to_owl(left, depth=2):
    """Left side of SubClassOf: plain class → <Class>, expression → recursive."""
    if not any(left.startswith(op) for op in ("AND(", "OR(", "NOT(")):
        return f"{'    ' * depth}<Class IRI=\"#{left}\"/>"
    return _expr_to_owl(left, depth)


def generate():
    lines = []
    W = lines.append

    W('<?xml version="1.0"?>')
    W(f'<Ontology xmlns="http://www.w3.org/2002/07/owl#"')
    W(f'     xml:base="{BASE_IRI}"')
    W(f'     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"')
    W(f'     xmlns:xml="http://www.w3.org/XML/1998/namespace"')
    W(f'     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"')
    W(f'     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"')
    W(f'     ontologyIRI="{BASE_IRI}">')
    W(f'    <Prefix name="" IRI="{BASE_IRI}"/>')
    W('    <Prefix name="owl" IRI="http://www.w3.org/2002/07/owl#"/>')
    W('    <Prefix name="rdf" IRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>')
    W('    <Prefix name="xml" IRI="http://www.w3.org/XML/1998/namespace"/>')
    W('    <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>')
    W('    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>')

    for cls in BUILDING_CLASSES + FEATURE_CLASSES:
        W(f'    <Declaration>\n        <Class IRI="#{cls}"/>\n    </Declaration>')

    W('    <Declaration>\n        <ObjectProperty IRI="#has"/>\n    </Declaration>')

    for ind, _ in INDIVIDUALS:
        W(f'    <Declaration>\n        <NamedIndividual IRI="#{ind}"/>\n    </Declaration>')

    for cls, expr in EQUIV_RULES:
        right = _expr_to_owl(expr, depth=2)
        W(f'    <EquivalentClasses>\n        <Class IRI="#{cls}"/>\n{right}\n    </EquivalentClasses>')

    for child, parent in HIERARCHY:
        W(f'    <SubClassOf>\n        <Class IRI="#{child}"/>\n        <Class IRI="#{parent}"/>\n    </SubClassOf>')

    for left, right in SUBCLASS_RULES:
        left_owl  = _left_to_owl(left, depth=2)
        right_owl = _expr_to_owl(right, depth=2)
        W(f'    <SubClassOf>\n{left_owl}\n{right_owl}\n    </SubClassOf>')

    for group in DISJOINT_SETS:
        inner = "\n".join(f'        <Class IRI="#{c}"/>' for c in group)
        W(f'    <DisjointClasses>\n{inner}\n    </DisjointClasses>')

    for ind, cls in INDIVIDUALS:
        W(f'    <ClassAssertion>\n        <Class IRI="#{cls}"/>\n        <NamedIndividual IRI="#{ind}"/>\n    </ClassAssertion>')

    W('    <SubObjectPropertyOf>\n        <ObjectProperty IRI="#has"/>\n        <ObjectProperty abbreviatedIRI="owl:topObjectProperty"/>\n    </SubObjectPropertyOf>')
    W('    <ObjectPropertyDomain>\n        <ObjectProperty IRI="#has"/>\n        <Class IRI="#Building"/>\n    </ObjectPropertyDomain>')
    W('    <ObjectPropertyRange>\n        <ObjectProperty IRI="#has"/>\n        <Class IRI="#Feature"/>\n    </ObjectPropertyRange>')

    W('</Ontology>')
    W('')
    W('')
    W('<!-- Generated by generate_ontology.py -->')
    W('')

    return "\n".join(lines)
    

if __name__ == "__main__":
    import os
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology_test.owl")
    content = generate()
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Written {out_path}")
