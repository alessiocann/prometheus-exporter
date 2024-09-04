SO: macOS Monterey 12.6 (ARM/M1-APPLE SILICON)

Python: 3.10

Docker: Docker Desktop 4.12.0

Prometheus: 2.37.1

L'exporter è stato implementato utilizzando le seguenti funzioni: get_metric_name(), exist_metric(), get_metrics_value(), get_job_list().

Mediante get_metric_name(), sono stati recuperati tutti i nomi delle metriche disponibili su prometheus. All'interno della funzione verrà effettuato un controllo affinchè, le metriche già esistenti contenenti il suffisso '_max', '_min' o '_avg' siano scartate, per evitare che possa essere calcolato "il massimo del massimo" e simili. La funzione restituirà una lista con tutti i nomi delle metriche disponibili su prometheus.

Successivamente, medinate get_job_list verrà restituita la lista di tutti i job attivi su Prometheus, utilizzando la PromQuery 'up' e prendendo soltanto i valori uguali a '1'.

Infine è stato creato un collettore MaxMinAvgCollector, ove sono state esposte le metriche. E' stato effettuato un controllo per verificare che la metrica sia esistente (dato che possono rimanere in cache dei residui indesiderati) e nel caso in cui la condizione sia verificata, viene effettuata una PromQuery che restituirà una lista di valori che verranno poi opportunamente elaborati per ottenere il massimo, il minimo e la media di ogni job di ogni metrica.
Il job di cui è stato calcolato il massimo, minimo o media è indicato nella label "old_job".

Vengono restituiti i valori 'raschiati' negli ultimi 10 minuti. E' possibile modificare la finestra temporale, modificando il parametro 'MINUTES'.

L'intervallo presente tra un collettore e il successivo è stato impostato a 10 secondi.

NB: L'exporter exporter verrà esposto sulla porta 8000. Se si vuole ottenere la lista delle metriche disponibili: localhost:8000




