import requests
import json
import os
import base64
import wx
# Obtener la ruta de la carpeta "Documentos" del usuario
documents_path = os.path.join(os.environ['USERPROFILE'], 'Documents')

# Crear la carpeta "github_client" dentro de "Documentos"
github_client_folder = os.path.join(documents_path, 'github_client')

if not os.path.exists(github_client_folder):
    os.makedirs(github_client_folder)  # Crear la carpeta si no existe

# Definir la ruta completa del archivo token.json dentro de la carpeta github_client
TOKEN_FILE = os.path.join(github_client_folder, 'token.json')

class GithubActions:
	def __init__(self):
		self.token = self.load_token()

	def load_token(self):
		"""Carga el token desde el archivo, o pide al usuario si no existe."""
		if os.path.exists(TOKEN_FILE):
			with open(TOKEN_FILE, 'r') as f:
				data = json.load(f)
				return data.get('token')
		else:
			return self.prompt_for_token()

	def prompt_for_token(self):
		"""Solicita al usuario que ingrese el token si no está presente."""
		with wx.TextEntryDialog(None, "Por favor ingresa tu token de GitHub:", "Autenticación") as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				token = dialog.GetValue()
				self.save_token(token)
				return token
			else:
				wx.MessageBox("El token es necesario para continuar.", "Error", wx.OK | wx.ICON_ERROR)
				raise Exception("Token no ingresado.")

	def save_token(self, token):
		"""Guarda el token en un archivo JSON."""
		with open(TOKEN_FILE, 'w') as f:
			json.dump({"token": token}, f)

	def authenticate_with_github(self):
		"""Autentica al usuario con GitHub usando el token."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}
		response = requests.get('https://api.github.com/user', headers=headers)
		if response.status_code == 200:
			return response.json()
		else:
			raise Exception(f"Error de autenticación: {response.status_code}")

	def list_repositories(self):
		"""Lista los repositorios del usuario autenticado."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}
		response = requests.get('https://api.github.com/user/repos', headers=headers)
		if response.status_code == 200:
			return response.json()
		else:
			raise Exception(f"Error al listar repositorios: {response.status_code}")

	def delete_repository(self, repo_name):
		"""Elimina un repositorio del usuario autenticado."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}
		username = self.authenticate_with_github()['login']
		url = f'https://api.github.com/repos/{username}/{repo_name}'
		response = requests.delete(url, headers=headers)
		return response.status_code == 204

	def edit_repository(self, repo_name, new_name=None, new_description=None):
		"""Edita el nombre o la descripción del repositorio si se proporciona."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}
		username = self.authenticate_with_github()['login']
		url = f'https://api.github.com/repos/{username}/{repo_name}'
		payload = {}
		if new_name:
			payload['name'] = new_name
		if new_description:
			payload['description'] = new_description

		response = requests.patch(url, json=payload, headers=headers)
		return response.status_code == 200
		
	def create_repository(self, repo_name, private=False, description=None):
		"""Crea un nuevo repositorio en GitHub."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}

		# Define la URL para crear un repositorio
		url = 'https://api.github.com/user/repos'
		# Prepara el payload con los datos del nuevo repositorio
		payload = {
			'name': repo_name,
			'private': private,
		}

		if description:
			payload['description'] = description

		# Realiza la solicitud POST para crear el repositorio
		response = requests.post(url, json=payload, headers=headers)

		if response.status_code == 201:
			return response.json()  # Devuelve los datos del nuevo repositorio
		else:
			raise Exception(f"Error al crear el repositorio: {response.status_code} - {response.text}")

	def upload_file(self, repo_name, file_path, commit_message):
		"""Sube un archivo a un repositorio específico."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}

		username = self.authenticate_with_github()['login']
		url = f'https://api.github.com/repos/{username}/{repo_name}/contents/{os.path.basename(file_path)}'

		with open(file_path, 'rb') as f:
			content = f.read()

		# Codificar el contenido en base64
		encoded_content = base64.b64encode(content).decode()

		payload = {
			'message': commit_message,
			'content': encoded_content,
		}

		response = requests.put(url, json=payload, headers=headers)

		if response.status_code in (201, 200):
			return response.json()
		else:
			raise Exception(f"Error al subir el archivo: {response.status_code}, {response.text}")

	def list_files(self, repo_name, path=''):
		"""Lista los archivos en un repositorio específico."""
		if not self.token:
			raise Exception("Token no encontrado")
		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}

		username = self.authenticate_with_github()['login']
		url = f'https://api.github.com/repos/{username}/{repo_name}/contents/{path}'

		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			return response.json()
		else:
			raise Exception(f"Error al listar archivos: {response.status_code}, {response.text}")

	def list_commits(self, repo_name):
		"""Lista los commits en un repositorio específico, mostrando información esencial."""
		if not self.token:
			raise Exception("Token no encontrado")

		headers = {
			'Authorization': f'token {self.token}',
			'Accept': 'application/vnd.github.v3+json',
		}

		# Autenticación y obtención del nombre de usuario
		username = self.authenticate_with_github()['login']
		url = f'https://api.github.com/repos/{username}/{repo_name}/commits'

		# Realizar la petición
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			commits = response.json()

			# Crear una lista de strings con la información formateada
			commit_list = []
			for commit in commits:
				essential_info = f"""
				SHA: {commit['sha']}
				Autor: {commit['commit']['author']['name']}
				Fecha: {commit['commit']['author']['date']}
				Mensaje: {commit['commit']['message']}
				URL: {commit['html_url']}
				---------------------------
				"""
				commit_list.append(essential_info.strip())  # Eliminar espacios en blanco alrededor

			# Unir todos los commits con un salto de línea entre ellos
			return "\n\n".join(commit_list)
		else:
			raise Exception(f"Error al listar commits: {response.status_code}, {response.text}")