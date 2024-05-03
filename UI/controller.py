import flet as ft
from model.nerc import Nerc


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._idMap = {}
        self.fillIDMap()

    def handleWorstCase(self, e):
        # TO FILL
        if self._view._ddNerc.value is None or self._view._txtYears.value is None or self._view._txtHours.value is None:
            self._view.create_alert("Selezionare tutti i campi")
        else:
            nerc = self._idMap[f"{self._view._ddNerc.value}"]  # estraggo l'oggetto nerc
            try:
                x_anni = int(self._view._txtYears.value)  # estraggo gli anni
                y_ore = int(self._view._txtHours.value)  # estraggo le ore
            except ValueError:
                self._view.create_alert("Inserire un numero")
                return
            self._model.worstCase(nerc, x_anni, y_ore)
            self._model.trova_massimo()
            self._view.print_massimo(self._model._solBest)
            print(self._model.iterazioni)

    def fillDD(self):
        nercList = self._model.listNerc

        for n in nercList:
            self._view._ddNerc.options.append(ft.dropdown.Option(n))
        self._view.update_page()

    def fillIDMap(self):
        values = self._model.listNerc
        for v in values:
            self._idMap[v.value] = v
