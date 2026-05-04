rule_BuildingTypes = {"left": "Building", "right": "OR(Residential, Commercial, Industrial)", "main_op": "BUILDING_FACT"}

rule_FeatureTypes = {"left": "Feature", "right": "OR(Awning, Billboard, Car, Chimney, Door, Machine, Pipe, Porch, "
"Sign, Statue, Table, TiledRoof, Truck, VendingMachine, WallSign, Window)", "main_op": "EQUIV"}

#preciso de implementar o Implica -> "IMPL"


''' Building ⊑ ¬((∃has.Car ⊔ ∃has.T ruck) ⊓ (∃has.Machine))'''
rule_Buiding_Impl_not_carAndTruck_OrMachine = {"left": "Building", "right":"NOT(AND(OR(Car,Truck),Machine))", "main_op":"BUILDING_FACT"}


#second rule Building ⊓¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning -> o meu codigo n ta preparado para isto, dps tenho de melhorar a logica


# Building ⊑¬(∃has.Car ⊓ ∃has.T ruck)
rule_Building_Impl_not_CarAndTruck = {"left": "Building", "right":"NOT(AND(Car,Truck))", "main_op":"BUILDING_FACT"}


#Building ⊑ ¬(∃has.Chimney ⊓ ∃has.Statue)
rule_Building_Impl_not_ChimneyAndStatue = {"left": "Building", "right":"NOT(AND(Chimney,Statue))", "main_op":"BUILDING_FACT"}

#FOR_OR
rule_CommercialBuildingType = {"left": "Commercial", "right": "OR(Cafe, Hotel, MiscCommercial, Restaurant, Store)", "main_op": "EQUIV"}
rule_IndustrialBuildingType = {"left": "Industrial", "right": "OR(ConstructionSite, MiscIndustrial, PowerPlant, WaterTreatment)", "main_op": "EQUIV"}
rule_ResidentialBuildingType = {"left": "Residential", "right": "OR(CountryHouse, MiscResidential, Suburban)", "main_op": "EQUIV"}


#rules related to final classes
#when using the second rule, its necessary to place a placeholder in this first slot

#equiv
rule_Hotel_Wallsign = {"left": "Hotel", "right": "WallSign", "main_op": "EQUIV"}
rule_Store_Billboard = {"left": "Store", "right": "Billboard", "main_op": "EQUIV"}
rule_Industrial_notTable = {"left": "Industrial", "right": "NOT(Table)", "main_op": "EQUIV"}

rule_ConstructionSite_Machine = {"left": "ConstructionSite", "right": "Machine", "main_op": "EQUIV"}
rule_Suburban_Porch = {"left": "Suburban", "right": "Porch", "main_op": "EQUIV"}

#conj
rule_MiscCommercial_AwningAndTable = {"left": "MiscCommercial", "right": "AND(Awning, Table)", "main_op": "EQUIV"}
rule_MiscIndustrial_notAwningAndTruck = {"left": "MiscIndustrial", "right": "AND(NOT(Awning), Truck)", "main_op": "EQUIV"}
rule_CH_CarAndTiledroof = {"left": "CountryHouse", "right": "AND(Car, TiledRoof)", "main_op": "EQUIV"}
rule_PowerPlant_ChimneyAndPipe = {"left": "PowerPlant", "right": "AND(Chimney, Pipe)", "main_op": "EQUIV"}
rule_WaterTreatment_PipeAndTruck = {"left": "WaterTreatment", "right": "AND(Pipe, Truck)", "main_op": "EQUIV"}


#disj
rule_Cafe_StatueOrVendingMachine = {"left": "Cafe", "right": "OR(Statue, VendingMachine)", "main_op": "EQUIV"}


#regras complexas
#Restaurant≡(∃has.Car ⊔ ∃has.T ruck) ⊓ ∃has.Sign
rule_Restaurant_CarOrTruckAndSign = {"left": "Restaurant", "right": "AND(OR(Car,Truck),Sign)", "main_op": "EQUIV"}


#MiscResidential≡ ¬(∃has.Awning ⊓ ∃has.T able) ⊓ ∃has.T iledRoof
rule_MiscResidential_not_AwningAndTable_AndTiledRoof = {"left": "MiscResidential", "right": "AND(NOT(AND(Awning,Table)),TiledRoof)", "main_op": "EQUIV"}

# Residential ⊑ ¬ (∃has.Chimney ⊔ ∃has.Pipe)
rule_Residential_Impl_not_ChimneyOrPipe = {"left": "Residential", "right":"NOT(OR(Chimney,Pipe))", "main_op":"IMPL"}

#Building ⊓ ¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning
rule_Building_noDoorOrNoWindow_Impl_noAwning = {"left": "NOT(OR(Door,Window))", "right":"NOT(Awning)", "main_op":"IMPL"}



ALL_AXIOMS = [
    {"axiom": rule_BuildingTypes, "active": False, "name": "building_types"}, #high level rules
    {"axiom": rule_FeatureTypes, "active": False, "name": "feature_types"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_CommercialBuildingType, "active": True, "name": "commercial"},
    {"axiom": rule_IndustrialBuildingType, "active": True, "name": "industrial"},
    {"axiom": rule_ResidentialBuildingType, "active": True, "name": "residential"},


    #done
    {"axiom": rule_Buiding_Impl_not_carAndTruck_OrMachine, "active": True, "name": "building_impl_complex"}, #implications, more related to the building creation process
    {"axiom": rule_Building_Impl_not_CarAndTruck, "active": True, "name": "building_no_car_truck"},
    {"axiom": rule_Building_Impl_not_ChimneyAndStatue, "active": True, "name": "building_no_chimney_statue"},
    {"axiom": rule_Building_noDoorOrNoWindow_Impl_noAwning, "active": True, "name": "building_noDoorOrNoWindow_Impl_noAwning"},


    #equiv
    {"axiom": rule_Hotel_Wallsign, "active": True, "name":"hotel"}, #comercial
    {"axiom": rule_Store_Billboard, "active": True, "name":"store"}, #comercial
    {"axiom": rule_Industrial_notTable, "active": True, "name":"industrial_not_table"}, #industrial
    {"axiom": rule_ConstructionSite_Machine, "active": True, "name":"constructionsite"}, #industrial
    {"axiom": rule_Suburban_Porch, "active": True, "name":"suburban"}, #residential


    #conj
    {"axiom": rule_MiscCommercial_AwningAndTable, "active": True, "name":"misccommercial"}, #comercial
    {"axiom": rule_MiscIndustrial_notAwningAndTruck, "active": True, "name":"miscindustrial"}, #industrial
    {"axiom": rule_CH_CarAndTiledroof, "active": True, "name":"countryhouse"}, #residential
    {"axiom": rule_PowerPlant_ChimneyAndPipe, "active": True, "name":"powerplant"}, #industrial
    {"axiom": rule_WaterTreatment_PipeAndTruck, "active": True, "name":"watertreatment"}, #industrial

    #disj
    {"axiom": rule_Cafe_StatueOrVendingMachine, "active": True, "name":"cafe"}, #comercial

    #complex
    {"axiom": rule_Restaurant_CarOrTruckAndSign, "active": True,"name":"restaurant"},#comercial
    {"axiom": rule_MiscResidential_not_AwningAndTable_AndTiledRoof, "active": True, "name":"miscresidential"},#residential
    {"axiom": rule_Residential_Impl_not_ChimneyOrPipe, "active": True, "name": "residential_no_chimney_pipe"},#residential

    ]




ALL_CLASSES = [
    #"Building",
    #"Feature",

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




''' NEW STUFF '''
rule_Hotel_Impl_Door = {"left": "Hotel", "right": "Door", "main_op": "IMPL"}
rule_Hotel_Impl_Window = {"left": "Hotel", "right": "Window", "main_op": "IMPL"}
rule_Hotel_Impl_Car = {"left": "Hotel", "right": "Car", "main_op": "IMPL"}

rule_Store_Impl_VendingMachine = {"left": "Store", "right": "VendingMachine", "main_op": "IMPL"}
rule_Store_Impl_Truck = {"left": "Store", "right": "Truck", "main_op": "IMPL"}
rule_Store_Impl_Statue = {"left": "Store", "right": "Statue", "main_op": "IMPL"}

rule_Suburban_Impl_Pipe = {"left": "Suburban", "right": "Pipe", "main_op": "IMPL"}
rule_Suburban_Impl_Chimney = {"left": "Suburban", "right": "Chimney", "main_op": "IMPL"}

rule_test1 = {"left": "NOT(AND(OR(AND(Awning, Billboard), Car), AND(Door, Machine)))", "right": "AND(Awning,NOT(OR(Billboard, Car)))", "main_op":"EQUIV"}
easy_Test_rule1 = {"left": "Suburban", "right": "AND(OR(Awning, Billboard), Car)", "main_op": "IMPL"}

NEW_AXIOMS = [
    {"axiom": rule_Hotel_Impl_Door, "active": False, "name": "rule_Hotel_Impl_Door"}, #high level rules
    {"axiom": rule_Hotel_Impl_Window, "active": False, "name": "rule_Hotel_Impl_Window"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Hotel_Impl_Car, "active": False, "name": "rule_Hotel_Impl_Car"}, #high level rules


    {"axiom": rule_Store_Impl_VendingMachine, "active": False, "name": "rule_Store_Impl_VendingMachine"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Store_Impl_Truck, "active": False, "name": "rule_Store_Impl_VendingMachine"}, #high level rules
    {"axiom": rule_Store_Impl_Statue, "active": False, "name": "rule_Store_Impl_Statue"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    {"axiom": rule_Suburban_Impl_Pipe, "active": False, "name": "rule_Suburban_Impl_Pipe"}, #high level rules
    {"axiom": rule_Suburban_Impl_Chimney, "active": False, "name": "rule_Suburban_Impl_Chimney"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    {"axiom":rule_test1, "active":True, "name":"rule_test1"},
]

NEW_AXIOMS_2 = [
    {"axiom": rule_Building_Impl_not_CarAndTruck, "active": True, "name": "building_no_car_truck"},
]

NEW_AXIOMS_3 = [
    {"axiom":rule_test1, "active":True, "name":"rule_test1"},
]

NEW_AXIOMS_1 = [
    {"axiom": easy_Test_rule1, "active": False, "name": "easy_Test_rule1"}, 
]



AXIOMS_BY_NAME = {item["name"]: item for item in NEW_AXIOMS}

'''
IMPL-> tenho de gerar o aplicable para o lado esquerdo, e o violation que representa o lado esq verdade, e o lado direito falso
basicamente

tenho de fazer
aplicable(left)
violation(left, NOT(right))

EQUIV -> fazer o IMPL nos dois sentidos

BUILDING_FACT -> n muda nada


'''
def generate_clingo_rules(new_axioms, new_lp_file, debug_mode=False):
    for ax in new_axioms:
        r = ax["axiom"]

        generate_clingo_rule(r["left"], r["right"], r["main_op"], ax["name"], new_lp_file, debug_mode)

    write_clingo_essentials(new_lp_file)

    

def generate_clingo_rule(l, r, main_op, axiom_name, new_lp_file, debug_mode=False):
    
    #print(f"debug_mode : {debug_mode}")
    left, right = normalize_rule(l,r, debug_mode)

    print(f"left: {left} | right: {right}")
    left = flatten_rec(left)
    right = flatten_rec(right)


    if main_op == "EQUIV":
        new_lp_file.write(f"\n\nrule({axiom_name}).\n")
        generate_aplicables_and_violations(left, right, axiom_name, new_lp_file)
        generate_aplicables_and_violations(right, left, axiom_name, new_lp_file)

    elif main_op == "IMPL":
        new_lp_file.write(f"\n\nrule({axiom_name}).\n")
        generate_aplicables_and_violations(left, right, axiom_name, new_lp_file)

    elif main_op == "BUILDING_FACT":
        new_lp_file.write(f"\n\nrule({axiom_name}).\n")
        if debug_mode: print("\n\n\nASSUMING THAT BUILDING FACT IS IMPL\n\n\n")
        generate_aplicables_and_violations(left, right, axiom_name, new_lp_file)

    else:
        print("TYPO ON MAIN OP")

    

'''
violation_count(Rule, N) :- rule(Rule), N = #count { X, Type : violation(X, Rule, Type) }.

applicable_count(Rule, N) :-rule(Rule),N = #count { X : applicable(X, Rule) }.


violating_sample(X, Rule) :-rule(Rule),violation(X, Rule, _).

violating_sample_count(Rule, N) :-rule(Rule),N = #count { X : violating_sample(X, Rule) }.

violation_type_count(Rule, Type, N) :-rule(Rule),violation(_, Rule, Type),N = #count { X : violation(X, Rule, Type) }.




#show violation_count/2.
#show applicable_count/2.
#show violating_sample_count/2.

#show violation_type_count/3.
%#show violation/2.

'''
def write_clingo_essentials(new_lp_file):
    new_lp_file.write("\n\n\n")

    new_lp_file.write("violation_count(Rule, N) :- rule(Rule), N = #count { X, Type : violation(X, Rule, Type) }.\n\n")
    new_lp_file.write("applicable_count(Rule, N) :-rule(Rule),N = #count { X : applicable(X, Rule) }.\n\n")
    new_lp_file.write("violating_sample(X, Rule) :-rule(Rule),violation(X, Rule, _).\n\n")
    new_lp_file.write("violating_sample_count(Rule, N) :-rule(Rule),N = #count { X : violating_sample(X, Rule) }.\n\n")
    new_lp_file.write("violation_type_count(Rule, Type, N) :-rule(Rule),violation(_, Rule, Type),N = #count { X : violation(X, Rule, Type) }.\n\n")

    new_lp_file.write("#show violation_count/2.\n")
    new_lp_file.write("#show applicable_count/2.\n")
    new_lp_file.write("#show violating_sample_count/2.\n")
    new_lp_file.write("#show violation_type_count/3.\n")



def normalize_rule(left, right,debug_mode=False):
    #print(f"debug:_mode {debug_mode}")
    return normalize_rule_rec(left,debug_mode=debug_mode), normalize_rule_rec(right,debug_mode=debug_mode)



def flatten_rec(node):
    if isinstance(node, list) and all(isinstance(x, str) for x in node):
        return [node]
    
    result = []
    for child in node:
        result.extend(flatten_rec(child))

    return result
            




'''
not e o base são intuitivos.

o or tem de criar duas possiveis soluções, enquanto o and tem de combinar todas as possiveis soluções do lado esquerdo com o lado direto


'''
def normalize_rule_rec(rule, invert=False,debug_mode=False):
    #print(f"debug_mode_rec {debug_mode}")
    op = rule.split("(")[0]
    if debug_mode:
        print(f"operation: {op}")

    #aqui tenho de combinar as soluções
    if op == "AND":
        #print("start AND")
        inner = rule[3:]
        if invert:
            return apply_or(inner, invert, debug_mode)

        return apply_and(inner, invert, debug_mode)

    elif op == "OR":
        #print("start OR")
        inner = rule[2:]
        if invert:
            return apply_and(inner, invert,debug_mode)

        return apply_or(inner, invert, debug_mode)


    elif op == "NOT":
        if debug_mode: print("start NOT")
        inner = rule[4:-1]

        return normalize_rule_rec(inner, invert=not invert, debug_mode=debug_mode)
    
    else:
        if not invert:
            return [f"{rule}"]
        else:
            return [f"NOT({rule})"]
            



def apply_and(inner, invert=False, debug_mode=False):
    # remove "AND" from start
    parts = split_top_level(inner)
    if debug_mode: 
        print(f"starting AND with inner {inner}")
            #for _and
    if len(parts) > 2:
        #print("inside for_and")
        start_obj = normalize_rule_rec(parts[0][1:].strip(), invert, debug_mode)

        complete_conj = start_obj

        for i in range(1, len(parts)):
            
            if i == len(parts) - 1:
                part = parts[i][:-1]
            else:
                part = parts[i]
        
            obj = normalize_rule_rec(part.strip(), invert=invert, debug_mode=debug_mode)
            print(f"in for and, complete_conj {complete_conj}, onj {obj}")
            complete_conj = complete_conj + obj


        return complete_conj
    
    l = normalize_rule_rec(parts[0][1:].strip(), invert, debug_mode)
    r = normalize_rule_rec(parts[1][:-1].strip(), invert, debug_mode)

    if debug_mode:
        print(f"l = {l}")
        print(f"r = {r}")

    return combine_sides(l,r, debug_mode)

def combine_sides(left, right, debug_mode = False):
    complete_conj = []
    if len(left) == 1:
        if len(right) == 1:
            
            to_append = flatten_concept(left) + flatten_concept(right)
            complete_conj.append(to_append)

            if debug_mode:
                print(f"left {flatten_concept(left)}, right {flatten_concept(right)} in left and right = 1")
                print(f"to append {to_append}")

        else:
            flat_left = flatten_concept(left)

            if debug_mode: print(f"left {flat_left}, left == 1, right > 2")
            
            for right_p in right:
                flat_right = flatten_concept(right_p)
                to_append = flat_left + flat_right

                if debug_mode:
                    print(f"right_p: {flat_right}")
                    print(f"to append {to_append}")

                complete_conj.append(to_append)

    else:
        if len(right) == 1:
            flat_right = flatten_concept(right)

            if debug_mode: print(f"right {flat_right}, right == 1, left > 2")

            for left_p in left:
                flat_left = flatten_concept(left_p)
                
                to_append = flat_left + flat_right
                
                if debug_mode:
                    print(f"left_p: {flat_left}")
                    print(f"to append {to_append}")

                complete_conj.append(to_append)

        else:
            if debug_mode: print(f"right and left are over 2")

            for left_p in left:

                flat_left = flatten_concept(left_p)
                if debug_mode: print(f"left_p: {flat_left}")

                for right_p in right:
                    flat_right = flatten_concept(right_p)
                    
                    to_append = flat_left + flat_right

                    if debug_mode:
                        print(f"right_p: {right_p}")
                        print(f"to_append {to_append}")

                    complete_conj.append(to_append)
    
    if debug_mode: print(f"combined sides: {complete_conj}")
    return complete_conj



def flatten_concept(c):
    flat = []
    for element in c:
        if isinstance(element, list):
            flat.extend(element)
        else:
            flat.append(element)
    return flat

def apply_or(inner, invert=False, debug_mode=False):        # remove "OR(" from start and ")" from end
    #print(f"inside OR, inner: {inner}")
    if debug_mode: print(f"starting OR with inner {inner}")
    parts = split_top_level(inner)

            #for _or?
    if len(parts) > 2:
        #print("inside for_or")
        start_obj = normalize_rule_rec(parts[0][1:].strip(),invert=invert, debug_mode=debug_mode)

        complete_disj = [start_obj]

        for i in range(1, len(parts)):
            
            if i == len(parts) - 1:
                part = parts[i][:-1]
            else:
                part = parts[i]
        
            obj = normalize_rule_rec(part.strip(), invert=invert, debug_mode=debug_mode)
            complete_disj.append(obj)

        
        #print(f"complete string {complete_string}")

        return complete_disj

    return normalize_rule_rec(parts[0][1:].strip(), invert, debug_mode=debug_mode), normalize_rule_rec(parts[1][:-1].strip(), invert, debug_mode=debug_mode)






def generate_aplicables_and_violations(left, right, axiom_name, new_lp_file):
    #GENERATE APLICABLE
    #new_lp_file.write(f"rule({axiom_name}).\n")

    for parts in left:
        write_applicable(axiom_name, parts, new_lp_file)
        for p in right:
            write_violations(axiom_name, parts, p, new_lp_file)

    print(f"left in generate a and vs: {left}")

    ""


def write_applicable(axiom_name, concept_list, new_lp_file):
    print(f"part: {concept_list}")

    new_lp_file.write(f"applicable(X, {axiom_name}) :- \n")
    
    c_len = len(concept_list)
    for i in range(c_len):
        concept = concept_list[i]
        op = concept.split("(")[0]
        print(f"write applicable {op}")

        if op == "NOT":
            concept = concept[4:-1].lower()
            if (i == c_len -1):
                new_lp_file.write(f"    not holds(X, {concept.lower()}).\n\n")
            else:
                new_lp_file.write(f"    not holds(X, {concept.lower()}),\n")

        else:
            if (i == c_len -1):
                new_lp_file.write(f"    holds(X, {concept.lower()}).\n\n")
            else:
                new_lp_file.write(f"    holds(X, {concept.lower()}),\n")


def write_violations(axiom_name, left, right, new_lp_file):
    print(f"write vs: left: {left}, right {right}")

    vName = generate_vName(left, right)

    new_lp_file.write(f"violation(X, {axiom_name}, {vName}) :- \n")
    
    #left side = 1
    for i in range(len(left)):
        concept = left[i]
        op = concept.split("(")[0]
        print(f"write applicable {op}")

        if op == "NOT":
            concept = concept[4:-1].lower()
            new_lp_file.write(f"    not holds(X, {concept.lower()}),\n")

        else:
            new_lp_file.write(f"    holds(X, {concept.lower()}),\n")

    #right side = 0
    c_len_right = len(right)
    for i in range(c_len_right):
        concept = right[i]
        op = concept.split("(")[0]
        print(f"write applicable {op}")

        # i want it to be 0, so i invert the not holds
        if op == "NOT":
            concept = concept[4:-1].lower()
            if (i == c_len_right -1):
                new_lp_file.write(f"    holds(X, {concept.lower()}).\n\n")
            else:
                new_lp_file.write(f"    holds(X, {concept.lower()}),\n")

        else:
            if (i == c_len_right -1):
                new_lp_file.write(f"    not holds(X, {concept.lower()}).\n\n")
            else:
                new_lp_file.write(f"    not holds(X, {concept.lower()}),\n")



def generate_vName(left, right):
    complete_str = "violation"

    for concept_l in left:
        op = concept_l.split("(")[0]
        if op == "NOT":
            concept_l = concept_l[4:-1].lower()
            complete_str = complete_str + f"_not_holds_{concept_l}"
        else:
            complete_str = complete_str + f"_holds_{concept_l}"

    for concept_r in right:
        op = concept_r.split("(")[0]
        if op == "NOT":
            concept_r = concept_r[4:-1].lower()
            complete_str = complete_str + f"_holds_{concept_r}"
        else:
            complete_str = complete_str + f"_not_holds_{concept_r}"

    return complete_str


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



new_lp_path = "newRules.lp"
new_lp_file = open(new_lp_path, "w+")

generate_clingo_rules(ALL_AXIOMS, new_lp_file, debug_mode=False)

