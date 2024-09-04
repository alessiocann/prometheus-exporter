import random
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import datetime
import time
import statistics
from prometheus_client import start_http_server
from prometheus_api_client import PrometheusConnect, MetricsList, Metric
import datetime


MINUTES = 10 #Parametro che definisce la finestra temporale




def get_metrics_name(): #Restituisce tutte le metriche su Prometheus
    metrics_name = []
    all_metrics = prom.all_metrics()
    for metric in all_metrics:
        if(('_max' in metric)and(metric[-1] == "x")): #Controlla che la metrica letta non sia già un massimo creato in precedenza ed esistente.
            continue  #Nel caso in cui la condizione fosse vera, la metrica verrà scartata affinchè possa essere ricalcolata da questo exporter.
        elif(('_min' in metric)and(metric[-1] == "n")): #Controlla che la metrica letta non sia già un minimo creato in precedenza ed esistente.
            continue
        elif(('_avg' in metric)and(metric[-1] == "g")): #Controlla che la metrica letta non sia già una media creata in precedenza ed esistente.
            continue
        else:
            metrics_name.append(metric)
    
    return metrics_name







def exist_metric(name, time): #Controlla se la metrica esiste
    metric = prom.get_metric_range_data(name,
    start_time=(datetime.datetime.now() - datetime.timedelta(seconds=time)),
    end_time=datetime.datetime.now()
    )
    
    if(len(metric) == 0):
        return False
    
    return True



def get_metrics_value(name, job, time): #Restituisce i valori delle metriche dato il nome della metrica il job e il nome
    metric_value_list = []

    metric = prom.get_metric_range_data(name + "{job='" + job + "'}",
    start_time=(datetime.datetime.now() - datetime.timedelta(minutes=time)),
    end_time=datetime.datetime.now()
    )
    
    if len(metric) == 0:
        return
    
    metric = str(metric).split()
    for i in range(len(metric)):
        if "'values':" == metric[i]:
            while(i < (len(metric)-1))and(metric[i+1] != "{'metric':"):
                metric_value = metric[i+2]
                i+=2
                metric_value = metric_value.replace("'", "")
                metric_value = metric_value.replace("],","")
                metric_value = metric_value.replace("]]},","")
                metric_value = metric_value.replace("]]}]","")
                metric_value_list.append(float(metric_value))
                
    return metric_value_list



def get_job_list(): #Restituisce tutti i job attivi su prometheus
    job_list = prom.custom_query(query="up == 1")
    job_list = str(job_list).split()
    job_list=job_list[6::10]
    for job in range(len(job_list)):
        job_list[job] = job_list[job].replace("'","")
        job_list[job] = job_list[job].replace("},","")
    return job_list



class MaxMinAvgCollector(object): #Collettore
    def __init__(self):
        pass
    def collect(self): 
        for metric_name in metrics_name:
            if(exist_metric(metric_name, MINUTES) == True): #Controlla se la metrica è esistente o è un residuo della cache
                for job in job_list:
                    metric_value_list = get_metrics_value(metric_name, job, MINUTES)
                    if(metric_value_list == None):
                        continue
                    
                    #print(metric_value_list) 
                    metric_max_value = max(metric_value_list) #Calcola il massimo valore della metrica
                    gauge_max = GaugeMetricFamily(metric_name + "_max", "Massimo della metrica " + metric_name, labels=["old_job"])
                    gauge_max.add_metric([job], metric_max_value)
                    yield gauge_max #Ritorna l'oggetto
                    
                    metric_min_value = min(metric_value_list) #Calcola il minimo valore della metrica  
                    gauge_min = GaugeMetricFamily(metric_name + "_min", "Minimo della metrica " + metric_name, labels=["old_job"])
                    gauge_min.add_metric([job], metric_min_value)
                    yield gauge_min #Ritorna l'oggetto
                    
                    metric_avg_value =  statistics.mean(metric_value_list) #Calcola la media valore della metrica             
                    gauge_avg = GaugeMetricFamily(metric_name + "_avg", "Media della metrica " + metric_name, labels=["old_job"])
                    gauge_avg.add_metric([job], metric_avg_value)
                    yield gauge_avg #Ritorna l'oggetto


                    
                    


if __name__ == "__main__":
    prom = PrometheusConnect(url ="http://localhost:9090", disable_ssl=True) #Connessione a prometheus
    metrics_name = get_metrics_name() 
    job_list = get_job_list()
    start_http_server(8000)
    REGISTRY.register(MaxMinAvgCollector()) #Inserisco il collettore nel registro
    while True:
        time.sleep(10) #Intervallo tra una collezione e l'altra
        