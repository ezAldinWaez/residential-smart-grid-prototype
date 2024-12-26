import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"# RSG System Graph")
    return


@app.cell
def _(code_editor, mo):
    mo.md(f"""{mo.mermaid(code_editor.value)}""")
    return


@app.cell
def _(mo):
    code_editor = mo.ui.code_editor(
        value="""graph TB

        subgraph SS[Solar System]
            SS_P([Panels])
            SS_B([Batteries])
            SS_I([Inverter])
        end

        subgraph SSMS[Solar System Mng. System]
            SSMS_PMM([Power Mng. Module])
            SSMS_MAM([Mobile API Module])
        end

        subgraph HS[Houses]
            HS_H1([House 1])
            HS_H2([House 2])
        	HS_Hk([...])
            HS_Hn([House n])
        end

        subgraph UMA[Users Mobile App]
            UMA_U1([User 1 App])
        	UMA_U2([User 2 App])
        	UMA_Uk([...])
        	UMA_Un([User n App])
        end

        SS_P --Power--> SS_I
        SS_B <--Power--> SS_I

        SS_I --Data----> SSMS_PMM
        SS_I --Load Line----> SSMS_PMM
        SSMS_PMM --Grid Line----> SS_I

        SSMS_PMM --Load Line---> HS_H1 & HS_H2 & HS_Hn
        HS_H1 & HS_H2 & HS_Hn --Grid Lin---> SSMS_PMM

        SSMS_MAM <--> SSMS_PMM

        SSMS_MAM <--Data----> UMA_U1 & UMA_U2 & UMA_Un
    """,
        language="mermaid",
        label="RSG system graph mermaid code editor",
    )
    code_editor
    return (code_editor,)


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
