import torch
import ltn


RULES = []

#rule1 = {"rule": ("MiscCommercial", "AND", ["Awning", "Table"]), "nbr_of_ops": 1}
rule1 = {"rule": ("MiscIndustrial", "NOT", ["Awning"], "AND",["Truck"]), "nbr_of_ops": 2}


RULES.append(rule1)

# Misc Industrial = (not Awning) and Truck

CLASSES = [
    "MiscIndustrial",
    "Awning",
    "Truck",
]

ALL_CLASSES = [
    "Residential",
    "Commercial",
    "Industrial",


    "Cafe",
    "Hotel",
    "Restaurant",
    "Store",
    "MiscCommercial",
    "Suburban",
    "MiscResidential",
    "CountryHouse",
    "ConstructionSite",
    "MiscIndustrial",
    "PowerPlant",
    "WaterTreatment",

    "Door",
    "Window",
    "Awning",
    "Billboard",
    "Porch",
    "Sign",
    "Table",
    "TiledRoof",
    "TiledRoofTop",
    "VendingMachine",
    "WallSign",
    "Statue",
    "Chimney",
    "Pipe",
    "Machine",
    "Truck",
    "Car"
]

'''

CLASSES = [
    "MiscCommercial",
    "Awning",
    "Table"
]

CLASSES = [
    "Cafe",
    "Hotel",
    "Store",
    "MiscCommercial",
    "Awning",
    "Billboard",
    "VendingMachine",
    "Statue",
    "Table",
    "WallSign",
]

CLASSES = [
    "Cafe",
    "Statue",
    "VendingMachine"
]

'''
CLASS_TO_IDX = {name: i for i, name in enumerate(CLASSES)}

final_classes = 1

# Constants
#final classes

'''
#CLASS_TO_IDX["Awning"]
#class_cafe = ltn.Constant(torch.tensor(CLASS_TO_IDX["Cafe"]), trainable=False)
#class_hotel = ltn.Constant(torch.tensor(CLASS_TO_IDX["Hotel"]), trainable=False)
#class_store = ltn.Constant(torch.tensor(CLASS_TO_IDX["Store"]), trainable=False)
class_misc_commercial = ltn.Constant(torch.tensor(CLASS_TO_IDX["MiscCommercial"]), trainable=False)

#concepts
class_awning = ltn.Constant(torch.tensor(CLASS_TO_IDX["Awning"]), trainable=False)
#class_billboard = ltn.Constant(torch.tensor(CLASS_TO_IDX["Billboard"]), trainable=False)
#class_vending_machine = ltn.Constant(torch.tensor(CLASS_TO_IDX["VendingMachine"]), trainable=False)
#class_statue = ltn.Constant(torch.tensor(CLASS_TO_IDX["Statue"]), trainable=False)
class_table = ltn.Constant(torch.tensor(CLASS_TO_IDX["Table"]), trainable=False)
#class_wall_sign = ltn.Constant(torch.tensor(CLASS_TO_IDX["WallSign"]), trainable=False)
'''

CLASS_CONSTANTS = {
    name: ltn.Constant(torch.tensor(idx), trainable=False)
    for name, idx in CLASS_TO_IDX.items()
}

'''
Access by

CLASS_CONSTANTS["Awning"]
CLASS_CONSTANTS["Table"]
'''


#Connectives
Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
And = ltn.Connective(ltn.fuzzy_ops.AndProd())
Or = ltn.Connective(ltn.fuzzy_ops.OrProbSum())
Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
Exists = ltn.Quantifier(ltn.fuzzy_ops.AggregPMean(p=2), quantifier="e")
Equiv = ltn.Connective(
    ltn.fuzzy_ops.Equiv(
        ltn.fuzzy_ops.AndProd(),
        ltn.fuzzy_ops.ImpliesReichenbach()
    )
)

formula_aggregator = ltn.fuzzy_ops.SatAgg(
    ltn.fuzzy_ops.AggregPMeanError(p=2)
)

def get_number_of_final_classes():
    return final_classes

def get_CLASSES():
    return CLASSES

def get_ALL_CLASSES():
    return ALL_CLASSES


def get_nbr_of_concepts():
    return len(CLASSES) - final_classes

def safe_forall(var, formula, device, default_value=0.5):
# Check if variable has zero elements
    
    if var.value.shape[0] == 0:  # no elements in the batch
        # Return a neutral truth value (0.5)
        print("\n\n\n\n\n\n\n\n miss \n\n\n\n\n\n")

        #missCounter += 1
        return ltn.Constant(torch.tensor(default_value, device=device))
    else:
        return Forall(var, formula)

'''
Type of rule:
Cafe = (A or b) and c

Class op1 [c1, c2] op2 [c3] -> Cafe or [A, B] and [C]

os parantesis tem de ser da esq para a direuta ou seja

Class equiv (((c1 op1 c2) op2 c3) op3 c4)

("Cafe", "OR", ["Statue", "VendingMachine"]),
("Hotel", "EQUIV", ["WallSign"]),

MI NOT A AND T
("MiscIndustrial", "NOT", ["Awning"], "AND",["Truck"])

# Misc Industrial = (not Awning) and Truck
        Forall(
            x,
            Equiv(
                p([x, class_misc_industrial]),
                And(Not(p([x, class_awning])), p([x, class_truck])),
            ),
        ),
'''    


'''
def build_axiom(x, p, rule, nbr_of_ops):
    target = rule[0]
    target_cnst = CLASS_CONSTANTS[target]

    expr = None

    for i in range(nbr_of_ops):
        op = rule[2*i + 1]
        concepts = rule[2*i + 2]
        concept_cnsts = [CLASS_CONSTANTS[c] for c in concepts]

        if op == "NOT":
            current = Not(p(x, concept_cnsts[0]))

        elif op == "AND":
            current = p(x, concept_cnsts[0])
            for c in concept_cnsts[1:]:
                current = And(current, p(x, c))

        elif op == "OR":
            current = p(x, concept_cnsts[0])
            for c in concept_cnsts[1:]:
                current = Or(current, p(x, c))

        elif op == "EQUIV":
            return Equiv(p(x, target_cnst), p(x, concept_cnsts[0]))

        # Combine with previous expression
        if expr is None:
            expr = current
        else:
            # Default chaining = AND (since your rule is sequential)
            expr = And(expr, current)

    return Equiv(p(x, target_cnst), expr)
'''


def build_axiom(x, p, rule, nbr_of_ops):
    #rule = ("Cafe", "OR", ["Statue", "VendingMachine"], "AND", ["", "Statue"])
    #nbr_of_ops = 2

    target = rule[0]
    target_cnst = CLASS_CONSTANTS[target]

    complete_axiom = ""

    for i in range(nbr_of_ops):

        op = rule[2*i +1] # pos 1, 3, 5 etc
        concepts = rule[2*i +2]# pos 2, 4, 6 etc

        concept_cnsts = [CLASS_CONSTANTS[c] for c in concepts]

        if op == "AND":

            conjunction = complete_axiom
            if i == 0:
                conjunction = p(x, concept_cnsts[0])

            #construir conjuntcion -> c1 and c2 and c3...
            for c in concept_cnsts[1:]:
                conjunction = And(conjunction, p(x, c))
            complete_axiom = conjunction

        elif op == "OR":
            disjunction = complete_axiom
            if i == 0:
                disjunction = p(x, concept_cnsts[0])

            #construir disjunction -> c1 or c2 or c3...
            for c in concept_cnsts[1:]:
                disjunction = Or(disjunction, p(x, c))
            complete_axiom =  disjunction

        elif op == "NOT":
            expression = complete_axiom
            if i == 0:
                expression = p(x, concept_cnsts[0])

            complete_axiom =  Not(expression)

        #apenas se usa se so quisermos uma equivalencia entre uma classe e um conceito Cafe = Statue
        elif op == "EQUIV":
            return Equiv(p(x, target_cnst), p(x, concept_cnsts[0]))

    #aplica as ops, e dps gera a equivalencia final
    return Equiv(p(x, target_cnst), complete_axiom)

    
def get_masked_variable(logits, args, class_name):
    idx = CLASS_TO_IDX[class_name]
    return ltn.Variable(f"x_{class_name}",logits[args[idx] == 1, :]), ltn.Variable(f"x_not_{class_name}",logits[args[idx] == 0, :])

def append_class_predicates(axioms, p, x, x_not, class_name, device):
    cnst = CLASS_CONSTANTS[class_name]

    p1 = safe_forall(x, p(x, cnst), device)
    p2 = safe_forall(x_not, Not(p(x_not, cnst)), device)

    axioms.append(p1)
    axioms.append(p2)



def compute_axioms(logits, *args, p):

    device = logits.device
    axioms = []

    #logits = logits_model(features_param)

    x = ltn.Variable("x", logits)
    #x_hotel = ltn.Variable("x_hotel", logits[args[CLASSES.index("Hotel")] == 1, :])
    #x_not_hotel = ltn.Variable("x_not_hotel", logits[args[CLASSES.index("Hotel")] == 0, :])

    #x_cafe = ltn.Variable("x_cafe", logits[args[CLASSES.index("Cafe")] == 1, :])
    #x_not_cafe = ltn.Variable("x_not_cafe", logits[args[CLASSES.index("Cafe")] == 0, :])

    #x_store = ltn.Variable("x_store", logits[args[CLASSES.index("Store")] == 1, :])
    #x_not_store = ltn.Variable("x_not_store", logits[args[CLASSES.index("Store")] == 0, :])

    #x_misc_commercial = ltn.Variable("x_misc_commercial", logits[args[CLASS_TO_IDX["MiscCommercial"]] == 1, :])
    #x_not_misc_commercial = ltn.Variable("x_not_misc_commercial",logits[args[CLASS_TO_IDX["MiscCommercial"]] == 0, :])


    #x_misc_commercial, x_not_misc_commercial = get_masked_variable(logits=logits, args=args, class_name="MiscCommercial")
    #append_class_predicates(axioms, p, x=x_misc_commercial, x_not=x_not_misc_commercial, class_name="MiscCommercial",device=device)

    x_misc_industrial, x_not_industrial = get_masked_variable(logits=logits, args=args, class_name="MiscIndustrial")
    append_class_predicates(axioms, p, x=x_misc_industrial, x_not=x_not_industrial, class_name="MiscIndustrial",device=device)



    for r in RULES:
        axioms.append(
            safe_forall(x, build_axiom(x, p, r["rule"], r["nbr_of_ops"]), device)
        )
    
    #print("values of axioms")
    #for a in axioms:
      #print(a.value)

    sat_level = formula_aggregator(*axioms)

    return sat_level



'''metrics functions'''


def get_classes_to_plot():
    class_train_metrics = []
    class_val_metrics = []
    concept_train_metrics= []
    concept_val_metrics = []

    final_classes_to_plot = CLASSES[:final_classes]
    concepts_to_plot = CLASSES[final_classes:]


    for c in final_classes_to_plot:
        class_train_metrics.append(f"{c.lower()}_train_accuracy")
        class_val_metrics.append(f"{c.lower()}_val_accuracy")

    for c in concepts_to_plot:
        concept_train_metrics.append(f"{c.lower()}_train_accuracy")
        concept_val_metrics.append(f"{c.lower()}_val_accuracy")

    class_train_metrics.append("alpha")
    class_val_metrics.append("alpha")
    concept_train_metrics.append("alpha")
    concept_val_metrics.append("alpha")

    return class_train_metrics, class_val_metrics, concept_train_metrics, concept_val_metrics


'''
    axioms_cafe_and_disjunction = [
    safe_forall(x_cafe, p(x_cafe, class_cafe), device),
    safe_forall(x_not_cafe, Not(p(x_not_cafe, class_cafe)), device),
    safe_forall(
        x,
        Equiv(
            p(x, class_cafe),
            Or(p(x, class_statue), p(x, class_vending_machine)),
        ),
        device
    ),
    ]
    

# Misc Industrial = (not Awning) and Truck
        Forall(
            x,
            Equiv(
                p([x, class_misc_industrial]),
                And(Not(p([x, class_awning])), p([x, class_truck])),
            ),
        ),

    
# Restaurant = (Car or Truck) and Sign
    Forall(
        x,
        Equiv(
            p([x, class_restaurant]),
            And(Or(p([x, class_car]), p([x, class_truck])), p([x, class_sign])),
        ),
    ),
'''
'''
axioms_misccommercial_conjunction = [
    safe_forall(x_misc_commercial, p(x_misc_commercial, CLASS_CONSTANTS["MiscCommercial"]), device),
    safe_forall(x_not_misc_commercial, Not(p(x_not_misc_commercial, CLASS_CONSTANTS["MiscCommercial"])), device),

    safe_forall(
        x,
        build_axiom(x, p, rule=rule1, nbr_of_ops=1),   
        device
    ),
    ]

    axioms_misccommercial_conjunction = [
    safe_forall(x_misc_commercial, p(x_misc_commercial, CLASS_CONSTANTS["MiscCommercial"]), device),
    safe_forall(x_not_misc_commercial, Not(p(x_not_misc_commercial, CLASS_CONSTANTS["MiscCommercial"])), device),
    safe_forall(
        x,
        Equiv(
            p(x, CLASS_CONSTANTS["MiscCommercial"]),
            And(p(x, CLASS_CONSTANTS["Awning"]), p(x, CLASS_CONSTANTS["Table"])),
        ),
        device
    ),
    ]


axioms = [
    # Grounded Predicates

    safe_forall(x_hotel, p(x_hotel, class_hotel), device),
    safe_forall(x_not_hotel, Not(p(x_not_hotel, class_hotel)),device),
    safe_forall(x_cafe, p(x_cafe, class_cafe), device),
    safe_forall(x_not_cafe, Not(p(x_not_cafe, class_cafe)), device),
    safe_forall(x_store, p(x_store, class_store), device),
    safe_forall(x_not_store, Not(p(x_not_store, class_store)), device),
    safe_forall(x_misc_commercial, p(x_misc_commercial, class_misc_commercial), device),
    safe_forall(x_not_misc_commercial, Not(p(x_not_misc_commercial, class_misc_commercial)), device),
    # Axioms
    # Cafe = Statue or Vending Machine
    safe_forall(
        x,
        Equiv(
            p(x, class_cafe),
            Or(p(x, class_statue), p(x, class_vending_machine)),
        ),
        device
    ),
    # Hotel = Wall Sign
    safe_forall(
        x,
        Equiv(p(x, class_hotel), p(x, class_wall_sign)),
        device
    ),
    # MiscCommercial = Awning and Table
    safe_forall(
        x,
        Equiv(
            p(x, class_misc_commercial),
            And(p(x, class_awning), p(x, class_table)),
        ),
        device
    ),
    # Store = Billboard
    safe_forall(
        x,
        Equiv(p(x, class_store), p(x, class_billboard)),
        device
    ),
]
'''