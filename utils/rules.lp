rule(misccommercial).
rule(miscindustrial).
rule(countryhouse).
rule(cafe).
rule(hotel).
rule(store).

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



%violation_type_count(Rule, Type, N) :- rule(Rule), N = #count { X : violation(X, Rule, Type) }.


#show violation_count/2.
#show applicable_count/2.
#show violating_sample_count/2.

%#show violation_type_count/3.
%#show violation/2.
