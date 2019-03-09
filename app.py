from api.app import create_app, initdb, generate

app = create_app()


# TODO: I don't know whether this function returns anything
@app.cli.command("initdb")
def initdb_():
    initdb()


# TODO: I don't know whether this function returns anything
@app.cli.command("generate")
def generate_():
    generate()
