"""Source of truth for dataset schema and research feature groups."""
FEATURES = ["school","sex","age","address","famsize","Pstatus","Medu","Fedu","Mjob","Fjob","reason","guardian","traveltime","studytime","failures","schoolsup","famsup","paid","activities","nursery","higher","internet","romantic","famrel","freetime","goout","Dalc","Walc","health","absences","G1","G2"]
TARGET = "G3"
ACADEMIC = ["G1","G2","studytime","failures","absences","schoolsup","paid","higher"]
BEHAVIOURAL = ["famsup","activities","romantic","famrel","freetime","goout","Dalc","Walc","health"]
CONTEXT = ["school","sex","age","address","famsize","Pstatus","Medu","Fedu","Mjob","Fjob","reason","guardian","traveltime","nursery","internet"]
GROUPS = {"academic": ACADEMIC, "behavioural": BEHAVIOURAL, "context": CONTEXT, "combined": FEATURES}
MODES = {"full": FEATURES, "early": [c for c in FEATURES if c not in {"G1","G2"}]}

def category(g3):
    """Map grade to specified ordinal classes; 0=At Risk, 1=Satisfactory, 2=Strong."""
    return 0 if g3 <= 9 else 1 if g3 <= 13 else 2
