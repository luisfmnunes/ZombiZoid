from nextcord import Embed
from nextcord.ext import menus

class EmbededModsPageSource(menus.ListPageSource):
  
  def __init__(self, data, per_page=30):
    super().__init__(data, per_page=per_page)

  async def  format_page(self, menu, entries):
    embed = Embed(title=f"Mods Page {menu.current_page + 1}", description="\n".join(entries))
    embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
    return embed