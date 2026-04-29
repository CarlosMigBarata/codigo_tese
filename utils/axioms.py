

import torch
import ltn
import utils.rules_and_concepts as rules_and_concepts

AXIOMS = rules_and_concepts.get_active_axioms()
CLASSES = rules_and_concepts.get_classes()

print(f"classes in axioms.py {CLASSES}")

list_of_final_classes = rules_and_concepts.get_final_classes()
final_classes = len(list_of_final_classes)

CLASS_TO_IDX = {name: i for i, name in enumerate(CLASSES)}


CLASS_CONSTANTS = {
    name: ltn.Constant(torch.tensor(idx), trainable=False)
    for name, idx in CLASS_TO_IDX.items()
}


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

class MeanMetric:
    def __init__(self):
        self.reset_state()

    def update(self, value, n=1):
        self.total += value * n
        self.count += n

    def compute(self):
        return self.total / self.count if self.count != 0 else 0.0


    def reset_state(self):
        self.total = 0.0
        self.count = 0

    def result(self):
        return self.compute()
    

metrics_dict = {}

axiom_train_accuracy_metric = {
    f"{axiom.lower()}_train_accuracy": MeanMetric()
    for axiom in AXIOMS
}

metrics_dict.update(axiom_train_accuracy_metric)

axiom_val_accuracy_metric = {
    f"{axiom.lower()}_val_accuracy": MeanMetric()
    for axiom in AXIOMS
}
metrics_dict.update(axiom_val_accuracy_metric)




def get_number_of_final_classes():
    return final_classes

def get_CLASSES():
    return CLASSES

def get_ALL_CLASSES():
    return rules_and_concepts.get_all_classes()


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
# Misc Industrial = (not Awning) and Truck
        safe_Forall(
            x,
            Equiv(
                p([x, class_misc_industrial]),
                And(Not(p([x, class_awning])), p([x, class_truck])),
            ),
            device
        ),

        safe_forall(
        x,
        Equiv(
            p(x, class_cafe),
            Or(p(x, class_statue), p(x, class_vending_machine)),
        ),
        device
    )
'''    


'''
Example rule

A and B = (C or not D) and E

AND(A , B); AND(OR(C,NOT(D)), E)

A = (A and B) or (C and D)

OR(AND(A,B),AND(C,D))

FOR_AND [A,B,C,D]

left
right
main_op
'''

def build_axiom(p, x, left, right, main_op, debug_mode=False):
        #aplica as ops, e dps gera a equivalencia final

    left_obj, left_str = build_axioms_rec(p, x, left)
    right_obj, right_str = build_axioms_rec(p, x, right)


    if main_op == "EQUIV":
        ax = Equiv(left_obj, right_obj)

        if debug_mode: 
            print(f"[AXIOM] EQUIV({left_str}, {right_str})")

        return ax

    elif main_op == "IMPL":
        ax = Implies(left_obj, right_obj)

        if debug_mode: 
            print(f"[AXIOM] IMPL({left_str}, {right_str})")

        return ax
    
    elif main_op == "BUILDING_FACT":
        if debug_mode: 
            print(f"[AXIOM] FACT({right_str})")

        return right_obj
    
    else:
        print("TYPO ON MAIN OP")


def build_axioms_rec(p, x, rule, depth=0, debug_mode=False):
    indent = "  " * depth
    if debug_mode:
        print(f"{indent}Processing: {rule}")

    op = rule.split("(")[0]
    #print(f"operation: {op}")

    if op == "AND":
        # remove "AND" from start
        inner = rule[3:]
        parts = split_top_level(inner)

                #for _and
        if len(parts) > 2:
            #print("inside for_and")
            start_obj, str = build_axioms_rec(p, x, parts[0][1:].strip(), depth+1, debug_mode)

            complete_conj = start_obj
            complete_string = f"AND({str}"

            for i in range(1, len(parts)):
                
                if i == len(parts) - 1:
                    part = parts[i][:-1]
                else:
                    part = parts[i]
            
                obj, s = build_axioms_rec(p, x, part.strip(), depth+1, debug_mode)
                complete_conj = And(complete_conj, obj)
                complete_string = complete_string + f", {s}"
            
            complete_string = complete_string + ")"

            #print(f"complete string {complete_string}")

            return complete_conj, complete_string


        left_obj, left_str = build_axioms_rec(p, x, parts[0][1:].strip(), depth+1, debug_mode)
        right_obj, right_str = build_axioms_rec(p, x, parts[1][:-1].strip(), depth+1, debug_mode)

        return And(left_obj, right_obj), f"AND({left_str}, {right_str})"

    elif op == "OR":
        # remove "OR(" from start and ")" from end
        inner = rule[2:]
        #print(f"inside OR, inner: {inner}")

        parts = split_top_level(inner)

                #for _or?
        if len(parts) > 2:
            #print("inside for_or")
            start_obj, str = build_axioms_rec(p, x, parts[0][1:].strip(), depth+1, debug_mode)

            complete_disj = start_obj
            complete_string = f"OR({str}"

            for i in range(1, len(parts)):
                
                if i == len(parts) - 1:
                    part = parts[i][:-1]
                else:
                    part = parts[i]
            
                obj, s = build_axioms_rec(p, x, part.strip(), depth+1, debug_mode)
                complete_disj = Or(complete_disj, obj)
                complete_string = complete_string + f", {s}"
            
            complete_string = complete_string + ")"

            #print(f"complete string {complete_string}")

            return complete_disj, complete_string



        left_obj, left_str = build_axioms_rec(p, x, parts[0][1:].strip(), depth+1, debug_mode)
        right_obj, right_str = build_axioms_rec(p, x, parts[1][:-1].strip(), depth+1, debug_mode)

        return Or(left_obj, right_obj), f"OR({left_str}, {right_str})"

    elif op == "NOT":
        #print(f"inside NOT, rule: {rule}")
        # remove "NOT(" from start and ")" from end
        inner = rule[4:-1]

        obj, s = build_axioms_rec(p, x, inner, depth+1, debug_mode)
        return Not(obj), f"NOT({s})"
    
    #the rule string is only concept,
    else:
        if rule not in CLASS_CONSTANTS:
            print(f"{rule} is not CLASS_CONSTANTS")


        target_cnst = CLASS_CONSTANTS[rule]
        #print(f"target_cnst {rule}")

        return p(x, target_cnst), rule


def split_top_level(s):
    parts = []
    current = []
    depth = 0

    for char in s:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1

        if char == ',' and depth == 1:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)

    parts.append(''.join(current))
    return parts
    
def get_masked_variable_and_append_predicates(logits, p, args, class_name, axioms, device):
    
    if class_name not in CLASS_CONSTANTS or class_name not in CLASS_TO_IDX:
        print(f"\n\n skipping class {class_name} \n\n")
        return
    
    cnst = CLASS_CONSTANTS.get(class_name)
    idx = CLASS_TO_IDX[class_name]

    x = ltn.Variable(f"x_{class_name}",logits[args[idx] == 1, :])
    x_not = ltn.Variable(f"x_not_{class_name}",logits[args[idx] == 0, :])

    p1 = safe_forall(x, p(x, cnst), device)
    p2 = safe_forall(x_not, Not(p(x_not, cnst)), device)

    axioms.append(p1)
    axioms.append(p2)


'''
metrics_dict = {}

axiom_train_accuracy_metric = {
    f"{rules_and_concepts.get_name_of_axiom(axiom).lower()}_train_accuracy": MeanMetric()
    for axiom in RULES
}

metrics_dict.update(axiom_train_accuracy_metric)

axiom_val_accuracy_metric = {
    f"{rules_and_concepts.get_name_of_axiom(axiom).lower()}_val_accuracy": MeanMetric()
    for axiom in RULES
}
metrics_dict.update(axiom_val_accuracy_metric)
'''


def compute_axioms(logits, *args, p, debug_mode=False, validation_mode=False):

    device = logits.device
    ltn_axioms = []

    #logits = logits_model(features_param)

    x = ltn.Variable("x", logits)

    #print(logits)
    #print(f" args {args}")


    for class_name in list_of_final_classes:
        get_masked_variable_and_append_predicates(logits=logits, p=p, args=args, class_name=class_name, axioms=ltn_axioms, device=device)


    for ax in AXIOMS.items():
        #print(f"R in compute axioms: {r}"
        print(f"ax in compute_Ax {ax}")
        r = ax[1]
        print(f"r in compute ax: {r}")

        ltn_axiom = safe_forall(x, build_axiom(p,x, r["left"], r["right"], r["main_op"], debug_mode), device)
        ltn_axioms.append(ltn_axiom)
        if not validation_mode:
            update_rule_sat_metric(ax, "train", ltn_axiom)
        else:
            update_rule_sat_metric(ax, "val", ltn_axiom)
    
    sat_level = formula_aggregator(*ltn_axioms)

    #print(sat_level)

    return sat_level

def update_rule_sat_metric(axiom, phase, value):
    ax_name = axiom.lower()
    print(f"ltn_axiom: {value}")

    metrics_dict[f"{ax_name}_{phase}_accuracy"].update(value)
    

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
DO NOT USE; ONLY FOR OLD TESTS
'''
def get_classes_to_plot_old():
    class_train_metrics = []
    class_val_metrics = []
    concept_train_metrics= []
    concept_val_metrics = []

    final_classes_to_plot = CLASSES[:final_classes]
    concepts_to_plot = CLASSES[final_classes:]


    for c in final_classes_to_plot:
        class_train_metrics.append(f"{c.lower()}_train_accuracy")
        class_val_metrics.append(f"{c.lower()}_test_accuracy")

    for c in concepts_to_plot:
        concept_train_metrics.append(f"{c.lower()}_train_accuracy")
        concept_val_metrics.append(f"{c.lower()}_test_accuracy")

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


        #get_masked_variable_and_append_predicates(logits=logits, p=p, args=args, class_name="Cafe", axioms=axioms, device=device)
        #get_masked_variable_and_append_predicates(logits=logits, p=p, args=args, class_name="Store", axioms=axioms, device=device)
        #get_masked_variable_and_append_predicates(logits=logits, p=p, args=args, class_name="MiscCommercial", axioms=axioms, device=device)


    #append_class_predicates(axioms, p, x=x_hotel, x_not=x_not_hotel, class_name="Hotel",device=device)

    #x_cafe, x_not_cafe = get_masked_variable(logits=logits, args=args, class_name="Cafe")
    #append_class_predicates(axioms, p, x=x_cafe, x_not=x_not_cafe, class_name="Cafe",device=device)

    #x_store, x_not_store = get_masked_variable(logits=logits, args=args, class_name="Store")
    #append_class_predicates(axioms, p, x=x_store, x_not=x_not_store, class_name="Store",device=device)

    #x_misc_commercial, x_not_misc_commercial = get_masked_variable(logits=logits, args=args, class_name="MiscCommercial")
    #append_class_predicates(axioms, p, x=x_misc_commercial, x_not=x_not_misc_commercial, class_name="MiscCommercial",device=device)

    #x_misc_industrial, x_not_industrial = get_masked_variable(logits=logits, args=args, class_name="MiscIndustrial")
    #append_class_predicates(axioms, p, x=x_misc_industrial, x_not=x_not_industrial, class_name="MiscIndustrial",device=device)


    #x_CH, x_not_CH = get_masked_variable(logits=logits, args=args, class_name="CountryHouse")
    #append_class_predicates(axioms, p, x=x_CH, x_not=x_not_CH, class_name="CountryHouse",device=device)
# Constants
#final classes

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


'''
dict:
#rule: the main axiom. A primeira classe é o conceito mais a esq da regra, a partir daí é Operation -> conceitos envolvidos. em relação as operações
#a Equivalencia/Implicação é ignorada, a menos que seja a unica operação. quando apenas existe um AND/OR/NOT, é só preciso meter essa operação
#sem mudanças; se houver mais do que uma, a partir da primeira operação a primeira posição da lista dos conceitos envolvidos é ignorada.

#nbr_of_ops: numero de opções, 1 se só houver uma equivalencia/implicacao ou se houver apenas 1 And/Or/not. conta o numero de OPs na rule
#MAIN_OP: "EQUIV"/"IMPL". representa a principal operação, que é ignorada quando existe outras operações.

#High Level Rules
rule_BuildingTypes = {"rule": ("Building", "OR", ["Residential", "Commercial", "Industrial"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_FeatureTypes = {"rule": ("Feature", "OR", ["Awning", "Billboard", "Car", "Chimney", "Door", "Machine", "Pipe","Porch",
             "Sign", "Statue", "Table", "TiledRoof", "Truck", "VendingMachine", "WallSign", "Window"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}

#preciso de implementar o Implica -> "IMPL"

#Building ⊑ ¬((∃has.Car ⊔ ∃has.T ruck) ⊓ (∃has.Machine))

rule_Buiding_Impl_not_carAndTruck_OrMachine = {"rule": ("Building", "OR", ["Car", "Truck"], "AND", ["Machine", "Machine"],
                                                                  "NOT", ["Machine"]), "nbr_of_ops": 3, "Main_OP": "IMPL"}


#second rule Building ⊓¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning -> o meu codigo n ta preparado para isto, dps tenho de melhorar a logica


# Building ⊑¬(∃has.Car ⊓ ∃has.T ruck)
rule_Building_Impl_not_CarAndTruck = {"rule": ("Building", "AND", ["Car", "Truck"], "NOT", ["Chimney"]), "nbr_of_ops": 2, "Main_OP": "IMPL"}


#Building ⊑ ¬(∃has.Chimney ⊓ ∃has.Statue)
rule_Building_Impl_not_ChimneyAndStatue = {"rule": ("Building", "AND", ["Chimney", "Statue"], "NOT", ["Chimney"]), "nbr_of_ops": 2, "Main_OP": "IMPL"}




rule_CommercialBuildingType = {"rule": ("Commercial", "OR", ["Cafe", "Hotel", "MiscCommercial", "Restaurant", "Store"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_IndustrialBuildingType = {"rule": ("Industrial", "OR", ["ConstructionSite", "MiscIndustrial", "PowerPlant", "WaterTreatment"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_ResidentialBuildingType = {"rule": ("Residential", "OR", ["CountryHouse", "MiscResidential", "Suburban"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}

#rules related to final classes
#when using the second rule, its necessary to place a placeholder in this first slot

#equiv
rule_Hotel_Wallsign = {"rule": ("Hotel", "EQUIV", ["WallSign"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_Store_Billboard = {"rule": ("Store", "EQUIV", ["Billboard"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_Industrial_notTable = {"rule": ("Industrial", "NOT", ["Table"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}

rule_ConstructionSite_Machine = {"rule": ("ConstructionSite", "EQUIV", ["Machine"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_Suburban_Porch = {"rule": ("Suburban", "EQUIV", ["Porch"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}

#conj
rule_MiscCommercial_AwningAndTable = {"rule": ("MiscCommercial", "AND", ["Awning", "Table"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_MiscIndustrial_notAwningAndTruck = {"rule": ("MiscIndustrial", "NOT", ["Awning"], "AND",["Truck", "Truck"]), "nbr_of_ops": 2, "Main_OP": "EQUIV"}
rule_CH_CarAndTiledroof = {"rule": ("CountryHouse", "AND",["Car", "TiledRoof"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_PowerPlant_ChimneyAndPipe = {"rule": ("PowerPlant", "AND",["Chimney", "Pipe"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_WaterTreatment_PipeAndTruck = {"rule": ("WaterTreatment", "AND", ["Pipe", "Truck"]), "nbr_of_ops":1, "Main_OP": "EQUIV"}


#disj
rule_Cafe_StatueOrVendingMachine = {"rule": ("Cafe", "OR", ["Statue", "VendingMachine"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}


#regras complexas
rule_Restaurant_CarOrTruckAndSign = {"rule": ("Restaurant", "OR", ["Car", "Truck"], "AND", ["Sign", "Sign"]), "nbr_of_ops": 2, "Main_OP": "EQUIV"}


#in this case, the awning inside of the NOT is NOT USED, its just a placeholder. same applies to the first TiledRoof
rule_MiscResidential_not_AwningAndTable_AndTiledRoof = {"rule": ("MiscResidential", "AND", ["Awning", "Table"], "NOT", ["Awning"],
                                                                  "OR", ["TiledRoof", "TiledRoof"]), "nbr_of_ops": 3, "Main_OP": "EQUIV"}

# Residential⊑¬(∃has.Chimney ⊔ ∃has.P ipe)
rule_Residential_Impl_not_ChimneyOrPipe = {"rule": ("Residential", "OR", ["Chimney", "Pipe"], "NOT", ["Chimney"]), "nbr_of_ops": 2, "Main_OP": "IMPL"}


'''
    # Axioms
    # MiscCommercial = Awning and Table
    # MiscIndustrial = not Awning and Truck
    # CountryHouse = Car and TiledRoof

    # Cafe = Statue or Vending Machine
    # Hotel = Wall Sign
    # Store = Billboard
'''


RULES.append(rule_MiscCommercial_AwningAndTable)
RULES.append(rule_MiscIndustrial_notAwningAndTruck)
RULES.append(rule_CH_CarAndTiledroof)

RULES.append(rule_Cafe_StatueOrVendingMachine)
RULES.append(rule_Hotel_Wallsign)
RULES.append(rule_Store_Billboard)

RULES.append(rule_Restaurant_CarOrTruckAndSign)


def get_final_classes_in_classes(classes, all_final_classes):
    return [c for c in all_final_classes if c in classes]



'''
"Awning",
"Billboard",
"VendingMachine",
"Statue",
"Table",
"WallSign",'''


CLASSES = [

    "CountryHouse",
    "MiscIndustrial",
    "MiscCommercial",
    "Restaurant",
    "Cafe",
    "Hotel",
    "Store",

    "Car",
    "TiledRoof",
    "Awning",
    "Truck",
    "Table",
    "Sign",
    "Billboard",
    "VendingMachine",
    "Statue",
    "WallSign",
]

ALL_FINAL_CLASSES = [
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
]

ALL_CLASSES = [
    "Building",
    "Feature",

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


def build_axiom(x, p, rule, nbr_of_ops, main_op):
    #rule = ("Cafe", "OR", ["Statue", "VendingMachine"], "AND", ["Statue", "Statue"])
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
            #se apenas um conceito tem de ser invertido, NOT tem de ser a primeira opção. caso contrario
            if i == 0:
                expression = p(x, concept_cnsts[0])

            complete_axiom =  Not(expression)

        #apenas se usa se so quisermos uma equivalencia entre uma classe e um conceito Cafe = Statue
        elif op == "EQUIV":
            return Equiv(p(x, target_cnst), p(x, concept_cnsts[0]))
        
        elif op == "IMPL":
            return Implies(p(x, target_cnst), p(x, concept_cnsts[0]))

    #aplica as ops, e dps gera a equivalencia final
    if main_op == "EQUIV":
        return Equiv(p(x, target_cnst), complete_axiom)
    
    elif main_op == "IMPL":
        return Implies(p(x, target_cnst), complete_axiom)
    
'''