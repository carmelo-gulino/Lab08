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
        self.iterazioni = None
        self.ore_cumulato = None  #caching per tenere conto del cumulato delle ore
        self.pop_cumulato = None
        self.recente = None
        self.vecchio = None  #caching per tenere conto dell'anno più recente e più vecchio

    def initialize(self):
        self.iterazioni = 0
        self.pop_cumulato = 0
        self.recente = 2015
        self.vecchio = 1999  # caching per tenere conto dell'anno più recente e più vecchio
        self._listEvents = []  # ogni volta che chiamo la funzione resetto la lista di eventi
        self.ore_cumulato = 0  # a ogni chiamata azzero il cumulato
        self._solBest = []

    def worstCase(self, nerc, maxY, maxH):
        self.initialize()
        self.loadEvents(nerc)  # carico gli eventi che mi interessano a seconda del nerc scelto
        t1 = time()
        self.ricorsione(set(), maxY, maxH, 0)  #parziale è una lista
        t2 = time()
        print(t2 - t1)

    def ricorsione(self, parziale, maxY, maxH, pos):  #possibili è l'insieme totale di eventi
        # se ho trovato già una soluzione migliore di quella che posso ottenere, tronco il ramo
        for s in self._solBest:
            pop_da_aggiungere = sum([e.customers_affected for e in self._listEvents[pos:]])  #eventi non ancora visti
            if s[1] > (self.pop_cumulato + pop_da_aggiungere):
                return
        # CASO BANALE
        self.iterazioni += 1
        if pos == len(self._listEvents):  #se sono arrivato alla fine degli eventi aggiungo la soluzione trovata
            sol = (parziale, copy.deepcopy(self.pop_cumulato), (copy.deepcopy(self.ore_cumulato) / 3600))
            if self.is_better(sol) == 0:
                self._solBest.append(copy.deepcopy(sol))
            elif self.is_better(sol) == 1:
                self._solBest = []
                self._solBest.append(copy.deepcopy(sol))
        # CASO RICORSIVO
        else:
            while pos < len(self._listEvents):
                evento = self._listEvents[pos]
                self.pop_cumulato += evento.customers_affected
                pos += 1
                parziale.add(evento)  # aggiungo l'evento al parziale
                if self.condizioni(evento, maxY, maxH):  #controllo le condizioni
                    self.ricorsione(parziale, maxY, maxH, pos)  #faccio ripartire la ricorsione con la copia
                self.backtracking(parziale, evento)

    def backtracking(self, parziale, evento):
        """
        Esegue le operazioni di backtracking
        """
        parziale.remove(evento)
        self.ore_cumulato -= (evento.date_event_finished - evento.date_event_began).total_seconds()
        self.pop_cumulato -= evento.customers_affected

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
        self.ore_cumulato += durata
        if self.ore_cumulato > maxH * 3600:
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

    def is_better(self, soluzione):
        """
        Se trovo una soluzione con le stesse persone la aggiungo, altrimenti azzero la lista e aggiungo la migliore
        """
        if len(self._solBest) == 0:
            return 0
        else:
            if soluzione[1] == self._solBest[0][1]:
                return 0  #0 corrisponde al solo append
            elif soluzione[1] > self._solBest[0][1]:
                return 1  #1 corrisponde a resettare solBest e poi append

    def loadEvents(self, nerc):
        self._listEvents = DAO.getAllEvents(nerc)

    def loadNerc(self):
        self._listNerc = DAO.getAllNerc()

    @property
    def listNerc(self):
        return self._listNerc
