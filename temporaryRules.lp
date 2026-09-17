holds(sample_id, class).


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
