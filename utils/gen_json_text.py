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

generate_json_config_file()