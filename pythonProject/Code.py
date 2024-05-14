from owlready2 import *
import pandas as pd

owlready2.JAVA_EXE = "C:\\Users\\estef\\Desktop\\Varios\\Útil\\Protege\\Protege-5.6.1\\jre\\bin\\java.exe"

onto = get_ontology("https://openclassmedia.org/ontosis/Ontosis/Syllabus.owx")

onto.load()

file_path = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-IXRrHrgGskrXGxwSyBJJ5-h-M-YHIiPdmtEz_UYnHIk1KhqW-lJDZAOxTAsgsTwngrbgXix3RNmJ/pub?output=xlsx"
resultados = pd.read_excel(file_path, sheet_name='Resultados')
actividades = pd.read_excel(file_path, sheet_name='Actividades')
categorizadaResult = pd.read_excel(file_path, sheet_name='Tabla categorizada Res. por dim')
categorizadaAct = pd.read_excel(file_path, sheet_name='Tabla categorizada Act. por dim')
print("================ONTOSIS================")

print(list(onto.classes()))
with onto:
    for index, row in resultados.iterrows():

        # Creacion de las dimensiones en evaluacion y los resultados de aprendizaje en evaluacion
        for column_name, value in row.items():
            if not pd.isnull(value):  # Verificar si el valor de la celda no está vacío
                if column_name == 'dimension':
                    value = "E_" + value
                    dimE = onto.evaluation_learning_dimension(value)
                    dimE.hasDimensionName = [value]
                else:
                    div2 = value.split()[0]
                    resultE = onto.evaluation_dimension_learning_outcome(div2)
                    resultE.hasOutcomeVerb = [div2]
                    dimE.hasAssociatedOutcome.append(resultE)

    for index, row in actividades.iterrows():

        # Creación de actividades y asociación con las dimensiones existentes en evaluación
        for column_name, value in row.items():
            if not pd.isnull(value):  # Verificar si el valor de la celda no está vacío
                if column_name == 'dimension':
                    # Buscar la dimensión existente por su nombre
                    value = "E_" + value
                    dim = onto.search_one(hasDimensionName=[value], is_a=onto.evaluation_learning_dimension)
                else:
                    div2 = value.split()[0]
                    act = onto.evaluation_dimension_learning_activity(div2)
                    act.hasActivityName = [div2]
                    dim.hasAssociatedActivity.append(act)

    for index, row in categorizadaResult.iterrows():

        for column_name in categorizadaResult.columns:
            value = row[column_name]
            if not pd.isnull(value):  # Check if the value of the cell is not empty
                if column_name == 'MATERIA':
                    div = value.split("_")
                    pref = div[0]
                    name = div[1]
                    subj = onto.subject(name)
                    aux = "S_" + name
                    syll = onto.syllabus(aux)
                    subj.hasSubjectName = [name]
                    syll.hasSyllabusName = [aux]
                elif column_name in ['APRENDERAAPRENDER', 'COMPROMISO', 'CONOCIMIENTOFUNDAMENTAL', 'APLICACION',
                                     'INTEGRACION', 'DIMENSIONHUMANA']:
                    aux2 = pref + "_" + column_name
                    aux2 = aux2.split(".")[0]
                    aux3 = "C_" + aux2
                    aux3 = aux3.split(".")[0]
                    con = onto.conclusion(aux3)
                    dimS = onto.learning_dimensions(aux2)
                    dimS.hasDimensionName = [aux2]
                    result = onto.dimension_learning_outcome(value)
                    result.hasOutcomeVerb = [value]
                    dimS.hasAssociatedOutcome.append(result)
                    syll.hasDimension.append(dim)
                    con.hasConclusionSyllabus.append(result)

    for index, row in categorizadaAct.iterrows():
        for column_name, value in row.items():
            if not pd.isnull(value):  # Verificar si el valor de la celda no está vacío
                if column_name == 'MATERIA':
                    div = value.split("_")
                    pref = div[0]
                    name = div[1]
                    subj = onto.search_one(hasSubjectName=[name], is_a=onto.subject)
                    aux = "S_" + name
                    syll = onto.search_one(hasSyllabusName=[aux], is_a=onto.syllabus)
                else:

                    aux2 = pref + "_" + column_name
                    aux2 = aux2.split(".")[0]
                    aux3 = "C_" + aux2

                    dimA = onto.search_one(hasDimensionName=[aux2], is_a=onto.learning_dimensions)
                    if dimA is not None:
                        con = onto.conclusion(aux3)
                        # Crear la actividad
                        div2 = value.split()[0]
                        act = onto.dimension_learning_activity(div2)
                        act.hasActivityName = [div2]
                        # Agregar la actividad a la dimensión
                        dimA.hasAssociatedActivity.append(act)
                        con.hasConclusionSyllabus.append(act)

rules = [
    """ 
    evaluation_learning_dimension(?evalDim) ^ evaluation_dimension_learning_activity(?evalAct) ^ hasAssociatedActivity(?evalDim, ?evalAct) ^ learning_dimensions(?learnDim) ^ dimension_learning_activity(?learnAct) ^ hasAssociatedActivity(?learnDim, ?learnAct) ^ sameAs(?evalDim, ?learnDim) ^ sameAs(?evalAct, ?learnAct) ^ hasConclusionSyllabus(?c, ?learnAct) -> hasConclusionAct(?c, "CONSISTENTE")
    """
]





with onto:
    for i, rule in enumerate(rules, start=1):
        imp = Imp()
        imp.set_as_rule(rule)

    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

onto.save("OntosisF.owl")


