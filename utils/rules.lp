rule(misccommercial).
rule(miscindustrial).
rule(countryhouse).
rule(cafe).
rule(hotel).
rule(store).
rule(restaurant).
rule(constructionsite).
rule(suburban).
rule(powerplant).
rule(watertreatment).
rule(commercial).
rule(industrial).
rule(residential).
rule(industrial_not_table).
rule(miscresidential).


rule(building_no_car_truck).
rule(building_no_chimney_statue).
rule(residential_no_chimney_pipe).
rule(building_impl_complex).

holds(sample_id, class).

%RULES


%rule1 MiscCom = awning and table
violation(X, misccommercial, missing_awning) :-
    holds(X, misccommercial),
    not holds(X, awning).

violation(X, misccommercial, missing_table) :-
    holds(X, misccommercial),
    not holds(X, table).

violation(X, misccommercial, not_predicted) :-
    holds(X, awning),
    holds(X, table),
    not holds(X, misccommercial).


applicable(X, misccommercial) :-
    holds(X, misccommercial).

applicable(X, misccommercial) :-
    holds(X, awning),
    holds(X, table).



%rule2, the negation can not be done?
% miscInd = not awning and truck
violation(X, miscindustrial, has_awning) :-
    holds(X, miscindustrial),
    holds(X, awning).

violation(X, miscindustrial, missing_truck) :-
    holds(X, miscindustrial),
    not holds(X, truck).

violation(X, miscindustrial, not_predicted) :-
    holds(X, truck),
    not holds(X, awning),
    not holds(X, miscindustrial).


applicable(X, miscindustrial) :-
    holds(X, miscindustrial).

applicable(X, miscindustrial) :-
    not holds(X, awning),
    holds(X, truck).



%rule3 countryHouse = car and tiledroof
violation(X, countryhouse, missing_car) :-
    holds(X, countryhouse),
    not holds(X, car).

violation(X, countryhouse, missing_tiledroof) :-
    holds(X, countryhouse),
    not holds(X, tiledroof).

violation(X, countryhouse, not_predicted) :-
    holds(X, car),
    holds(X, tiledroof),
    not holds(X, countryhouse).


applicable(X, countryhouse) :-
    holds(X, countryhouse).

applicable(X, countryhouse) :-
    holds(X, car),
    holds(X, tiledroof).



%rule4
%cafe = statue or vendingMachine
violation(X, cafe, missing_both) :-
    holds(X, cafe),
    not holds(X, statue),
    not holds(X, vendingmachine).

violation(X, cafe, has_statue_not_cafe) :-
    holds(X, statue),
    not holds(X, cafe).

violation(X, cafe, has_vendingMachine_not_cafe) :-
    holds(X, vendingmachine),
    not holds(X, cafe).


applicable(X, cafe) :-
    holds(X, cafe).

applicable(X, cafe) :-
    holds(X, statue).

applicable(X, cafe) :-
    holds(X, vendingmachine).



%rule5
%hotel = wallsign
violation(X, hotel, missing_wallsign) :-
    holds(X, hotel),
    not holds(X, wallsign).

violation(X, hotel, not_predicted) :-
    holds(X, wallsign),
    not holds(X, hotel).


applicable(X, hotel) :-
    holds(X, hotel).

applicable(X, hotel) :-
    holds(X, wallsign).


%rule6
%store = billboard
violation(X, store, missing_billboard) :-
    holds(X, store),
    not holds(X, billboard).

violation(X, store, not_predicted) :-
    holds(X, billboard),
    not holds(X, store).

applicable(X, store) :-
    holds(X, store).

applicable(X, store) :-
    holds(X, billboard).

%rule 7
% restaurant = (car or truck) and sign
violation(X, restaurant, missing_sign) :-
    holds(X, restaurant),
    not holds(X, sign).

violation(X, restaurant, missing_vehicle) :-
    holds(X, restaurant),
    not holds(X, car),
    not holds(X, truck).

violation(X, restaurant, not_predicted) :-
    holds(X, sign),
    holds(X, car),
    not holds(X, restaurant).

violation(X, restaurant, not_predicted) :-
    holds(X, sign),
    holds(X, truck),
    not holds(X, restaurant).

applicable(X, restaurant) :-
    holds(X, restaurant).

applicable(X, restaurant) :-
    holds(X, car),
    holds(X, sign).

applicable(X, restaurant) :-
    holds(X, truck),
    holds(X, sign).


%rule8 constructionSite = Machine
violation(X, constructionsite, missing_machine) :-
    holds(X, constructionsite),
    not holds(X, machine).

violation(X, constructionsite, not_predicted) :-
    holds(X, machine),
    not holds(X, constructionsite).

applicable(X, constructionsite) :-
    holds(X, constructionsite).

applicable(X, constructionsite) :-
    holds(X, machine).

%rule9 Suburban ≡ Porch
violation(X, suburban, missing_porch) :-
    holds(X, suburban),
    not holds(X, porch).

violation(X, suburban, not_predicted) :-
    holds(X, porch),
    not holds(X, suburban).

applicable(X, suburban) :-
    holds(X, suburban).

applicable(X, suburban) :-
    holds(X, porch).

%rule10 PowerPlant = Chimney AND Pipe

violation(X, powerplant, missing_chimney) :-
    holds(X, powerplant),
    not holds(X, chimney).

violation(X, powerplant, missing_pipe) :-
    holds(X, powerplant),
    not holds(X, pipe).

violation(X, powerplant, not_predicted) :-
    holds(X, chimney),
    holds(X, pipe),
    not holds(X, powerplant).

applicable(X, powerplant) :-
    holds(X, powerplant).

applicable(X, powerplant) :-
    holds(X, chimney),
    holds(X, pipe).

%rule11 WaterTreatment = Pipe AND Truck

violation(X, watertreatment, missing_pipe) :-
    holds(X, watertreatment),
    not holds(X, pipe).

violation(X, watertreatment, missing_truck) :-
    holds(X, watertreatment),
    not holds(X, truck).

violation(X, watertreatment, not_predicted) :-
    holds(X, pipe),
    holds(X, truck),
    not holds(X, watertreatment).

applicable(X, watertreatment) :-
    holds(X, watertreatment).

applicable(X, watertreatment) :-
    holds(X, pipe),
    holds(X, truck).


%rule 12
%Industrial_not_table = Not Table
violation(X, industrial_not_table, has_table) :-
    holds(X, industrial),
    holds(X, table).

%violation(X, industrial_not_table, not_predicted) :-
    %not holds(X, industrial),
    %not holds(X, table).

applicable(X, industrial_not_table) :-
    holds(X, industrial).


%rule13 Commercial = Cafe OR Hotel OR MiscCommercial OR Restaurant OR Store
violation(X, commercial, missing_all) :-
    holds(X, commercial),
    not holds(X, cafe),
    not holds(X, hotel),
    not holds(X, misccommercial),
    not holds(X, restaurant),
    not holds(X, store).

violation(X, commercial, not_predicted) :-
    holds(X, cafe),
    not holds(X, commercial).

violation(X, commercial, not_predicted) :-
    holds(X, hotel),
    not holds(X, commercial).

violation(X, commercial, not_predicted) :-
    holds(X, misccommercial),
    not holds(X, commercial).

violation(X, commercial, not_predicted) :-
    holds(X, restaurant),
    not holds(X, commercial).

violation(X, commercial, not_predicted) :-
    holds(X, store),
    not holds(X, commercial).

applicable(X, commercial) :-
    holds(X, commercial).

applicable(X, commercial) :-
    holds(X, cafe).
applicable(X, commercial) :-
    holds(X, hotel).
applicable(X, commercial) :-
    holds(X, misccommercial).
applicable(X, commercial) :-
    holds(X, restaurant).
applicable(X, commercial) :-
    holds(X, store).

%rule 14 Rule: Industrial hierarchy
violation(X, industrial, missing_all) :-
    holds(X, industrial),
    not holds(X, constructionsite),
    not holds(X, miscindustrial),
    not holds(X, powerplant),
    not holds(X, watertreatment).

applicable(X, industrial) :-
    holds(X, industrial).

%rule15 Rule: Residential hierarchy
violation(X, residential, missing_all) :-
    holds(X, residential),
    not holds(X, countryhouse),
    not holds(X, miscresidential),
    not holds(X, suburban).

applicable(X, residential) :-
    holds(X, residential).

%rule 16 MiscResidential ≡ NOT(Awning ∧ Table) OR TiledRoof
violation(X, miscresidential, contradiction) :-
    holds(X, miscresidential),
    holds(X, awning),
    holds(X, table),
    not holds(X, tiledroof).

%violation(X, miscresidential, not_predicted) :-
   % not holds(X, awning),
   % not holds(X, table),
   % not holds(X, miscresidential).

violation(X, miscresidential, not_predicted) :-
    holds(X, tiledroof),
    not holds(X, miscresidential).

applicable(X, miscresidential) :-
    holds(X, miscresidential).

%applicable(X, miscresidential) :-
    %not holds(X, awning),
    %not holds(X, table).

applicable(X, miscresidential) :-
    holds(X, tiledroof).


%rule 17 Building ⊑ ¬(Car ∧ Truck)

violation(X, building_no_car_truck, has_both_car_truck) :-
    holds(X, building),
    holds(X, car),
    holds(X, truck).

applicable(X, building_no_car_truck) :-
    holds(X, building).


%rule18 Building ⊑ ¬(Chimney ∧ Statue)

violation(X, building_no_chimney_statue, has_both) :-
    holds(X, building),
    holds(X, chimney),
    holds(X, statue).

applicable(X, building_no_chimney_statue) :-
    holds(X, building).



%rule 19 Residential ⊑ ¬(Chimney ∨ Pipe)

violation(X, residential_no_chimney_pipe, has_chimney) :-
    holds(X, residential),
    holds(X, chimney).

violation(X, residential_no_chimney_pipe, has_pipe) :-
    holds(X, residential),
    holds(X, pipe).

applicable(X, residential_no_chimney_pipe) :-
    holds(X, residential).

%rule 20 Building ⊑ ¬((Car ∨ Truck) ∧ Machine) 
violation(X, building_impl_complex, invalid_combination) :-
    holds(X, building),
    holds(X, car),
    holds(X, machine).

violation(X, building_impl_complex, invalid_combination) :-
    holds(X, building),
    holds(X, truck),
    holds(X, machine).


applicable(X, building_impl_complex) :-
    holds(X, building).








violation_count(Rule, N) :-
    rule(Rule),
    N = #count { X, Type : violation(X, Rule, Type) }.

applicable_count(Rule, N) :-
    rule(Rule),
    N = #count { X : applicable(X, Rule) }.


violating_sample(X, Rule) :-
    rule(Rule),
    violation(X, Rule, _).

violating_sample_count(Rule, N) :-
    rule(Rule),
    N = #count { X : violating_sample(X, Rule) }.

violation_type_count(Rule, Type, N) :-
    rule(Rule),
    violation(_, Rule, Type),
    N = #count { X : violation(X, Rule, Type) }.


%violation_type_count(Rule, Type, N) :- rule(Rule), N = #count { X : violation(X, Rule, Type) }.


#show violation_count/2.
#show applicable_count/2.
#show violating_sample_count/2.

#show violation_type_count/3.
%#show violation/2.
