import networkx as nx
from flask import Flask, render_template, jsonify, url_for, request, send_file
from matplotlib import pyplot as plt
from owlready2 import *

app = Flask(__name__)

onto = get_ontology("http://localhost:9000/OntosisFinal.owl").load()


@app.route('/')
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
import networkx as nx
from flask import Flask, render_template, jsonify, url_for, request, send_file
from owlready2 import *

app = Flask(__name__)

onto = get_ontology("http://localhost:9000/OntosisFinal.owl").load()


def create_graph():
    # Crea un grafo dirigido
    G = nx.DiGraph()

    # Recorre todas las clases de la ontología y agrega los nodos al grafo
    for cls in onto.classes():
        G.add_node(cls.name)

        # Agrega arcos entre clases y sus superclases
        for sub in cls.subclasses():
            G.add_edge(sub.name, cls.name)

    return G


@app.route('/')
def ontology_page():
    classes = [(Class.name, url_for("class_page", iri=Class.iri)) for Class in Thing.subclasses()]
    return render_template("ontology.html", classes=classes)


@app.route('/ontograph')
def ontograph():
    G = create_graph()

    # Genera los datos del grafo
    nodes = [{'name': node} for node in G.nodes()]
    edges = [{'source': edge[0], 'target': edge[1]} for edge in G.edges()]

    # Envia los datos del grafo como respuesta JSON
    return jsonify(nodes=nodes, edges=edges)


@app.route('/ontology_graph')
def ontology_graph():
    G = create_graph()

    # Define la disposición del grafo
    pos = nx.spring_layout(G)

    # Dibuja el grafo
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=10, font_weight="bold",
            arrowsize=20)
    plt.title("Grafo de la ontología")
    plt.savefig("ontology_graph.png")  # Guarda el grafo como imagen
    plt.close()

    return send_file("ontology_graph.png", mimetype='image/png')


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
