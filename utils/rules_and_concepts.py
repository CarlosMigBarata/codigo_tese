



#NAO USAR PLACEHOLDERS QUE NAO APARECEM NA REGRA CORRESPONDENTE. breaks o getClassesFromRules

#High Level Rules
import re
import json

#FOR_OR, FOR_AND
#rule_BuildingTypes = {"left": "Building", "right": "OR(Residential, Commercial, Industrial)", "main_op": "BUILDING_FACT"}

#rule_FeatureTypes = {"left": "Feature", "right": "OR(Awning, Billboard, Car, Chimney, Door, Machine, Pipe, Porch, "
#"Sign, Statue, Table, TiledRoof, Truck, VendingMachine, WallSign, Window)", "main_op": "EQUIV"}

from enum import Enum

class MainOperations(Enum):
    EQUIVALENCE = "EQUIV"
    IMPLICATION = "IMPL"
    BUILDING_FACT = "BUILDIG_FACT"

''' Building ⊑ ¬((∃has.Car ⊔ ∃has.T ruck) ⊓ (∃has.Machine))'''
rule_Buiding_Impl_not_carAndTruck_OrMachine = {"left": "Building", "right":"NOT(AND(OR(Car,Truck),Machine))", "main_op":MainOperations.BUILDING_FACT}


#second rule Building ⊓¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning -> o meu codigo n ta preparado para isto, dps tenho de melhorar a logica


# Building ⊑¬(∃has.Car ⊓ ∃has.T ruck)
rule_Building_Impl_not_CarAndTruck = {"left": "Building", "right":"NOT(AND(Car,Truck))", "main_op":MainOperations.BUILDING_FACT}


#Building ⊑ ¬(∃has.Chimney ⊓ ∃has.Statue)
rule_Building_Impl_not_ChimneyAndStatue = {"left": "Building", "right":"NOT(AND(Chimney,Statue))", "main_op":MainOperations.BUILDING_FACT}

#FOR_OR
rule_CommercialBuildingType = {"left": "Commercial", "right": "OR(Cafe, Hotel, MiscCommercial, Restaurant, Store)", "main_op": MainOperations.EQUIVALENCE}
rule_IndustrialBuildingType = {"left": "Industrial", "right": "OR(ConstructionSite, MiscIndustrial, PowerPlant, WaterTreatment)", "main_op":  MainOperations.EQUIVALENCE}
rule_ResidentialBuildingType = {"left": "Residential", "right": "OR(CountryHouse, MiscResidential, Suburban)", "main_op":  MainOperations.EQUIVALENCE}

rule_CommercialRestrictions= {"left": "Commercial", "right":"OR(NOT(Machine), NOT(Pipe), NOT(Porch), NOT(TiledRoof))", "main_op": MainOperations.IMPLICATION }
rule_IndustrialRestrictions= {"left": "Industrial", "right":"OR(NOT(WallSign), NOT(Billboard), NOT(Sign), NOT(Statue), NOT(VendingMachine), NOT(Porch), NOT(TiledRoof))", "main_op": MainOperations.IMPLICATION }
rule_ResidentialRestrictions= {"left": "Residential", "right":"OR(NOT(WallSign), NOT(Billboard), NOT(Sign), NOT(Statue), NOT(VendingMachine), NOT(Machine))", "main_op": MainOperations.IMPLICATION }


#rules related to final classes
#when using the second rule, its necessary to place a placeholder in this first slot

#equiv
rule_Hotel_Wallsign = {"left": "Hotel", "right": "WallSign", "main_op":  MainOperations.EQUIVALENCE}
rule_Store_Billboard = {"left": "Store", "right": "Billboard", "main_op":  MainOperations.EQUIVALENCE}
rule_Industrial_notTable = {"left": "Industrial", "right": "NOT(Table)", "main_op": MainOperations.IMPLICATION}

rule_ConstructionSite_Machine = {"left": "ConstructionSite", "right": "Machine", "main_op":  MainOperations.EQUIVALENCE}
rule_Suburban_Porch = {"left": "Suburban", "right": "Porch", "main_op":  MainOperations.EQUIVALENCE}

#conj
rule_MiscCommercial_AwningAndTable = {"left": "MiscCommercial", "right": "AND(Awning, Table)", "main_op": MainOperations.EQUIVALENCE}
rule_MiscIndustrial_notAwningAndTruck = {"left": "MiscIndustrial", "right": "AND(AND(NOT(Awning), Truck),NOT(Sign))", "main_op":  MainOperations.EQUIVALENCE}
rule_CH_CarAndTiledroof = {"left": "CountryHouse", "right": "AND(Car, TiledRoof)", "main_op":  MainOperations.EQUIVALENCE}
rule_PowerPlant_ChimneyAndPipe = {"left": "PowerPlant", "right": "AND(Chimney, Pipe)", "main_op":  MainOperations.EQUIVALENCE}
rule_WaterTreatment_PipeAndTruck = {"left": "WaterTreatment", "right": "AND(Pipe, Truck)", "main_op":  MainOperations.EQUIVALENCE}


#disj
rule_Cafe_StatueOrVendingMachine = {"left": "Cafe", "right": "OR(Statue, VendingMachine)", "main_op":  MainOperations.EQUIVALENCE}


#regras complexas
#Restaurant≡(∃has.Car ⊔ ∃has.T ruck) ⊓ ∃has.Sign
rule_Restaurant_CarOrTruckAndSign = {"left": "Restaurant", "right": "AND(OR(Car,Truck),Sign)", "main_op":  MainOperations.EQUIVALENCE}


#MiscResidential≡ ¬(∃has.Awning ⊓ ∃has.T able) ⊓ ∃has.T iledRoof
rule_MiscResidential_not_AwningAndTable_AndTiledRoof = {"left": "MiscResidential", "right": "AND(NOT(AND(Awning,Table)),TiledRoof)", "main_op":  MainOperations.EQUIVALENCE}

# Residential ⊑ ¬ (∃has.Chimney ⊔ ∃has.Pipe)
rule_Residential_Impl_not_ChimneyOrPipe = {"left": "Residential", "right":"NOT(OR(Chimney,Pipe))", "main_op":MainOperations.IMPLICATION}

#Building ⊓ ¬(∃has.Door ⊔ ∃has.Window) ⊑ ¬∃has.Awning
rule_Building_noDoorOrNoWindow_Impl_noAwning = {"left": "NOT(OR(Door,Window))", "right":"NOT(Awning)", "main_op":MainOperations.IMPLICATION}


''' NEW STUFF '''
#rule_Hotel_Impl_Door = {"left": "Hotel", "right": "AND(Door, Chimney)", "main_op": "IMPL"}
#rule_Hotel_Impl_Window = {"left": "Hotel", "right": "AND(Window, Pipe)", "main_op": "IMPL"}
rule_Hotel_Impl_Car = {"left": "Hotel", "right": "AND(NOT(Car), Awning)", "main_op": MainOperations.IMPLICATION}

#rule_Store_Impl_Door = {"left": "Store", "right": "AND(Door, NOT(Chimney))", "main_op": "IMPL"}
#rule_Store_Impl_Window = {"left": "Store", "right": "AND(Window, NOT(Pipe))", "main_op": "IMPL"}
rule_Store_Impl_Car = {"left": "Store", "right": "AND(Car, Pipe)", "main_op": MainOperations.IMPLICATION}


#rule_cSite_Impl_Truck = {"left": "ConstructionSite", "right": "OR(Truck, Chimney)", "main_op": "IMPL"}
#rule_cSite_Impl_Table = {"left": "ConstructionSite", "right": "OR(Table, Window)", "main_op": "IMPL"}
rule_cSite_Impl_Car = {"left": "ConstructionSite", "right": "OR(NOT(Car), TiledRoof)", "main_op": MainOperations.IMPLICATION}

#rule_Suburban_Impl_Truck = {"left": "Suburban", "right": "OR(Truck, NOT(Chimney))", "main_op": "IMPL"}
rule_Suburban_Impl_CarPipe = {"left": "Suburban", "right": "AND(Car, VendingMachine)", "main_op": MainOperations.IMPLICATION}
rule_Suburban_Impl_Car = {"left": "Suburban", "right": "OR(Car, Door)", "main_op": MainOperations.IMPLICATION}


'''DATASET test1''' #changin comercials: Cafe, Hotel, MiscCommercial, Restaurant, Store
rule_Cafe_notCarAwning = {"left": "Cafe", "right": "AND(NOT(Car), Awning)", "main_op": MainOperations.EQUIVALENCE}
rule_Hotel_CarPipe = {"left": "Hotel", "right": "AND(Car, Pipe)", "main_op": MainOperations.EQUIVALENCE}
rule_MiscCommercial_notCarTiledroof = {"left": "MiscCommercial", "right": "OR(NOT(Car), TiledRoof)", "main_op": MainOperations.EQUIVALENCE}
rule_Restaurant_CarVendingMachine = {"left": "Restaurant", "right": "AND(Car, VendingMachine)", "main_op": MainOperations.EQUIVALENCE}
rule_Store_CarDoor = {"left": "Store", "right": "OR(Car, Door)", "main_op": MainOperations.EQUIVALENCE}


'''DATASET test2''' #changin comercials: Cafe, Hotel, MiscCommercial, Restaurant, Store, Billboard
rule_Cafe_WallSignAndAwning = {"left": "Cafe", "right": "AND(WallSign, Awning)", "main_op": MainOperations.EQUIVALENCE}
rule_Cafe_WallSignAndBillboard = {"left": "Cafe", "right": "AND(WallSign, Billboard)", "main_op": MainOperations.EQUIVALENCE}
rule_Hotel_WallSignOrAwning = {"left": "Hotel", "right": "OR(WallSign, Awning)", "main_op": MainOperations.EQUIVALENCE}
rule_Hotel_WallSignAndBillboard = {"left": "Hotel", "right": "OR(WallSign, Billboard)", "main_op": MainOperations.EQUIVALENCE}

rule_PowerPlant_ChimneyAndPipe = {"left": "PowerPlant", "right": "AND(Chimney, Pipe)", "main_op":  MainOperations.EQUIVALENCE}
rule_PowerPlant_NotChimneyAndMachine = {"left": "PowerPlant", "right": "AND(NOT(Chimney), Machine)", "main_op":  MainOperations.EQUIVALENCE}
rule_WaterTreatment_ChimneyAndPipe = {"left": "WaterTreatment", "right": "OR(Chimney, Pipe)", "main_op":  MainOperations.EQUIVALENCE}
rule_WaterTreatment_NotChimneyAndMachine = {"left": "WaterTreatment", "right": "OR(NOT(Chimney), Machine)", "main_op":  MainOperations.EQUIVALENCE}

rule_CH_NotCarAndTiledroof = {"left": "CountryHouse", "right": "AND(NOT(Car), TiledRoof)", "main_op":  MainOperations.EQUIVALENCE}
rule_CH_NotCarAndDoor = {"left": "CountryHouse", "right": "AND(NOT(Car), Door)", "main_op":  MainOperations.EQUIVALENCE}
rule_Suburban_NotCarAndTiledroof = {"left": "Suburban", "right": "OR(NOT(Car), TiledRoof)", "main_op":  MainOperations.EQUIVALENCE}
rule_Suburban_NotCarAndDoor = {"left": "Suburban", "right": "OR(NOT(Car), Door)", "main_op":  MainOperations.EQUIVALENCE}

rule_DT2_CommercialBuildingType = {"left": "Commercial", "right": "OR(Cafe, Hotel)", "main_op": MainOperations.EQUIVALENCE}
rule_DT2_IndustrialBuildingType = {"left": "Industrial", "right": "OR(PowerPlant, WaterTreatment)", "main_op":  MainOperations.EQUIVALENCE}
rule_DT2_ResidentialBuildingType = {"left": "Residential", "right": "OR(CountryHouse, Suburban)", "main_op":  MainOperations.EQUIVALENCE}



NEW_AXIOMS_EQUIV = [
    {"axiom": rule_Cafe_notCarAwning, "active": True, "name": "rule_Cafe_notCarAwning".lower()}, #high level rules
    {"axiom": rule_Hotel_CarPipe, "active": True, "name": "rule_Hotel_CarPipe".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_MiscCommercial_notCarTiledroof, "active": True, "name": "rule_MiscCommercial_notCarTiledroof".lower()}, #high level rules
    {"axiom": rule_Restaurant_CarVendingMachine, "active": True, "name": "rule_Restaurant_CarVendingMachine".lower()}, #high level rules
    {"axiom": rule_Store_CarDoor, "active": True, "name": "rule_Store_CarDoor".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
]

NEW_AXIOMS_IMPL = [
    #{"axiom": rule_Hotel_Impl_Door, "active": False, "name": "rule_hotel_impl_door"}, #high level rules
    #{"axiom": rule_Hotel_Impl_Window, "active": False, "name": "rule_hotel_impl_window"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Hotel_Impl_Car, "active": True, "name": "rule_hotel_impl_car"}, #high level rules

    #{"axiom": rule_Store_Impl_Door, "active": False, "name": "rule_store_impl_door".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    #{"axiom": rule_Store_Impl_Window, "active": False, "name": "rule_store_impl_window".lower()}, #high level rules
    {"axiom": rule_Store_Impl_Car, "active": True, "name": "rule_store_impl_car".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    #{"axiom": rule_cSite_Impl_Truck, "active": False, "name": "rule_constructionsite_impl_truck"}, #high level rules
    #{"axiom": rule_cSite_Impl_Table, "active": False, "name": "rule_constructionsite_impl_table"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_cSite_Impl_Car, "active": True, "name": "rule_constructionsite_impl_car"}, #high level rules

    #{"axiom": rule_Suburban_Impl_Truck, "active": False, "name": "rule_suburban_impl_truck".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Suburban_Impl_CarPipe, "active": True, "name": "rule_Suburban_Impl_Pipe".lower()}, #high level rules
    {"axiom": rule_Suburban_Impl_Car, "active": True, "name": "rule_suburban_impl_car".lower()}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
]


CLASSIC_ONTOLOGY = [    

    {"axiom": rule_Buiding_Impl_not_carAndTruck_OrMachine, "active": True, "name": "building_impl_complex"}, #implications, more related to the building creation process
    {"axiom": rule_Building_Impl_not_CarAndTruck, "active": True, "name": "building_no_car_truck"},
    {"axiom": rule_Building_Impl_not_ChimneyAndStatue, "active": True, "name": "building_no_chimney_statue"},
    {"axiom": rule_Building_noDoorOrNoWindow_Impl_noAwning, "active": True, "name": "building_noDoorOrNoWindow_Impl_noAwning"},

    {"axiom": rule_CommercialRestrictions, "active":False, "name":"rule_CommercialRestrictions"},
    {"axiom": rule_IndustrialRestrictions, "active":False, "name":"rule_IndustrialRestrictions"},
    {"axiom": rule_ResidentialRestrictions, "active":False, "name":"rule_ResidentialRestrictions"},


    {"axiom": rule_CommercialBuildingType, "active": True, "name": "commercial"},
        {"axiom": rule_Hotel_Wallsign, "active": True, "name":"hotel"}, #basic equiv
        {"axiom": rule_Store_Billboard, "active": True, "name":"store"}, #basic equiv
        {"axiom": rule_MiscCommercial_AwningAndTable, "active": True, "name":"misccommercial"}, #conj
        {"axiom": rule_Cafe_StatueOrVendingMachine, "active": True, "name":"cafe"}, #disj
        {"axiom": rule_Restaurant_CarOrTruckAndSign, "active": True,"name":"restaurant"},#complex?


    {"axiom": rule_IndustrialBuildingType, "active": True, "name": "industrial"},
        {"axiom": rule_Industrial_notTable, "active": False, "name":"industrial_not_table"}, #basic equiv
        {"axiom": rule_ConstructionSite_Machine, "active": False, "name":"constructionsite"}, #basic equiv
        {"axiom": rule_MiscIndustrial_notAwningAndTruck, "active": False, "name":"miscindustrial"}, #conj
        {"axiom": rule_PowerPlant_ChimneyAndPipe, "active": False, "name":"powerplant"}, #conj
        {"axiom": rule_WaterTreatment_PipeAndTruck, "active": False, "name":"watertreatment"}, #conj


    {"axiom": rule_ResidentialBuildingType, "active": True, "name": "residential"},
        {"axiom": rule_Suburban_Porch, "active": False, "name":"suburban"}, #basic equiv
        {"axiom": rule_CH_CarAndTiledroof, "active": False, "name":"countryhouse"}, #conj
        {"axiom": rule_MiscResidential_not_AwningAndTable_AndTiledRoof, "active": False, "name":"miscresidential"},#residential
        {"axiom": rule_Residential_Impl_not_ChimneyOrPipe, "active": False, "name": "residential_no_chimney_pipe"},#residential    
]


'''DATASET test2''' #changin comercials: Cafe, Hotel, MiscCommercial, Restaurant, Store, Billboard
rule_Cafe_WallSignAndAwning = {"left": "Cafe", "right": "AND(WallSign, Awning)", "main_op": MainOperations.IMPLICATION}
rule_Cafe_WallSignAndBillboard = {"left": "Cafe", "right": "AND(WallSign, Billboard)", "main_op": MainOperations.IMPLICATION}
rule_Hotel_WallSignOrAwning = {"left": "Hotel", "right": "OR(WallSign, Awning)", "main_op": MainOperations.IMPLICATION}
rule_Hotel_WallSignOrBillboard = {"left": "Hotel", "right": "OR(WallSign, Billboard)", "main_op": MainOperations.IMPLICATION}

rule_PowerPlant_ChimneyAndPipe = {"left": "PowerPlant", "right": "AND(Chimney, Pipe)", "main_op":  MainOperations.IMPLICATION}
#rule_PowerPlant_NotChimneyAndMachine = {"left": "PowerPlant", "right": "AND(NOT(Chimney), Machine)", "main_op":  MainOperations.IMPLICATION}
rule_WaterTreatment_ChimneyOrPipe = {"left": "WaterTreatment", "right": "OR(Chimney, Pipe)", "main_op":  MainOperations.IMPLICATION}
rule_WaterTreatment_NotChimneyOrMachine = {"left": "WaterTreatment", "right": "OR(NOT(Chimney), Machine)", "main_op":  MainOperations.IMPLICATION}

rule_CH_NotCarAndTiledroof = {"left": "CountryHouse", "right": "AND(NOT(Car), TiledRoof)", "main_op":  MainOperations.IMPLICATION}
rule_CH_NotCarAndDoor = {"left": "CountryHouse", "right": "AND(NOT(Car), Door)", "main_op":  MainOperations.IMPLICATION}
rule_Suburban_NotCarOrTiledroof = {"left": "Suburban", "right": "OR(NOT(Car), TiledRoof)", "main_op":  MainOperations.IMPLICATION}
rule_Suburban_NotCarOrDoor = {"left": "Suburban", "right": "OR(NOT(Car), Door)", "main_op":  MainOperations.IMPLICATION}

rule_DT2_CommercialBuildingType = {"left": "Commercial", "right": "OR(Cafe, Hotel)", "main_op": MainOperations.EQUIVALENCE}
rule_DT2_IndustrialBuildingType = {"left": "Industrial", "right": "OR(PowerPlant, WaterTreatment)", "main_op":  MainOperations.EQUIVALENCE}
rule_DT2_ResidentialBuildingType = {"left": "Residential", "right": "OR(CountryHouse, Suburban)", "main_op":  MainOperations.EQUIVALENCE}



NEW_ONTOLOGY1 = [    

    {"axiom": rule_DT2_CommercialBuildingType, "active": True, "name": "rule_DT2_CommercialBuildingType"},
        {"axiom": rule_Cafe_WallSignAndAwning, "active": True, "name":"rule_Cafe_WallSignAndAwning"}, #basic equiv
        {"axiom": rule_Cafe_WallSignAndBillboard, "active": True, "name":"rule_Cafe_WallSignAndBillboard"}, #basic equiv
        {"axiom": rule_Hotel_WallSignOrAwning, "active": True, "name":"rule_Hotel_WallSignOrAwning"}, #conj
        {"axiom": rule_Hotel_WallSignOrBillboard, "active": True, "name":"rule_Hotel_WallSignOrBillboard"}, #disj


    {"axiom": rule_DT2_IndustrialBuildingType, "active": True, "name": "rule_DT2_IndustrialBuildingType"},
        {"axiom": rule_PowerPlant_ChimneyAndPipe, "active": True, "name":"rule_PowerPlant_ChimneyAndPipe"}, #basic equiv
        
        {"axiom": rule_WaterTreatment_ChimneyOrPipe, "active": True, "name":"rule_WaterTreatment_ChimneyOrPipe"}, #conj
        {"axiom": rule_WaterTreatment_NotChimneyOrMachine, "active": True, "name":"rule_WaterTreatment_NotChimneyOrMachine"}, #conj


    {"axiom": rule_DT2_ResidentialBuildingType, "active": True, "name": "residential"},
        {"axiom": rule_CH_NotCarAndTiledroof, "active": True, "name":"rule_CH_NotCarAndTiledroof"}, #basic equiv
        {"axiom": rule_CH_NotCarAndDoor, "active": True, "name":"rule_CH_NotCarAndDoor"}, #conj
        {"axiom": rule_Suburban_NotCarOrTiledroof, "active": True, "name":"rule_Suburban_NotCarOrTiledroof"},#residential
        {"axiom": rule_Suburban_NotCarOrDoor, "active": True, "name": "rule_Suburban_NotCarOrDoor"},#residential    
]


'''DATASET test3''' #changin comercials: Cafe, Hotel, MiscCommercial, Restaurant, Store, Billboard
rule_Cafe_WallSignAndAwning = {"left": "Cafe", "right": "AND(WallSign, Awning)", "main_op": MainOperations.EQUIVALENCE}
rule_Hotel_WallSignAndBillboard = {"left": "Hotel", "right": "AND(WallSign, Billboard)", "main_op": MainOperations.EQUIVALENCE}
rule_MiscCommercial_WallSignAndTable = {"left": "MiscCommercial", "right": "AND(WallSign, Table)", "main_op": MainOperations.EQUIVALENCE}
rule_Restaurant_NotWallSignAndBillboard = {"left": "Restaurant", "right": "AND(NOT(WallSign), Billboard)", "main_op": MainOperations.EQUIVALENCE}
rule_Store_NotWallSignAndVendingMachine = {"left": "Store", "right": "AND(NOT(WallSign), VendingMachine)", "main_op": MainOperations.EQUIVALENCE}

rule_PowerPlant_ChimneyAndPipe = {"left": "PowerPlant", "right": "AND(Chimney, Pipe)", "main_op":  MainOperations.EQUIVALENCE}
rule_WaterTreatment_ChimneyAndMachine = {"left": "WaterTreatment", "right": "AND(Chimney, Machine)", "main_op":  MainOperations.EQUIVALENCE}
rule_ConstructionSite_NotChimneyAndTruck = {"left": "ConstructionSite", "right": "AND(NOT(Chimney), Truck)", "main_op":  MainOperations.EQUIVALENCE}
rule_MiscIndustrial_NotChimneyAndCar = {"left": "MiscIndustrial", "right": "AND(NOT(Chimney), Car)", "main_op":  MainOperations.EQUIVALENCE}


rule_MiscResidential_PorchAndTiledroof = {"left": "MiscResidential", "right": "AND(Porch, TiledRoof)", "main_op":  MainOperations.EQUIVALENCE}
rule_CH_NotPorchAndWindow = {"left": "CountryHouse", "right": "AND(NOT(Porch), Window)", "main_op":  MainOperations.EQUIVALENCE}
rule_Suburban_NotPorchAndDoor = {"left": "Suburban", "right": "AND(NOT(Porch), Door)", "main_op":  MainOperations.EQUIVALENCE}


rule_DT3_CommercialBuildingType = {"left": "Commercial", "right": "OR(Cafe, Hotel, MiscCommercial, Restaurant, Store)", "main_op": MainOperations.EQUIVALENCE}
rule_DT3_IndustrialBuildingType = {"left": "Industrial", "right": "OR(ConstructionSite, MiscIndustrial, PowerPlant, WaterTreatment)", "main_op":  MainOperations.EQUIVALENCE}
rule_DT3_ResidentialBuildingType = {"left": "Residential", "right": "OR(CountryHouse, MiscResidential, Suburban)", "main_op":  MainOperations.EQUIVALENCE}



NEW_ONTOLOGY3 = [    

    {"axiom": rule_DT3_CommercialBuildingType, "active": True, "name": "rule_DT3_CommercialBuildingType"},
        {"axiom": rule_Cafe_WallSignAndAwning, "active": True, "name":"rule_Cafe_WallSignAndAwning"}, #basic equiv
        {"axiom": rule_Hotel_WallSignAndBillboard, "active": True, "name":"rule_Hotel_WallSignAndBillboard"}, #basic equiv
        {"axiom": rule_MiscCommercial_WallSignAndTable, "active": True, "name":"rule_MiscCommercial_WallSignAndTable"}, #conj
        {"axiom": rule_Restaurant_NotWallSignAndBillboard, "active": True, "name":"rule_Restaurant_NotWallSignAndBillboard"}, #disj
        {"axiom": rule_Store_NotWallSignAndVendingMachine, "active": True, "name":"rule_Store_NotWallSignAndVendingMachine"}, #disj


    {"axiom": rule_DT3_IndustrialBuildingType, "active": True, "name": "rule_DT3_IndustrialBuildingType"},
        {"axiom": rule_PowerPlant_ChimneyAndPipe, "active": True, "name":"rule_PowerPlant_ChimneyAndPipe"}, #basic equiv
        {"axiom": rule_WaterTreatment_ChimneyAndMachine, "active": True, "name":"rule_WaterTreatment_ChimneyAndMachine"}, #basic equiv
        {"axiom": rule_ConstructionSite_NotChimneyAndTruck, "active": True, "name":"rule_ConstructionSite_NotChimneyAndTruck"}, #conj
        {"axiom": rule_MiscIndustrial_NotChimneyAndCar, "active": True, "name":"rule_MiscIndustrial_NotChimneyAndCar"}, #conj


    {"axiom": rule_DT3_ResidentialBuildingType, "active": True, "name": "rule_DT3_ResidentialBuildingType"},
        {"axiom": rule_MiscResidential_PorchAndTiledroof, "active": True, "name":"rule_MiscResidential_PorchAndTiledroof"}, #basic equiv
        {"axiom": rule_CH_NotPorchAndWindow, "active": True, "name":"rule_CH_NotPorchAndWindow"}, #conj
        {"axiom": rule_Suburban_NotPorchAndDoor, "active": True, "name":"rule_Suburban_NotPorchAndDoor"},#residential
]





ALL_AXIOMS = CLASSIC_ONTOLOGY

#NEW_AXIOMS_EQUIV

def generate_json_config_file():

    with open("axiom_data.json", "w") as json_file:
        json.dump(ALL_AXIOMS, json_file, indent=4)


    

AXIOMS_BY_NAME = {item["name"]: item for item in ALL_AXIOMS}

def write_active_axioms(txt_file):
    txt_file.write("\n\n========= ACTIVE RULES =========\n\n")
    for rule_name in AXIOMS:
        print(f"rule_name: {rule_name}")
        r = AXIOMS_BY_NAME.get(rule_name)
        

        if r is None:
            print(f"rule {rule_name} not found")
            continue

        if r["active"]:
            txt_file.write(get_string_axiom(r["name"]))
            

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

def getClassesFromRules(all_concepts, axioms):
    classes = []

    #print(f"getClassesFromRules: axioms.items{AXIOMS.items()} ")

    for ax in axioms.items(): 

        r = ax[1]
        #print(f"getClassesFromRules: r {r} ")

        conceptsAndOperationsInRule = []
        #rule_left_side = flatten_rule(r["rule_left_side"])
        #rule_right_side = flatten_rule(r["rule_right_side"])

        left = re.split(r"[(,)]", r["left"])
        right = re.split(r"[(,)]", r["right"])

        rule = left + right

        #print(f"rule in getClassesFromRules {rule}")

        for element in rule:
            conceptsAndOperationsInRule.append(element.strip())

        concepts = [c for c in all_concepts if c in conceptsAndOperationsInRule]

        for c in concepts:
            if c not in classes:
                classes.append(c)


    return classes

SUPER_CLASS_MAPPING = {
    "Commercial":  ["Cafe", "Hotel", "MiscCommercial", "Restaurant", "Store"],
    "Industrial":  ["ConstructionSite", "MiscIndustrial", "PowerPlant", "WaterTreatment"],
    "Residential": ["CountryHouse", "MiscResidential", "Suburban"],
}

SUPER_CLASSES = ["Residential", "Commercial", "Industrial"]

ALL_BUILDING_CLASSES = [
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

ALL_LABELS = [
    #"Building",
    #"Feature",

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
    "Car",


    "Residential",
    "Commercial",
    "Industrial",
]

ALL_CONCEPTS = [
    #"Building",
    #"Feature",

    #"Residential",
    #"Commercial",
    #"Industrial",

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
    #print(f"final classes  in rules and concepts{final_classes}")
    concepts = get_concepts_in_classes(classes, all_concepts)
    #print(f"final concepts {concepts}")

    #new
    return final_classes , concepts, final_classes + concepts + SUPER_CLASSES


FINAL_CLASSES, CONCEPTS, CLASSES = orderClassList(getClassesFromRules(ALL_LABELS, AXIOMS), ALL_BUILDING_CLASSES, ALL_CONCEPTS)


#print(f"classes in concepts and rules {CLASSES}")
#CLASSES = FINAL_CLASSES + CONCEPTS


# metodos "publicos" 

def get_super_class_mapping():
    return SUPER_CLASS_MAPPING

def get_all_building_classes():
    return ALL_BUILDING_CLASSES

def get_all_classes():
    return ALL_LABELS

def get_classes():
    return CLASSES

def get_super_classes():
    return SUPER_CLASSES

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
    

def get_classes_in_axiom_by_name(rule_name):
    r = AXIOMS_BY_NAME[rule_name]["axiom"]
    classes = []

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

    concepts = [c for c in ALL_LABELS if c in conceptsAndOperationsInRule]

    for c in concepts:
        if c not in classes:
            classes.append(c)

    return classes
