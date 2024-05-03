import copy
from time import time
from database.DAO import DAO


class Model:
    def __init__(self):
        self._solBest = []
        self._listNerc = None
        self._listEvents = None
        self.loadNerc()
        self.soluzioni = []
        self.iterazioni = 0
        self.costo_cumulato = 0  #caching per tenere conto del cumulato delle ore
        self.recente = 2015
        self.vecchio = 1999  #caching per tenere conto dell'anno più recente e più vecchio

    def worstCase(self, nerc, maxY, maxH):
        self._listEvents = []  #ogni volta che chiamo la funzione resetto la lista di eventi
        self.loadEvents(nerc)  #carico gli eventi che mi interessano a seconda del nerc scelto
        self.costo_cumulato = 0  #a ogni chiamata azzero il cumulato
        t1 = time()
        self.ricorsione(set(), maxY, maxH, 0)  #parziale è una lista
        t2 = time()
        print(t2 - t1)

    def ricorsione(self, parziale, maxY, maxH, pos):  #possibili è l'insieme totale di eventi
        # CASO BANALE
        self.iterazioni += 1
        if pos == len(self._listEvents):  #se sono arrivato alla fine degli eventi aggiungo la soluzione trovata
            if self.is_nuova(parziale):
                sol = self.calcola_parametri(parziale)
                self.soluzioni.append(copy.deepcopy(sol))
        # CASO RICORSIVO
        else:
            for evento in self._listEvents[pos:]:
                pos += 1
                parziale.add(evento)  # aggiungo l'evento al parziale
                if self.condizioni(evento, maxY, maxH):  #controllo le condizioni
                    self.ricorsione(parziale, maxY, maxH, pos)  #faccio ripartire la ricorsione con la copia
                self.backtracking(parziale, evento)

    def backtracking(self, parziale, evento):
        parziale.remove(evento)
        self.costo_cumulato -= (evento.date_event_finished - evento.date_event_began).total_seconds()

    def condizioni(self, evento, maxY, maxH):
        if self.condizione_durata(evento, maxH) and self.condizione_anni(evento, maxY):
            return True
        else:
            return False

    def condizione_durata(self, evento, maxH):
        '''
        Aggiunge le ore al costo cumulato e verifica che non superino la soglia
        '''
        durata = (evento.date_event_finished - evento.date_event_began).total_seconds()
        self.costo_cumulato += durata
        if self.costo_cumulato > maxH * 3600:
            return False
        else:
            return True

    def condizione_anni(self, evento, maxY):
        anno = evento.date_event_began.year
        if anno < self.recente:
            self.recente = anno
        if anno > self.vecchio:
            self.vecchio = anno
        if self.recente - self.vecchio > maxY:
            return False
        else:
            return True

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
            for sol in self.soluzioni:
                if parziale == sol[0]:
                    return False
            return True

    def loadEvents(self, nerc):
        self._listEvents = DAO.getAllEvents(nerc)

    def loadNerc(self):
        self._listNerc = DAO.getAllNerc()

    @property
    def listNerc(self):
        return self._listNerc
