Для запуска приложения необходимо установить докер и выполнить команды:   
1. `cd app`
2. `docker build -t python-image .`
3. `docker run --rm -it -p 8050:8050 --name python python-image`   

И открыть страницу http://0.0.0.0:8050  