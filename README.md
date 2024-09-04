# api_clima
Prueba técnica

Descripcion:
 	Este proyecto realiza la creación de usuario para poder realizar una consulta de clima en una ciudad y guarda el resultado en base de datos.

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

# Instalación y cambios para correr el proyecto

- Se instalo una versión un poco mas nueva de pyenv

```sh
	pyenv install 3.12.5
	pyenv global 3.12.5
	pyenv virtualenv 3.12.5 api_clima_3_12_5
	pyenv local api_clima_3_12_5
	pyenv activate api_clima_3_12_5

	pip install --no-cache-dir -r requirements.txt
```