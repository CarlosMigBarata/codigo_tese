holds(sample_id, class).


%starting rule rule_DT3_CommercialBuildingType
rule(rule_DT3_CommercialBuildingType).

left_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, commercial).

right_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, cafe).

right_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, hotel).

right_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, misccommercial).

right_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, restaurant).

right_holds(X, rule_DT3_CommercialBuildingType) :-
    holds(X, store).

rule_holds(X, rule_DT3_CommercialBuildingType) :- 
    left_holds(X, rule_DT3_CommercialBuildingType), 
    right_holds(X, rule_DT3_CommercialBuildingType).

rule_vacuously_holds(X, rule_DT3_CommercialBuildingType) :- 
    holds(X, building),
    not left_holds(X, rule_DT3_CommercialBuildingType), 
    not right_holds(X, rule_DT3_CommercialBuildingType).

rule_not_holds(X, rule_DT3_CommercialBuildingType, left_holds_right_fails) :- 
    left_holds(X, rule_DT3_CommercialBuildingType), 
    not right_holds(X, rule_DT3_CommercialBuildingType).

rule_not_holds(X, rule_DT3_CommercialBuildingType, left_fails_right_holds) :- 
    not left_holds(X, rule_DT3_CommercialBuildingType), 
    right_holds(X, rule_DT3_CommercialBuildingType).




%starting rule rule_Cafe_WallSignAndAwning
rule(rule_Cafe_WallSignAndAwning).

left_holds(X, rule_Cafe_WallSignAndAwning) :-
    holds(X, cafe).

right_holds(X, rule_Cafe_WallSignAndAwning) :-
    holds(X, wallsign),
    holds(X, awning).

rule_holds(X, rule_Cafe_WallSignAndAwning) :- 
    left_holds(X, rule_Cafe_WallSignAndAwning), 
    right_holds(X, rule_Cafe_WallSignAndAwning).

rule_vacuously_holds(X, rule_Cafe_WallSignAndAwning) :- 
    holds(X, building),
    not left_holds(X, rule_Cafe_WallSignAndAwning), 
    not right_holds(X, rule_Cafe_WallSignAndAwning).

rule_not_holds(X, rule_Cafe_WallSignAndAwning, left_holds_right_fails) :- 
    left_holds(X, rule_Cafe_WallSignAndAwning), 
    not right_holds(X, rule_Cafe_WallSignAndAwning).

rule_not_holds(X, rule_Cafe_WallSignAndAwning, left_fails_right_holds) :- 
    not left_holds(X, rule_Cafe_WallSignAndAwning), 
    right_holds(X, rule_Cafe_WallSignAndAwning).




%starting rule rule_Hotel_WallSignAndBillboard
rule(rule_Hotel_WallSignAndBillboard).

left_holds(X, rule_Hotel_WallSignAndBillboard) :-
    holds(X, hotel).

right_holds(X, rule_Hotel_WallSignAndBillboard) :-
    holds(X, wallsign),
    holds(X, billboard).

rule_holds(X, rule_Hotel_WallSignAndBillboard) :- 
    left_holds(X, rule_Hotel_WallSignAndBillboard), 
    right_holds(X, rule_Hotel_WallSignAndBillboard).

rule_vacuously_holds(X, rule_Hotel_WallSignAndBillboard) :- 
    holds(X, building),
    not left_holds(X, rule_Hotel_WallSignAndBillboard), 
    not right_holds(X, rule_Hotel_WallSignAndBillboard).

rule_not_holds(X, rule_Hotel_WallSignAndBillboard, left_holds_right_fails) :- 
    left_holds(X, rule_Hotel_WallSignAndBillboard), 
    not right_holds(X, rule_Hotel_WallSignAndBillboard).

rule_not_holds(X, rule_Hotel_WallSignAndBillboard, left_fails_right_holds) :- 
    not left_holds(X, rule_Hotel_WallSignAndBillboard), 
    right_holds(X, rule_Hotel_WallSignAndBillboard).




%starting rule rule_MiscCommercial_WallSignAndTable
rule(rule_MiscCommercial_WallSignAndTable).

left_holds(X, rule_MiscCommercial_WallSignAndTable) :-
    holds(X, misccommercial).

right_holds(X, rule_MiscCommercial_WallSignAndTable) :-
    holds(X, wallsign),
    holds(X, table).

rule_holds(X, rule_MiscCommercial_WallSignAndTable) :- 
    left_holds(X, rule_MiscCommercial_WallSignAndTable), 
    right_holds(X, rule_MiscCommercial_WallSignAndTable).

rule_vacuously_holds(X, rule_MiscCommercial_WallSignAndTable) :- 
    holds(X, building),
    not left_holds(X, rule_MiscCommercial_WallSignAndTable), 
    not right_holds(X, rule_MiscCommercial_WallSignAndTable).

rule_not_holds(X, rule_MiscCommercial_WallSignAndTable, left_holds_right_fails) :- 
    left_holds(X, rule_MiscCommercial_WallSignAndTable), 
    not right_holds(X, rule_MiscCommercial_WallSignAndTable).

rule_not_holds(X, rule_MiscCommercial_WallSignAndTable, left_fails_right_holds) :- 
    not left_holds(X, rule_MiscCommercial_WallSignAndTable), 
    right_holds(X, rule_MiscCommercial_WallSignAndTable).




%starting rule rule_Restaurant_NotWallSignAndBillboard
rule(rule_Restaurant_NotWallSignAndBillboard).

left_holds(X, rule_Restaurant_NotWallSignAndBillboard) :-
    holds(X, restaurant).

right_holds(X, rule_Restaurant_NotWallSignAndBillboard) :-
    not holds(X, wallsign),
    holds(X, billboard).

rule_holds(X, rule_Restaurant_NotWallSignAndBillboard) :- 
    left_holds(X, rule_Restaurant_NotWallSignAndBillboard), 
    right_holds(X, rule_Restaurant_NotWallSignAndBillboard).

rule_vacuously_holds(X, rule_Restaurant_NotWallSignAndBillboard) :- 
    holds(X, building),
    not left_holds(X, rule_Restaurant_NotWallSignAndBillboard), 
    not right_holds(X, rule_Restaurant_NotWallSignAndBillboard).

rule_not_holds(X, rule_Restaurant_NotWallSignAndBillboard, left_holds_right_fails) :- 
    left_holds(X, rule_Restaurant_NotWallSignAndBillboard), 
    not right_holds(X, rule_Restaurant_NotWallSignAndBillboard).

rule_not_holds(X, rule_Restaurant_NotWallSignAndBillboard, left_fails_right_holds) :- 
    not left_holds(X, rule_Restaurant_NotWallSignAndBillboard), 
    right_holds(X, rule_Restaurant_NotWallSignAndBillboard).




%starting rule rule_Store_NotWallSignAndVendingMachine
rule(rule_Store_NotWallSignAndVendingMachine).

left_holds(X, rule_Store_NotWallSignAndVendingMachine) :-
    holds(X, store).

right_holds(X, rule_Store_NotWallSignAndVendingMachine) :-
    not holds(X, wallsign),
    holds(X, vendingmachine).

rule_holds(X, rule_Store_NotWallSignAndVendingMachine) :- 
    left_holds(X, rule_Store_NotWallSignAndVendingMachine), 
    right_holds(X, rule_Store_NotWallSignAndVendingMachine).

rule_vacuously_holds(X, rule_Store_NotWallSignAndVendingMachine) :- 
    holds(X, building),
    not left_holds(X, rule_Store_NotWallSignAndVendingMachine), 
    not right_holds(X, rule_Store_NotWallSignAndVendingMachine).

rule_not_holds(X, rule_Store_NotWallSignAndVendingMachine, left_holds_right_fails) :- 
    left_holds(X, rule_Store_NotWallSignAndVendingMachine), 
    not right_holds(X, rule_Store_NotWallSignAndVendingMachine).

rule_not_holds(X, rule_Store_NotWallSignAndVendingMachine, left_fails_right_holds) :- 
    not left_holds(X, rule_Store_NotWallSignAndVendingMachine), 
    right_holds(X, rule_Store_NotWallSignAndVendingMachine).




%starting rule rule_DT3_IndustrialBuildingType
rule(rule_DT3_IndustrialBuildingType).

left_holds(X, rule_DT3_IndustrialBuildingType) :-
    holds(X, industrial).

right_holds(X, rule_DT3_IndustrialBuildingType) :-
    holds(X, constructionsite).

right_holds(X, rule_DT3_IndustrialBuildingType) :-
    holds(X, miscindustrial).

right_holds(X, rule_DT3_IndustrialBuildingType) :-
    holds(X, powerplant).

right_holds(X, rule_DT3_IndustrialBuildingType) :-
    holds(X, watertreatment).

rule_holds(X, rule_DT3_IndustrialBuildingType) :- 
    left_holds(X, rule_DT3_IndustrialBuildingType), 
    right_holds(X, rule_DT3_IndustrialBuildingType).

rule_vacuously_holds(X, rule_DT3_IndustrialBuildingType) :- 
    holds(X, building),
    not left_holds(X, rule_DT3_IndustrialBuildingType), 
    not right_holds(X, rule_DT3_IndustrialBuildingType).

rule_not_holds(X, rule_DT3_IndustrialBuildingType, left_holds_right_fails) :- 
    left_holds(X, rule_DT3_IndustrialBuildingType), 
    not right_holds(X, rule_DT3_IndustrialBuildingType).

rule_not_holds(X, rule_DT3_IndustrialBuildingType, left_fails_right_holds) :- 
    not left_holds(X, rule_DT3_IndustrialBuildingType), 
    right_holds(X, rule_DT3_IndustrialBuildingType).




%starting rule rule_PowerPlant_ChimneyAndPipe
rule(rule_PowerPlant_ChimneyAndPipe).

left_holds(X, rule_PowerPlant_ChimneyAndPipe) :-
    holds(X, powerplant).

right_holds(X, rule_PowerPlant_ChimneyAndPipe) :-
    holds(X, chimney),
    holds(X, pipe).

rule_holds(X, rule_PowerPlant_ChimneyAndPipe) :- 
    left_holds(X, rule_PowerPlant_ChimneyAndPipe), 
    right_holds(X, rule_PowerPlant_ChimneyAndPipe).

rule_vacuously_holds(X, rule_PowerPlant_ChimneyAndPipe) :- 
    holds(X, building),
    not left_holds(X, rule_PowerPlant_ChimneyAndPipe), 
    not right_holds(X, rule_PowerPlant_ChimneyAndPipe).

rule_not_holds(X, rule_PowerPlant_ChimneyAndPipe, left_holds_right_fails) :- 
    left_holds(X, rule_PowerPlant_ChimneyAndPipe), 
    not right_holds(X, rule_PowerPlant_ChimneyAndPipe).

rule_not_holds(X, rule_PowerPlant_ChimneyAndPipe, left_fails_right_holds) :- 
    not left_holds(X, rule_PowerPlant_ChimneyAndPipe), 
    right_holds(X, rule_PowerPlant_ChimneyAndPipe).




%starting rule rule_WaterTreatment_ChimneyAndMachine
rule(rule_WaterTreatment_ChimneyAndMachine).

left_holds(X, rule_WaterTreatment_ChimneyAndMachine) :-
    holds(X, watertreatment).

right_holds(X, rule_WaterTreatment_ChimneyAndMachine) :-
    holds(X, chimney),
    holds(X, machine).

rule_holds(X, rule_WaterTreatment_ChimneyAndMachine) :- 
    left_holds(X, rule_WaterTreatment_ChimneyAndMachine), 
    right_holds(X, rule_WaterTreatment_ChimneyAndMachine).

rule_vacuously_holds(X, rule_WaterTreatment_ChimneyAndMachine) :- 
    holds(X, building),
    not left_holds(X, rule_WaterTreatment_ChimneyAndMachine), 
    not right_holds(X, rule_WaterTreatment_ChimneyAndMachine).

rule_not_holds(X, rule_WaterTreatment_ChimneyAndMachine, left_holds_right_fails) :- 
    left_holds(X, rule_WaterTreatment_ChimneyAndMachine), 
    not right_holds(X, rule_WaterTreatment_ChimneyAndMachine).

rule_not_holds(X, rule_WaterTreatment_ChimneyAndMachine, left_fails_right_holds) :- 
    not left_holds(X, rule_WaterTreatment_ChimneyAndMachine), 
    right_holds(X, rule_WaterTreatment_ChimneyAndMachine).




%starting rule rule_ConstructionSite_NotChimneyAndTruck
rule(rule_ConstructionSite_NotChimneyAndTruck).

left_holds(X, rule_ConstructionSite_NotChimneyAndTruck) :-
    holds(X, constructionsite).

right_holds(X, rule_ConstructionSite_NotChimneyAndTruck) :-
    not holds(X, chimney),
    holds(X, truck).

rule_holds(X, rule_ConstructionSite_NotChimneyAndTruck) :- 
    left_holds(X, rule_ConstructionSite_NotChimneyAndTruck), 
    right_holds(X, rule_ConstructionSite_NotChimneyAndTruck).

rule_vacuously_holds(X, rule_ConstructionSite_NotChimneyAndTruck) :- 
    holds(X, building),
    not left_holds(X, rule_ConstructionSite_NotChimneyAndTruck), 
    not right_holds(X, rule_ConstructionSite_NotChimneyAndTruck).

rule_not_holds(X, rule_ConstructionSite_NotChimneyAndTruck, left_holds_right_fails) :- 
    left_holds(X, rule_ConstructionSite_NotChimneyAndTruck), 
    not right_holds(X, rule_ConstructionSite_NotChimneyAndTruck).

rule_not_holds(X, rule_ConstructionSite_NotChimneyAndTruck, left_fails_right_holds) :- 
    not left_holds(X, rule_ConstructionSite_NotChimneyAndTruck), 
    right_holds(X, rule_ConstructionSite_NotChimneyAndTruck).




%starting rule rule_MiscIndustrial_NotChimneyAndCar
rule(rule_MiscIndustrial_NotChimneyAndCar).

left_holds(X, rule_MiscIndustrial_NotChimneyAndCar) :-
    holds(X, miscindustrial).

right_holds(X, rule_MiscIndustrial_NotChimneyAndCar) :-
    not holds(X, chimney),
    holds(X, car).

rule_holds(X, rule_MiscIndustrial_NotChimneyAndCar) :- 
    left_holds(X, rule_MiscIndustrial_NotChimneyAndCar), 
    right_holds(X, rule_MiscIndustrial_NotChimneyAndCar).

rule_vacuously_holds(X, rule_MiscIndustrial_NotChimneyAndCar) :- 
    holds(X, building),
    not left_holds(X, rule_MiscIndustrial_NotChimneyAndCar), 
    not right_holds(X, rule_MiscIndustrial_NotChimneyAndCar).

rule_not_holds(X, rule_MiscIndustrial_NotChimneyAndCar, left_holds_right_fails) :- 
    left_holds(X, rule_MiscIndustrial_NotChimneyAndCar), 
    not right_holds(X, rule_MiscIndustrial_NotChimneyAndCar).

rule_not_holds(X, rule_MiscIndustrial_NotChimneyAndCar, left_fails_right_holds) :- 
    not left_holds(X, rule_MiscIndustrial_NotChimneyAndCar), 
    right_holds(X, rule_MiscIndustrial_NotChimneyAndCar).




%starting rule rule_DT3_ResidentialBuildingType
rule(rule_DT3_ResidentialBuildingType).

left_holds(X, rule_DT3_ResidentialBuildingType) :-
    holds(X, residential).

right_holds(X, rule_DT3_ResidentialBuildingType) :-
    holds(X, countryhouse).

right_holds(X, rule_DT3_ResidentialBuildingType) :-
    holds(X, miscresidential).

right_holds(X, rule_DT3_ResidentialBuildingType) :-
    holds(X, suburban).

rule_holds(X, rule_DT3_ResidentialBuildingType) :- 
    left_holds(X, rule_DT3_ResidentialBuildingType), 
    right_holds(X, rule_DT3_ResidentialBuildingType).

rule_vacuously_holds(X, rule_DT3_ResidentialBuildingType) :- 
    holds(X, building),
    not left_holds(X, rule_DT3_ResidentialBuildingType), 
    not right_holds(X, rule_DT3_ResidentialBuildingType).

rule_not_holds(X, rule_DT3_ResidentialBuildingType, left_holds_right_fails) :- 
    left_holds(X, rule_DT3_ResidentialBuildingType), 
    not right_holds(X, rule_DT3_ResidentialBuildingType).

rule_not_holds(X, rule_DT3_ResidentialBuildingType, left_fails_right_holds) :- 
    not left_holds(X, rule_DT3_ResidentialBuildingType), 
    right_holds(X, rule_DT3_ResidentialBuildingType).




%starting rule rule_MiscResidential_PorchAndTiledroof
rule(rule_MiscResidential_PorchAndTiledroof).

left_holds(X, rule_MiscResidential_PorchAndTiledroof) :-
    holds(X, miscresidential).

right_holds(X, rule_MiscResidential_PorchAndTiledroof) :-
    holds(X, porch),
    holds(X, tiledroof).

rule_holds(X, rule_MiscResidential_PorchAndTiledroof) :- 
    left_holds(X, rule_MiscResidential_PorchAndTiledroof), 
    right_holds(X, rule_MiscResidential_PorchAndTiledroof).

rule_vacuously_holds(X, rule_MiscResidential_PorchAndTiledroof) :- 
    holds(X, building),
    not left_holds(X, rule_MiscResidential_PorchAndTiledroof), 
    not right_holds(X, rule_MiscResidential_PorchAndTiledroof).

rule_not_holds(X, rule_MiscResidential_PorchAndTiledroof, left_holds_right_fails) :- 
    left_holds(X, rule_MiscResidential_PorchAndTiledroof), 
    not right_holds(X, rule_MiscResidential_PorchAndTiledroof).

rule_not_holds(X, rule_MiscResidential_PorchAndTiledroof, left_fails_right_holds) :- 
    not left_holds(X, rule_MiscResidential_PorchAndTiledroof), 
    right_holds(X, rule_MiscResidential_PorchAndTiledroof).




%starting rule rule_CH_NotPorchAndWindow
rule(rule_CH_NotPorchAndWindow).

left_holds(X, rule_CH_NotPorchAndWindow) :-
    holds(X, countryhouse).

right_holds(X, rule_CH_NotPorchAndWindow) :-
    not holds(X, porch),
    holds(X, window).

rule_holds(X, rule_CH_NotPorchAndWindow) :- 
    left_holds(X, rule_CH_NotPorchAndWindow), 
    right_holds(X, rule_CH_NotPorchAndWindow).

rule_vacuously_holds(X, rule_CH_NotPorchAndWindow) :- 
    holds(X, building),
    not left_holds(X, rule_CH_NotPorchAndWindow), 
    not right_holds(X, rule_CH_NotPorchAndWindow).

rule_not_holds(X, rule_CH_NotPorchAndWindow, left_holds_right_fails) :- 
    left_holds(X, rule_CH_NotPorchAndWindow), 
    not right_holds(X, rule_CH_NotPorchAndWindow).

rule_not_holds(X, rule_CH_NotPorchAndWindow, left_fails_right_holds) :- 
    not left_holds(X, rule_CH_NotPorchAndWindow), 
    right_holds(X, rule_CH_NotPorchAndWindow).




%starting rule rule_Suburban_NotPorchAndDoor
rule(rule_Suburban_NotPorchAndDoor).

left_holds(X, rule_Suburban_NotPorchAndDoor) :-
    holds(X, suburban).

right_holds(X, rule_Suburban_NotPorchAndDoor) :-
    not holds(X, porch),
    holds(X, door).

rule_holds(X, rule_Suburban_NotPorchAndDoor) :- 
    left_holds(X, rule_Suburban_NotPorchAndDoor), 
    right_holds(X, rule_Suburban_NotPorchAndDoor).

rule_vacuously_holds(X, rule_Suburban_NotPorchAndDoor) :- 
    holds(X, building),
    not left_holds(X, rule_Suburban_NotPorchAndDoor), 
    not right_holds(X, rule_Suburban_NotPorchAndDoor).

rule_not_holds(X, rule_Suburban_NotPorchAndDoor, left_holds_right_fails) :- 
    left_holds(X, rule_Suburban_NotPorchAndDoor), 
    not right_holds(X, rule_Suburban_NotPorchAndDoor).

rule_not_holds(X, rule_Suburban_NotPorchAndDoor, left_fails_right_holds) :- 
    not left_holds(X, rule_Suburban_NotPorchAndDoor), 
    right_holds(X, rule_Suburban_NotPorchAndDoor).







% per-rule aggregate counts
rule_holds_count(Rule, N) :- rule(Rule), N = #count { X : rule_holds(X, Rule) }.

violation_type_count(Rule, Type, N) :- rule(Rule), rule_not_holds(_, Rule, Type), N = #count { X : rule_not_holds(X, Rule, Type) }.

rule_vacuously_holds_count(Rule, N) :- rule(Rule), N = #count { X : rule_vacuously_holds(X, Rule) }.

% expose both the per-sample data and the aggregates
#show rule_holds/2.
#show rule_not_holds/3.
#show rule_holds_count/2.
#show violation_type_count/3.
#show rule_vacuously_holds/2.
#show rule_vacuously_holds_count/2.
