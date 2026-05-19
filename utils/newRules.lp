holds(sample_id, class).


%starting rule building_types
rule(building_types).

left_holds(X, building_types) :-
    holds(X, building).

right_holds(X, building_types) :-
    holds(X, residential).

right_holds(X, building_types) :-
    holds(X, commercial).

right_holds(X, building_types) :-
    holds(X, industrial).

rule_holds(X, building_types) :- 
    left_holds(X, building_types), 
    right_holds(X, building_types).

rule_vacuously_holds(X, building_types) :- 
    holds(X, building),
    not left_holds(X, building_types). 

rule_not_holds(X, building_types, left_holds_right_fails) :- 
    left_holds(X, building_types), 
    not right_holds(X, building_types).




%starting rule feature_types
rule(feature_types).

left_holds(X, feature_types) :-
    holds(X, feature).

right_holds(X, feature_types) :-
    holds(X, awning).

right_holds(X, feature_types) :-
    holds(X, billboard).

right_holds(X, feature_types) :-
    holds(X, car).

right_holds(X, feature_types) :-
    holds(X, chimney).

right_holds(X, feature_types) :-
    holds(X, door).

right_holds(X, feature_types) :-
    holds(X, machine).

right_holds(X, feature_types) :-
    holds(X, pipe).

right_holds(X, feature_types) :-
    holds(X, porch).

right_holds(X, feature_types) :-
    holds(X, sign).

right_holds(X, feature_types) :-
    holds(X, statue).

right_holds(X, feature_types) :-
    holds(X, table).

right_holds(X, feature_types) :-
    holds(X, tiledroof).

right_holds(X, feature_types) :-
    holds(X, truck).

right_holds(X, feature_types) :-
    holds(X, vendingmachine).

right_holds(X, feature_types) :-
    holds(X, wallsign).

right_holds(X, feature_types) :-
    holds(X, window).

rule_holds(X, feature_types) :- 
    left_holds(X, feature_types), 
    right_holds(X, feature_types).

rule_vacuously_holds(X, feature_types) :- 
    holds(X, building),
    not left_holds(X, feature_types), 
    not right_holds(X, feature_types).

rule_not_holds(X, feature_types, left_holds_right_fails) :- 
    left_holds(X, feature_types), 
    not right_holds(X, feature_types).

rule_not_holds(X, feature_types, left_fails_right_holds) :- 
    not left_holds(X, feature_types), 
    right_holds(X, feature_types).




%starting rule commercial
rule(commercial).

left_holds(X, commercial) :-
    holds(X, commercial).

right_holds(X, commercial) :-
    holds(X, cafe).

right_holds(X, commercial) :-
    holds(X, hotel).

right_holds(X, commercial) :-
    holds(X, misccommercial).

right_holds(X, commercial) :-
    holds(X, restaurant).

right_holds(X, commercial) :-
    holds(X, store).

rule_holds(X, commercial) :- 
    left_holds(X, commercial), 
    right_holds(X, commercial).

rule_vacuously_holds(X, commercial) :- 
    holds(X, building),
    not left_holds(X, commercial), 
    not right_holds(X, commercial).

rule_not_holds(X, commercial, left_holds_right_fails) :- 
    left_holds(X, commercial), 
    not right_holds(X, commercial).

rule_not_holds(X, commercial, left_fails_right_holds) :- 
    not left_holds(X, commercial), 
    right_holds(X, commercial).




%starting rule industrial
rule(industrial).

left_holds(X, industrial) :-
    holds(X, industrial).

right_holds(X, industrial) :-
    holds(X, constructionsite).

right_holds(X, industrial) :-
    holds(X, miscindustrial).

right_holds(X, industrial) :-
    holds(X, powerplant).

right_holds(X, industrial) :-
    holds(X, watertreatment).

rule_holds(X, industrial) :- 
    left_holds(X, industrial), 
    right_holds(X, industrial).

rule_vacuously_holds(X, industrial) :- 
    holds(X, building),
    not left_holds(X, industrial), 
    not right_holds(X, industrial).

rule_not_holds(X, industrial, left_holds_right_fails) :- 
    left_holds(X, industrial), 
    not right_holds(X, industrial).

rule_not_holds(X, industrial, left_fails_right_holds) :- 
    not left_holds(X, industrial), 
    right_holds(X, industrial).




%starting rule residential
rule(residential).

left_holds(X, residential) :-
    holds(X, residential).

right_holds(X, residential) :-
    holds(X, countryhouse).

right_holds(X, residential) :-
    holds(X, miscresidential).

right_holds(X, residential) :-
    holds(X, suburban).

rule_holds(X, residential) :- 
    left_holds(X, residential), 
    right_holds(X, residential).

rule_vacuously_holds(X, residential) :- 
    holds(X, building),
    not left_holds(X, residential), 
    not right_holds(X, residential).

rule_not_holds(X, residential, left_holds_right_fails) :- 
    left_holds(X, residential), 
    not right_holds(X, residential).

rule_not_holds(X, residential, left_fails_right_holds) :- 
    not left_holds(X, residential), 
    right_holds(X, residential).




%starting rule building_impl_complex
rule(building_impl_complex).

left_holds(X, building_impl_complex) :-
    holds(X, building).

right_holds(X, building_impl_complex) :-
    not holds(X, car),
    not holds(X, truck),
    holds(X, building).

right_holds(X, building_impl_complex) :-
    not holds(X, machine),
    holds(X, building).

rule_holds(X, building_impl_complex) :- 
    left_holds(X, building_impl_complex), 
    right_holds(X, building_impl_complex).

rule_vacuously_holds(X, building_impl_complex) :- 
    holds(X, building),
    not left_holds(X, building_impl_complex). 

rule_not_holds(X, building_impl_complex, left_holds_right_fails) :- 
    left_holds(X, building_impl_complex), 
    not right_holds(X, building_impl_complex).




%starting rule building_no_car_truck
rule(building_no_car_truck).

left_holds(X, building_no_car_truck) :-
    holds(X, building).

right_holds(X, building_no_car_truck) :-
    not holds(X, car),
    holds(X, building).

right_holds(X, building_no_car_truck) :-
    not holds(X, truck),
    holds(X, building).

rule_holds(X, building_no_car_truck) :- 
    left_holds(X, building_no_car_truck), 
    right_holds(X, building_no_car_truck).

rule_vacuously_holds(X, building_no_car_truck) :- 
    holds(X, building),
    not left_holds(X, building_no_car_truck). 

rule_not_holds(X, building_no_car_truck, left_holds_right_fails) :- 
    left_holds(X, building_no_car_truck), 
    not right_holds(X, building_no_car_truck).




%starting rule building_no_chimney_statue
rule(building_no_chimney_statue).

left_holds(X, building_no_chimney_statue) :-
    holds(X, building).

right_holds(X, building_no_chimney_statue) :-
    not holds(X, chimney),
    holds(X, building).

right_holds(X, building_no_chimney_statue) :-
    not holds(X, statue),
    holds(X, building).

rule_holds(X, building_no_chimney_statue) :- 
    left_holds(X, building_no_chimney_statue), 
    right_holds(X, building_no_chimney_statue).

rule_vacuously_holds(X, building_no_chimney_statue) :- 
    holds(X, building),
    not left_holds(X, building_no_chimney_statue). 

rule_not_holds(X, building_no_chimney_statue, left_holds_right_fails) :- 
    left_holds(X, building_no_chimney_statue), 
    not right_holds(X, building_no_chimney_statue).




%starting rule building_noDoorOrNoWindow_Impl_noAwning
rule(building_noDoorOrNoWindow_Impl_noAwning).

left_holds(X, building_noDoorOrNoWindow_Impl_noAwning) :-
    not holds(X, door),
    not holds(X, window),
    holds(X, building).

right_holds(X, building_noDoorOrNoWindow_Impl_noAwning) :-
    not holds(X, awning),
    holds(X, building).

rule_holds(X, building_noDoorOrNoWindow_Impl_noAwning) :- 
    left_holds(X, building_noDoorOrNoWindow_Impl_noAwning), 
    right_holds(X, building_noDoorOrNoWindow_Impl_noAwning).

rule_vacuously_holds(X, building_noDoorOrNoWindow_Impl_noAwning) :- 
    holds(X, building),
    not left_holds(X, building_noDoorOrNoWindow_Impl_noAwning). 

rule_not_holds(X, building_noDoorOrNoWindow_Impl_noAwning, left_holds_right_fails) :- 
    left_holds(X, building_noDoorOrNoWindow_Impl_noAwning), 
    not right_holds(X, building_noDoorOrNoWindow_Impl_noAwning).




%starting rule hotel
rule(hotel).

left_holds(X, hotel) :-
    holds(X, hotel).

right_holds(X, hotel) :-
    holds(X, wallsign).

rule_holds(X, hotel) :- 
    left_holds(X, hotel), 
    right_holds(X, hotel).

rule_vacuously_holds(X, hotel) :- 
    holds(X, building),
    not left_holds(X, hotel), 
    not right_holds(X, hotel).

rule_not_holds(X, hotel, left_holds_right_fails) :- 
    left_holds(X, hotel), 
    not right_holds(X, hotel).

rule_not_holds(X, hotel, left_fails_right_holds) :- 
    not left_holds(X, hotel), 
    right_holds(X, hotel).




%starting rule store
rule(store).

left_holds(X, store) :-
    holds(X, store).

right_holds(X, store) :-
    holds(X, billboard).

rule_holds(X, store) :- 
    left_holds(X, store), 
    right_holds(X, store).

rule_vacuously_holds(X, store) :- 
    holds(X, building),
    not left_holds(X, store), 
    not right_holds(X, store).

rule_not_holds(X, store, left_holds_right_fails) :- 
    left_holds(X, store), 
    not right_holds(X, store).

rule_not_holds(X, store, left_fails_right_holds) :- 
    not left_holds(X, store), 
    right_holds(X, store).




%starting rule industrial_not_table
rule(industrial_not_table).

left_holds(X, industrial_not_table) :-
    holds(X, industrial).

right_holds(X, industrial_not_table) :-
    not holds(X, table),
    holds(X, building).

rule_holds(X, industrial_not_table) :- 
    left_holds(X, industrial_not_table), 
    right_holds(X, industrial_not_table).

rule_vacuously_holds(X, industrial_not_table) :- 
    holds(X, building),
    not left_holds(X, industrial_not_table). 

rule_not_holds(X, industrial_not_table, left_holds_right_fails) :- 
    left_holds(X, industrial_not_table), 
    not right_holds(X, industrial_not_table).




%starting rule constructionsite
rule(constructionsite).

left_holds(X, constructionsite) :-
    holds(X, constructionsite).

right_holds(X, constructionsite) :-
    holds(X, machine).

rule_holds(X, constructionsite) :- 
    left_holds(X, constructionsite), 
    right_holds(X, constructionsite).

rule_vacuously_holds(X, constructionsite) :- 
    holds(X, building),
    not left_holds(X, constructionsite), 
    not right_holds(X, constructionsite).

rule_not_holds(X, constructionsite, left_holds_right_fails) :- 
    left_holds(X, constructionsite), 
    not right_holds(X, constructionsite).

rule_not_holds(X, constructionsite, left_fails_right_holds) :- 
    not left_holds(X, constructionsite), 
    right_holds(X, constructionsite).




%starting rule suburban
rule(suburban).

left_holds(X, suburban) :-
    holds(X, suburban).

right_holds(X, suburban) :-
    holds(X, porch).

rule_holds(X, suburban) :- 
    left_holds(X, suburban), 
    right_holds(X, suburban).

rule_vacuously_holds(X, suburban) :- 
    holds(X, building),
    not left_holds(X, suburban), 
    not right_holds(X, suburban).

rule_not_holds(X, suburban, left_holds_right_fails) :- 
    left_holds(X, suburban), 
    not right_holds(X, suburban).

rule_not_holds(X, suburban, left_fails_right_holds) :- 
    not left_holds(X, suburban), 
    right_holds(X, suburban).




%starting rule misccommercial
rule(misccommercial).

left_holds(X, misccommercial) :-
    holds(X, misccommercial).

right_holds(X, misccommercial) :-
    holds(X, awning),
    holds(X, table).

rule_holds(X, misccommercial) :- 
    left_holds(X, misccommercial), 
    right_holds(X, misccommercial).

rule_vacuously_holds(X, misccommercial) :- 
    holds(X, building),
    not left_holds(X, misccommercial), 
    not right_holds(X, misccommercial).

rule_not_holds(X, misccommercial, left_holds_right_fails) :- 
    left_holds(X, misccommercial), 
    not right_holds(X, misccommercial).

rule_not_holds(X, misccommercial, left_fails_right_holds) :- 
    not left_holds(X, misccommercial), 
    right_holds(X, misccommercial).




%starting rule miscindustrial
rule(miscindustrial).

left_holds(X, miscindustrial) :-
    holds(X, miscindustrial).

right_holds(X, miscindustrial) :-
    not holds(X, awning),
    holds(X, truck).

rule_holds(X, miscindustrial) :- 
    left_holds(X, miscindustrial), 
    right_holds(X, miscindustrial).

rule_vacuously_holds(X, miscindustrial) :- 
    holds(X, building),
    not left_holds(X, miscindustrial), 
    not right_holds(X, miscindustrial).

rule_not_holds(X, miscindustrial, left_holds_right_fails) :- 
    left_holds(X, miscindustrial), 
    not right_holds(X, miscindustrial).

rule_not_holds(X, miscindustrial, left_fails_right_holds) :- 
    not left_holds(X, miscindustrial), 
    right_holds(X, miscindustrial).




%starting rule countryhouse
rule(countryhouse).

left_holds(X, countryhouse) :-
    holds(X, countryhouse).

right_holds(X, countryhouse) :-
    holds(X, car),
    holds(X, tiledroof).

rule_holds(X, countryhouse) :- 
    left_holds(X, countryhouse), 
    right_holds(X, countryhouse).

rule_vacuously_holds(X, countryhouse) :- 
    holds(X, building),
    not left_holds(X, countryhouse), 
    not right_holds(X, countryhouse).

rule_not_holds(X, countryhouse, left_holds_right_fails) :- 
    left_holds(X, countryhouse), 
    not right_holds(X, countryhouse).

rule_not_holds(X, countryhouse, left_fails_right_holds) :- 
    not left_holds(X, countryhouse), 
    right_holds(X, countryhouse).




%starting rule powerplant
rule(powerplant).

left_holds(X, powerplant) :-
    holds(X, powerplant).

right_holds(X, powerplant) :-
    holds(X, chimney),
    holds(X, pipe).

rule_holds(X, powerplant) :- 
    left_holds(X, powerplant), 
    right_holds(X, powerplant).

rule_vacuously_holds(X, powerplant) :- 
    holds(X, building),
    not left_holds(X, powerplant), 
    not right_holds(X, powerplant).

rule_not_holds(X, powerplant, left_holds_right_fails) :- 
    left_holds(X, powerplant), 
    not right_holds(X, powerplant).

rule_not_holds(X, powerplant, left_fails_right_holds) :- 
    not left_holds(X, powerplant), 
    right_holds(X, powerplant).




%starting rule watertreatment
rule(watertreatment).

left_holds(X, watertreatment) :-
    holds(X, watertreatment).

right_holds(X, watertreatment) :-
    holds(X, pipe),
    holds(X, truck).

rule_holds(X, watertreatment) :- 
    left_holds(X, watertreatment), 
    right_holds(X, watertreatment).

rule_vacuously_holds(X, watertreatment) :- 
    holds(X, building),
    not left_holds(X, watertreatment), 
    not right_holds(X, watertreatment).

rule_not_holds(X, watertreatment, left_holds_right_fails) :- 
    left_holds(X, watertreatment), 
    not right_holds(X, watertreatment).

rule_not_holds(X, watertreatment, left_fails_right_holds) :- 
    not left_holds(X, watertreatment), 
    right_holds(X, watertreatment).




%starting rule cafe
rule(cafe).

left_holds(X, cafe) :-
    holds(X, cafe).

right_holds(X, cafe) :-
    holds(X, statue).

right_holds(X, cafe) :-
    holds(X, vendingmachine).

rule_holds(X, cafe) :- 
    left_holds(X, cafe), 
    right_holds(X, cafe).

rule_vacuously_holds(X, cafe) :- 
    holds(X, building),
    not left_holds(X, cafe), 
    not right_holds(X, cafe).

rule_not_holds(X, cafe, left_holds_right_fails) :- 
    left_holds(X, cafe), 
    not right_holds(X, cafe).

rule_not_holds(X, cafe, left_fails_right_holds) :- 
    not left_holds(X, cafe), 
    right_holds(X, cafe).




%starting rule restaurant
rule(restaurant).

left_holds(X, restaurant) :-
    holds(X, restaurant).

right_holds(X, restaurant) :-
    holds(X, car),
    holds(X, sign).

right_holds(X, restaurant) :-
    holds(X, truck),
    holds(X, sign).

rule_holds(X, restaurant) :- 
    left_holds(X, restaurant), 
    right_holds(X, restaurant).

rule_vacuously_holds(X, restaurant) :- 
    holds(X, building),
    not left_holds(X, restaurant), 
    not right_holds(X, restaurant).

rule_not_holds(X, restaurant, left_holds_right_fails) :- 
    left_holds(X, restaurant), 
    not right_holds(X, restaurant).

rule_not_holds(X, restaurant, left_fails_right_holds) :- 
    not left_holds(X, restaurant), 
    right_holds(X, restaurant).




%starting rule miscresidential
rule(miscresidential).

left_holds(X, miscresidential) :-
    holds(X, miscresidential).

right_holds(X, miscresidential) :-
    not holds(X, awning),
    holds(X, tiledroof).

right_holds(X, miscresidential) :-
    not holds(X, table),
    holds(X, tiledroof).

rule_holds(X, miscresidential) :- 
    left_holds(X, miscresidential), 
    right_holds(X, miscresidential).

rule_vacuously_holds(X, miscresidential) :- 
    holds(X, building),
    not left_holds(X, miscresidential), 
    not right_holds(X, miscresidential).

rule_not_holds(X, miscresidential, left_holds_right_fails) :- 
    left_holds(X, miscresidential), 
    not right_holds(X, miscresidential).

rule_not_holds(X, miscresidential, left_fails_right_holds) :- 
    not left_holds(X, miscresidential), 
    right_holds(X, miscresidential).




%starting rule residential_no_chimney_pipe
rule(residential_no_chimney_pipe).

left_holds(X, residential_no_chimney_pipe) :-
    holds(X, residential).

right_holds(X, residential_no_chimney_pipe) :-
    not holds(X, chimney),
    not holds(X, pipe),
    holds(X, building).

rule_holds(X, residential_no_chimney_pipe) :- 
    left_holds(X, residential_no_chimney_pipe), 
    right_holds(X, residential_no_chimney_pipe).

rule_vacuously_holds(X, residential_no_chimney_pipe) :- 
    holds(X, building),
    not left_holds(X, residential_no_chimney_pipe). 

rule_not_holds(X, residential_no_chimney_pipe, left_holds_right_fails) :- 
    left_holds(X, residential_no_chimney_pipe), 
    not right_holds(X, residential_no_chimney_pipe).




%starting rule rule_hotel_impl_door
rule(rule_hotel_impl_door).

left_holds(X, rule_hotel_impl_door) :-
    holds(X, hotel).

right_holds(X, rule_hotel_impl_door) :-
    holds(X, door),
    holds(X, chimney).

rule_holds(X, rule_hotel_impl_door) :- 
    left_holds(X, rule_hotel_impl_door), 
    right_holds(X, rule_hotel_impl_door).

rule_vacuously_holds(X, rule_hotel_impl_door) :- 
    holds(X, building),
    not left_holds(X, rule_hotel_impl_door). 

rule_not_holds(X, rule_hotel_impl_door, left_holds_right_fails) :- 
    left_holds(X, rule_hotel_impl_door), 
    not right_holds(X, rule_hotel_impl_door).




%starting rule rule_hotel_impl_window
rule(rule_hotel_impl_window).

left_holds(X, rule_hotel_impl_window) :-
    holds(X, hotel).

right_holds(X, rule_hotel_impl_window) :-
    holds(X, window),
    holds(X, pipe).

rule_holds(X, rule_hotel_impl_window) :- 
    left_holds(X, rule_hotel_impl_window), 
    right_holds(X, rule_hotel_impl_window).

rule_vacuously_holds(X, rule_hotel_impl_window) :- 
    holds(X, building),
    not left_holds(X, rule_hotel_impl_window). 

rule_not_holds(X, rule_hotel_impl_window, left_holds_right_fails) :- 
    left_holds(X, rule_hotel_impl_window), 
    not right_holds(X, rule_hotel_impl_window).




%starting rule rule_hotel_impl_car
rule(rule_hotel_impl_car).

left_holds(X, rule_hotel_impl_car) :-
    holds(X, hotel).

right_holds(X, rule_hotel_impl_car) :-
    not holds(X, car),
    holds(X, awning).

rule_holds(X, rule_hotel_impl_car) :- 
    left_holds(X, rule_hotel_impl_car), 
    right_holds(X, rule_hotel_impl_car).

rule_vacuously_holds(X, rule_hotel_impl_car) :- 
    holds(X, building),
    not left_holds(X, rule_hotel_impl_car). 

rule_not_holds(X, rule_hotel_impl_car, left_holds_right_fails) :- 
    left_holds(X, rule_hotel_impl_car), 
    not right_holds(X, rule_hotel_impl_car).




%starting rule rule_store_impl_door
rule(rule_store_impl_door).

left_holds(X, rule_store_impl_door) :-
    holds(X, store).

right_holds(X, rule_store_impl_door) :-
    holds(X, door),
    not holds(X, chimney).

rule_holds(X, rule_store_impl_door) :- 
    left_holds(X, rule_store_impl_door), 
    right_holds(X, rule_store_impl_door).

rule_vacuously_holds(X, rule_store_impl_door) :- 
    holds(X, building),
    not left_holds(X, rule_store_impl_door). 

rule_not_holds(X, rule_store_impl_door, left_holds_right_fails) :- 
    left_holds(X, rule_store_impl_door), 
    not right_holds(X, rule_store_impl_door).




%starting rule rule_store_impl_window
rule(rule_store_impl_window).

left_holds(X, rule_store_impl_window) :-
    holds(X, store).

right_holds(X, rule_store_impl_window) :-
    holds(X, window),
    not holds(X, pipe).

rule_holds(X, rule_store_impl_window) :- 
    left_holds(X, rule_store_impl_window), 
    right_holds(X, rule_store_impl_window).

rule_vacuously_holds(X, rule_store_impl_window) :- 
    holds(X, building),
    not left_holds(X, rule_store_impl_window). 

rule_not_holds(X, rule_store_impl_window, left_holds_right_fails) :- 
    left_holds(X, rule_store_impl_window), 
    not right_holds(X, rule_store_impl_window).




%starting rule rule_store_impl_car
rule(rule_store_impl_car).

left_holds(X, rule_store_impl_car) :-
    holds(X, store).

right_holds(X, rule_store_impl_car) :-
    holds(X, car),
    not holds(X, pipe).

rule_holds(X, rule_store_impl_car) :- 
    left_holds(X, rule_store_impl_car), 
    right_holds(X, rule_store_impl_car).

rule_vacuously_holds(X, rule_store_impl_car) :- 
    holds(X, building),
    not left_holds(X, rule_store_impl_car). 

rule_not_holds(X, rule_store_impl_car, left_holds_right_fails) :- 
    left_holds(X, rule_store_impl_car), 
    not right_holds(X, rule_store_impl_car).




%starting rule rule_constructionsite_impl_truck
rule(rule_constructionsite_impl_truck).

left_holds(X, rule_constructionsite_impl_truck) :-
    holds(X, constructionsite).

right_holds(X, rule_constructionsite_impl_truck) :-
    holds(X, truck).

right_holds(X, rule_constructionsite_impl_truck) :-
    holds(X, chimney).

rule_holds(X, rule_constructionsite_impl_truck) :- 
    left_holds(X, rule_constructionsite_impl_truck), 
    right_holds(X, rule_constructionsite_impl_truck).

rule_vacuously_holds(X, rule_constructionsite_impl_truck) :- 
    holds(X, building),
    not left_holds(X, rule_constructionsite_impl_truck). 

rule_not_holds(X, rule_constructionsite_impl_truck, left_holds_right_fails) :- 
    left_holds(X, rule_constructionsite_impl_truck), 
    not right_holds(X, rule_constructionsite_impl_truck).




%starting rule rule_constructionsite_impl_table
rule(rule_constructionsite_impl_table).

left_holds(X, rule_constructionsite_impl_table) :-
    holds(X, constructionsite).

right_holds(X, rule_constructionsite_impl_table) :-
    holds(X, table).

right_holds(X, rule_constructionsite_impl_table) :-
    holds(X, pipe).

rule_holds(X, rule_constructionsite_impl_table) :- 
    left_holds(X, rule_constructionsite_impl_table), 
    right_holds(X, rule_constructionsite_impl_table).

rule_vacuously_holds(X, rule_constructionsite_impl_table) :- 
    holds(X, building),
    not left_holds(X, rule_constructionsite_impl_table). 

rule_not_holds(X, rule_constructionsite_impl_table, left_holds_right_fails) :- 
    left_holds(X, rule_constructionsite_impl_table), 
    not right_holds(X, rule_constructionsite_impl_table).




%starting rule rule_constructionsite_impl_car
rule(rule_constructionsite_impl_car).

left_holds(X, rule_constructionsite_impl_car) :-
    holds(X, constructionsite).

right_holds(X, rule_constructionsite_impl_car) :-
    not holds(X, car),
    holds(X, building).

right_holds(X, rule_constructionsite_impl_car) :-
    holds(X, tiledroof).

rule_holds(X, rule_constructionsite_impl_car) :- 
    left_holds(X, rule_constructionsite_impl_car), 
    right_holds(X, rule_constructionsite_impl_car).

rule_vacuously_holds(X, rule_constructionsite_impl_car) :- 
    holds(X, building),
    not left_holds(X, rule_constructionsite_impl_car). 

rule_not_holds(X, rule_constructionsite_impl_car, left_holds_right_fails) :- 
    left_holds(X, rule_constructionsite_impl_car), 
    not right_holds(X, rule_constructionsite_impl_car).




%starting rule rule_suburban_impl_truck
rule(rule_suburban_impl_truck).

left_holds(X, rule_suburban_impl_truck) :-
    holds(X, suburban).

right_holds(X, rule_suburban_impl_truck) :-
    holds(X, truck).

right_holds(X, rule_suburban_impl_truck) :-
    not holds(X, chimney),
    holds(X, building).

rule_holds(X, rule_suburban_impl_truck) :- 
    left_holds(X, rule_suburban_impl_truck), 
    right_holds(X, rule_suburban_impl_truck).

rule_vacuously_holds(X, rule_suburban_impl_truck) :- 
    holds(X, building),
    not left_holds(X, rule_suburban_impl_truck). 

rule_not_holds(X, rule_suburban_impl_truck, left_holds_right_fails) :- 
    left_holds(X, rule_suburban_impl_truck), 
    not right_holds(X, rule_suburban_impl_truck).




%starting rule rule_suburban_impl_table
rule(rule_suburban_impl_table).

left_holds(X, rule_suburban_impl_table) :-
    holds(X, suburban).

right_holds(X, rule_suburban_impl_table) :-
    holds(X, table).

right_holds(X, rule_suburban_impl_table) :-
    not holds(X, pipe),
    holds(X, building).

rule_holds(X, rule_suburban_impl_table) :- 
    left_holds(X, rule_suburban_impl_table), 
    right_holds(X, rule_suburban_impl_table).

rule_vacuously_holds(X, rule_suburban_impl_table) :- 
    holds(X, building),
    not left_holds(X, rule_suburban_impl_table). 

rule_not_holds(X, rule_suburban_impl_table, left_holds_right_fails) :- 
    left_holds(X, rule_suburban_impl_table), 
    not right_holds(X, rule_suburban_impl_table).




%starting rule rule_suburban_impl_car
rule(rule_suburban_impl_car).

left_holds(X, rule_suburban_impl_car) :-
    holds(X, suburban).

right_holds(X, rule_suburban_impl_car) :-
    holds(X, car).

right_holds(X, rule_suburban_impl_car) :-
    not holds(X, awning),
    holds(X, building).

rule_holds(X, rule_suburban_impl_car) :- 
    left_holds(X, rule_suburban_impl_car), 
    right_holds(X, rule_suburban_impl_car).

rule_vacuously_holds(X, rule_suburban_impl_car) :- 
    holds(X, building),
    not left_holds(X, rule_suburban_impl_car). 

rule_not_holds(X, rule_suburban_impl_car, left_holds_right_fails) :- 
    left_holds(X, rule_suburban_impl_car), 
    not right_holds(X, rule_suburban_impl_car).







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
