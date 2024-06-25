# api_clima
Prueba técnica

Descripcion:
	Servicio que se encarga de registrar el clima de una ciudad

Requerimientos:
```
	pyenv 2.4.2
	Python 3.12.4
	Docker 23.0.3
```

Instalación:
```
	git clone https://github.com/AntonyDicio/api_clima.git
	cd api_clima

	pyenv install 3.12.4
	pyenv global 3.12.4
	pyenv virtualenv 3.12.4 api_clima_3_12_4
	pyenv local api_clima_3_12_4
	pyenv activate api_clima_3_12_4

	pip install --no-cache-dir -r requirements.txt
```

Ejecución:
```
	cd api_clima
	uvicorn main:app --reload
```