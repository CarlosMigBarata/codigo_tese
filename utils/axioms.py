import torch
import ltn


'''


'''


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

'''
CLASSES = [
    "Cafe",
    "Statue",
    "VendingMachine"
]

'''


final_classes = 4

# Constants
#final classes
class_cafe = ltn.Constant(torch.tensor(CLASSES.index("Cafe")), trainable=False)
class_hotel = ltn.Constant(torch.tensor(CLASSES.index("Hotel")), trainable=False)
class_store = ltn.Constant(torch.tensor(CLASSES.index("Store")), trainable=False)
class_misc_commercial = ltn.Constant(torch.tensor(CLASSES.index("MiscCommercial")), trainable=False)

#concepts
class_awning = ltn.Constant(torch.tensor(CLASSES.index("Awning")), trainable=False)
class_billboard = ltn.Constant(torch.tensor(CLASSES.index("Billboard")), trainable=False)
class_vending_machine = ltn.Constant(torch.tensor(CLASSES.index("VendingMachine")), trainable=False)
class_statue = ltn.Constant(torch.tensor(CLASSES.index("Statue")), trainable=False)
class_table = ltn.Constant(torch.tensor(CLASSES.index("Table")), trainable=False)
class_wall_sign = ltn.Constant(torch.tensor(CLASSES.index("WallSign")), trainable=False)



#Connectives
Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
And = ltn.Connective(ltn.fuzzy_ops.AndProd())
Or = ltn.Connective(ltn.fuzzy_ops.OrProbSum())
Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
Exists = ltn.Quantifier(ltn.fuzzy_ops.AggregPMean(p=2), quantifier="e")
Equiv = ltn.Connective(
    ltn.fuzzy_ops.Equiv(
        ltn.fuzzy_ops.AndProd(),
        ltn.fuzzy_ops.ImpliesReichenbach()
    )
)

formula_aggregator = ltn.fuzzy_ops.SatAgg(
    ltn.fuzzy_ops.AggregPMeanError(p=2)
)

def get_number_of_final_classes():
    return final_classes

def get_CLASSES():
    return CLASSES

def safe_forall(var, formula, device, default_value=0.5):
# Check if variable has zero elements
    
    if var.value.shape[0] == 0:  # no elements in the batch
        # Return a neutral truth value (0.5)
        print("\n\n\n\n\n\n\n\n miss \n\n\n\n\n\n")

        #missCounter += 1
        return ltn.Constant(torch.tensor(default_value, device=device))
    else:
        return Forall(var, formula)
    
def compute_axioms(logits, *args, p):

    device = logits.device

    #logits = logits_model(features_param)

    x = ltn.Variable("x", logits)
    x_hotel = ltn.Variable("x_hotel", logits[args[CLASSES.index("Hotel")] == 1, :])
    x_not_hotel = ltn.Variable("x_not_hotel", logits[args[CLASSES.index("Hotel")] == 0, :])

    x_cafe = ltn.Variable("x_cafe", logits[args[CLASSES.index("Cafe")] == 1, :])
    x_not_cafe = ltn.Variable("x_not_cafe", logits[args[CLASSES.index("Cafe")] == 0, :])

    x_store = ltn.Variable("x_store", logits[args[CLASSES.index("Store")] == 1, :])
    x_not_store = ltn.Variable("x_not_store", logits[args[CLASSES.index("Store")] == 0, :])

    x_misc_commercial = ltn.Variable("x_misc_commercial", logits[args[CLASSES.index("MiscCommercial")] == 1, :])
    x_not_misc_commercial = ltn.Variable("x_not_misc_commercial",logits[args[CLASSES.index("MiscCommercial")] == 0, :])

    '''
        axioms_cafe_and_disjunction = [
        safe_forall(x_cafe, p(x_cafe, class_cafe), device),
        safe_forall(x_not_cafe, Not(p(x_not_cafe, class_cafe)), device),
        safe_forall(
            x,
            Equiv(
                p(x, class_cafe),
                Or(p(x, class_statue), p(x, class_vending_machine)),
            ),
            device
        ),

    ]
    '''
    
    axioms = [
        # Grounded Predicates

        safe_forall(x_hotel, p(x_hotel, class_hotel), device),
        safe_forall(x_not_hotel, Not(p(x_not_hotel, class_hotel)),device),
        safe_forall(x_cafe, p(x_cafe, class_cafe), device),
        safe_forall(x_not_cafe, Not(p(x_not_cafe, class_cafe)), device),
        safe_forall(x_store, p(x_store, class_store), device),
        safe_forall(x_not_store, Not(p(x_not_store, class_store)), device),
        safe_forall(x_misc_commercial, p(x_misc_commercial, class_misc_commercial), device),
        safe_forall(
            x_not_misc_commercial,
            Not(p(x_not_misc_commercial, class_misc_commercial)),
            device
        ),
        # Axioms
        # Cafe = Statue or Vending Machine
        safe_forall(
            x,
            Equiv(
                p(x, class_cafe),
                Or(p(x, class_statue), p(x, class_vending_machine)),
            ),
            device
        ),
        # Hotel = Wall Sign
        safe_forall(
            x,
            Equiv(p(x, class_hotel), p(x, class_wall_sign)),
            device
        ),
        # MiscCommercial = Awning and Table
        safe_forall(
            x,
            Equiv(
                p(x, class_misc_commercial),
                And(p(x, class_awning), p(x, class_table)),
            ),
            device
        ),
        # Store = Billboard
        safe_forall(
            x,
            Equiv(p(x, class_store), p(x, class_billboard)),
            device
        ),
    ]

    
    #print("values of axioms")
    #for a in axioms:
      #print(a.value)

    sat_level = formula_aggregator(*axioms)

    return sat_level