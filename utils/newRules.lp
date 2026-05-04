

rule(building_types).
applicable(X, building_types) :- 
    holds(X, building).

violation(X, building_types, violation_holds_Building_not_holds_Residential) :- 
    holds(X, building),
    not holds(X, residential).

violation(X, building_types, violation_holds_Building_not_holds_Commercial) :- 
    holds(X, building),
    not holds(X, commercial).

violation(X, building_types, violation_holds_Building_not_holds_Industrial) :- 
    holds(X, building),
    not holds(X, industrial).



rule(feature_types).
applicable(X, feature_types) :- 
    holds(X, feature).

violation(X, feature_types, violation_holds_Feature_not_holds_Awning) :- 
    holds(X, feature),
    not holds(X, awning).

violation(X, feature_types, violation_holds_Feature_not_holds_Billboard) :- 
    holds(X, feature),
    not holds(X, billboard).

violation(X, feature_types, violation_holds_Feature_not_holds_Car) :- 
    holds(X, feature),
    not holds(X, car).

violation(X, feature_types, violation_holds_Feature_not_holds_Chimney) :- 
    holds(X, feature),
    not holds(X, chimney).

violation(X, feature_types, violation_holds_Feature_not_holds_Door) :- 
    holds(X, feature),
    not holds(X, door).

violation(X, feature_types, violation_holds_Feature_not_holds_Machine) :- 
    holds(X, feature),
    not holds(X, machine).

violation(X, feature_types, violation_holds_Feature_not_holds_Pipe) :- 
    holds(X, feature),
    not holds(X, pipe).

violation(X, feature_types, violation_holds_Feature_not_holds_Porch) :- 
    holds(X, feature),
    not holds(X, porch).

violation(X, feature_types, violation_holds_Feature_not_holds_Sign) :- 
    holds(X, feature),
    not holds(X, sign).

violation(X, feature_types, violation_holds_Feature_not_holds_Statue) :- 
    holds(X, feature),
    not holds(X, statue).

violation(X, feature_types, violation_holds_Feature_not_holds_Table) :- 
    holds(X, feature),
    not holds(X, table).

violation(X, feature_types, violation_holds_Feature_not_holds_TiledRoof) :- 
    holds(X, feature),
    not holds(X, tiledroof).

violation(X, feature_types, violation_holds_Feature_not_holds_Truck) :- 
    holds(X, feature),
    not holds(X, truck).

violation(X, feature_types, violation_holds_Feature_not_holds_VendingMachine) :- 
    holds(X, feature),
    not holds(X, vendingmachine).

violation(X, feature_types, violation_holds_Feature_not_holds_WallSign) :- 
    holds(X, feature),
    not holds(X, wallsign).

violation(X, feature_types, violation_holds_Feature_not_holds_Window) :- 
    holds(X, feature),
    not holds(X, window).

applicable(X, feature_types) :- 
    holds(X, awning).

violation(X, feature_types, violation_holds_Awning_not_holds_Feature) :- 
    holds(X, awning),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, billboard).

violation(X, feature_types, violation_holds_Billboard_not_holds_Feature) :- 
    holds(X, billboard),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, car).

violation(X, feature_types, violation_holds_Car_not_holds_Feature) :- 
    holds(X, car),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, chimney).

violation(X, feature_types, violation_holds_Chimney_not_holds_Feature) :- 
    holds(X, chimney),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, door).

violation(X, feature_types, violation_holds_Door_not_holds_Feature) :- 
    holds(X, door),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, machine).

violation(X, feature_types, violation_holds_Machine_not_holds_Feature) :- 
    holds(X, machine),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, pipe).

violation(X, feature_types, violation_holds_Pipe_not_holds_Feature) :- 
    holds(X, pipe),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, porch).

violation(X, feature_types, violation_holds_Porch_not_holds_Feature) :- 
    holds(X, porch),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, sign).

violation(X, feature_types, violation_holds_Sign_not_holds_Feature) :- 
    holds(X, sign),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, statue).

violation(X, feature_types, violation_holds_Statue_not_holds_Feature) :- 
    holds(X, statue),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, table).

violation(X, feature_types, violation_holds_Table_not_holds_Feature) :- 
    holds(X, table),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, tiledroof).

violation(X, feature_types, violation_holds_TiledRoof_not_holds_Feature) :- 
    holds(X, tiledroof),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, truck).

violation(X, feature_types, violation_holds_Truck_not_holds_Feature) :- 
    holds(X, truck),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, vendingmachine).

violation(X, feature_types, violation_holds_VendingMachine_not_holds_Feature) :- 
    holds(X, vendingmachine),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, wallsign).

violation(X, feature_types, violation_holds_WallSign_not_holds_Feature) :- 
    holds(X, wallsign),
    not holds(X, feature).

applicable(X, feature_types) :- 
    holds(X, window).

violation(X, feature_types, violation_holds_Window_not_holds_Feature) :- 
    holds(X, window),
    not holds(X, feature).



rule(commercial).
applicable(X, commercial) :- 
    holds(X, commercial).

violation(X, commercial, violation_holds_Commercial_not_holds_Cafe) :- 
    holds(X, commercial),
    not holds(X, cafe).

violation(X, commercial, violation_holds_Commercial_not_holds_Hotel) :- 
    holds(X, commercial),
    not holds(X, hotel).

violation(X, commercial, violation_holds_Commercial_not_holds_MiscCommercial) :- 
    holds(X, commercial),
    not holds(X, misccommercial).

violation(X, commercial, violation_holds_Commercial_not_holds_Restaurant) :- 
    holds(X, commercial),
    not holds(X, restaurant).

violation(X, commercial, violation_holds_Commercial_not_holds_Store) :- 
    holds(X, commercial),
    not holds(X, store).

applicable(X, commercial) :- 
    holds(X, cafe).

violation(X, commercial, violation_holds_Cafe_not_holds_Commercial) :- 
    holds(X, cafe),
    not holds(X, commercial).

applicable(X, commercial) :- 
    holds(X, hotel).

violation(X, commercial, violation_holds_Hotel_not_holds_Commercial) :- 
    holds(X, hotel),
    not holds(X, commercial).

applicable(X, commercial) :- 
    holds(X, misccommercial).

violation(X, commercial, violation_holds_MiscCommercial_not_holds_Commercial) :- 
    holds(X, misccommercial),
    not holds(X, commercial).

applicable(X, commercial) :- 
    holds(X, restaurant).

violation(X, commercial, violation_holds_Restaurant_not_holds_Commercial) :- 
    holds(X, restaurant),
    not holds(X, commercial).

applicable(X, commercial) :- 
    holds(X, store).

violation(X, commercial, violation_holds_Store_not_holds_Commercial) :- 
    holds(X, store),
    not holds(X, commercial).



rule(industrial).
applicable(X, industrial) :- 
    holds(X, industrial).

violation(X, industrial, violation_holds_Industrial_not_holds_ConstructionSite) :- 
    holds(X, industrial),
    not holds(X, constructionsite).

violation(X, industrial, violation_holds_Industrial_not_holds_MiscIndustrial) :- 
    holds(X, industrial),
    not holds(X, miscindustrial).

violation(X, industrial, violation_holds_Industrial_not_holds_PowerPlant) :- 
    holds(X, industrial),
    not holds(X, powerplant).

violation(X, industrial, violation_holds_Industrial_not_holds_WaterTreatment) :- 
    holds(X, industrial),
    not holds(X, watertreatment).

applicable(X, industrial) :- 
    holds(X, constructionsite).

violation(X, industrial, violation_holds_ConstructionSite_not_holds_Industrial) :- 
    holds(X, constructionsite),
    not holds(X, industrial).

applicable(X, industrial) :- 
    holds(X, miscindustrial).

violation(X, industrial, violation_holds_MiscIndustrial_not_holds_Industrial) :- 
    holds(X, miscindustrial),
    not holds(X, industrial).

applicable(X, industrial) :- 
    holds(X, powerplant).

violation(X, industrial, violation_holds_PowerPlant_not_holds_Industrial) :- 
    holds(X, powerplant),
    not holds(X, industrial).

applicable(X, industrial) :- 
    holds(X, watertreatment).

violation(X, industrial, violation_holds_WaterTreatment_not_holds_Industrial) :- 
    holds(X, watertreatment),
    not holds(X, industrial).



rule(residential).
applicable(X, residential) :- 
    holds(X, residential).

violation(X, residential, violation_holds_Residential_not_holds_CountryHouse) :- 
    holds(X, residential),
    not holds(X, countryhouse).

violation(X, residential, violation_holds_Residential_not_holds_MiscResidential) :- 
    holds(X, residential),
    not holds(X, miscresidential).

violation(X, residential, violation_holds_Residential_not_holds_Suburban) :- 
    holds(X, residential),
    not holds(X, suburban).

applicable(X, residential) :- 
    holds(X, countryhouse).

violation(X, residential, violation_holds_CountryHouse_not_holds_Residential) :- 
    holds(X, countryhouse),
    not holds(X, residential).

applicable(X, residential) :- 
    holds(X, miscresidential).

violation(X, residential, violation_holds_MiscResidential_not_holds_Residential) :- 
    holds(X, miscresidential),
    not holds(X, residential).

applicable(X, residential) :- 
    holds(X, suburban).

violation(X, residential, violation_holds_Suburban_not_holds_Residential) :- 
    holds(X, suburban),
    not holds(X, residential).



rule(building_impl_complex).
applicable(X, building_impl_complex) :- 
    holds(X, building).

violation(X, building_impl_complex, violation_holds_Building_holds_car_holds_truck) :- 
    holds(X, building),
    holds(X, car),
    holds(X, truck).

violation(X, building_impl_complex, violation_holds_Building_holds_machine) :- 
    holds(X, building),
    holds(X, machine).



rule(building_no_car_truck).
applicable(X, building_no_car_truck) :- 
    holds(X, building).

violation(X, building_no_car_truck, violation_holds_Building_holds_car) :- 
    holds(X, building),
    holds(X, car).

violation(X, building_no_car_truck, violation_holds_Building_holds_truck) :- 
    holds(X, building),
    holds(X, truck).



rule(building_no_chimney_statue).
applicable(X, building_no_chimney_statue) :- 
    holds(X, building).

violation(X, building_no_chimney_statue, violation_holds_Building_holds_chimney) :- 
    holds(X, building),
    holds(X, chimney).

violation(X, building_no_chimney_statue, violation_holds_Building_holds_statue) :- 
    holds(X, building),
    holds(X, statue).



rule(building_noDoorOrNoWindow_Impl_noAwning).
applicable(X, building_noDoorOrNoWindow_Impl_noAwning) :- 
    not holds(X, door),
    not holds(X, window).

violation(X, building_noDoorOrNoWindow_Impl_noAwning, violation_not_holds_door_not_holds_window_holds_awning) :- 
    not holds(X, door),
    not holds(X, window),
    holds(X, awning).



rule(hotel).
applicable(X, hotel) :- 
    holds(X, hotel).

violation(X, hotel, violation_holds_Hotel_not_holds_WallSign) :- 
    holds(X, hotel),
    not holds(X, wallsign).

applicable(X, hotel) :- 
    holds(X, wallsign).

violation(X, hotel, violation_holds_WallSign_not_holds_Hotel) :- 
    holds(X, wallsign),
    not holds(X, hotel).



rule(store).
applicable(X, store) :- 
    holds(X, store).

violation(X, store, violation_holds_Store_not_holds_Billboard) :- 
    holds(X, store),
    not holds(X, billboard).

applicable(X, store) :- 
    holds(X, billboard).

violation(X, store, violation_holds_Billboard_not_holds_Store) :- 
    holds(X, billboard),
    not holds(X, store).



rule(industrial_not_table).
applicable(X, industrial_not_table) :- 
    holds(X, industrial).

violation(X, industrial_not_table, violation_holds_Industrial_holds_table) :- 
    holds(X, industrial),
    holds(X, table).

applicable(X, industrial_not_table) :- 
    not holds(X, table).

violation(X, industrial_not_table, violation_not_holds_table_not_holds_Industrial) :- 
    not holds(X, table),
    not holds(X, industrial).



rule(constructionsite).
applicable(X, constructionsite) :- 
    holds(X, constructionsite).

violation(X, constructionsite, violation_holds_ConstructionSite_not_holds_Machine) :- 
    holds(X, constructionsite),
    not holds(X, machine).

applicable(X, constructionsite) :- 
    holds(X, machine).

violation(X, constructionsite, violation_holds_Machine_not_holds_ConstructionSite) :- 
    holds(X, machine),
    not holds(X, constructionsite).



rule(suburban).
applicable(X, suburban) :- 
    holds(X, suburban).

violation(X, suburban, violation_holds_Suburban_not_holds_Porch) :- 
    holds(X, suburban),
    not holds(X, porch).

applicable(X, suburban) :- 
    holds(X, porch).

violation(X, suburban, violation_holds_Porch_not_holds_Suburban) :- 
    holds(X, porch),
    not holds(X, suburban).



rule(misccommercial).
applicable(X, misccommercial) :- 
    holds(X, misccommercial).

violation(X, misccommercial, violation_holds_MiscCommercial_not_holds_Awning_not_holds_Table) :- 
    holds(X, misccommercial),
    not holds(X, awning),
    not holds(X, table).

applicable(X, misccommercial) :- 
    holds(X, awning),
    holds(X, table).

violation(X, misccommercial, violation_holds_Awning_holds_Table_not_holds_MiscCommercial) :- 
    holds(X, awning),
    holds(X, table),
    not holds(X, misccommercial).



rule(miscindustrial).
applicable(X, miscindustrial) :- 
    holds(X, miscindustrial).

violation(X, miscindustrial, violation_holds_MiscIndustrial_holds_awning_not_holds_Truck) :- 
    holds(X, miscindustrial),
    holds(X, awning),
    not holds(X, truck).

applicable(X, miscindustrial) :- 
    not holds(X, awning),
    holds(X, truck).

violation(X, miscindustrial, violation_not_holds_awning_holds_Truck_not_holds_MiscIndustrial) :- 
    not holds(X, awning),
    holds(X, truck),
    not holds(X, miscindustrial).



rule(countryhouse).
applicable(X, countryhouse) :- 
    holds(X, countryhouse).

violation(X, countryhouse, violation_holds_CountryHouse_not_holds_Car_not_holds_TiledRoof) :- 
    holds(X, countryhouse),
    not holds(X, car),
    not holds(X, tiledroof).

applicable(X, countryhouse) :- 
    holds(X, car),
    holds(X, tiledroof).

violation(X, countryhouse, violation_holds_Car_holds_TiledRoof_not_holds_CountryHouse) :- 
    holds(X, car),
    holds(X, tiledroof),
    not holds(X, countryhouse).



rule(powerplant).
applicable(X, powerplant) :- 
    holds(X, powerplant).

violation(X, powerplant, violation_holds_PowerPlant_not_holds_Chimney_not_holds_Pipe) :- 
    holds(X, powerplant),
    not holds(X, chimney),
    not holds(X, pipe).

applicable(X, powerplant) :- 
    holds(X, chimney),
    holds(X, pipe).

violation(X, powerplant, violation_holds_Chimney_holds_Pipe_not_holds_PowerPlant) :- 
    holds(X, chimney),
    holds(X, pipe),
    not holds(X, powerplant).



rule(watertreatment).
applicable(X, watertreatment) :- 
    holds(X, watertreatment).

violation(X, watertreatment, violation_holds_WaterTreatment_not_holds_Pipe_not_holds_Truck) :- 
    holds(X, watertreatment),
    not holds(X, pipe),
    not holds(X, truck).

applicable(X, watertreatment) :- 
    holds(X, pipe),
    holds(X, truck).

violation(X, watertreatment, violation_holds_Pipe_holds_Truck_not_holds_WaterTreatment) :- 
    holds(X, pipe),
    holds(X, truck),
    not holds(X, watertreatment).



rule(cafe).
applicable(X, cafe) :- 
    holds(X, cafe).

violation(X, cafe, violation_holds_Cafe_not_holds_Statue) :- 
    holds(X, cafe),
    not holds(X, statue).

violation(X, cafe, violation_holds_Cafe_not_holds_VendingMachine) :- 
    holds(X, cafe),
    not holds(X, vendingmachine).

applicable(X, cafe) :- 
    holds(X, statue).

violation(X, cafe, violation_holds_Statue_not_holds_Cafe) :- 
    holds(X, statue),
    not holds(X, cafe).

applicable(X, cafe) :- 
    holds(X, vendingmachine).

violation(X, cafe, violation_holds_VendingMachine_not_holds_Cafe) :- 
    holds(X, vendingmachine),
    not holds(X, cafe).



rule(restaurant).
applicable(X, restaurant) :- 
    holds(X, restaurant).

violation(X, restaurant, violation_holds_Restaurant_not_holds_Car_not_holds_Sign) :- 
    holds(X, restaurant),
    not holds(X, car),
    not holds(X, sign).

violation(X, restaurant, violation_holds_Restaurant_not_holds_Truck_not_holds_Sign) :- 
    holds(X, restaurant),
    not holds(X, truck),
    not holds(X, sign).

applicable(X, restaurant) :- 
    holds(X, car),
    holds(X, sign).

violation(X, restaurant, violation_holds_Car_holds_Sign_not_holds_Restaurant) :- 
    holds(X, car),
    holds(X, sign),
    not holds(X, restaurant).

applicable(X, restaurant) :- 
    holds(X, truck),
    holds(X, sign).

violation(X, restaurant, violation_holds_Truck_holds_Sign_not_holds_Restaurant) :- 
    holds(X, truck),
    holds(X, sign),
    not holds(X, restaurant).



rule(miscresidential).
applicable(X, miscresidential) :- 
    holds(X, miscresidential).

violation(X, miscresidential, violation_holds_MiscResidential_holds_awning_not_holds_TiledRoof) :- 
    holds(X, miscresidential),
    holds(X, awning),
    not holds(X, tiledroof).

violation(X, miscresidential, violation_holds_MiscResidential_holds_table_not_holds_TiledRoof) :- 
    holds(X, miscresidential),
    holds(X, table),
    not holds(X, tiledroof).

applicable(X, miscresidential) :- 
    not holds(X, awning),
    holds(X, tiledroof).

violation(X, miscresidential, violation_not_holds_awning_holds_TiledRoof_not_holds_MiscResidential) :- 
    not holds(X, awning),
    holds(X, tiledroof),
    not holds(X, miscresidential).

applicable(X, miscresidential) :- 
    not holds(X, table),
    holds(X, tiledroof).

violation(X, miscresidential, violation_not_holds_table_holds_TiledRoof_not_holds_MiscResidential) :- 
    not holds(X, table),
    holds(X, tiledroof),
    not holds(X, miscresidential).



rule(residential_no_chimney_pipe).
applicable(X, residential_no_chimney_pipe) :- 
    holds(X, residential).

violation(X, residential_no_chimney_pipe, violation_holds_Residential_holds_chimney_holds_pipe) :- 
    holds(X, residential),
    holds(X, chimney),
    holds(X, pipe).




violation_count(Rule, N) :- rule(Rule), N = #count { X, Type : violation(X, Rule, Type) }.

applicable_count(Rule, N) :-rule(Rule),N = #count { X : applicable(X, Rule) }.

violating_sample(X, Rule) :-rule(Rule),violation(X, Rule, _).

violating_sample_count(Rule, N) :-rule(Rule),N = #count { X : violating_sample(X, Rule) }.

violation_type_count(Rule, Type, N) :-rule(Rule),violation(_, Rule, Type),N = #count { X : violation(X, Rule, Type) }.

#show violation_count/2.
#show applicable_count/2.
#show violating_sample_count/2.
#show violation_type_count/3.
