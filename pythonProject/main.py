from flask import Flask, render_template, url_for, request
from owlready2 import *

app = Flask(__name__)

onto = get_ontology("https://openclassmedia.org/ontosis/Ontosis/OntosisFinal.owl").load()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ontology_page')
def ontology_page():
    classes = [(Class.name, url_for("class_page", iri=Class.iri)) for Class in Thing.subclasses()]
    return render_template("ontology.html", classes=classes)


@app.route('/class/<path:iri>')
def class_page(iri):
    Class = IRIS[iri]
    subclasses = [(SubClass.name, url_for("class_page", iri=SubClass.iri)) for SubClass in Class.subclasses()]

    # Obtener el término de búsqueda de la URL
    search_term = request.args.get('search', '')

    # Filtrar los individuos que coincidan con el término de búsqueda
    individuals = [(individual2.name, url_for("individual_page", iri=individual2.iri)) for individual2 in
                   Class.instances() if search_term.lower() in individual2.name.lower()]

    return render_template("class.html", class_name=Class.name, subclasses=subclasses, individuals=individuals, iri=iri)


@app.route('/individual/<path:iri>')
def individual_page(iri):
    individual = IRIS[iri]
    classes = [(cls.name, url_for("class_page", iri=cls.iri)) for cls in individual.is_a]
    object_properties = {}
    data_properties = {}
    individual_name = str(individual).split(".")[1]

    for prop in individual.get_properties():
        values = []
        if isinstance(prop, ObjectPropertyClass):
            values = [obj.name for obj in getattr(individual, prop.name)]
            object_properties[prop.name] = values
        else:
            values = [str(getattr(individual, prop.name))]
            data_properties[prop.name] = values

    return render_template('individual.html', individual=individual, classes=classes,
                           object_properties=object_properties, data_properties=data_properties,
                           individual_name=individual_name)


if __name__ == "__main__":
    app.run(debug=True)
