import wx
from repo_list import RepoListDialog
from actions import GithubActions

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		super(MainFrame, self).__init__(parent, title=title, size=(600, 400))
		
		self.init_ui()
		self.init_github_api()
		
	def init_ui(self):
		menubar = wx.MenuBar()
		repo_menu = wx.Menu()
		list_repos_item = repo_menu.Append(wx.ID_ANY, "Administrar repositorios\tCtrl+A")
		create_repo_item = repo_menu.Append(wx.ID_ANY, "Nuevo repositorio\tCtrl+N")
		menubar.Append(repo_menu, "Repositorios")
		self.SetMenuBar(menubar)
		
		self.Bind(wx.EVT_MENU, self.on_list_repos, list_repos_item)
		self.Bind(wx.EVT_MENU, self.on_create_repo, create_repo_item)
		self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
		
	def init_github_api(self):
		self.api = GithubActions()
		user_info = self.api.authenticate_with_github()
		self.username = user_info['login']
		self.SetTitle(f"GitHub Client - {self.username}")
		
	def on_list_repos(self, event):
		dialog = RepoListDialog(self)
		dialog.load_repos()
		dialog.ShowModal()
		dialog.Destroy()
		
	def on_create_repo(self, event):
		repo_name = wx.GetTextFromUser("Nombre del nuevo repositorio:", "Crear Repositorio")
		if not repo_name:
			return
		
		private = wx.MessageBox("¿Deseas que el repositorio sea privado?", "Configuración de privacidad", 
								wx.YES_NO | wx.ICON_QUESTION) == wx.YES
		
		description = wx.GetTextFromUser("Descripción del repositorio (opcional):", "Crear Repositorio")
		
		try:
			new_repo = self.api.create_repository(repo_name, private, description)
			wx.MessageBox(f"Repositorio creado: {new_repo['html_url']}", "Éxito", wx.OK | wx.ICON_INFORMATION)
		except Exception as e:
			wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
			
	def on_key_down(self, event):
		event.Skip()  # No es necesario manejar la tecla Escape aquí

class MyApp(wx.App):
	def OnInit(self):
		frame = MainFrame(None, "GitHub client")
		frame.Show(True)
		return True

if __name__ == '__main__':
	app = MyApp()
	app.MainLoop()