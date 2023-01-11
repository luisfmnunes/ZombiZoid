from nextcord import Embed
from nextcord.ext import menus

class EmbededModsPageSource(menus.ListPageSource):
  
  def __init__(self, data, per_page=30):
    super().__init__(data, per_page=per_page)

  async def  format_page(self, menu, entries):
    embed = Embed(title=f"Mods Page {menu.current_page + 1}")
    for e in entries:
      mod_id, mod_title = e.split(sep=": ")
      embed.add_field(name=mod_title, value=mod_id)
    embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
    return embed
