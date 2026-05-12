

#dict:
#rule: the main axiom. A primeira classe é o conceito mais a esq da regra, a partir daí é Operation -> conceitos envolvidos. em relação as operações
#a Equivalencia/Implicação é ignorada, a menos que seja a unica operação. quando apenas existe um AND/OR/NOT, é só preciso meter essa operação
#sem mudanças; se houver mais do que uma, a partir da primeira operação a primeira posição da lista dos conceitos envolvidos é ignorada.

#nbr_of_ops: numero de opções, 1 se só houver uma equivalencia/implicacao ou se houver apenas 1 And/Or/not. conta o numero de OPs na rule
#MAIN_OP: "EQUIV"/"IMPL". representa a principal operação, que é ignorada quando existe outras operações.

#NAO USAR PLACEHOLDERS QUE NAO APARECEM NA REGRA CORRESPONDENTE. breaks o getClassesFromRules

#High Level Rules
import re
import json

#FOR_OR, FOR_AND
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
rule_Industrial_notTable = {"left": "Industrial", "right": "NOT(Table)", "main_op": "IMPL"}

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


''' NEW STUFF '''
rule_Hotel_Impl_Door = {"left": "Hotel", "right": "AND(Door, Chimney)", "main_op": "IMPL"}
rule_Hotel_Impl_Window = {"left": "Hotel", "right": "AND(Window, Pipe)", "main_op": "IMPL"}
rule_Hotel_Impl_Car = {"left": "Hotel", "right": "AND(Car, Awning)", "main_op": "IMPL"}

rule_Store_Impl_Door = {"left": "Store", "right": "AND(Door, NOT(Chimney))", "main_op": "IMPL"}
rule_Store_Impl_Window = {"left": "Store", "right": "AND(Window, NOT(Pipe))", "main_op": "IMPL"}
rule_Store_Impl_Car = {"left": "Store", "right": "AND(Car, NOT(Awning))", "main_op": "IMPL"}


rule_cSite_Impl_Truck = {"left": "ConstructionSite", "right": "OR(Truck, Chimney)", "main_op": "IMPL"}
rule_cSite_Impl_Table = {"left": "ConstructionSite", "right": "OR(Table, Pipe)", "main_op": "IMPL"}
rule_cSite_Impl_Car = {"left": "ConstructionSite", "right": "OR(Car, Awning)", "main_op": "IMPL"}

rule_Suburban_Impl_Truck = {"left": "Suburban", "right": "OR(Truck, NOT(Chimney))", "main_op": "IMPL"}
rule_Suburban_Impl_Table = {"left": "Suburban", "right": "OR(Table, NOT(Pipe))", "main_op": "IMPL"}
rule_Suburban_Impl_Car = {"left": "Suburban", "right": "OR(Car, NOT(Awning))", "main_op": "IMPL"}




rule_Suburban_Impl_Pipe = {"left": "Suburban", "right": "Pipe", "main_op": "IMPL"}
rule_Suburban_Impl_Chimney = {"left": "Suburban", "right": "Chimney", "main_op": "IMPL"}

rule_test1 = {"left": "NOT(AND(OR(AND(Awning, Billboard), Car), AND(Door, Machine)))", "right": "AND(Awning,NOT(OR(Billboard, Car)))", "main_op":"EQUIV"}
easy_Test_rule1 = {"left": "Suburban", "right": "AND(OR(Awning, Billboard), Car)", "main_op": "IMPL"}


ALL_AXIOMS = [
    {"axiom": rule_BuildingTypes, "active": False, "name": "building_types"}, #high level rules
    {"axiom": rule_FeatureTypes, "active": False, "name": "feature_types"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_CommercialBuildingType, "active": False, "name": "commercial"},
    {"axiom": rule_IndustrialBuildingType, "active": False, "name": "industrial"},
    {"axiom": rule_ResidentialBuildingType, "active": False, "name": "residential"},


    #done
    {"axiom": rule_Buiding_Impl_not_carAndTruck_OrMachine, "active": False, "name": "building_impl_complex"}, #implications, more related to the building creation process
    {"axiom": rule_Building_Impl_not_CarAndTruck, "active": False, "name": "building_no_car_truck"},
    {"axiom": rule_Building_Impl_not_ChimneyAndStatue, "active": False, "name": "building_no_chimney_statue"},
    {"axiom": rule_Building_noDoorOrNoWindow_Impl_noAwning, "active": False, "name": "building_noDoorOrNoWindow_Impl_noAwning"},


    #equiv
    {"axiom": rule_Hotel_Wallsign, "active": True, "name":"hotel"}, #comercial
    {"axiom": rule_Store_Billboard, "active": True, "name":"store"}, #comercial
    {"axiom": rule_Industrial_notTable, "active": False, "name":"industrial_not_table"}, #industrial
    {"axiom": rule_ConstructionSite_Machine, "active": True, "name":"constructionsite"}, #industrial
    {"axiom": rule_Suburban_Porch, "active": True, "name":"suburban"}, #residential


    #conj
    {"axiom": rule_MiscCommercial_AwningAndTable, "active": False, "name":"misccommercial"}, #comercial
    {"axiom": rule_MiscIndustrial_notAwningAndTruck, "active": False, "name":"miscindustrial"}, #industrial
    {"axiom": rule_CH_CarAndTiledroof, "active": False, "name":"countryhouse"}, #residential
    {"axiom": rule_PowerPlant_ChimneyAndPipe, "active": False, "name":"powerplant"}, #industrial
    {"axiom": rule_WaterTreatment_PipeAndTruck, "active": False, "name":"watertreatment"}, #industrial

    #disj
    {"axiom": rule_Cafe_StatueOrVendingMachine, "active": False, "name":"cafe"}, #comercial

    #complex
    {"axiom": rule_Restaurant_CarOrTruckAndSign, "active": False,"name":"restaurant"},#comercial
    {"axiom": rule_MiscResidential_not_AwningAndTable_AndTiledRoof, "active": False, "name":"miscresidential"},#residential
    {"axiom": rule_Residential_Impl_not_ChimneyOrPipe, "active": False, "name": "residential_no_chimney_pipe"},#residential    
    
    
    {"axiom": rule_Hotel_Impl_Door, "active": True, "name": "rule_hotel_impl_door"}, #high level rules
    {"axiom": rule_Hotel_Impl_Window, "active": True, "name": "rule_hotel_impl_window"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Hotel_Impl_Car, "active": True, "name": "rule_hotel_impl_car"}, #high level rules

    {"axiom": rule_Store_Impl_Door, "active": True, "name": "rule_store_impl_door".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Store_Impl_Window, "active": True, "name": "rule_store_impl_window".lower()}, #high level rules
    {"axiom": rule_Store_Impl_Car, "active": True, "name": "rule_store_impl_car".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    {"axiom": rule_cSite_Impl_Truck, "active": True, "name": "rule_constructionsite_impl_truck"}, #high level rules
    {"axiom": rule_cSite_Impl_Table, "active": True, "name": "rule_constructionsite_impl_table"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_cSite_Impl_Car, "active": True, "name": "rule_constructionsite_impl_car"}, #high level rules

    {"axiom": rule_Suburban_Impl_Truck, "active": True, "name": "rule_suburban_impl_truck".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Suburban_Impl_Table, "active": True, "name": "rule_suburban_impl_table".lower()}, #high level rules
    {"axiom": rule_Suburban_Impl_Car, "active": True, "name": "rule_suburban_impl_car".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    #{"axiom": rule_Suburban_Impl_Pipe, "active": False, "name": "rule_suburban_impl_pipe"}, #high level rules
    #{"axiom": rule_Suburban_Impl_Chimney, "active": False, "name": "rule_suburban_impl_chimney"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    #new stuff

]

def generate_json_config_file():

    with open("axiom_data.json", "w") as json_file:
        json.dump(ALL_AXIOMS, json_file, indent=4)


    

AXIOMS_BY_NAME = {item["name"]: item for item in ALL_AXIOMS}

def print_only_active_rules(consistency, rule_holds_counts, rule_vacuously_holds_count, violation_type_counts, txt_file):
    #print("start printing in rules and concepts")

    txt_file.write("\n\n========= ACTIVE RULES =========\n\n")
    for rule_name, value in consistency.items():
        r = AXIOMS_BY_NAME.get(rule_name)

        if r is None:
            print(f"rule {rule_name} not found")
            continue

        if r["active"]:
            txt_file.write(get_string_axiom(r["name"]))
    
    
    txt_file.write("\n\n========= CONISTENCY PER RULE =========\n\n")
    for rule_name, value in consistency.items():
        r = AXIOMS_BY_NAME.get(rule_name)


        if r is None:
            print(f"rule {rule_name} not found")
            continue

        if r["active"]:
            holds = rule_holds_counts.get(rule_name, 0)
            vac_holds = rule_vacuously_holds_count.get(rule_name, 0)
            vtypes = violation_type_counts.get(rule_name, {})
            total_violations = sum(vtypes.values())
            total = holds + total_violations + vac_holds

            txt_file.write(
                f"{rule_name} | consistency={value:.4f} | "
                f"rule_holds={holds} | rule_vac_holds={vac_holds} | violations={total_violations} | total={total}\n"
            )

            for vtype, count in sorted(vtypes.items(), key=lambda x: -x[1]):
                txt_file.write(f"    - {vtype}: {count}\n")

            txt_file.write("\n")
        


#rule1 = {"rule_left_side": "MiscIndustrial", "rule_right_side": "AND(NOT(Awning), Truck)", "Main_OP": "EQUIV"}

#rule2 = {"rule_left_side": "Hotel", "rule_right_side": "WallSign", "main_op": "EQUIV"}

AXIOMS = {a["name"]:a["axiom"] for a in ALL_AXIOMS if a["active"]}

def getClassesFromRules(all_concepts):
    classes = []

    #print(f"getClassesFromRules: axioms.items{AXIOMS.items()} ")

    for ax in AXIOMS.items(): 

        r = ax[1]
        #print(f"getClassesFromRules: r {r} ")

        conceptsAndOperationsInRule = []
        #rule_left_side = flatten_rule(r["rule_left_side"])
        #rule_right_side = flatten_rule(r["rule_right_side"])

        left = re.split(r"[(,)]", r["left"])
        right = re.split(r"[(,)]", r["right"])

        rule = left + right

        print(f"rule in getClassesFromRules {rule}")

        for element in rule:
            conceptsAndOperationsInRule.append(element.strip())

        concepts = [c for c in all_concepts if c in conceptsAndOperationsInRule]

        for c in concepts:
            if c not in classes:
                classes.append(c)


    return classes

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
    "WaterTreatment"
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

ALL_CONCEPTS = [
    #"Building",
    #"Feature",

    "Residential",
    "Commercial",
    "Industrial",

    #nbr de vezes que aparece em todas as regras
    "Door", #1
    "Window", #1
    "Awning", #4
    "Billboard",#1
    "Porch",#1
    "Sign",#1
    "Table",#3
    "TiledRoof",#2
    "TiledRoofTop",#0
    "VendingMachine",#1
    "WallSign",#1
    "Statue",#2
    "Chimney",#3
    "Pipe",#3
    "Machine",#2
    "Truck",#5
    "Car"#4
    #o carro e o camião aparacem muitas vezes, mas 3 das 4 vezes que o carro aparece,
    #aparece em conjunto com o camião
]


def get_final_classes_in_classes(classes, all_final_classes):
    return [c for c in all_final_classes if c in classes]

def get_concepts_in_classes(classes, all_concepts):
    return [c for c in all_concepts if c in classes]

def orderClassList(classes, all_final_classes, all_concepts):
    final_classes = get_final_classes_in_classes(classes, all_final_classes)
    print(f"final classes  in rules and concepts{final_classes}")
    concepts = get_concepts_in_classes(classes, all_concepts)
    print(f"final concepts {concepts}")


    return final_classes , concepts, final_classes + concepts


FINAL_CLASSES, CONCEPTS, CLASSES = orderClassList(getClassesFromRules(ALL_CLASSES), ALL_FINAL_CLASSES, ALL_CONCEPTS)


print(f"classes in concepts and rules {CLASSES}")
#CLASSES = FINAL_CLASSES + CONCEPTS


# metodos "publicos" 

def get_all_final_classes():
    return ALL_FINAL_CLASSES

def get_all_classes():
    return ALL_CLASSES

def get_classes():
    return CLASSES

def get_final_classes():
    return FINAL_CLASSES

def get_concepts():
    return CONCEPTS

def get_all_axioms():
    return ALL_AXIOMS

def get_ALL_CONCEPTS():
    return ALL_CONCEPTS

def get_active_axioms():
    return AXIOMS

def get_normalized_FINAL_CLASSES():
    normalized_list = []

    for cls in FINAL_CLASSES:
        normalized_list.append(cls.lower())

    return normalized_list

def get_string_axiom(rule_name):
    ax = AXIOMS_BY_NAME[rule_name]["axiom"]

    return f"{rule_name}: [AXIOM] {ax["main_op"]}({ax["left"]}, {ax["right"]})\n"
    

    




'''
    # Axioms
    # MiscCommercial = Awning and Table
    # MiscIndustrial = not Awning and Truck
    # CountryHouse = Car and TiledRoof

    # Cafe = Statue or Vending Machine
    # Hotel = Wall Sign
    # Store = Billboard
'''

'''
def flatten_rule(rule):
    flat = []
    for element in rule:
        if isinstance(element, list):
            flat.extend(element)
        else:
            flat.append(element)
    return flat

test = getClassesFromRules(ALL_CLASSES)
print(f"test {test}")
#test1 = get_final_classes_in_classes(test, ALL_FINAL_CLASSES)

test1 = orderClassList(test, ALL_FINAL_CLASSES, ALL_CONCEPTS)
print(f"test1 {test1}")
CLASSES = [
    "MiscIndustrial",
    "Awning",
    "Truck",
]


CLASSES = [
    "CountryHouse",
    "MiscIndustrial",
    "MiscCommercial",

    "Car",
    "TiledRoof",
    "Awning",
    "Truck",
    "Table",
]


CLASSES = [
    "CountryHouse",
    "Car",
    "TiledRoof",
]

CLASSES = [
    "MiscIndustrial",
    "Awning",
    "Truck",
]

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

rule_BuildingTypes = {"rule": ("Building", "OR", ["Residential", "Commercial", "Industrial"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}
rule_FeatureTypes = {"rule": ("Feature", "OR", ["Awning", "Billboard", "Car", "Chimney", "Door", "Machine", "Pipe","Porch",
             "Sign", "Statue", "Table", "TiledRoof", "Truck", "VendingMachine", "WallSign", "Window"]), "nbr_of_ops": 1, "Main_OP": "EQUIV"}

#preciso de implementar o Implica -> "IMPL"


Building ⊑ ¬((∃has.Car ⊔ ∃has.T ruck) ⊓ (∃has.Machine))
rule_Buiding_Impl_not_carAndTruck_OrMachine = {"rule": ("Building", "OR", ["Car", "Truck"], "AND", ["Machine", "Machine"],
                                                                  "NOT", ["Machine"]), "nbr_of_ops": 3, "Main_OP": "IMPL"}


#second rule Building ⊓¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning -> o meu codigo n ta preparado para isto, dps tenho de melhorar a logica


# Building ⊑¬(∃has.Car ⊓ ∃has.T ruck)
rule_Building_Impl_not_CarAndTruck = {"rule": ("Building", "AND", ["Car", "Truck"], "NOT", ["Car"]), "nbr_of_ops": 2, "Main_OP": "IMPL"}


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

# Residential⊑¬(∃has.Chimney ⊔ ∃has.Pipe)
rule_Residential_Impl_not_ChimneyOrPipe = {"rule": ("Residential", "OR", ["Chimney", "Pipe"], "NOT", ["Chimney"]), "nbr_of_ops": 2, "Main_OP": "IMPL"}

'''