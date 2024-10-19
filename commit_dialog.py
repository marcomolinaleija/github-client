import wx

class CommitDialog(wx.Dialog):
	def __init__(self, parent, title, commits):
		super().__init__(parent, title=title, size=(600, 400))
		
		panel = wx.Panel(self)
		
		# Crear un cuadro de texto de solo lectura
		self.label_text = wx.StaticText(panel, label="Commits:")
		self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		# Añadir los commits al cuadro de texto
		for commit in commits:
			self.text_ctrl.AppendText(f"SHA: {commit.get('sha', 'N/A')}\n")
			self.text_ctrl.AppendText(f"Autor: {commit.get('author', 'N/A')}\n")
			self.text_ctrl.AppendText(f"Fecha: {commit.get('date', 'N/A')}\n")
			self.text_ctrl.AppendText(f"Mensaje: {commit.get('message', 'N/A')}\n")
			self.text_ctrl.AppendText(f"URL: {commit.get('url', 'N/A')}\n")
			self.text_ctrl.AppendText("-" * 50 + "\n\n")
		
		# Botón para cerrar el diálogo
		close_button = wx.Button(panel, label="&Cerrar")
		close_button.Bind(wx.EVT_BUTTON, self.on_close)
		
		# Organizar los elementos en el panel
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.label_text, 1, wx.EXPAND | wx.ALL, 10)
		sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
		sizer.Add(close_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		
		panel.SetSizer(sizer)
	
	def on_close(self, event):
		self.EndModal(wx.ID_CLOSE)