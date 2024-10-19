import wx
import os
from actions import GithubActions
from commit_dialog import CommitDialog


class RepoListDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Lista de Repositorios", size=(500, 400))

		self.api = GithubActions()

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.repo_list_label = wx.StaticText(self, label="Repositorios:")
		self.repo_list = wx.ListCtrl(self, style=wx.LC_REPORT)
		self.repo_list.InsertColumn(0, 'Nombre', width=150)
		self.repo_list.InsertColumn(1, 'Descripción', width=300)
		self.repo_list.InsertColumn(2, 'Lenguaje', width=100)

		sizer.Add(self.repo_list_label, 1, wx.EXPAND | wx.ALL, 10)
		sizer.Add(self.repo_list, 1, wx.EXPAND | wx.ALL, 10)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.edit_button = wx.Button(self, label="&Editar")
		self.delete_button = wx.Button(self, label="&Eliminar")
		self.list_commits = wx.Button(self, label="&Commits del repositorio")
		self.list_files_button = wx.Button(self, label="&Listar Archivos")
		self.upload_file_button = wx.Button(self, label="&Cargar Archivos")
		self.close_list = wx.Button(self, label="Cerrar lista de repositorios")

		btn_sizer.Add(self.edit_button, 0, wx.ALL, 5)
		btn_sizer.Add(self.delete_button, 0, wx.ALL, 5)
		btn_sizer.Add(self.list_commits, 0, wx.ALL, 5)
		btn_sizer.Add(self.list_files_button, 0, wx.ALL, 5)
		btn_sizer.Add(self.upload_file_button, 0, wx.ALL, 5)
		btn_sizer.Add(self.close_list, 0, wx.ALL, 5)

		sizer.Add(btn_sizer, 0, wx.CENTER)

		self.SetSizer(sizer)

		# Bind events to buttons
		self.edit_button.Bind(wx.EVT_BUTTON, self.on_edit_repo)
		self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete_repo)
		self.list_commits.Bind(wx.EVT_BUTTON, self.on_list_commits)
		self.list_files_button.Bind(wx.EVT_BUTTON, self.on_list_files)
		self.upload_file_button.Bind(wx.EVT_BUTTON, self.on_upload_file)
		self.close_list.Bind(wx.EVT_BUTTON, self.on_close_dialog)

		self.load_repos()  # Cargar repositorios al inicializar el diálogo

	def load_repos(self):
		"""Cargar repositorios desde la API de GitHub."""
		self.repo_list.DeleteAllItems()  # Limpiar la lista antes de añadir repos
		try:
			repos = self.api.list_repositories()
			for repo in repos:
				name = repo['name'] if repo['name'] else ""
				description = repo.get('description', "") if repo.get('description', None) else ""
				language = repo.get('language', "") if repo.get('language', None) else ""

				index = self.repo_list.InsertItem(self.repo_list.GetItemCount(), name)
				self.repo_list.SetItem(index, 1, description)
				self.repo_list.SetItem(index, 2, language)
		except Exception as e:
			wx.MessageBox(f"Error al obtener repositorios: {e}", "Error", wx.OK | wx.ICON_ERROR)

	def on_edit_repo(self, event):
		"""Abrir un diálogo para editar el repositorio seleccionado."""
		selected_index = self.repo_list.GetFirstSelected()
		if selected_index == -1:
			wx.MessageBox("No has seleccionado ningún repositorio.", "Error", wx.OK | wx.ICON_ERROR)
			return

		repo_name = self.repo_list.GetItemText(selected_index)
		new_name = wx.GetTextFromUser(f"Nuevo nombre para '{repo_name}':", "Editar nombre", repo_name)
		new_description = wx.GetTextFromUser(f"Nueva descripción para '{repo_name}':", "Editar descripción")

		if new_name or new_description:
			success = self.api.edit_repository(repo_name, new_name, new_description)
			if success:
				wx.MessageBox(f"Repositorio '{repo_name}' actualizado correctamente.", "Éxito", wx.OK | wx.ICON_INFORMATION)
				self.load_repos()
			else:
				wx.MessageBox(f"Error al actualizar el repositorio '{repo_name}'.", "Error", wx.OK | wx.ICON_ERROR)

	def on_delete_repo(self, event):
		"""Eliminar el repositorio seleccionado."""
		selected_index = self.repo_list.GetFirstSelected()
		if selected_index == -1:
			wx.MessageBox("No has seleccionado ningún repositorio.", "Error", wx.OK | wx.ICON_ERROR)
			return

		repo_name = self.repo_list.GetItemText(selected_index)
		confirmation = wx.MessageBox(f"¿Estás seguro de eliminar el repositorio '{repo_name}'?", "Confirmar", wx.YES_NO | wx.ICON_WARNING)

		if confirmation == wx.YES:
			success = self.api.delete_repository(repo_name)
			if success:
				wx.MessageBox(f"Repositorio '{repo_name}' eliminado correctamente.", "Éxito", wx.OK | wx.ICON_INFORMATION)
				self.load_repos()
			else:
				wx.MessageBox(f"Error al eliminar el repositorio '{repo_name}'.", "Error", wx.OK | wx.ICON_ERROR)

	def on_list_commits(self, event):
		selected_index = self.repo_list.GetFirstSelected()
		if selected_index == -1:
			wx.MessageBox("No haz seleccionado ningún repositorio", "Error", wx.ICON_ERROR)
			return
		repo_name = self.repo_list.GetItemText(selected_index)
		commits = self.api.list_commits(repo_name)
		if commits:
			# Procesar los commits como cadenas de texto
			commit_list = []
			current_commit = {}
			for line in commits.split('\n'):
				line = line.strip()
				if line.startswith("SHA:"):
					if current_commit:
						commit_list.append(current_commit)
					current_commit = {'sha': line.split("SHA:")[1].strip()}
				elif line.startswith("Autor:"):
					current_commit['author'] = line.split("Autor:")[1].strip()
				elif line.startswith("Fecha:"):
					current_commit['date'] = line.split("Fecha:")[1].strip()
				elif line.startswith("Mensaje:"):
					current_commit['message'] = line.split("Mensaje:")[1].strip()
				elif line.startswith("URL:"):
					current_commit['url'] = line.split("URL:")[1].strip()
			
			if current_commit:
				commit_list.append(current_commit)
			
			# Crear y mostrar el diálogo de commits
			commit_dialog = CommitDialog(self, f"Commits de {repo_name}", commit_list)
			commit_dialog.ShowModal()
			commit_dialog.Destroy()
			#wx.MessageBox(f"commits del repositorio {repo_name}: {commits}", "Información", wx.ICON_INFORMATION)
	def on_list_files(self, event):
		"""Listar archivos del repositorio seleccionado."""
		selected_index = self.repo_list.GetFirstSelected()
		if selected_index == -1:
			wx.MessageBox("No has seleccionado ningún repositorio.", "Error", wx.OK | wx.ICON_ERROR)
			return

		repo_name = self.repo_list.GetItemText(selected_index)
		try:
			files = self.api.list_files(repo_name)
			if files:
				file_names = "\n".join(file['name'] for file in files)
				wx.MessageBox(f"Archivos en '{repo_name}':\n{file_names}", "Archivos", wx.OK | wx.ICON_INFORMATION)
			else:
				wx.MessageBox(f"No hay archivos en '{repo_name}'.", "Sin archivos", wx.OK | wx.ICON_INFORMATION)
		except Exception as e:
			wx.MessageBox(f"Error al listar archivos: {e}", "Error", wx.OK | wx.ICON_ERROR)

	def on_upload_file(self, event):
		"""Subir archivos al repositorio seleccionado."""
		selected_index = self.repo_list.GetFirstSelected()
		if selected_index == -1:
			wx.MessageBox("No has seleccionado ningún repositorio.", "Error", wx.OK | wx.ICON_ERROR)
			return

		repo_name = self.repo_list.GetItemText(selected_index)
		file_dialog = wx.FileDialog(
			self,
			"Selecciona archivos para subir",
			"",
			"",
			"*.*",
			wx.FD_OPEN | wx.FD_MULTIPLE  # Permitir selección múltiple
		)

		if file_dialog.ShowModal() == wx.ID_OK:
			file_paths = file_dialog.GetPaths()  # Obtener todos los archivos seleccionados
			commit_message = wx.GetTextFromUser("Mensaje del commit:", "Subir Archivos")
			if commit_message:
				for file_path in file_paths:
					try:
						success = self.api.upload_file(repo_name, file_path, commit_message)
						if success:
							wx.MessageBox(f"Archivo '{os.path.basename(file_path)}' subido con éxito.", "Éxito", wx.OK | wx.ICON_INFORMATION)
						else:
							wx.MessageBox(f"Error al subir el archivo '{os.path.basename(file_path)}'.", "Error", wx.OK | wx.ICON_ERROR)
					except Exception as e:
						wx.MessageBox(f"Error al subir el archivo '{os.path.basename(file_path)}': {e}", "Error", wx.OK | wx.ICON_ERROR)

		file_dialog.Destroy()

	def on_close_dialog(self, event):
		self.Hide()
