import utils.rules_and_concepts as rules_and_concepts

ALL_AXIOMS = rules_and_concepts.get_all_axioms()
ALL_CLASSES = rules_and_concepts.get_all_classes()
MainOperations = rules_and_concepts.MainOperations


AXIOMS_BY_NAME = {item["name"]: item for item in ALL_AXIOMS}

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
    new_lp_file.write(f"holds(sample_id, class).\n\n\n")

    for ax in new_axioms:
        r = ax["axiom"]

        generate_clingo_rule(r["left"], r["right"], r["main_op"], ax["name"], new_lp_file, debug_mode)

    write_clingo_essentials(new_lp_file)

    

def generate_clingo_rule(l, r, main_op, axiom_name, new_lp_file, debug_mode=False):
    
    #print(f"debug_mode : {debug_mode}")
    left, right = normalize_rule(l,r, debug_mode)

    if debug_mode:
        print(f"left: {left} | right: {right}")
    left = flatten_rec(left)
    right = flatten_rec(right)
    generate_clingo_holds(left, right, axiom_name, new_lp_file, main_op)
    

'''
% per-rule aggregate counts
rule_holds_count(Rule, N) :- rule(Rule), N = #count { X : rule_holds(X, Rule) }.

violation_type_count(Rule, Type, N) :- rule(Rule), rule_not_holds(_, Rule, Type), N = #count { X : rule_not_holds(X, Rule, Type) }.

% expose both the per-sample data and the aggregates
#show rule_holds/2.
#show rule_not_holds/3.
#show rule_holds_count/2.
#show violation_type_count/3.

'''
def write_clingo_essentials(new_lp_file):
    new_lp_file.write("\n\n\n")

    new_lp_file.write("% per-rule aggregate counts\n")
    new_lp_file.write("rule_holds_count(Rule, N) :- rule(Rule), N = #count { X : rule_holds(X, Rule) }.\n\n")

    new_lp_file.write("violation_type_count(Rule, Type, N) :- rule(Rule), rule_not_holds(_, Rule, Type), N = #count { X : rule_not_holds(X, Rule, Type) }.\n\n")

    new_lp_file.write("rule_vacuously_holds_count(Rule, N) :- rule(Rule), N = #count { X : rule_vacuously_holds(X, Rule) }.\n\n")

    new_lp_file.write(f"% expose both the per-sample data and the aggregates\n")

    new_lp_file.write("#show rule_holds/2.\n")
    new_lp_file.write("#show rule_not_holds/3.\n")
    new_lp_file.write("#show rule_holds_count/2.\n")
    new_lp_file.write("#show violation_type_count/3.\n")
    new_lp_file.write("#show rule_vacuously_holds/2.\n")
    new_lp_file.write("#show rule_vacuously_holds_count/2.\n")



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
            #print(f"in for and, complete_conj {complete_conj}, onj {obj}")
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




def generate_clingo_holds(left, right, axiom_name, new_lp_file, main_op):
    #GENERATE APLICABLE
    #new_lp_file.write(f"rule({axiom_name}).\n")

    #print(f"in clingo holds left: {left}, right: {right}")

    new_lp_file.write(f"%starting rule {axiom_name}\n")
    new_lp_file.write(f"rule({axiom_name}).\n\n")
    for l_part in left:
        generate_part_holds(l_part, axiom_name, "left", new_lp_file)

    for r_part in right:
        generate_part_holds(r_part, axiom_name, "right", new_lp_file)

    generate_rule_holds_and_rule_not_holds(axiom_name, new_lp_file, main_op)

    new_lp_file.write("\n\n\n")

    
def generate_rule_holds_and_rule_not_holds(axiom_name, new_lp_file, main_op):
    new_lp_file.write(f"rule_holds(X, {axiom_name}) :- \n")
    new_lp_file.write(f"    left_holds(X, {axiom_name}), \n")
    new_lp_file.write(f"    right_holds(X, {axiom_name}).\n\n")

    #print(f"main op in gen stuff {main_op}\n")
    if main_op == rules_and_concepts.MainOperations.EQUIVALENCE:
        #print("\n\n\n\n\n\n inside condition EQUIV \n\n\n\n\n\n\n")
        new_lp_file.write(f"rule_vacuously_holds(X, {axiom_name}) :- \n")
        new_lp_file.write(f"    holds(X, building),\n")
        new_lp_file.write(f"    not left_holds(X, {axiom_name}), \n")
        new_lp_file.write(f"    not right_holds(X, {axiom_name}).\n\n")

    if main_op == MainOperations.IMPLICATION or main_op == MainOperations.BUILDING_FACT:
        #print("\n\n\n\n\n\n inside condition \n\n\n\n\n\n\n")
        new_lp_file.write(f"rule_vacuously_holds(X, {axiom_name}) :- \n")
        new_lp_file.write(f"    holds(X, building),\n")
        new_lp_file.write(f"    not left_holds(X, {axiom_name}). \n\n")

    new_lp_file.write(f"rule_not_holds(X, {axiom_name}, left_holds_right_fails) :- \n")
    new_lp_file.write(f"    left_holds(X, {axiom_name}), \n")
    new_lp_file.write(f"    not right_holds(X, {axiom_name}).\n\n")

    if main_op == MainOperations.EQUIVALENCE:
        #print("\n\n\n\n\n\n inside condition \n\n\n\n\n\n\n")
        #print("writing an equivalence violation to the rule")
        new_lp_file.write(f"rule_not_holds(X, {axiom_name}, left_fails_right_holds) :- \n")
        new_lp_file.write(f"    not left_holds(X, {axiom_name}), \n")
        new_lp_file.write(f"    right_holds(X, {axiom_name}).\n\n")




    

def generate_part_holds(rule, axiom_name, part, new_lp_file):
    #print(f"rule in part_holds {rule}, in part {part}")
    part_holds_string = f"{part}_holds(X, {axiom_name}) :-\n"

    c_len_rule = len(rule)
    all_concepts_are_negative = True

    for i in range(c_len_rule):
        concept = rule[i]
        op = concept.split("(")[0]
        #print(f"write op in part holds {op}")

        # i want it to be 0, so i invert the not holds
        if op == "NOT":
            concept = concept[4:-1].lower()
            if (i == c_len_rule -1) and not all_concepts_are_negative:
                part_holds_string = part_holds_string + f"    not holds(X, {concept.lower()}).\n\n"
            else: 
                part_holds_string = part_holds_string + f"    not holds(X, {concept.lower()}),\n"

        else:
            all_concepts_are_negative = False
            if (i == c_len_rule -1):
                part_holds_string = part_holds_string + f"    holds(X, {concept.lower()}).\n\n"
            else:
                part_holds_string = part_holds_string + f"    holds(X, {concept.lower()}),\n"
    
    if all_concepts_are_negative:
        part_holds_string = part_holds_string + f"    holds(X, building).\n\n"

    new_lp_file.write(part_holds_string)
    



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




'''
 NEW STUFF testing
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
]

NEW_AXIOMS_1 = [
    
    {"axiom": rule_Hotel_Impl_Door, "active": False, "name": "rule_Hotel_Impl_Door"}, #high level rules
    {"axiom": rule_Hotel_Impl_Window, "active": False, "name": "rule_Hotel_Impl_Window"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Hotel_Impl_Car, "active": False, "name": "rule_Hotel_Impl_Car"}, #high level rules


    {"axiom": rule_Store_Impl_VendingMachine, "active": False, "name": "rule_Store_Impl_VendingMachine"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
    {"axiom": rule_Store_Impl_Truck, "active": False, "name": "rule_Store_Impl_VendingMachine"}, #high level rules
    {"axiom": rule_Store_Impl_Statue, "active": False, "name": "rule_Store_Impl_Statue"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante

    {"axiom": rule_Suburban_Impl_Pipe, "active": False, "name": "rule_Suburban_Impl_Pipe"}, #high level rules
    {"axiom": rule_Suburban_Impl_Chimney, "active": False, "name": "rule_Suburban_Impl_Chimney"}, #N funciona, pq ainda nao lidei com o Feature. tbm n é relevante
]
'''