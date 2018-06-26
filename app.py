from api.app import create_app, initdb, generate

app = create_app()

@app.cli.command("initdb")
def initdb_():
    initdb()


@app.cli.command("generate")
def generate_():
    generate()
