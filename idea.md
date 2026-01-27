1)manager chiama la post per i report
2)l'endpoint mette nel db il report con id e status = pending
3)l'endpoint ritorna l'id del report e il suo status (status possibili sono pending, running, done, failed(?))
4)visto che mi hanno detto che potrebbe richiedere molto tempo penso ad un job asincrono come la generazione dati in wallabies??
5)vengono aggiunti a delle code??? vengono processati nella notte?? idk questo punto ma pensavo di creare un task da lanciare con qualche servizio (qualcosa di redis? mqtt? celery? devo capire anche questo)
6)quando viene chiamata la get restituisce tutti i report in questo modo: se sono completati li restituisce completi, senno' stato e id.

