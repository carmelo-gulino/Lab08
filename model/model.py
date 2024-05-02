import copy

from database.DAO import DAO


class Model:
    def __init__(self):
        self._solBest = []
        self._listNerc = None
        self._listEvents = None
        self.loadNerc()
        self.soluzioni = []

    def worstCase(self, nerc, maxY, maxH):
        self._listEvents = []  #ogni volta che chiamo la funzione resetto la lista di eventi
        self.loadEvents(nerc)  #carico gli eventi che mi interessano a seconda del nerc scelto
        self.ricorsione(set(), maxY, maxH, 0)  #parziale è una lista

    def ricorsione(self, parziale, maxY, maxH, pos):  #possibili è l'insieme totale di eventi
        # CASO BANALE
        if pos == len(self._listEvents):  #se sono arrivato alla fine degli eventi aggiungo la soluzione trovata
            sol = self.calcola_parametri(parziale)
            self.soluzioni.append(copy.deepcopy(sol))
        # CASO RICORSIVO
        else:
            for evento in self._listEvents[pos:]:
                pos += 1
                parziale.add(evento)  # aggiungo l'evento al parziale
                if self.condizioni(parziale, maxY, maxH):  #controllo le condizioni
                    self.ricorsione(parziale, maxY, maxH, pos)  #faccio ripartire la ricorsione con la copia
                parziale.remove(evento)

    def condizioni(self, parziale, maxY, maxH):
        if self.condizione_durata(parziale, maxH) and self.condizione_anni(parziale, maxY):
            return True

    def condizione_durata(self, parziale, maxH):
        '''
        Verifica che il numero di ore degli eventi considerati non superi la soglia
        '''
        s = 0
        for e in parziale:
            durata = (e.date_event_finished - e.date_event_began).total_seconds()
            s += durata
        if s > maxH * 3600:
            return False
        else:
            return True

    def condizione_anni(self, parziale, maxY):
        recente = self.trova_piu_recente(parziale)
        vecchio = self.trova_piu_vecchio(parziale)
        if recente - vecchio > maxY:
            return False
        else:
            return True

    def trova_piu_recente(self, parziale):
        recente = 2015
        for e in parziale:
            anno = e.date_event_began.year
            if anno < recente:
                recente = anno
        return recente

    def trova_piu_vecchio(self, parziale):
        vecchio = 1999
        for e in parziale:
            anno = e.date_event_began.year
            if anno > vecchio:
                vecchio = anno
        return vecchio

    def calcola_parametri(self, parziale):
        ppl = self.calcola_persone(parziale)
        hrs = self.calcola_ore_totali(parziale)
        return parziale, ppl, hrs

    def calcola_persone(self, parziale):
        ppl = 0
        for e in parziale:
            ppl += e.customers_affected
        return ppl

    def calcola_ore_totali(self, parziale):
        hrs = 0
        for e in parziale:
            hrs += (e.date_event_finished - e.date_event_began).total_seconds() / 3600
        return hrs

    def estrai_persone(self, soluzione):
        return soluzione[1]

    def trova_massimo(self):
        massimo = max(self.soluzioni, key=self.estrai_persone)
        self._solBest.append(massimo)

    def is_nuova(self, parziale):
        if len(self.soluzioni) == 0:
            return True
        else:
            for soluzione in self.soluzioni:
                for evento in soluzione:
                    for e in parziale:
                        if e != evento:
                            return True
            return False

    def loadEvents(self, nerc):
        self._listEvents = DAO.getAllEvents(nerc)

    def loadNerc(self):
        self._listNerc = DAO.getAllNerc()

    @property
    def listNerc(self):
        return self._listNerc
